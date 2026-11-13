"""M2.1: deterministic script-to-shot drafts and REAL measured segment-level WAV timing.

No LLM inference, translation, voice synthesis, forced word-level alignment, footage download,
rights adjudication, or public publishing is implied. Humans supply source script, translations,
and per-segment narration. Project/source/approval revisions are strictly bound.
"""
from __future__ import annotations
import hashlib, io, json, re, shutil, subprocess, wave, os
from pathlib import Path
from typing import Literal
from fastapi import HTTPException, UploadFile, File
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field, ConfigDict, model_validator
from . import db
from .studio_contracts import StudioPlanIn
from .studio_routes import sha_file

MAX_WAV_BYTES = 8 * 1024 * 1024
RATE = 16000
PAUSE_FRAMES = 2880  # 180ms per shot; deterministic

class DirectorDraftIn(BaseModel):
    model_config = ConfigDict(extra='forbid')
    locale: str = Field(pattern=r'^[a-z]{2}-[A-Z]{2}$')
    translated_script: str | None = Field(default=None,min_length=25,max_length=12000)
    locale_reviewed: bool = False
    @model_validator(mode='after')
    def translation_rules(self):
        if self.translated_script is not None and not self.locale_reviewed:
            raise ValueError('Translated text requires owner review of names, facts, numbers and idioms')
        return self


def make_segments(text: str) -> list[str]:
    """Preserve all substantive script words; never auto-add source claims or silently truncate."""
    raw = [s.strip() for s in re.split(r'(?<=[.!?।॥])\s+|\n+',text) if s.strip()]
    segments: list[str] = []
    for section in raw:
        words = section.split()
        if not words:continue
        # Block on exceptionally long unbroken words; don't cut the original text.
        if any(len(w)>90 for w in words):raise ValueError('Word too long for captions: simplify the original script')
        while len(words)>19:
            take = 15
            segments.append(' '.join(words[:take]));words=words[take:]
        if words:segments.append(' '.join(words))
    if not segments:raise ValueError('Empty script')
    # For a short one-sentence narration create two beats without adding words.
    if len(segments)==1:
        words=segments[0].split()
        if len(words)<8:raise ValueError('At least eight words needed for a meaningful HOOK and PAYOFF')
        mid=len(words)//2;segments=[' '.join(words[:mid]),' '.join(words[mid:])]
    if len(segments)>12:raise ValueError('Current CPU Studio supports 12 shots maximum; split into a new video project')
    if any(len(s)>160 for s in segments):raise ValueError('A sentence segment exceeds 160 caption characters; shorten sentence')
    return segments


def draft_description(segments:list[str], domain:str, locale:str, reviewed:bool, voice:bool):
    return {'engine':'M2.1_DETERMINISTIC_SCRIPT_SEGMENTER',
            'shot_count':len(segments),'domain_visual_policy':domain,
            'locale':locale,'localization_review':reviewed,
            'voice_aligned':voice,'word_level_alignment':False,
            'claim_verification':'NOT_PERFORMED_BY_CREATIVE_DIRECTOR',
            'auto_translation':False,'auto_video_generation':False,'publish_ready':False}


def read_frames(path):
    with wave.open(str(path),'rb') as wf:
        if wf.getnchannels()!=1 or wf.getsampwidth()!=2 or wf.getframerate()!=RATE or wf.getcomptype()!='NONE':
            raise ValueError('Measured segment not canonical PCM16 mono 16000 Hz')
        frames=wf.getnframes();raw=wf.readframes(frames)
    if not frames or len(raw)!=frames*2:raise ValueError('Corrupt segment WAV')
    return frames,raw


def store_normalized_wav(upload:bytes, dest:Path)->int:
    """Validate then convert user WAV through installed local FFmpeg. No network services."""
    if not shutil.which('ffmpeg'):raise HTTPException(503,'Local FFmpeg needed for voice normalization')
    try:
        with wave.open(io.BytesIO(upload),'rb') as wf:
            if wf.getnchannels() not in (1,2) or wf.getsampwidth() not in (1,2,3,4) or wf.getframerate() not in range(8000,96001):
                raise ValueError('Unsupported WAV format')
            secs=wf.getnframes()/wf.getframerate()
            if secs<0.7 or secs>11.4:raise ValueError('Segment narration must be 0.7–11.4 seconds')
    except (EOFError,wave.Error,ValueError,ZeroDivisionError) as ex:
        raise HTTPException(422,'Invalid voice segment: '+str(ex))
    dest.parent.mkdir(parents=True,exist_ok=True)
    staging=dest.with_suffix('.incoming.wav');staging.write_bytes(upload)
    tmp=dest.with_suffix('.normalized.wav')
    try:
        cp=subprocess.run(['ffmpeg','-nostdin','-y','-v','error','-i',str(staging),'-vn','-ac','1','-ar',str(RATE),'-c:a','pcm_s16le',str(tmp)],capture_output=True,text=True,timeout=35)
        if cp.returncode:
            tmp.unlink(missing_ok=True)
            raise HTTPException(422,'WAV decode failed: '+cp.stderr[-180:])
        frames,raw=read_frames(tmp)
        if frames/RATE<.7 or frames/RATE>11.4:raise HTTPException(422,'Normalized WAV duration out of range')
        # A measured silence is not speech. Don't claim voice alignment for a silent file.
    except Exception:
        tmp.unlink(missing_ok=True)
        raise
    finally:
        staging.unlink(missing_ok=True)
    # Portable non-silent check without audioop (supports Python 3.12/3.13).
    import array, sys
    samples=array.array('h');samples.frombytes(raw)
    if sys.byteorder!='little':samples.byteswap()
    if max(abs(v) for v in samples[::max(1,len(samples)//20000)])<250:
        tmp.unlink(missing_ok=True)
        raise HTTPException(422,'Voice WAV appears silent; record audible narration')
    tmp.replace(dest)
    return frames


def mapped_claims(segments: list[str], source_script: str, links: list[dict]) -> list[list[str]]:
    """Conservatively map only exact, unambiguous script-linked quotes to scenes.

    No claim is asserted 'verified' here; the existing human evidence workflow
    remains authoritative. Claims spanning scene boundaries remain unmapped.
    """
    result=[[] for _ in segments]
    for link in links:
        quote=source_script[link['span_start']:link['span_end']]
        if not quote or source_script.count(quote)!=1:continue
        matches=[i for i,segment in enumerate(segments) if quote in segment]
        if len(matches)==1:result[matches[0]].append(link['claim_id'])
    return result


def draw_shots(segments:list[str], durations:list[int],locale:str,sport:str,has_voice:bool,
               claim_links:list[list[str]]|None=None):
    shots=[];captions=[];start=0
    for i,(segment,dur) in enumerate(zip(segments,durations)):
        role='HOOK' if i==0 else 'PAYOFF' if i==len(segments)-1 else 'EXPLANATION'
        # Do NOT print the exact narration sentence as a second large headline.
        # The heading is a generic, factual-neutral explanatory title; actual
        # narration remains verbatim in measurable captions.
        labels={
            'nfl':{
                'en-US':{'HOOK':'THE FORMATION QUESTION','CONTEXT':'FIELD CONTEXT','EXPLANATION':'READ THE POSITIONS','PAYOFF':'TACTICAL TAKEAWAY'},
                'hi-IN':{'HOOK':'फॉर्मेशन का सवाल','CONTEXT':'मैदान का संदर्भ','EXPLANATION':'स्थिति की व्याख्या','PAYOFF':'मुख्य सीख'}},
            'cricket':{
                'en-US':{'HOOK':'FIELD POSITIONING','CONTEXT':'FIELD CONTEXT','EXPLANATION':'TACTICAL EXPLANATION','PAYOFF':'KEY TAKEAWAY'},
                'hi-IN':{'HOOK':'फील्ड की रणनीति','CONTEXT':'मैदान का संदर्भ','EXPLANATION':'रणनीति की व्याख्या','PAYOFF':'मुख्य सीख'}}}
        language='hi-IN' if locale.startswith('hi-') else 'en-US'
        headline_map=labels.get(sport,labels['nfl']).get(language,labels['nfl']['en-US'])
        heading=headline_map.get(role,'EXPLANATION')
        # Only a brief role cue, not a second copy of the narrated sentence.
        cue=('ORIGINAL ANALYSIS' if i==0 else 'KEY TAKEAWAY' if i==len(segments)-1 else None)
        overlays=([{'text':cue,'start_ms':260,'end_ms':min(1200,dur-220),
                    'anchor':'LOWER_THIRD','style':'LABEL'}] if cue else [])
        shots.append({'role':role,'duration_ms':dur,'headline':heading,
            'visual':{'kind':'ORIGINAL_DIAGRAM','motion':'ILLUSTRATIVE_ROUTE'},'claim_ids':(claim_links[i] if claim_links else []),
            'overlays':overlays})
        if has_voice:
            captions.append({'start_ms':start,'end_ms':start+dur-round(PAUSE_FRAMES*1000/RATE),'text':segment})
        start+=dur
    return {'locale':locale,'locale_reviewed':False,'music_asset_id':None,
            'shots':shots,'captions':captions,
            'captions_provenance':'SEGMENT_TIMED_MEASURED' if has_voice else 'NOT_PROVIDED'}


def register_director(app):
    from . import main as m

    def get_draft(c,project_id,draft_id):
        p=m.from_project(c,project_id)
        d=db.one(c,'SELECT * FROM m21_director_drafts WHERE project_id=? AND draft_id=?',(project_id,draft_id))
        if not d:raise HTTPException(404,'Director draft not found in project')
        script=m.must(m.latest_script(c,project_id),'Script missing')
        valid_revision=(p['revision']==d['project_revision'])
        if d['status']=='ASSEMBLED':
            linked=db.one(c,'SELECT plan_id FROM m21_plan_audio WHERE draft_id=? AND project_id=?',(draft_id,project_id))
            valid_revision=bool(linked and p['revision']==d['project_revision']+1)
        if script['script_version_id']!=d['script_version_id'] or not valid_revision:
            raise HTTPException(409,'Director draft is stale after script/project revision; make a fresh draft')
        return p,script,d,json.loads(d['segments_json'])

    @app.get('/api/director/capabilities')
    def capabilities():
        return {'version':'M2.1','automatic_script_segmentation':True,
                'creative_draft':'DETERMINISTIC_NOT_LLM','locale_variants':'OWNER_SUPPLIED_TRANSLATION',
                'voice_source':'OWNER_RECORDED_WAV_PER_SHOT',
                'segment_alignment':'MEASURED_WAV_DURATION','word_level_forced_alignment':False,
                'automatic_dubbing':False,'optional_piper_opt_in':True,'youtube_upload':False,'publish_ready':False}

    @app.post('/api/projects/{project_id}/director/drafts')
    def create_draft(project_id:str,body:DirectorDraftIn):
        with db.transaction() as c:
            p=m.from_project(c,project_id)
            script=m.must(m.latest_script(c,project_id),'Save script before drafting')
            translated=body.translated_script is not None
            if body.locale!=p['locale'] and not translated:
                raise HTTPException(422,'Different locale requires owner-supplied script, not the original language silently reused')
            if translated and not body.locale_reviewed:
                raise HTTPException(422,'Translation review required')
            text=body.translated_script if translated else script['script_text']
            try:segments=make_segments(text)
            except ValueError as e:raise HTTPException(422,str(e))
            raw={'source_script_id':script['script_version_id'],'project_revision':p['revision'],
                 'locale':body.locale,'segments':segments,'human_reviewed_translation':bool(translated and body.locale_reviewed)}
            digest=m.sha(m.j(raw))
            old=db.one(c,'SELECT draft_id,status FROM m21_director_drafts WHERE draft_sha256=?',(digest,))
            if old:return {'draft_id':old['draft_id'],'segments':segments,'already_exists':True,'status':old['status'],
                           'limits':'12 shots, 90s total','publish_ready':False}
            did=m.uid()
            c.execute('INSERT INTO m21_director_drafts(draft_id,project_id,script_version_id,project_revision,locale,source_text_sha256,segments_json,visual_policy,translation_review,draft_sha256,status,created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
                (did,project_id,script['script_version_id'],p['revision'],body.locale,m.sha(text),m.j(segments),p['sport_id'],
                 'OWNER_REVIEWED_TRANSLATION' if translated else 'SOURCE_LANGUAGE',digest,'DRAFT',m.now()))
        return {'draft_id':did,'segments':segments,'already_exists':False,'status':'DRAFT',
                'notes':draft_description(segments,p['sport_id'],body.locale,bool(translated and body.locale_reviewed),False)}

    @app.get('/api/projects/{project_id}/director/drafts/{draft_id}')
    def read_draft(project_id:str,draft_id:str):
        with db.read() as c:
            p,script,d,segments=get_draft(c,project_id,draft_id)
            saved=db.many(c,'SELECT segment_index,sample_frames,audio_sha256 FROM m21_voice_segments WHERE draft_id=? ORDER BY segment_index',(draft_id,))
        return {'draft_id':draft_id,'project_id':project_id,'locale':d['locale'],
                'segments':[{'index':i,'text':s,'audio_ready':any(a['segment_index']==i for a in saved)} for i,s in enumerate(segments)],
                'voice_uploaded':len(saved),'status':d['status'],'expected_voice_segments':len(segments),'publish_ready':False}

    @app.get('/api/projects/{project_id}/director/plans/{plan_id}/captions.srt')
    def measured_captions_srt(project_id:str,plan_id:str):
        with db.read() as c:
            m.from_project(c,project_id)
            rec=db.one(c,'SELECT p.plan_json,a.voice_sha256 FROM m2_studio_plans p JOIN m21_plan_audio a ON a.plan_id=p.plan_id WHERE p.project_id=? AND p.plan_id=?',(project_id,plan_id))
            if not rec:raise HTTPException(404,'Director caption plan not found in project')
        cues=json.loads(rec['plan_json'])['captions']
        def fmt(ms):
            n=ms//1000
            return f'{n//3600:02}:{(n//60)%60:02}:{n%60:02},{ms%1000:03}'
        result=''.join(f"{i+1}\n{fmt(c['start_ms'])} --> {fmt(c['end_ms'])}\n{c['text']}\n\n" for i,c in enumerate(cues))
        return PlainTextResponse(result,media_type='application/x-subrip; charset=utf-8',headers={'Content-Disposition':'attachment; filename="ViralOS_segment_timed_captions.srt"'})

    @app.post('/api/projects/{project_id}/director/drafts/{draft_id}/voice/{segment_index}')
    async def upload_voice_segment(project_id:str,draft_id:str,segment_index:int,file:UploadFile=File(...)):
        with db.read() as c:
            p,script,d,segments=get_draft(c,project_id,draft_id)
        if d['status']!='DRAFT':raise HTTPException(409,'Already assembled; create fresh script/draft to change narration')
        if segment_index<0 or segment_index>=len(segments):raise HTTPException(422,'Segment index out of range')
        data=await file.read(MAX_WAV_BYTES+1)
        if not data or len(data)>MAX_WAV_BYTES:raise HTTPException(413,'Owner voice WAV must be <=8MB')
        target=m.OUT/project_id/'director'/draft_id/f'segment_{segment_index:02}.wav'
        frames=store_normalized_wav(data,target)
        with db.transaction() as c:
            get_draft(c,project_id,draft_id)
            c.execute('INSERT INTO m21_voice_segments(draft_id,segment_index,asset_relpath,audio_sha256,sample_rate,sample_frames,source_kind,uploaded_at) VALUES (?,?,?,?,?,?,?,?) ON CONFLICT(draft_id,segment_index) DO UPDATE SET asset_relpath=excluded.asset_relpath,audio_sha256=excluded.audio_sha256,sample_frames=excluded.sample_frames,source_kind=excluded.source_kind,uploaded_at=excluded.uploaded_at',
                      (draft_id,segment_index,str(target.relative_to(m.OUT)),sha_file(target),RATE,frames,'OWNER_RECORDED_WAV',m.now()))
        return {'segment_index':segment_index,'duration_ms':round(frames*1000/RATE),
                'alignment':'MEASURED_SEGMENT_DURATION_NOT_WORD_LEVEL','audio_sha256':sha_file(target)}

    @app.post('/api/projects/{project_id}/director/drafts/{draft_id}/synthesize-piper')
    def synthesize_piper_segments(project_id:str,draft_id:str):
        """Opt-in offline synthesis: requires a user-installed licensed model matching locale.

        Each Piper-generated segment is measured from its own normalized WAV. This is not
        translation, word alignment, natural prosody QA or voice cloning.
        """
        from . import tts
        with db.read() as c:
            p,script,d,segments=get_draft(c,project_id,draft_id)
        if d['status']!='DRAFT':raise HTTPException(409,'Director draft already assembled')
        cfg=tts.piper_config()
        if not cfg['installed'] or not cfg['licensed_model_reviewed']:
            raise HTTPException(409,'Install Piper and an appropriately licensed voice model; approve rights explicitly')
        if os.getenv('VIRALOS_PIPER_LOCALE')!=d['locale']:
            raise HTTPException(409,'Piper voice locale must match draft locale; set VIRALOS_PIPER_LOCALE')
        folder=m.OUT/project_id/'director'/draft_id
        folder.mkdir(parents=True,exist_ok=True)
        results=[]
        for i,text in enumerate(segments):
            scratch=folder/f'piper_{i:02}.wav'
            target=folder/f'segment_{i:02}.wav'
            try:
                tts.generate(text,scratch)
                frames=store_normalized_wav(scratch.read_bytes(),target)
                with db.transaction() as c:
                    get_draft(c,project_id,draft_id)
                    c.execute('INSERT INTO m21_voice_segments(draft_id,segment_index,asset_relpath,audio_sha256,sample_rate,sample_frames,source_kind,uploaded_at) VALUES (?,?,?,?,?,?,?,?) ON CONFLICT(draft_id,segment_index) DO UPDATE SET asset_relpath=excluded.asset_relpath,audio_sha256=excluded.audio_sha256,sample_frames=excluded.sample_frames,source_kind=excluded.source_kind,uploaded_at=excluded.uploaded_at',
                              (draft_id,i,str(target.relative_to(m.OUT)),sha_file(target),RATE,frames,'OPT_IN_LOCAL_PIPER',m.now()))
                results.append({'index':i,'duration_ms':round(frames*1000/RATE)})
            except HTTPException:raise
            except Exception as ex:
                raise HTTPException(422,f'Piper failed on segment {i}: {str(ex)[:170]}')
            finally:scratch.unlink(missing_ok=True)
        return {'voice_source':'OPT_IN_OFFLINE_PIPER','locale':d['locale'],
                'generated_segments':results,'pronunciation_review':'REQUIRED',
                'actual_duration_alignment':'MEASURED_PER_SEGMENT','word_level_alignment':False,
                'publish_ready':False}

    @app.post('/api/projects/{project_id}/director/drafts/{draft_id}/assemble')
    def assemble(project_id:str,draft_id:str):
        with db.read() as c:
            p,script,d,segments=get_draft(c,project_id,draft_id)
            if d['status']!='DRAFT':raise HTTPException(409,'Draft already assembled')
            assets=db.many(c,'SELECT * FROM m21_voice_segments WHERE draft_id=? ORDER BY segment_index',(draft_id,))
        if len(assets)!=len(segments) or [a['segment_index'] for a in assets]!=list(range(len(segments))):
            raise HTTPException(409,'Every segment needs an individually recorded and uploaded narration WAV')
        all_raw=[];lengths=[];source_hash=[]
        for item in assets:
            dest=(m.OUT/item['asset_relpath']).resolve()
            if m.OUT.resolve() not in dest.parents or not dest.is_file() or sha_file(dest)!=item['audio_sha256']:
                raise HTTPException(409,'Voice asset missing/changed since upload')
            frames,raw=read_frames(dest)
            if frames!=item['sample_frames']:raise HTTPException(409,'WAV duration changed since upload')
            all_raw.append(raw+b'\0\0'*PAUSE_FRAMES)
            lengths.append(round((frames+PAUSE_FRAMES)*1000/RATE))
            source_hash.append(item['audio_sha256'])
        if sum(lengths)>90000:raise HTTPException(422,'Total CPU preview exceeds 90 seconds')
        links=[]
        if d['translation_review']=='SOURCE_LANGUAGE':
            with db.read() as c:
                links=db.many(c,'SELECT claim_id,span_start,span_end FROM script_claim_links WHERE script_version_id=?',(script['script_version_id'],))
        claim_links=mapped_claims(segments,script['script_text'],links)
        plan=draw_shots(segments,lengths,d['locale'],p['sport_id'],True,claim_links)
        plan['locale_reviewed']=d['translation_review']=='OWNER_REVIEWED_TRANSLATION'
        try:plan=StudioPlanIn.model_validate(plan).model_dump(mode='json')
        except Exception as e:raise HTTPException(422,'Generated Studio plan validation failed: '+str(e)[:350])
        # Create atomic immutable project-bound Studio plan and audio. Never overwrite global voice.wav.
        plan_id=m.uid();revised=p['revision']+1
        final_dir=m.OUT/project_id/'director'/draft_id
        final_audio=final_dir/f'{plan_id}_voice.wav'
        final_dir.mkdir(parents=True,exist_ok=True)
        tmp=final_audio.with_suffix('.tmp')
        with wave.open(str(tmp),'wb') as f:
            f.setnchannels(1);f.setsampwidth(2);f.setframerate(RATE)
            for raw in all_raw:f.writeframes(raw)
        tmp.replace(final_audio)
        voice_hash=sha_file(final_audio)
        plan_sha=m.sha(m.j(plan)+'|script:'+script['script_version_id']+'|revision:'+str(revised))
        with db.transaction() as c:
            get_draft(c,project_id,draft_id)
            c.execute('UPDATE content_projects SET revision=?,updated_at=? WHERE project_id=?',(revised,m.now(),project_id))
            c.execute('INSERT INTO m2_studio_plans(plan_id,project_id,script_version_id,project_revision,locale,plan_json,plan_sha256,status,created_at) VALUES (?,?,?,?,?,?,?,?,?)',
                      (plan_id,project_id,script['script_version_id'],revised,d['locale'],m.j(plan),plan_sha,'DRAFT',m.now()))
            c.execute('INSERT INTO m21_plan_audio(plan_id,draft_id,project_id,script_version_id,voice_relpath,voice_sha256,audio_segments_sha256,duration_ms,alignment_provenance,created_at) VALUES (?,?,?,?,?,?,?,?,?,?)',
                      (plan_id,draft_id,project_id,script['script_version_id'],str(final_audio.relative_to(m.OUT)),voice_hash,m.sha(m.j(source_hash)),sum(lengths),'MEASURED_PER_SEGMENT_NOT_WORD_LEVEL',m.now()))
            c.execute("UPDATE m21_director_drafts SET status='ASSEMBLED' WHERE draft_id=?",(draft_id,))
        return {'plan_id':plan_id,'locale':d['locale'],'duration_ms':sum(lengths),
                'shot_count':len(segments),'caption_alignment':'MEASURED_SEGMENT_LEVEL_NOT_WORD_LEVEL',
                'voice_sha256':voice_hash,'mapped_existing_claim_ids':sum(len(x) for x in claim_links),
                'existing_script_claim_links':len(links),
                'voice_sources':sorted({a['source_kind'] for a in assets}), 'publish_ready':False,
                'next':'Use existing /api/projects/{id}/studio/queue and /api/studio/run-next for CPU MP4 preview'}
