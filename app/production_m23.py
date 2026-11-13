"""M2.3 conservative evidence-to-screen and opt-in local ASR proposal workflow."""
from __future__ import annotations
import json, math, os
from pathlib import Path
from typing import Literal
from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict, Field
from . import db, alignment_m23
from .studio_routes import sha_file
from .creative_m22 import word_time_check, normalize_tokens

class Strict(BaseModel):model_config=ConfigDict(extra='forbid')

class EdgeReview(Strict):
    reviewer:str=Field(min_length=3,max_length=100)
    source_and_locator_checked:bool
    explanation:str=Field(min_length=15,max_length=600)

class EvidenceCardIn(Strict):
    claim_id:str
    source_version_id:str
    attribution_and_rights_reviewed:bool

class AlignmentReview(Strict):
    owner_checked_audio_and_words:bool
    words:list[dict]=Field(min_length=2,max_length=900)


def current_plan(c,pid,plan_id):
    from . import main as m
    p=m.from_project(c,pid)
    plan=db.one(c,'SELECT * FROM m2_studio_plans WHERE plan_id=? AND project_id=?',(plan_id,pid))
    script=m.latest_script(c,pid)
    if not plan:raise HTTPException(404,'Studio plan not found in project')
    if not script or script['script_version_id']!=plan['script_version_id'] or p['revision']!=plan['project_revision']:
        raise HTTPException(409,'Studio plan stale after script/project revision')
    aud=db.one(c,'SELECT * FROM m21_plan_audio WHERE plan_id=? AND project_id=?',(plan_id,pid))
    if not aud:raise HTTPException(409,'Measured M2.1 narration required')
    voice=(m.OUT/aud['voice_relpath']).resolve()
    if m.OUT.resolve() not in voice.parents or not voice.is_file() or sha_file(voice)!=aud['voice_sha256']:
        raise HTTPException(409,'Narration changed or missing')
    return p,plan,script,aud,voice


def checked_evidence(c,pid,cid,source_version_id):
    from . import main as m
    p=m.from_project(c,pid)
    research=m._plan(c,p)
    claim=db.one(c,'SELECT * FROM claims WHERE claim_id=? AND research_plan_id=?',(cid,research['research_plan_id']))
    if not claim or claim['verification_status']!='SUPPORTED' or not claim['reviewer_id']:
        raise HTTPException(409,'Owner-reviewed SUPPORTED claim required in this project')
    edge=db.one(c,"SELECT * FROM evidence_edges WHERE claim_id=? AND source_version_id=? AND relation='SUPPORTS'",(cid,source_version_id))
    if not edge or edge['human_review_required']!=0 or not edge['checked_by']:
        raise HTTPException(409,'Supporting edge needs owner source/locator review')
    source=db.one(c,'SELECT sv.*,s.canonical_url,s.original_publisher FROM source_versions sv JOIN sources s ON sv.source_id=s.source_id JOIN m1_project_sources bind ON bind.source_version_id=sv.source_version_id WHERE sv.source_version_id=? AND bind.project_id=?',(source_version_id,pid))
    if not source:raise HTTPException(409,'Source not explicitly bound to the project')
    return claim,edge,source


def make_card(path,proposition,publisher,url,locale='en-US'):
    from PIL import Image,ImageDraw
    from .studio_render import font,wrap
    w,h=1080,750
    im=Image.new('RGB',(w,h),(9,20,35));d=ImageDraw.Draw(im)
    d.rounded_rectangle((38,34,1040,715),radius=38,fill=(17,40,60),outline=(92,201,182),width=5)
    d.rounded_rectangle((78,74,1002,160),radius=18,fill=(22,93,91))
    d.text((102,90),'REVIEWED EVIDENCE • SOURCE CARD',font=font(locale,32),fill=(246,255,251))
    f=font(locale,47)
    lines=wrap(d,proposition,f,865,6)
    y=210
    for line in lines:
        d.text((92,y),line,font=f,fill=(245,247,250));y+=69
    publisher=(publisher or 'Owner-provided source')[:82]
    f2=font(locale,26)
    d.text((92,587),'SOURCE: '+publisher,font=f2,fill=(178,231,225))
    from urllib.parse import urlsplit
    host=urlsplit(url).hostname or 'source URL available in metadata'
    d.text((92,632),host[:75],font=f2,fill=(212,225,236))
    d.text((92,675),'OWNER REVIEWED • NOT INDEPENDENTLY VERIFIED',font=font(locale,19),fill=(252,208,148))
    path.parent.mkdir(parents=True,exist_ok=True);im.save(path,format='PNG')


def verify_generated_asset(c,pid,asset_id):
    """Fail final review if an original evidence card has stale provenance."""
    row=db.one(c,'SELECT * FROM m23_evidence_cards WHERE asset_id=? AND project_id=?',(asset_id,pid))
    if not row:return None
    claim,edge,source=checked_evidence(c,pid,row['claim_id'],row['source_version_id'])
    saved=json.loads(row['provenance_json'])
    if (claim['updated_at']!=row['claim_updated_at'] or source['content_sha256']!=row['source_content_sha256']
        or saved['source_url']!=source['canonical_url'] or saved['publisher']!=source['original_publisher']):
        raise HTTPException(409,'Evidence graphic provenance stale: regenerate sourced card')
    return {'card_id':row['card_id'],'claim_id':row['claim_id'],'claim_updated_at':row['claim_updated_at'],
            'source_version_id':row['source_version_id'],'source_sha256':source['content_sha256'],
            'checked_by':edge['checked_by'],'checked_at':edge['checked_at']}


def register_m23(app):
    from . import main as m

    @app.get('/api/m23/capabilities')
    def capabilities():
        return {'evidence_to_screen':'OWNER_VERIFIED_ORIGINAL_PNG_WITH_PROVENANCE',
                'automatic_factual_verification':False,'voice_alignment':alignment_m23.config_for_public(),
                'dubbing':'EXISTING_OWNER_REVIEWED_LOCALE_PLUS_PER_SEGMENT_VOICE',
                'automatic_translation':False,'professional_voice_guarantee':False}

    @app.get('/api/projects/{project_id}/m23/evidence-edges')
    def project_evidence_edges(project_id:str):
        with db.read() as c:
            p=m.from_project(c,project_id);research=m._plan(c,p)
            return db.many(c,"SELECT e.evidence_edge_id,e.claim_id,e.source_version_id,e.relation,e.locator,"
                           "e.checked_by,e.checked_at,e.human_review_required,cl.verification_status,cl.proposition "
                           "FROM evidence_edges e JOIN claims cl ON cl.claim_id=e.claim_id "
                           "WHERE cl.research_plan_id=? ORDER BY e.evidence_edge_id",(research['research_plan_id'],))

    @app.post('/api/projects/{project_id}/m23/evidence-edges/{edge_id}/review')
    def review_edge(project_id:str,edge_id:str,b:EdgeReview):
        if not b.source_and_locator_checked:raise HTTPException(409,'Must inspect source AND claim locator manually')
        with db.transaction() as c:
            p=m.from_project(c,project_id);research=m._plan(c,p)
            edge=db.one(c,'SELECT e.*,cl.research_plan_id FROM evidence_edges e JOIN claims cl ON cl.claim_id=e.claim_id WHERE e.evidence_edge_id=?',(edge_id,))
            if not edge or edge['research_plan_id']!=research['research_plan_id']:
                raise HTTPException(404,'Evidence edge not in project')
            source=db.one(c,'SELECT source_version_id FROM m1_project_sources WHERE project_id=? AND source_version_id=?',(project_id,edge['source_version_id']))
            if not source:raise HTTPException(409,'Evidence source is not bound to project')
            if edge['relation']!='SUPPORTS':raise HTTPException(422,'Only supporting evidence can be used in evidence proof cards')
            c.execute('UPDATE evidence_edges SET human_review_required=0,checked_by=?,checked_at=? WHERE evidence_edge_id=?',(b.reviewer,m.now(),edge_id))
            # Invalidate past export fingerprints and all existing derived evidence cards.
            c.execute('UPDATE claims SET updated_at=? WHERE claim_id=?',(m.now(),edge['claim_id']))
        return {'edge_id':edge_id,'review_type':'OWNER_SOURCE_AND_LOCATOR_ATTESTATION','independently_verified':False}

    @app.post('/api/projects/{project_id}/m23/evidence-cards')
    def generate_evidence_card(project_id:str,b:EvidenceCardIn):
        if not b.attribution_and_rights_reviewed:raise HTTPException(409,'Attribution and original graphic rights must be owner-reviewed')
        with db.read() as c:
            p=m.from_project(c,project_id)
            script=m.latest_script(c,project_id)
            if not script or not db.one(c,'SELECT claim_id FROM script_claim_links WHERE claim_id=? AND script_version_id=?',(b.claim_id,script['script_version_id'])):
                raise HTTPException(409,'Only claims linked to current script can be pictured')
            claim,edge,source=checked_evidence(c,project_id,b.claim_id,b.source_version_id)
            if len(claim['proposition'])>155:raise HTTPException(422,'Evidence card claim too long; write a more precise reviewed claim')
            old=db.one(c,'SELECT * FROM m23_evidence_cards WHERE project_id=? AND claim_id=? AND source_version_id=?',(project_id,b.claim_id,b.source_version_id))
            if old:
                try:
                    prove=verify_generated_asset(c,project_id,old['asset_id'])
                    asset=db.one(c,'SELECT * FROM m2_studio_assets WHERE asset_id=?',(old['asset_id'],))
                    path=m.OUT/asset['local_relpath']
                    if path.is_file() and sha_file(path)==asset['content_sha256']:
                        return {'asset_id':old['asset_id'],'already_exists':True,'kind':'OWNER_REVIEWED_EVIDENCE_CARD'}
                except HTTPException:pass
                raise HTTPException(409,'Existing evidence card is stale; revise script/project and generate a new card')
            frozen=(claim['proposition'],source['original_publisher'],source['canonical_url'],p['locale'],
                    claim['updated_at'],source['content_sha256'])
        aid=m.uid();cid=m.uid()
        output=m.OUT/project_id/'evidence_cards'/f'{aid}.png'
        make_card(output,*frozen[:4])
        dig=sha_file(output)
        try:
            with db.transaction() as c:
                claim2,edge2,source2=checked_evidence(c,project_id,b.claim_id,b.source_version_id)
                current_script=m.latest_script(c,project_id)
                if (claim2['updated_at']!=frozen[4] or source2['content_sha256']!=frozen[5]
                   or current_script['script_version_id']!=script['script_version_id']):
                    raise HTTPException(409,'Claim/source/script changed during evidence card generation')
                c.execute('INSERT INTO m2_studio_assets(asset_id,project_id,kind,local_relpath,origin,license_note,rights_attested,content_sha256,mime,duration_ms,created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)',
                          (aid,project_id,'STILL',str(output.relative_to(m.OUT)),
                           'ViralOS ORIGINAL TEXT GRAPHIC • '+source2['canonical_url'][:500],
                           'Owner checked source attribution and original authored graphic; no third-party image copied.',
                           1,dig,'image/png',None,m.now()))
                c.execute('INSERT INTO m23_evidence_cards(card_id,project_id,claim_id,source_version_id,asset_id,claim_updated_at,source_content_sha256,provenance_json,created_at) VALUES (?,?,?,?,?,?,?,?,?)',
                          (cid,project_id,b.claim_id,b.source_version_id,aid,claim2['updated_at'],source2['content_sha256'],
                           m.j({'source_url':source2['canonical_url'],'publisher':source2['original_publisher'],
                                'reviewed_by':edge2['checked_by'],'verification':'OWNER_ATTESTED_NOT_INDEPENDENT'}),m.now()))
        except Exception:
            output.unlink(missing_ok=True);raise
        return {'asset_id':aid,'card_id':cid,'already_exists':False,
                'use_in_studio_as':'IMAGE_INSERT or RIGHTS_APPROVED_STILL','owner_reviewed':True,
                'independently_verified':False,'third_party_image_reproduced':False}

    @app.get('/api/projects/{project_id}/m23/evidence-cards/{asset_id}/image')
    def card_image(project_id:str,asset_id:str):
        from fastapi.responses import FileResponse
        with db.read() as c:
            m.from_project(c,project_id)
            proof=verify_generated_asset(c,project_id,asset_id)
            if not proof:raise HTTPException(404,'Original evidence graphic not found in project')
            asset=db.one(c,'SELECT local_relpath,content_sha256 FROM m2_studio_assets WHERE asset_id=? AND project_id=?',(asset_id,project_id))
            if not asset:raise HTTPException(404,'Evidence asset missing')
            path=(m.OUT/asset['local_relpath']).resolve()
            if m.OUT.resolve() not in path.parents or not path.is_file() or sha_file(path)!=asset['content_sha256']:
                raise HTTPException(409,'Evidence image changed since creation')
        return FileResponse(path,media_type='image/png',filename='ViralOS_original_evidence_card.png')

    @app.get('/api/projects/{project_id}/m23/evidence-cards')
    def cards(project_id:str):
        with db.read() as c:
            m.from_project(c,project_id)
            rows=db.many(c,'SELECT card_id,asset_id,claim_id,source_version_id,created_at FROM m23_evidence_cards WHERE project_id=?',(project_id,))
            for row in rows:
                try:verify_generated_asset(c,project_id,row['asset_id']);row['status']='CURRENT_OWNER_REVIEWED'
                except HTTPException:row['status']='STALE_BLOCKED'
            return rows

    @app.post('/api/projects/{project_id}/m23/plans/{plan_id}/asr-proposal')
    def asr_proposal(project_id:str,plan_id:str):
        with db.read() as c:
            p,plan,script,audio,voice=current_plan(c,project_id,plan_id)
            lang=plan['locale'].split('-')[0]
            if lang not in ('en','hi'):raise HTTPException(422,'ASR language not supported by this optional adapter')
            existing=db.one(c,'SELECT draft_id FROM m23_alignment_drafts WHERE plan_id=? AND voice_sha256=? AND plan_sha256=?',(plan_id,audio['voice_sha256'],plan['plan_sha256']))
            if existing:return {'draft_id':existing['draft_id'],'already_exists':True,'human_review_required':True}
        try:words=alignment_m23.transcribe_local(voice,lang)
        except (RuntimeError,ValueError,OSError) as ex:raise HTTPException(409,str(ex)[:240])
        if len(words)>900:raise HTTPException(422,'ASR output too long for checkpoint')
        data=json.loads(plan['plan_json'])
        expected=[w for cue in data['captions'] for w in normalize_tokens(cue['text'])]
        received=[t for w in words for t in normalize_tokens(w['token'])]
        transcript_matches=expected==received
        did=m.uid()
        with db.transaction() as c:
            p2,plan2,script2,audio2,voice2=current_plan(c,project_id,plan_id)
            if audio2['voice_sha256']!=audio['voice_sha256'] or plan2['plan_sha256']!=plan['plan_sha256']:
                raise HTTPException(409,'Audio or plan changed during ASR inference')
            c.execute('INSERT INTO m23_alignment_drafts(draft_id,project_id,plan_id,plan_sha256,script_version_id,voice_sha256,asr_model_label,language,candidate_json,transcript_matches,status,created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
                      (did,project_id,plan_id,plan['plan_sha256'],script['script_version_id'],audio['voice_sha256'],
                       'LOCAL_FASTER_WHISPER_CPU_INT8',lang,m.j(words),int(transcript_matches),'REVIEW_REQUIRED',m.now()))
        return {'draft_id':did,'already_exists':False,'words':words,'transcript_matches':transcript_matches,
                'human_review_required':True,'provenance':'ASR_WORD_TIMESTAMP_PROPOSAL_NOT_FORCED_ALIGNMENT'}

    @app.get('/api/projects/{project_id}/m23/alignment-drafts/{draft_id}')
    def read_alignment(project_id:str,draft_id:str):
        with db.read() as c:
            m.from_project(c,project_id)
            row=db.one(c,'SELECT * FROM m23_alignment_drafts WHERE project_id=? AND draft_id=?',(project_id,draft_id))
            if not row:raise HTTPException(404,'ASR proposal not found')
            return {'draft_id':draft_id,'words':json.loads(row['candidate_json']),'status':row['status'],
                    'transcript_matches':bool(row['transcript_matches']),'word_timing_source':'OPTIONAL_LOCAL_ASR'}

    @app.post('/api/projects/{project_id}/m23/alignment-drafts/{draft_id}/approve')
    def approve_alignment(project_id:str,draft_id:str,body:AlignmentReview):
        if not body.owner_checked_audio_and_words:
            raise HTTPException(409,'Owner must listen and correct every timestamp/token before approval')
        from .creative_m22 import WordsIn
        try:validated=WordsIn(provenance='EXTERNAL_ALIGNER_OWNER_REVIEWED',words=body.words,owner_checked_spelling=True)
        except ValueError as e:raise HTTPException(422,str(e))
        with db.transaction() as c:
            rec=db.one(c,'SELECT * FROM m23_alignment_drafts WHERE draft_id=? AND project_id=?',(draft_id,project_id))
            if not rec:raise HTTPException(404,'ASR proposal not found')
            if rec['status']!='REVIEW_REQUIRED':raise HTTPException(409,'Proposal is not awaiting review')
            p,plan,script,audio,voice=current_plan(c,project_id,rec['plan_id'])
            if rec['voice_sha256']!=audio['voice_sha256'] or rec['plan_sha256']!=plan['plan_sha256'] or rec['script_version_id']!=script['script_version_id']:
                raise HTTPException(409,'Stale ASR proposal after voice/script/plan change')
            if db.one(c,'SELECT alignment_id FROM m22_word_alignments WHERE plan_id=?',(rec['plan_id'],)):
                raise HTTPException(409,'Reviewed alignment already bound')
            try:word_time_check(json.loads(plan['plan_json']),validated.model_dump()['words'])
            except ValueError as e:raise HTTPException(422,str(e))
            aid=m.uid()
            c.execute('INSERT INTO m22_word_alignments(alignment_id,plan_id,project_id,script_version_id,voice_sha256,plan_sha256,words_json,provenance,submitted_at) VALUES (?,?,?,?,?,?,?,?,?)',
                      (aid,rec['plan_id'],project_id,script['script_version_id'],audio['voice_sha256'],plan['plan_sha256'],
                       m.j(validated.model_dump()['words']),'EXTERNAL_ALIGNER_OWNER_REVIEWED',m.now()))
            c.execute("UPDATE m23_alignment_drafts SET status='OWNER_APPROVED',reviewed_at=? WHERE draft_id=?",(m.now(),draft_id))
        return {'alignment_id':aid,'owner_reviewed':True,'automatic_forced_alignment':False,
                'can_download_existing_vtt':True,'provenance':('LOCAL_CTC_FORCED_OWNER_REVIEWED' if rec['asr_model_label'].startswith('WHISPERX_LOCAL_CTC') else 'ASR_PROPOSAL_OWNER_CORRECTED')}

    @app.get('/api/projects/{project_id}/m23/plans/{plan_id}/locale-audit')
    def locale_audit(project_id:str,plan_id:str):
        with db.read() as c:
            p,plan,script,audio,voice=current_plan(c,project_id,plan_id)
            draft=db.one(c,'SELECT d.* FROM m21_plan_audio a JOIN m21_director_drafts d ON a.draft_id=d.draft_id WHERE a.plan_id=?',(plan_id,))
            obj=json.loads(plan['plan_json'])
            warnings=[];blockers=[]
            if obj['locale']!=plan['locale']:blockers.append('Studio locale and plan locale disagree')
            if draft and draft['locale']!=plan['locale']:blockers.append('Narration draft and plan locale disagree')
            if plan['locale']!=p['locale'] and not obj.get('locale_reviewed'):
                blockers.append('Target locale needs human script, overlays and narration review')
            if not obj['captions']:blockers.append('Localized captions missing')
            if not draft:warnings.append('Voice not linked to a multilingual Director draft')
            if len(obj['shots'])<2:warnings.append('Insufficient visual variety')
            return {'plan_id':plan_id,'locale':plan['locale'],'blocks_publication':bool(blockers),'blockers':blockers,
                    'warnings':warnings,'human_voice_pronunciation_review_required':True,
                    'translation_generated_by_system':False,'voice_duration_ms':round(__import__('app.studio_render',fromlist=['wav_duration']).wav_duration(voice)*1000)}
