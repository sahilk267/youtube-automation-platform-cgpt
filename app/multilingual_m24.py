"""M2.4 conservative localized production: independently reviewed Hindi/English scripts,
per-segment owner audio or opt-in local Piper, pronunciation cues, measured CPU video.
No automatic translation, pretrained model downloads, voice cloning or upload privileges.
"""
from __future__ import annotations
import hashlib, io, json, os, re, wave
from pathlib import Path
from typing import Literal
from fastapi import HTTPException, UploadFile, File
from fastapi.responses import FileResponse, PlainTextResponse
from pydantic import BaseModel, ConfigDict, Field
from . import db
from .director_m21 import RATE, PAUSE_FRAMES, make_segments, read_frames, store_normalized_wav, draw_shots
from .studio_contracts import StudioPlanIn
from .studio_routes import sha_file
from .studio_render import render_studio

class Strict(BaseModel):model_config=ConfigDict(extra='forbid')
class VariantIn(Strict):
    locale:Literal['en-US','hi-IN']
    reviewed_script:str=Field(min_length=25,max_length=12000)
    reviewer:str=Field(min_length=3,max_length=90)
    regional_notes:str=Field(min_length=15,max_length=500)
    words_names_numbers_and_meaning_reviewed:bool
    on_screen_language_reviewed:bool
class PronunciationIn(Strict):
    written:str=Field(min_length=1,max_length=55)
    speak_as:str=Field(min_length=1,max_length=85)
    reviewer:str=Field(min_length=3,max_length=80)
    reviewer_checked_identity_and_meaning:bool
class VoiceOptIn(Strict):
    owner_approved_model_license:bool
    owner_approved_pronunciation:bool


def current_variant(c,pid,vid):
    from . import main as m
    p=m.from_project(c,pid)
    v=db.one(c,'SELECT * FROM m24_variants WHERE variant_id=? AND project_id=?',(vid,pid))
    if not v:raise HTTPException(404,'Localization variant not found in selected project')
    script=m.latest_script(c,pid)
    if not script or script['script_version_id']!=v['source_script_version_id'] or script['content_sha256']!=v['source_script_sha256'] or p['revision']!=v['project_revision']:
        raise HTTPException(409,'Localized voice or video stale: source script/project changed')
    if m.sha(v['reviewed_text'])!=v['reviewed_text_sha256']:
        raise HTTPException(409,'Reviewed translation changed')
    return p,v,json.loads(v['segment_json'])


def verify_voices(c,pid,v,segments):
    from . import main as m
    rows=db.many(c,'SELECT * FROM m24_voices WHERE variant_id=? ORDER BY segment_index',(v['variant_id'],))
    if len(rows)!=len(segments) or [r['segment_index'] for r in rows]!=list(range(len(segments))):
        raise HTTPException(409,'Each localized segment requires its own voice WAV')
    result=[]
    for item in rows:
        dest=(m.OUT/item['file_relpath']).resolve()
        if m.OUT.resolve() not in dest.parents or not dest.is_file() or sha_file(dest)!=item['file_sha256']:
            raise HTTPException(409,'A localized voice segment was modified or deleted')
        frames,raw=read_frames(dest)
        if frames!=item['sample_frames']:raise HTTPException(409,'Voice duration changed')
        result.append((item,raw))
    return result


def locale_substitutions(text,lexicon):
    """Only explicit owner-reviewed phonetic cues affect TTS input, not captions."""
    for row in sorted(lexicon,key=lambda x:len(x['written']),reverse=True):
        term=row['written']
        text=re.sub(r'(?<!\w)'+re.escape(term)+r'(?!\w)',lambda _m:row['speak_as'],text,flags=re.I)
    return text


def fmt_srt_ms(ms):
    s=ms//1000
    return f'{s//3600:02}:{s//60%60:02}:{s%60:02},{ms%1000:03}'


def register_m24(app):
    from . import main as m

    @app.get('/api/m24/capabilities')
    def capabilities():
        from . import tts
        return {'supported_locales':['hi-IN','en-US'],'translation':'OWNER_SUPPLIED_AND_REVIEWED_ONLY',
                'dubbing':'SEPARATE_REVIEWED_TEXT_AND_MEASURED_VOICE_PER_LOCALE',
                'word_level_forced_alignment':'OPTIONAL_WHISPERX_LOCAL_CTC_PROPOSAL_OWNER_REVIEW_REQUIRED',
                'piper_opt_in_local_model':tts.piper_config()['installed'],
                'optional_ctc_forced_aligner':__import__('app.alignment_m24',fromlist=['config']).config(),
                'licensed_piper_voice_quality_live_tested':False,
                'native_locale_graphics':'AVAILABLE_WITH_LOCAL_FONT',
                'outputs':'TECHNICAL_PREVIEW_ONLY_NOT_PUBLISH_APPROVED',
                'owner_upload_automatically_enabled':False}

    @app.post('/api/projects/{project_id}/m24/variants')
    def create_variant(project_id:str,b:VariantIn):
        if not (b.words_names_numbers_and_meaning_reviewed and b.on_screen_language_reviewed):
            raise HTTPException(409,'A human must review language, names, numerical meaning and on-screen wording')
        try:segments=make_segments(b.reviewed_script.strip())
        except ValueError as ex:raise HTTPException(422,str(ex)) from ex
        with db.transaction() as c:
            p=m.from_project(c,project_id);script=m.latest_script(c,project_id)
            if not script:raise HTTPException(409,'Save source script before translating')
            existing=db.one(c,'SELECT variant_id,state FROM m24_variants WHERE project_id=? AND source_script_version_id=? AND locale=? AND reviewed_text_sha256=?',
                            (project_id,script['script_version_id'],b.locale,m.sha(b.reviewed_script.strip())))
            if existing:return dict(existing,already_exists=True)
            other=db.one(c,"SELECT variant_id FROM m24_variants WHERE project_id=? AND locale=? AND source_script_version_id=?",
                         (project_id,b.locale,script['script_version_id']))
            if other:raise HTTPException(409,'This locale already has a reviewed variant; create a new source script revision before replacing')
            vid=m.uid()
            c.execute('INSERT INTO m24_variants(variant_id,project_id,source_script_version_id,source_script_sha256,project_revision,locale,reviewed_text,reviewed_text_sha256,reviewer,regional_notes,segment_json,state,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)',
                      (vid,project_id,script['script_version_id'],script['content_sha256'],p['revision'],b.locale,b.reviewed_script.strip(),m.sha(b.reviewed_script.strip()),b.reviewer,b.regional_notes,m.j(segments),'DRAFT',m.now()))
        return {'variant_id':vid,'state':'DRAFT','locale':b.locale,'segments':len(segments),'translation_engine':'NONE_HUMAN_REVIEWED','already_exists':False}

    @app.get('/api/projects/{project_id}/m24/variants')
    def variants(project_id:str):
        with db.read() as c:
            m.from_project(c,project_id)
            return db.many(c,'SELECT variant_id,locale,reviewer,state,created_at FROM m24_variants WHERE project_id=? ORDER BY created_at',(project_id,))

    @app.get('/api/projects/{project_id}/m24/variants/{variant_id}')
    def detail(project_id:str,variant_id:str):
        with db.read() as c:
            p,v,segments=current_variant(c,project_id,variant_id)
            voices=db.many(c,'SELECT segment_index,source_kind,sample_frames FROM m24_voices WHERE variant_id=?',(variant_id,))
            lexicon=db.many(c,'SELECT written,speak_as,reviewed_by FROM m24_pronunciation WHERE variant_id=?',(variant_id,))
        return {'variant_id':variant_id,'locale':v['locale'],'state':v['state'],'reviewer':v['reviewer'],
                'segments':[{'index':i,'text':s,'has_voice':any(r['segment_index']==i for r in voices)} for i,s in enumerate(segments)],
                'pronunciation':lexicon,'voice_source':'OWNER_WAV_OR_OPT_IN_LOCAL_PIPER',
                'stale':False,'publish_ready':False}

    @app.post('/api/projects/{project_id}/m24/variants/{variant_id}/pronunciation')
    def pronunciation(project_id:str,variant_id:str,b:PronunciationIn):
        if not b.reviewer_checked_identity_and_meaning:raise HTTPException(409,'Pronunciation reviewer approval required')
        with db.transaction() as c:
            p,v,segments=current_variant(c,project_id,variant_id)
            if v['state']!='DRAFT':raise HTTPException(409,'Cannot change voice cues after rendering')
            if not any(re.search(r'(?<!\w)'+re.escape(b.written)+r'(?!\w)',s,flags=re.I) for s in segments):
                raise HTTPException(422,'The pronunciation term must occur as an exact word in reviewed script')
            c.execute('INSERT INTO m24_pronunciation(variant_id,written,speak_as,reviewed_by) VALUES(?,?,?,?) ON CONFLICT(variant_id,written) DO UPDATE SET speak_as=excluded.speak_as,reviewed_by=excluded.reviewed_by',
                      (variant_id,b.written,b.speak_as,b.reviewer))
        return {'written':b.written,'speak_as':b.speak_as,'applies_to':'LOCAL_TTS_INPUT_ONLY',
                'caption_text_changed':False,'real_lexicon_model_tested':False}

    @app.post('/api/projects/{project_id}/m24/variants/{variant_id}/voice/{segment_index}')
    async def upload_voice(project_id:str,variant_id:str,segment_index:int,file:UploadFile=File(...)):
        with db.read() as c:
            p,v,segments=current_variant(c,project_id,variant_id)
            if v['state']!='DRAFT':raise HTTPException(409,'Variant is immutable after rendering')
            if segment_index<0 or segment_index>=len(segments):raise HTTPException(422,'Invalid localized segment index')
        data=await file.read(8*1024*1024+1)
        if not data or len(data)>8*1024*1024:raise HTTPException(413,'WAV exceeds 8MB or empty')
        dest=m.OUT/project_id/'m24'/variant_id/f'segment_{segment_index:02}.wav'
        frames=store_normalized_wav(data,dest)
        with db.transaction() as c:
            p,v,segments=current_variant(c,project_id,variant_id)
            if v['state']!='DRAFT':raise HTTPException(409,'Variant was rendered while uploading')
            c.execute('INSERT INTO m24_voices(variant_id,segment_index,file_relpath,file_sha256,sample_frames,source_kind,created_at) VALUES(?,?,?,?,?,?,?) ON CONFLICT(variant_id,segment_index) DO UPDATE SET file_relpath=excluded.file_relpath,file_sha256=excluded.file_sha256,sample_frames=excluded.sample_frames,source_kind=excluded.source_kind,created_at=excluded.created_at',
                      (variant_id,segment_index,str(dest.relative_to(m.OUT)),sha_file(dest),frames,'OWNER_RECORDED_WAV',m.now()))
        return {'index':segment_index,'duration_ms':round(frames*1000/RATE),'provenance':'OWNER_RECORDED_WAV_MEASURED_NOT_WORD_ALIGNED'}

    @app.post('/api/projects/{project_id}/m24/variants/{variant_id}/synthesize-piper')
    def synthesize(project_id:str,variant_id:str,b:VoiceOptIn):
        from . import tts
        if not b.owner_approved_model_license or not b.owner_approved_pronunciation:
            raise HTTPException(409,'Owner must explicitly approve local voice model rights and pronunciation')
        cfg=tts.piper_config()
        if not (cfg['installed'] and cfg['licensed_model_reviewed'] and os.getenv('VIRALOS_PIPER_LOCALE')):
            raise HTTPException(409,'Piper executable, local model, reviewed license and locale must be configured')
        with db.read() as c:
            p,v,segments=current_variant(c,project_id,variant_id)
            lexicon=db.many(c,'SELECT * FROM m24_pronunciation WHERE variant_id=?',(variant_id,))
        if v['state']!='DRAFT' or os.getenv('VIRALOS_PIPER_LOCALE')!=v['locale']:
            raise HTTPException(409,'Voice model locale must match immutable draft locale')
        result=[]
        for i,text in enumerate(segments):
            folder=m.OUT/project_id/'m24'/variant_id;folder.mkdir(parents=True,exist_ok=True)
            scratch=folder/f'piper_{i}.wav';dest=folder/f'segment_{i:02}.wav'
            try:
                tts.generate(locale_substitutions(text,lexicon),scratch)
                frames=store_normalized_wav(scratch.read_bytes(),dest)
                with db.transaction() as c:
                    _,v,_=current_variant(c,project_id,variant_id)
                    if v['state']!='DRAFT':raise HTTPException(409,'Variant changed during synthesis')
                    c.execute('INSERT INTO m24_voices(variant_id,segment_index,file_relpath,file_sha256,sample_frames,source_kind,created_at) VALUES(?,?,?,?,?,?,?) ON CONFLICT(variant_id,segment_index) DO UPDATE SET file_relpath=excluded.file_relpath,file_sha256=excluded.file_sha256,sample_frames=excluded.sample_frames,source_kind=excluded.source_kind,created_at=excluded.created_at',
                              (variant_id,i,str(dest.relative_to(m.OUT)),sha_file(dest),frames,'OPT_IN_LOCAL_PIPER',m.now()))
                result.append({'index':i,'duration_ms':round(frames*1000/RATE)})
            except Exception as ex:
                if isinstance(ex,HTTPException):raise
                raise HTTPException(422,f'Local Piper segment {i} failed: {type(ex).__name__}') from ex
            finally:scratch.unlink(missing_ok=True)
        return {'generated':result,'locale':v['locale'],'rights_operator_attested':True,
                'live_model_tested_in_release':False,'pronunciation_listener_review_required':True,
                'voice_cloning':False,'automatic_translation':False}


    @app.post('/api/projects/{project_id}/m24/plans/{plan_id}/forced-proposal')
    def local_forced_proposal(project_id:str,plan_id:str):
        """Genuine optional local transcript-constrained aligner; produces only a review draft.
        Does not synthesize or accept words, and cannot bypass existing M2.2 owner gate.
        """
        from . import alignment_m24
        from .production_m23 import current_plan
        from .creative_m22 import word_time_check, normalize_tokens
        with db.read() as c:
            p,rec,script,audio,voice=current_plan(c,project_id,plan_id)
            if db.one(c,'SELECT draft_id FROM m23_alignment_drafts WHERE plan_id=? AND voice_sha256=? AND plan_sha256=?',(plan_id,audio['voice_sha256'],rec['plan_sha256'])):
                raise HTTPException(409,'An alignment proposal already exists for this plan/voice fingerprint')
            plan=json.loads(rec['plan_json'])
        try:words=alignment_m24.align_transcript(voice,plan)
        except (RuntimeError,ValueError,OSError) as ex:raise HTTPException(409,str(ex)[:200]) from ex
        if len(words)>900:raise HTTPException(422,'Forced aligner returned too many tokens')
        try:word_time_check(plan,words);matched=True
        except ValueError:matched=False
        did=m.uid()
        with db.transaction() as c:
            p2,rec2,script2,audio2,voice2=current_plan(c,project_id,plan_id)
            if audio2['voice_sha256']!=audio['voice_sha256'] or rec2['plan_sha256']!=rec['plan_sha256']:
                raise HTTPException(409,'Voice/plan changed during forced alignment')
            c.execute('INSERT INTO m23_alignment_drafts(draft_id,project_id,plan_id,plan_sha256,script_version_id,voice_sha256,asr_model_label,language,candidate_json,transcript_matches,status,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',
                      (did,project_id,plan_id,rec['plan_sha256'],script['script_version_id'],audio['voice_sha256'],
                       'WHISPERX_LOCAL_CTC_FORCED_OWNER_REVIEW_REQUIRED',plan['locale'].split('-')[0],m.j(words),int(matched),'REVIEW_REQUIRED',m.now()))
        return {'draft_id':did,'words':words,'transcript_matches_and_timing_valid':matched,
                'alignment_method':'LOCAL_CTC_FORCED_TRANSCRIPT_CONSTRAINED',
                'human_review_required':True,'accepted_as_final':False,'model_live_tested_in_delivery':False}

    @app.post('/api/projects/{project_id}/m24/variants/{variant_id}/render')
    def render_variant(project_id:str,variant_id:str):
        with db.read() as c:
            p,v,segments=current_variant(c,project_id,variant_id)
            if v['state']!='DRAFT':raise HTTPException(409,'Variant already rendered; never overwrite immutable preview')
            items=verify_voices(c,project_id,v,segments)
            glossary=db.many(c,'SELECT written,speak_as,reviewed_by FROM m24_pronunciation WHERE variant_id=? ORDER BY written',(variant_id,))
        lengths=[round((entry['sample_frames']+PAUSE_FRAMES)*1000/RATE) for entry,_ in items]
        if sum(lengths)>90000:raise HTTPException(422,'Localized preview exceeds 90 seconds')
        plan=draw_shots(segments,lengths,v['locale'],p['sport_id'],True)
        plan['locale_reviewed']=True
        if v['locale']=='hi-IN':
            for shot in plan['shots']:
                for overlay in shot['overlays']:
                    overlay['text']={'ORIGINAL ANALYSIS':'मूल विश्लेषण','KEY TAKEAWAY':'मुख्य सीख'}.get(overlay['text'],overlay['text'])
        plan=StudioPlanIn.model_validate(plan).model_dump(mode='json')
        folder=m.OUT/project_id/'m24'/variant_id
        folder.mkdir(parents=True,exist_ok=True)
        voice=folder/'assembled_voice.wav';staging=voice.with_suffix('.new')
        with wave.open(str(staging),'wb') as f:
            f.setnchannels(1);f.setsampwidth(2);f.setframerate(RATE)
            for _,raw in items:f.writeframes(raw+b'\0\0'*PAUSE_FRAMES)
        staging.replace(voice)
        from .voice_quality_m24 import inspect_pcm16_mono
        voice_qc=inspect_pcm16_mono(voice)
        if voice_qc['blockers']:
            raise HTTPException(422,'Localized narration fails objective QC: '+', '.join(voice_qc['blockers']))
        input_obj={'variant_id':variant_id,'source_script_sha256':v['source_script_sha256'],
                   'locale_text_sha256':v['reviewed_text_sha256'],'voice_sha256':sha_file(voice),
                   'voice_segment_hashes':[entry['file_sha256'] for entry,_ in items],
                   'pronunciation':glossary,'plan':plan}
        fingerprint=m.sha(m.j(input_obj))
        video,report,manifest=render_studio(plan,p['sport_id'],p['format'],{},voice,folder/'video',release=False)
        report['m24_voice_qc']=voice_qc
        report['m24_locale']=v['locale']
        report['m24_segment_sources']=[entry['source_kind'] for entry,_ in items]
        preview_id=m.uid()
        with db.transaction() as c:
            _,still,_=current_variant(c,project_id,variant_id)
            if still['state']!='DRAFT':raise HTTPException(409,'Variant state changed during rendering')
            again=verify_voices(c,project_id,still,segments)
            if [x['file_sha256'] for x,_ in again]!=[x['file_sha256'] for x,_ in items]:
                raise HTTPException(409,'Narration changed during rendering; discard preview')
            c.execute('INSERT INTO m24_previews(preview_id,variant_id,file_relpath,file_sha256,narration_sha256,input_fingerprint,plan_json,qc_json,created_at) VALUES(?,?,?,?,?,?,?,?,?)',
                      (preview_id,variant_id,str(video.relative_to(m.OUT)),sha_file(video),sha_file(voice),fingerprint,m.j(plan),m.j(report),m.now()))
            c.execute("UPDATE m24_variants SET state='RENDERED' WHERE variant_id=? AND state='DRAFT'",(variant_id,))
        return {'preview_id':preview_id,'locale':v['locale'],'duration_ms':sum(lengths),
                'preview_url':f'/api/projects/{project_id}/m24/previews/{preview_id}.mp4',
                'captions_url':f'/api/projects/{project_id}/m24/previews/{preview_id}.srt',
                'technical_qc':report['status'],'automatic_translation':False,
                'word_level_forced_alignment':False,'owner_final_review_required':True,
                'publishing_eligible':False}

    def checked_preview(c,project_id,preview_id):
        p=m.from_project(c,project_id)
        row=db.one(c,'SELECT v.*,pr.preview_id,pr.file_relpath,pr.file_sha256,pr.plan_json,pr.qc_json FROM m24_previews pr JOIN m24_variants v ON v.variant_id=pr.variant_id WHERE pr.preview_id=? AND v.project_id=?',(preview_id,project_id))
        if not row:raise HTTPException(404,'Localized preview not found in project')
        current_variant(c,project_id,row['variant_id'])
        f=(m.OUT/row['file_relpath']).resolve()
        if m.OUT.resolve() not in f.parents or not f.is_file() or sha_file(f)!=row['file_sha256']:
            raise HTTPException(409,'Localized preview modified or missing')
        return row,f

    @app.get('/api/projects/{project_id}/m24/previews/{preview_id}.mp4')
    def preview(project_id:str,preview_id:str):
        with db.read() as c:row,f=checked_preview(c,project_id,preview_id)
        return FileResponse(f,media_type='video/mp4',filename=f'ViralOS_{row["locale"]}_TECHNICAL_PREVIEW.mp4')

    @app.get('/api/projects/{project_id}/m24/previews/{preview_id}.srt')
    def caption_export(project_id:str,preview_id:str):
        with db.read() as c:row,f=checked_preview(c,project_id,preview_id)
        cues=json.loads(row['plan_json'])['captions']
        out=''.join(f"{i+1}\n{fmt_srt_ms(cue['start_ms'])} --> {fmt_srt_ms(cue['end_ms'])}\n{cue['text']}\n\n" for i,cue in enumerate(cues))
        return PlainTextResponse(out,media_type='application/x-subrip; charset=utf-8')

    @app.get('/api/projects/{project_id}/m24/previews/{preview_id}/qc')
    def quality(project_id:str,preview_id:str):
        with db.read() as c:row,f=checked_preview(c,project_id,preview_id)
        return {'locale':row['locale'],'quality':json.loads(row['qc_json']),
                'source_script_hash':row['source_script_sha256'],
                'publish_ready':False,'human_final_listen_required':True}
