"""M2.2: objective creative audit, reviewed word timestamps and final CPU export.

A final export is *owner reviewed*, not legally cleared or guaranteed professional.
No automatic ASR, translation, fact verification or YouTube uploads happen here.
"""
from __future__ import annotations
import hashlib, json, re, unicodedata
from pathlib import Path
from typing import Literal
from fastapi import HTTPException
from fastapi.responses import FileResponse, PlainTextResponse
from pydantic import BaseModel, Field, ConfigDict, model_validator
from . import db
from .studio_routes import sha_file
from .studio_render import render_studio
from .studio_contracts import StudioPlanIn

# Category-specific editorial constraints; no duplicated renderer/model runtime.
DIRECTOR_POLICIES = {
 'sports.cricket':{'visuals':['original pitch & field diagram','sourced scorecard','verified statistics'], 'hook':'tactical question', 'voice':'energetic but precise', 'verification':'overs, wickets, player context, ball count', 'formats':['analysis','explainer','preview']},
 'sports.nfl':{'visuals':['original gridiron routes','down-and-distance cards','sourced play statistics'], 'hook':'decision or formation', 'voice':'clear American football terminology', 'verification':'downs, possession, clock and week', 'formats':['analysis','explainer','preview']},
 'sports.mlb':{'visuals':['original diamond diagram','innings','pitch/at-bat charts'], 'hook':'play or statistical puzzle', 'voice':'measured analytics', 'verification':'inning, lineup, date', 'formats':['analysis','explainer']},
 'sports.nba':{'visuals':['original court positioning','shot chart','team stats'], 'hook':'tactical possession', 'voice':'energetic analyst', 'verification':'game clock, possession, totals', 'formats':['analysis','explainer']},
 'sports.soccer':{'visuals':['original pitch formations','pass map','verified xG with methodology'], 'hook':'formation shift', 'voice':'tactical and accessible', 'verification':'competition, goal events, xG source', 'formats':['analysis','explainer']},
 'newsroom':{'visuals':['source quote cards','dated document comparisons','timeline'], 'hook':'public-interest question', 'voice':'calm and proportionate', 'verification':'original context, rebuttal, citations', 'formats':['investigation','news_brief']},
 'science':{'visuals':['labeled mechanism diagram','data chart','study design'], 'hook':'testable phenomenon', 'voice':'caveated and clear', 'verification':'study methods, uncertainty, retraction', 'formats':['explainer','demonstration']},
 'technology':{'visuals':['authentic captured screen','version/test results','side-by-side benchmark'], 'hook':'user problem', 'voice':'demonstration first', 'verification':'actual reproducible result', 'formats':['tutorial','review']},
 'business':{'visuals':['dated filing','waterfall chart','assumptions card'], 'hook':'financial puzzle', 'voice':'neutral and numerical', 'verification':'units, reporting period, arithmetic', 'formats':['case_study','explainer']},
 'gaming':{'visuals':['owned game capture','authentic HUD','patch comparison'], 'hook':'real attempt', 'voice':'entertaining and accurate', 'verification':'game version, outcomes, rights', 'formats':['gameplay','guide']},
 'history':{'visuals':['dated archive','period map','labeled reconstruction'], 'hook':'historical question', 'voice':'narrative with provenance', 'verification':'primary archives, temporal context', 'formats':['documentary','explainer']},
 'space':{'visuals':['mission primary image','scaled diagram','simulation label'], 'hook':'scientific question', 'voice':'wonder with rigor', 'verification':'physical units, timestamps, provenance', 'formats':['mission_update','explainer']},
 'learning':{'visuals':['worked example','stepwise diagram','practice question'], 'hook':'specific learning objective', 'voice':'calm instructor', 'verification':'learning correctness, prerequisites', 'formats':['lesson','tutorial']},
 'career':{'visuals':['region-tagged job evidence','skills pathway','portfolio demo'], 'hook':'practical career problem', 'voice':'practical and cautious', 'verification':'period, regional salaries and credentials', 'formats':['guide','tutorial']},
 'productivity':{'visuals':['owned screen capture','workflow map','measured before/after'], 'hook':'measurable bottleneck', 'voice':'clear and instructional', 'verification':'measured outcomes, confounders', 'formats':['demo','experiment']},
 'culture':{'visuals':['dated social evidence','origin timeline','attributed context'], 'hook':'where trend came from', 'voice':'context aware', 'verification':'origin claims, privacy, rights', 'formats':['explainer','commentary']},
}

class Strict(BaseModel):
    model_config=ConfigDict(extra='forbid')

class Word(Strict):
    token: str=Field(min_length=1,max_length=90)
    start_ms: int=Field(ge=0)
    end_ms: int=Field(gt=0)
    @model_validator(mode='after')
    def valid(self):
        if self.end_ms<=self.start_ms:raise ValueError('Invalid word timing')
        return self

class WordsIn(Strict):
    provenance:Literal['OWNER_TIMED_REVIEWED','EXTERNAL_ALIGNER_OWNER_REVIEWED']
    words:list[Word]=Field(min_length=2,max_length=900)
    owner_checked_spelling:bool
    @model_validator(mode='after')
    def reviewed(self):
        if not self.owner_checked_spelling:raise ValueError('Owner must review alignment and spelling')
        return self

class FinalReviewIn(Strict):
    reviewer:str=Field(min_length=2,max_length=100)
    watched_full_video:bool
    original_or_rights_reviewed:bool
    facts_sources_reviewed:bool
    narration_and_captions_reviewed:bool
    notes:str=Field(min_length=15,max_length=1500)


def normalize_tokens(text):
    # Comparison is vocabulary-preserving; punctuation is stripped but digits/letters remain.
    return [re.sub(r'^\W+|\W+$','',unicodedata.normalize('NFKC',x)).casefold() for x in text.split() if re.sub(r'^\W+|\W+$','',x)]


def word_time_check(plan,words):
    if not plan['captions']:raise ValueError('Timed captions required before word-level import')
    expected=[]
    for cue in plan['captions']:
        expected.extend(normalize_tokens(cue['text']))
    actual=[normalize_tokens(w['token']) for w in words]
    if any(len(x)!=1 for x in actual) or [x[0] for x in actual]!=expected:
        raise ValueError('Imported word sequence must exactly match timed narration captions; no hallucinated transcript')
    last=0
    idx=0
    for cue in plan['captions']:
        size=len(normalize_tokens(cue['text']))
        for w in words[idx:idx+size]:
            if w['start_ms']<last or w['start_ms']<cue['start_ms'] or w['end_ms']>cue['end_ms']:
                raise ValueError('Word timestamps must be ordered and inside their scene caption interval')
            last=w['end_ms']
        idx+=size


def fingerprint(c,pid,render_id):
    from . import main as m
    p=m.from_project(c,pid)
    row=db.one(c,'SELECT * FROM m2_studio_renders WHERE studio_render_id=? AND project_id=?',(render_id,pid))
    if not row:raise HTTPException(404,'Studio preview not found in project')
    plan=db.one(c,'SELECT * FROM m2_studio_plans WHERE plan_id=? AND project_id=?',(row['plan_id'],pid))
    if not plan:raise HTTPException(409,'Studio plan not found')
    script=m.latest_script(c,pid)
    if not script or plan['script_version_id']!=script['script_version_id'] or plan['project_revision']!=p['revision']:
        raise HTTPException(409,'Studio preview stale: project or script changed')
    path=(m.OUT/row['output_relpath']).resolve()
    if m.OUT.resolve() not in path.parents or not path.is_file() or sha_file(path)!=row['output_sha256']:
        raise HTTPException(409,'Preview file missing or modified')
    plan_obj=json.loads(plan['plan_json'])
    asset_ids={x['visual'].get('asset_id') for x in plan_obj['shots']}
    asset_ids|={ov.get('image_asset_id') for x in plan_obj['shots'] for ov in x['overlays']}
    asset_ids.add(plan_obj.get('music_asset_id'));asset_ids.discard(None)
    assets={}
    for aid in sorted(asset_ids):
        rec=db.one(c,'SELECT * FROM m2_studio_assets WHERE asset_id=? AND project_id=?',(aid,pid))
        if not rec or rec['rights_attested']!=1:raise HTTPException(409,'Missing owner-reviewed rights asset')
        file=(m.OUT/rec['local_relpath']).resolve()
        if m.OUT.resolve() not in file.parents or not file.is_file() or sha_file(file)!=rec['content_sha256']:
            raise HTTPException(409,'Asset missing or modified')
        assets[aid]=dict(rec,path=file)
    audio=db.one(c,'SELECT * FROM m21_plan_audio WHERE plan_id=? AND project_id=?',(plan['plan_id'],pid))
    if audio:
        voice=(m.OUT/audio['voice_relpath']).resolve()
        if m.OUT.resolve() not in voice.parents or not voice.is_file() or sha_file(voice)!=audio['voice_sha256']:
            raise HTTPException(409,'Narration changed after preview')
    else:
        voice=m.OUT/pid/'voice.wav'
        if not voice.is_file():raise HTTPException(409,'Final video requires narration')
    # Regenerated source graphics cannot remain approved after a source/claim correction.
    from .production_m23 import verify_generated_asset
    sourced_cards={}
    for aid in sorted(assets):
        proof=verify_generated_asset(c,pid,aid)
        if proof is not None:sourced_cards[aid]=proof
    links=db.many(c,'SELECT scl.claim_id,cl.verification_status,cl.updated_at FROM script_claim_links scl JOIN claims cl ON cl.claim_id=scl.claim_id WHERE scl.script_version_id=? ORDER BY scl.claim_id',(script['script_version_id'],))
    research=db.many(c,'SELECT cl.claim_id,cl.verification_status,cl.updated_at FROM claims cl JOIN research_plans r ON r.research_plan_id=cl.research_plan_id WHERE r.channel_id=? AND json_extract(r.plan_json,\'$.project_id\')=? ORDER BY cl.claim_id',(p['channel_id'],pid))
    sources=db.many(c,'SELECT source_version_id FROM m1_project_sources WHERE project_id=? ORDER BY source_version_id',(pid,))
    alignment=db.one(c,'SELECT alignment_id,voice_sha256,plan_sha256 FROM m22_word_alignments WHERE plan_id=?',(plan['plan_id'],))
    info={'project_revision':p['revision'],'plan_hash':plan['plan_sha256'],
          'script_hash':script['content_sha256'],'preview_hash':row['output_sha256'],
          'voice_hash':sha_file(voice),'assets':[(x,assets[x]['content_sha256']) for x in sorted(assets)],
          'links':links,'research':research,'sources':sources,
          'alignment':alignment,'m23_evidence_provenance':sourced_cards}
    digest=m.sha(m.j(info))
    return digest,p,row,plan,plan_obj,script,links,research,assets,voice


def audit(plan,links,research,voice):
    blockers=[];warnings=[]
    if not voice.is_file():blockers.append('Narration WAV required')
    if not plan['captions']:blockers.append('Timed captions required')
    linked={x['claim_id'] for x in links}
    verified={x['claim_id'] for x in research if x['verification_status']=='SUPPORTED'}
    for row in links:
        if row['verification_status']!='SUPPORTED':blockers.append('Unverified linked claim: '+row['claim_id'])
    for shot in plan['shots']:
        for cid in shot.get('claim_ids',[]):
            if cid not in linked or cid not in verified:blockers.append('Unverified/unlinked shot claim: '+cid)
    if not research:warnings.append('No structured research claims: human must confirm script is original analysis/illustration, not unsupported factual assertions')
    unused=[x['claim_id'] for x in links if not any(x['claim_id'] in shot.get('claim_ids',[]) for shot in plan['shots'])]
    if unused:warnings.append('Verified script claims not explicitly tied to a visual shot: '+','.join(unused))
    if len({s['visual']['kind'] for s in plan['shots']})==1:
        warnings.append('All shots share one visual type; consider category-appropriate variety')
    if any(len(s['headline'])>90 for s in plan['shots']):warnings.append('Long on-screen headlines may obscure important visuals')
    if plan['captions'] and any(len(x['text'])/((x['end_ms']-x['start_ms'])/1000)>35 for x in plan['captions']):
        warnings.append('Caption density above 35 characters per second; visual review strongly recommended')
    return {'status':'BLOCKED' if blockers else 'OWNER_REVIEW_REQUIRED',
            'blockers':sorted(set(blockers)),'warnings':warnings,
            'shot_count':len(plan['shots']),'caption_count':len(plan['captions']),
            'automated_professional_score':None,'independent_fact_verification':False,
            'rights_legality_verified':False,'owner_final_approval':False}


def register_creative_m22(app):
    from . import main as m

    @app.get('/api/m22/creative-policies')
    def policies():
        return {'profiles':DIRECTOR_POLICIES,'active_launch_adapters':['sports.cricket','sports.nfl'],
                'remaining_profiles':'DESIGN_GUIDANCE_NOT_IMPLEMENTED_AS_AUTONOMOUS_DIRECTORS'}

    @app.get('/api/projects/{project_id}/m22/creative-audit/{render_id}')
    def creative_audit(project_id:str,render_id:str):
        with db.read() as c:
            digest,p,row,rec,plan,script,links,research,assets,voice=fingerprint(c,project_id,render_id)
        key='sports.'+p['sport_id'] if p['domain_id']=='sports' else p['domain_id']
        report=audit(plan,links,research,voice)
        return {'render_id':render_id,'plan_id':rec['plan_id'],'input_fingerprint':digest,
                'policy':DIRECTOR_POLICIES.get(key),'report':report}

    @app.post('/api/projects/{project_id}/m22/plans/{plan_id}/words')
    def import_words(project_id:str,plan_id:str,body:WordsIn):
        with db.transaction() as c:
            p=m.from_project(c,project_id)
            rec=db.one(c,'SELECT * FROM m2_studio_plans WHERE plan_id=? AND project_id=?',(plan_id,project_id))
            if not rec:raise HTTPException(404,'Studio plan not found')
            script=m.latest_script(c,project_id)
            if rec['project_revision']!=p['revision'] or not script or rec['script_version_id']!=script['script_version_id']:
                raise HTTPException(409,'Plan stale after script revision')
            audio=db.one(c,'SELECT * FROM m21_plan_audio WHERE plan_id=? AND project_id=?',(plan_id,project_id))
            if not audio:raise HTTPException(409,'Word timestamps require a measured, immutable M2.1 narration track')
            voice=(m.OUT/audio['voice_relpath']).resolve()
            if m.OUT.resolve() not in voice.parents or not voice.is_file() or sha_file(voice)!=audio['voice_sha256']:
                raise HTTPException(409,'Measured voice file tampered or missing')
            plan=json.loads(rec['plan_json']);words=body.model_dump(mode='json')['words']
            try:word_time_check(plan,words)
            except ValueError as e:raise HTTPException(422,str(e))
            existed=db.one(c,'SELECT alignment_id FROM m22_word_alignments WHERE plan_id=?',(plan_id,))
            if existed:raise HTTPException(409,'Word alignment already bound; create a fresh plan after narration changes')
            aid=m.uid()
            c.execute('INSERT INTO m22_word_alignments(alignment_id,plan_id,project_id,script_version_id,voice_sha256,plan_sha256,words_json,provenance,submitted_at) VALUES (?,?,?,?,?,?,?,?,?)',
                (aid,plan_id,project_id,script['script_version_id'],audio['voice_sha256'],rec['plan_sha256'],m.j(words),body.provenance,m.now()))
        return {'alignment_id':aid,'word_count':len(words),'provenance':body.provenance,
                'automatic_forced_alignment':False,'audio_text_verified_by_asr':False,'owner_reviewed':True}

    @app.get('/api/projects/{project_id}/m22/plans/{plan_id}/words.vtt')
    def word_vtt(project_id:str,plan_id:str):
        with db.read() as c:
            p=m.from_project(c,project_id)
            rec=db.one(c,'SELECT * FROM m22_word_alignments WHERE project_id=? AND plan_id=?',(project_id,plan_id))
            plan=db.one(c,'SELECT * FROM m2_studio_plans WHERE plan_id=?',(plan_id,))
            if not rec or not plan or p['revision']!=plan['project_revision'] or m.latest_script(c,project_id)['script_version_id']!=rec['script_version_id']:
                raise HTTPException(409,'No current reviewed word alignment')
            audio=db.one(c,'SELECT * FROM m21_plan_audio WHERE plan_id=?',(plan_id,))
            voice=(m.OUT/audio['voice_relpath']).resolve() if audio else None
            if not audio or not voice or not voice.is_file() or sha_file(voice)!=rec['voice_sha256'] or plan['plan_sha256']!=rec['plan_sha256']:
                raise HTTPException(409,'Voice or plan changed since word review')
        def ts(ms):return f'{ms//3600000:02}:{(ms//60000)%60:02}:{(ms//1000)%60:02}.{ms%1000:03}'
        words=json.loads(rec['words_json']);content='WEBVTT\n\n'+''.join(f"{ts(w['start_ms'])} --> {ts(w['end_ms'])}\n{w['token']}\n\n" for w in words)
        return PlainTextResponse(content,media_type='text/vtt',headers={'Content-Disposition':'attachment; filename="ViralOS_owner_reviewed_words.vtt"'})

    @app.post('/api/projects/{project_id}/m22/studio/renders/{render_id}/review-final')
    def review_final(project_id:str,render_id:str,body:FinalReviewIn):
        if not all([body.watched_full_video,body.original_or_rights_reviewed,body.facts_sources_reviewed,body.narration_and_captions_reviewed]):
            raise HTTPException(409,'All four independent human reviews must be checked')
        with db.transaction() as c:
            digest,p,row,planrow,plan,script,links,research,assets,voice=fingerprint(c,project_id,render_id)
            quality=json.loads(row['quality_report_json'])
            if quality['status']!='TECHNICAL_QC_PASSED_HUMAN_REVIEW_REQUIRED':
                raise HTTPException(409,'Video technical QC not passed')
            qa=audit(plan,links,research,voice)
            if qa['blockers']:raise HTTPException(409,'Creative audit blockers: '+', '.join(qa['blockers']))
            prior=db.one(c,'SELECT review_id FROM m22_studio_reviews WHERE preview_render_id=? AND fingerprint=?',(render_id,digest))
            if prior:return {'review_id':prior['review_id'],'already_exists':True,'owner_reviewed':True}
            rid=m.uid()
            c.execute('INSERT INTO m22_studio_reviews(review_id,project_id,preview_render_id,plan_id,fingerprint,reviewer,watched_full_video,original_or_rights_reviewed,facts_sources_reviewed,narration_and_captions_reviewed,notes,status,created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)',
                (rid,project_id,render_id,planrow['plan_id'],digest,body.reviewer,1,1,1,1,body.notes,'OWNER_APPROVED_FOR_FINAL_EXPORT',m.now()))
        return {'review_id':rid,'already_exists':False,'status':'OWNER_APPROVED_FOR_FINAL_EXPORT',
                'does_not_guarantee_youtube_monetization_or_copyright_clearance':True}

    @app.post('/api/projects/{project_id}/m22/reviews/{review_id}/export-final')
    def export_final(project_id:str,review_id:str):
        with db.read() as c:
            review=db.one(c,'SELECT * FROM m22_studio_reviews WHERE review_id=? AND project_id=?',(review_id,project_id))
            if not review:raise HTTPException(404,'Review not found')
            digest,p,row,planrow,plan,script,links,research,assets,voice=fingerprint(c,project_id,review['preview_render_id'])
            if digest!=review['fingerprint']:raise HTTPException(409,'Review stale: evidence, files or script changed')
            previous=db.one(c,'SELECT export_id,file_relpath,file_sha256,status FROM m22_final_exports WHERE review_id=?',(review_id,))
            if previous:
                if previous['status']!='OWNER_APPROVED_FINAL_EXPORT':
                    raise HTTPException(409,'Previous final export invalidated; new human review and render required')
                target=(m.OUT/previous['file_relpath']).resolve()
                if m.OUT.resolve() in target.parents and target.is_file() and sha_file(target)==previous['file_sha256']:
                    return {'export_id':previous['export_id'],'already_exists':True,'status':'OWNER_APPROVED_FINAL_EXPORT'}
                raise HTTPException(409,'Final export file modified; cannot silently recreate')
        eid=m.uid();folder=m.OUT/project_id/'m22_final'/eid
        try:
            out,report,manifest=render_studio(plan,p['sport_id'],p['format'],assets,voice,folder,release=True)
        except Exception as ex:raise HTTPException(422,'Final render failed; '+str(ex)[:170])
        sha=sha_file(out)
        with db.transaction() as c:
            review=db.one(c,'SELECT * FROM m22_studio_reviews WHERE review_id=? AND project_id=?',(review_id,project_id))
            if not review:raise HTTPException(409,'Review removed')
            new_digest,*_=fingerprint(c,project_id,review['preview_render_id'])
            if new_digest!=review['fingerprint']:raise HTTPException(409,'Project changed during final render; discard export')
            c.execute('INSERT INTO m22_final_exports(export_id,project_id,plan_id,review_id,fingerprint,file_relpath,file_sha256,report_json,manifest_json,status,created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)',
                (eid,project_id,planrow['plan_id'],review_id,digest,str(out.relative_to(m.OUT)),sha,m.j(report),m.j(manifest),'OWNER_APPROVED_FINAL_EXPORT',m.now()))
        return {'export_id':eid,'already_exists':False,'download_url':f'/api/m22/final-exports/{eid}/download',
                'status':'OWNER_APPROVED_FINAL_EXPORT','privacy':'LOCAL_FILE_ONLY','youtube_uploaded':False,
                'note':'Owner approval is not external copyright or monetization clearance'}

    @app.get('/api/m22/final-exports/{export_id}/download')
    def download_final(export_id:str):
        with db.read() as c:
            e=db.one(c,'SELECT * FROM m22_final_exports WHERE export_id=?',(export_id,))
            if not e:raise HTTPException(404,'Export not found')
            if e['status']!='OWNER_APPROVED_FINAL_EXPORT':
                raise HTTPException(409,'Final export invalidated; new owner review required')
            r=db.one(c,'SELECT * FROM m22_studio_reviews WHERE review_id=?',(e['review_id'],))
            digest,*_=fingerprint(c,e['project_id'],r['preview_render_id'])
            if digest!=e['fingerprint']:raise HTTPException(409,'Final export obsolete after changes')
        p=(m.OUT/e['file_relpath']).resolve()
        if m.OUT.resolve() not in p.parents or not p.is_file() or sha_file(p)!=e['file_sha256']:
            raise HTTPException(409,'Final file missing or altered')
        return FileResponse(p,media_type='video/mp4',filename='ViralOS_Owner_Reviewed_Final.mp4')