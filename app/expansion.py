"""M1/M2/M3 operational extensions. Honest limits: owner-supplied != verified, previews != publishable."""
from datetime import date
from pathlib import Path
import csv, hashlib, io, json, os, re, zipfile
from typing import Literal
from fastapi import HTTPException
from fastapi.responses import FileResponse, PlainTextResponse
from pydantic import BaseModel, Field
from . import db
from .intelligence import parse_owner_rss,research_audit,story_plan,srt_from_plan
from .source_connectors import registry,fetch_approved
from .tts import piper_config,generate

class FeedIn(BaseModel):
    feed_url:str=Field(min_length=12,max_length=1500)
    title:str=Field(min_length=3,max_length=120)
    xml_text:str=Field(min_length=35,max_length=262144)
class BindSource(BaseModel):
    source_version_id:str
class LocaleIn(BaseModel):
    locale:str=Field(pattern=r'^[a-z]{2}-[A-Z]{2}$')
    localized_scenes:list[str]=Field(min_length=1,max_length=20)
    owner_checked:bool=False
class ReviewIn(BaseModel):
    render_attempt_id:str
    reviewer:str=Field(min_length=2,max_length=80)
    rights_attested:bool
    claims_attested:bool
    watched_full_video:bool
    notes:str=Field(min_length=12,max_length=1000)
class YouTubeSyncIn(BaseModel):
    local_channel_id:str
    start_date:date
    end_date:date

class AnalyticsIn(BaseModel):
    channel_id:str
    report_date:date
    format:Literal['SHORT','LONG','ALL']
    views:int=Field(ge=0)
    watch_hours:float|None=Field(default=None,ge=0)
    subscribers_gained:int|None=Field(default=None,ge=0)
    estimated_revenue:float|None=Field(default=None,ge=0)
    currency:str|None=Field(default=None,max_length=3)


def register(app):
    from . import main as m
    def snapshot(c,pid):
        p=m.from_project(c,pid);plan=m._plan(c,p)
        claims=db.many(c,'SELECT * FROM claims WHERE research_plan_id=?',(plan['research_plan_id'],))
        edges=db.many(c,'SELECT * FROM evidence_edges WHERE claim_id IN (SELECT claim_id FROM claims WHERE research_plan_id=?)',(plan['research_plan_id'],))
        bound={x['source_version_id'] for x in db.many(c,'SELECT source_version_id FROM m1_project_sources WHERE project_id=?',(pid,))}
        script=m.latest_script(c,pid)
        scenes=m.latest_scenes(c,pid,script['script_version_id']) if script else []
        return p,claims,edges,bound,script,scenes

    @app.post('/api/projects/{project_id}/bind-source')
    def bind_source(project_id:str,b:BindSource):
        """Explicit opt-in for M0 source versions pre-dating project binding migration."""
        with db.transaction() as c:
            m.from_project(c,project_id)
            m.must(db.one(c,'SELECT source_version_id FROM source_versions WHERE source_version_id=?',(b.source_version_id,)),'Source not found')
            c.execute('INSERT OR IGNORE INTO m1_project_sources(project_id,source_version_id,bound_at) VALUES(?,?,?)',(project_id,b.source_version_id,m.now()))
        return {'project_id':project_id,'source_version_id':b.source_version_id,'verification':'NOT_AUTOMATIC'}

    @app.post('/api/projects/{project_id}/rss-import')
    def ingest_rss(project_id:str,b:FeedIn):
        """RSS/Atom provided by owner; never pretend it was fetched or independently validated."""
        try:entries=parse_owner_rss(b.xml_text)
        except ValueError as e:raise HTTPException(422,str(e))
        except Exception:raise HTTPException(422,'Malformed RSS/Atom XML')
        if not entries:raise HTTPException(422,'Feed had no usable public-http(s) entries')
        feed_id=m.uid()
        with db.transaction() as c:
            m.from_project(c,project_id)
            c.execute('INSERT INTO m1_source_feeds(feed_id,project_id,feed_url,title,imported_at,entries_json,source_status) VALUES(?,?,?,?,?,?,?)',
                      (feed_id,project_id,b.feed_url,b.title,m.now(),m.j(entries),'OWNER_SUPPLIED_XML'))
        return {'feed_id':feed_id,'entries':entries,'status':'OWNER_SUPPLIED_XML','fetched_remotely':False,
                'fact_verified':False}

    @app.get('/api/research/approved-feeds')
    def list_approved_feeds():
        return {'feeds':registry(),'network_collection':'EXPLICIT_APPROVED_ONLY',
                'default':'DISABLED','verification':'ARTICLE_CONTENT_NOT_VERIFIED'}

    @app.post('/api/projects/{project_id}/feeds/sync/{feed_key}')
    def fetch_approved_feed(project_id:str,feed_key:str):
        with db.read() as c:m.from_project(c,project_id)
        try:entry,items=fetch_approved(feed_key)
        except (ValueError,OSError) as e:raise HTTPException(422,str(e))
        if not items:raise HTTPException(422,'Approved feed contained no valid entries')
        fid=m.uid()
        with db.transaction() as c:
            m.from_project(c,project_id)
            c.execute('INSERT INTO m1_source_feeds(feed_id,project_id,feed_url,title,imported_at,entries_json,source_status) VALUES (?,?,?,?,?,?,?)',
                      (fid,project_id,entry['url'],entry['name'],m.now(),m.j(items),'FETCHED_FROM_APPROVED_FEED'))
        return {'feed_id':fid,'items':items,'remote_fetch':True,'permission_reviewed':True,
                'factual_claims_verified':False,'source_url':entry['url']}

    @app.get('/api/voice/piper-capabilities')
    def voice_capabilities():
        return {**piper_config(),'status':'OPTIONAL_OWNER_SETUP',
                'auto_voice_available':piper_config()['installed'] and piper_config()['licensed_model_reviewed']}

    @app.post('/api/projects/{project_id}/voice/opt-in-piper')
    def synthesize_opt_in_voice(project_id:str):
        with db.read() as c:
            m.from_project(c,project_id)
            script=m.must(m.latest_script(c,project_id),'Script required before narration')
        try:result=generate(script['script_text'],m.OUT/project_id/'voice.wav')
        except (ValueError,FileNotFoundError,TimeoutError) as e:raise HTTPException(409,str(e))
        with db.transaction() as c:
            c.execute('INSERT OR REPLACE INTO m2_voice_provenance(project_id,script_version_id,script_sha256,voice_source,generated_at) VALUES(?,?,?,?,?)',
                      (project_id,script['script_version_id'],script['content_sha256'],'OPT_IN_LOCAL_PIPER',m.now()))
        return {**result,'status':'NARRATION_REVIEW_REQUIRED','new_render_required':True}

    @app.get('/api/projects/{project_id}/research-audit')
    def audit(project_id:str):
        with db.read() as c:
            p,claims,edges,bound,script,scenes=snapshot(c,project_id)
            report=research_audit(claims,edges,script,bound)
            rows=db.many(c,'SELECT feed_id,title,source_status,imported_at FROM m1_source_feeds WHERE project_id=?',(project_id,))
        return {**report,'feed_ingestions':rows,'coverage':'ONLY_RECORDED_SOURCES_NOT_THE_WHOLE_WEB'}

    @app.post('/api/projects/{project_id}/story-plan')
    def compile_story(project_id:str):
        with db.transaction() as c:
            p,claims,edges,bound,script,scenes=snapshot(c,project_id)
            if not script or not scenes:raise HTTPException(409,'Script and storyboard scenes required')
            data=story_plan(script,scenes,p['locale'],p['format'],p['sport_id'])
            fp=m.sha(m.j(data));old=db.one(c,'SELECT story_plan_id FROM m2_story_plans WHERE project_id=? AND fingerprint=?',(project_id,fp))
            story_id=old['story_plan_id'] if old else m.uid()
            if not old:
                c.execute('INSERT INTO m2_story_plans(story_plan_id,project_id,script_version_id,plan_json,fingerprint,status,created_at) VALUES (?,?,?,?,?,?,?)',
                          (story_id,project_id,script['script_version_id'],m.j(data),fp,'QC_REQUIRED',m.now()))
        return {'story_plan_id':story_id,'story':data,'status':'QC_REQUIRED','claim_verification':'REQUIRES_HUMAN'}

    def latest_plan(c,project_id):
        p,claims,edges,bound,script,scenes=snapshot(c,project_id)
        if not script:raise HTTPException(409,'Script required')
        row=m.must(db.one(c,'SELECT * FROM m2_story_plans WHERE project_id=? AND script_version_id=? ORDER BY created_at DESC LIMIT 1',
                            (project_id,script['script_version_id'])),'Generate story plan first')
        expected=m.sha(m.j(story_plan(script,scenes,p['locale'],p['format'],p['sport_id'])))
        if expected!=row['fingerprint']:raise HTTPException(409,'Story plan stale; regenerate after scene changes')
        return p,script,json.loads(row['plan_json']),row

    @app.get('/api/projects/{project_id}/story-plan')
    def get_plan(project_id:str):
        with db.read() as c:
            p,script,data,row=latest_plan(c,project_id)
        return {'story_plan_id':row['story_plan_id'],'story':data,'status':row['status']}

    @app.post('/api/projects/{project_id}/locales')
    def save_locale(project_id:str,b:LocaleIn):
        with db.transaction() as c:
            p,script,data,row=latest_plan(c,project_id)
            if len(b.localized_scenes)!=data['beat_count']:raise HTTPException(422,'One localized on-screen text string is required per beat')
            texts=[t.strip() for t in b.localized_scenes]
            if any(not t or len(t)>450 for t in texts):raise HTTPException(422,'Each localized scene requires 1–450 characters')
            content_hash=m.sha(m.j(texts));old=db.one(c,'SELECT locale_edit_id FROM m2_locale_edits WHERE project_id=? AND script_version_id=? AND locale=?',
                                                    (project_id,script['script_version_id'],b.locale))
            locale_id=old['locale_edit_id'] if old else m.uid()
            if old:c.execute('UPDATE m2_locale_edits SET localized_scenes_json=?,owner_checked=?,content_sha256=?,created_at=? WHERE locale_edit_id=?',
                             (m.j(texts),int(b.owner_checked),content_hash,m.now(),locale_id))
            else:c.execute('INSERT INTO m2_locale_edits(locale_edit_id,project_id,script_version_id,locale,localized_scenes_json,owner_checked,content_sha256,created_at) VALUES (?,?,?,?,?,?,?,?)',
                           (locale_id,project_id,script['script_version_id'],b.locale,m.j(texts),int(b.owner_checked),content_hash,m.now()))
        return {'locale_edit_id':locale_id,'locale':b.locale,'owner_checked':b.owner_checked,
                'status':'NEEDS_VOICE_AND_FINAL_TIMING_QC','is_machine_translation':False}

    @app.get('/api/projects/{project_id}/captions/{locale}')
    def captions(project_id:str,locale:str):
        with db.read() as c:
            p,script,plan,row=latest_plan(c,project_id)
            localized=None
            if locale!=p['locale']:
                rec=db.one(c,'SELECT * FROM m2_locale_edits WHERE project_id=? AND script_version_id=? AND locale=?',
                           (project_id,script['script_version_id'],locale))
                if not rec:raise HTTPException(404,'Locale not prepared')
                localized=json.loads(rec['localized_scenes_json'])
        text=srt_from_plan(plan,localized)
        return PlainTextResponse(text,media_type='text/plain; charset=utf-8',headers={'X-Caption-Timing':'SCENE_APPROXIMATION_NOT_WORD_ALIGNED'})

    def fingerprint(c,project_id,render_id):
        p,claims,edges,bound,script,scenes=snapshot(c,project_id)
        rend=m.must(db.one(c,'SELECT * FROM render_attempts WHERE render_attempt_id=? AND project_id=?',(render_id,project_id)),
                    'Render not found for this project')
        claimstate=[(x['claim_id'],x['verification_status'],x['updated_at']) for x in claims]
        locale_edits=db.many(c,'SELECT locale,content_sha256,owner_checked FROM m2_locale_edits WHERE project_id=?',(project_id,))
        # Material project change invalidates human approvals; rendering might be based on older scenes/voice.
        fields={'render_sha256':rend['output_sha256'],'project_revision':p['revision'],
                'render_project_revision':rend['project_revision'],'script_id':script['script_version_id'] if script else None,
                'claims':claimstate,'bound_sources':sorted(bound),
                'scene_sha256':[x['spec_sha256'] for x in scenes],
                'locale_edits':locale_edits}
        return m.sha(m.j(fields)),p,rend,claims,script

    @app.post('/api/projects/{project_id}/review-video')
    def review_video(project_id:str,b:ReviewIn):
        with db.transaction() as c:
            fp,p,rend,claims,script=fingerprint(c,project_id,b.render_attempt_id)
            if rend['status']!='TECHNICAL_PREVIEW':raise HTTPException(409,'Only recognized local render artifacts may be reviewed')
            if not (b.rights_attested and b.claims_attested and b.watched_full_video):
                raise HTTPException(409,'Require full watch-through, factual and rights review to record approval')
            if not (m.OUT/str(rend['output_relpath'])).is_file():raise HTTPException(409,'Review blocked: video file missing')
            if not script:raise HTTPException(409,'Script missing')
            if rend['project_revision']!=p['revision']:raise HTTPException(409,'Video stale after project revision; re-render')
            if any(x['verification_status']!='SUPPORTED' for x in claims):
                raise HTTPException(409,'Unreviewed/unsupported claims must be resolved first')
            rid=m.uid()
            c.execute('INSERT INTO m3_review_records(review_id,project_id,render_attempt_id,fingerprint,rights_attested,claims_attested,watched_full_video,reviewer,notes,status,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)',
                      (rid,project_id,b.render_attempt_id,fp,1,1,1,b.reviewer,b.notes,'APPROVED',m.now()))
        return {'review_id':rid,'reviewed':True,'status':'APPROVED_FOR_REVIEW_PACKET',
                'publication_ready':False,'note':'Rendered file remains technical preview; professional production QC is missing'}

    @app.post('/api/projects/{project_id}/export-review-packet')
    def export_packet(project_id:str):
        with db.transaction() as c:
            p=m.from_project(c,project_id)
            rev=m.must(db.one(c,"SELECT * FROM m3_review_records WHERE project_id=? AND status='APPROVED' ORDER BY created_at DESC LIMIT 1",(project_id,)),
                       'Approved review of latest video required')
            fp,p,rend,claims,script=fingerprint(c,project_id,rev['render_attempt_id'])
            if fp!=rev['fingerprint']:raise HTTPException(409,'Approval stale due to project/claim/locale changes')
            src=(m.OUT/rend['output_relpath']).resolve()
            if m.OUT.resolve() not in src.parents or not src.exists():raise HTTPException(409,'Render missing')
            latest_plan_row=db.one(c,'SELECT * FROM m2_story_plans WHERE project_id=? AND script_version_id=? ORDER BY created_at DESC LIMIT 1',
                                   (project_id,script['script_version_id']))
            packet=m.OUT/project_id/'export_packets'
            packet.mkdir(exist_ok=True,parents=True)
            path=packet/f'{rend["render_attempt_id"]}.zip'
            audit_result=research_audit(claims,db.many(c,'SELECT * FROM evidence_edges WHERE claim_id IN (SELECT claim_id FROM claims WHERE research_plan_id=(SELECT research_plan_id FROM research_plans WHERE channel_id=? AND json_extract(plan_json,\'$.project_id\')=?))',(p['channel_id'],project_id)),script,
                                        {r['source_version_id'] for r in db.many(c,'SELECT source_version_id FROM m1_project_sources WHERE project_id=?',(project_id,))})
            pack_manifest={'kind':'PRIVATE_REVIEW_PACKET_NOT_PUBLISH_READY','project_id':project_id,'video_sha256':rend['output_sha256'],
                           'human_review_id':rev['review_id'],'project_claim_audit':audit_result,
                           'publication_authorized':False,'requires_professional_final_render':True}
            with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED) as z:
                z.write(src,'technical_preview.mp4')
                z.writestr('README.txt','Technical prototype preview ONLY. This ZIP is not cleared for YouTube publication.\n')
                z.writestr('review_manifest.json',json.dumps(pack_manifest,indent=2,ensure_ascii=False))
                z.writestr('script.txt',script['script_text'])
                if latest_plan_row:
                    plan=json.loads(latest_plan_row['plan_json'])
                    z.writestr('creative_timeline.json',json.dumps(plan,indent=2,ensure_ascii=False))
                    z.writestr('approximate_scene_cards.srt',srt_from_plan(plan))
                z.writestr('project_claims.json',json.dumps(claims,indent=2,ensure_ascii=False))
            eid=m.uid();relative=str(path.relative_to(m.OUT))
            c.execute('INSERT INTO m3_exports(export_id,project_id,render_attempt_id,review_id,video_sha256,export_relpath,status,created_at) VALUES(?,?,?,?,?,?,?,?)',
                      (eid,project_id,rend['render_attempt_id'],rev['review_id'],rend['output_sha256'],relative,'REVIEW_ONLY',m.now()))
        return {'export_id':eid,'download_url':f'/api/review-packets/{eid}','status':'REVIEW_ONLY','publication_ready':False}

    @app.get('/api/review-packets/{export_id}')
    def get_packet(export_id:str):
        with db.read() as c:
            row=m.must(db.one(c,'SELECT * FROM m3_exports WHERE export_id=?',(export_id,)),'Export not found')
        path=(m.OUT/row['export_relpath']).resolve()
        if m.OUT.resolve() not in path.parents or not path.is_file():raise HTTPException(404,'Packet missing')
        return FileResponse(path,media_type='application/zip',filename='ViralOS_Private_Review_Packet.zip')

    @app.post('/api/analytics/owner-entry')
    def owner_analytics(b:AnalyticsIn):
        if (b.estimated_revenue is None) != (b.currency is None):
            raise HTTPException(422,'Revenue and currency must be provided together')
        rid=m.uid()
        with db.transaction() as c:
            m.must(db.one(c,'SELECT channel_id FROM channels WHERE channel_id=?',(b.channel_id,)),'Channel not found')
            c.execute('INSERT OR REPLACE INTO m3_analytics_imports(import_id,channel_id,report_date,format,views,watch_hours,subscribers_gained,estimated_revenue,revenue_currency,provenance,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)',
                      (rid,b.channel_id,str(b.report_date),b.format,b.views,b.watch_hours,b.subscribers_gained,b.estimated_revenue,b.currency,
                       'OWNER_ENTERED_NOT_VERIFIED',m.now()))
        return {'import_id':rid,'provenance':'OWNER_ENTERED_NOT_VERIFIED','youtube_api_verified':False}

    @app.get('/api/analytics/{channel_id}')
    def channel_analytics(channel_id:str):
        with db.read() as c:
            m.must(db.one(c,'SELECT channel_id FROM channels WHERE channel_id=?',(channel_id,)),'Channel not found')
            entries=db.many(c,'SELECT * FROM m3_analytics_imports WHERE channel_id=? ORDER BY report_date DESC LIMIT 365',(channel_id,))
        return {'observations':entries,'source':'OWNER_ENTERED_NOT_VERIFIED','inferred_revenue':False}

    @app.get('/api/projects/{project_id}/quality-report')
    def quality_report(project_id:str):
        with db.read() as c:
            p,claims,edges,bound,script,scenes=snapshot(c,project_id)
            research=research_audit(claims,edges,script,bound)
            renders=db.many(c,'SELECT * FROM render_attempts WHERE project_id=? ORDER BY started_at DESC LIMIT 1',(project_id,))
            issues=list(research['gaps'])
            if not scenes:issues.append('No storyboard scenes')
            if not (m.OUT/project_id/'voice.wav').exists():issues.append('No narration audio')
            if not renders:issues.append('No playable render')
            elif renders[0]['project_revision']!=p['revision']:issues.append('Latest render stale after scene/script revision')
            else:issues.append('Latest render is a TECHNICAL_PREVIEW, not professionally finished output')
            prov=db.one(c,'SELECT * FROM m2_voice_provenance WHERE project_id=?',(project_id,))
            if prov and script and prov['script_version_id']!=script['script_version_id']:
                issues.append('Locally generated voice was produced for a previous script revision')
            if script and not db.one(c,'SELECT story_plan_id FROM m2_story_plans WHERE project_id=? AND script_version_id=?',(project_id,script['script_version_id'])):
                issues.append('No typed creative timeline compiled')
        return {'status':'BLOCKED_FOR_PUBLICATION','issues':issues,'research':research,
                'human_video_review':'REQUIRED','youtube_upload':'DISABLED',
                'development_stage':'M1_M3_ASSISTED_PROTOTYPE'}

    @app.post('/api/youtube/analytics/sync')
    def sync_authorized_youtube(b:YouTubeSyncIn):
        from .youtube_analytics import credentials_for,verify_channel,fetch_daily_report,normalize_report
        if b.end_date<b.start_date or (b.end_date-b.start_date).days>90:
            raise HTTPException(422,'Date range must be ordered and at most 90 days')
        with db.read() as c:
            account=m.must(db.one(c,'SELECT * FROM m3_youtube_accounts WHERE local_channel_id=?',(b.local_channel_id,)),
                           'Connect owner account with the read-only OAuth CLI first')
        try:
            creds=credentials_for(b.local_channel_id)
            verify_channel(creds,account['remote_channel_id'])
            report=fetch_daily_report(creds,str(b.start_date),str(b.end_date))
            rows=normalize_report(report)
        except Exception as e:
            # Do not reveal secrets or detailed OAuth error payload in API response.
            raise HTTPException(503,'Authorized YouTube analytics unavailable; check local credentials, API access and logs') from e
        with db.transaction() as c:
            for item in rows:
                c.execute('INSERT OR REPLACE INTO m3_analytics_imports(import_id,channel_id,report_date,format,views,watch_hours,subscribers_gained,estimated_revenue,revenue_currency,provenance,created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)',
                          (m.uid(),b.local_channel_id,item['report_date'],'ALL',item['views'],item['watch_hours'],item['subscribers_gained'],None,None,'AUTHORIZED_API',m.now()))
        return {'imported_days':len(rows),'provenance':'AUTHORIZED_API','remote_channel_id':account['remote_channel_id'],
                'format':'ALL','revenue':'NOT_REQUESTED_NO_MONETARY_SCOPE','published':False}

    @app.get('/api/youtube/capabilities')
    def youtube_capabilities():
        from .youtube_analytics import environment
        return {'youtube_upload_enabled':False,'oauth_connected':'REQUIRES_EXPLICIT_CLI_LINK','authenticated_channel':None,
                'read_only_analytics_adapter':environment(),
                'video_upload_status':'LEGACY_UPLOAD_ROUTE_DISABLED; OPT_IN_PRIVATE_VIA_/api/m3/private-upload/intents',
                'manual_package':'PRIVATE_REVIEW_ONLY','analytics':'OWNER_ENTRY_OR_AUTHORIZED_READONLY_WHEN_CONNECTED',
                'future_adapter':'google-api-python-client OAuth youtube.upload; NOT active',
                'reason':'No professional final render/credential verification or monetization assurance'}

    @app.post('/api/youtube/upload')
    def safe_upload_gate():
        raise HTTPException(403,'Publishing is disabled for M1–M3 development previews. Owner approval, final QC and authorized OAuth required.')
