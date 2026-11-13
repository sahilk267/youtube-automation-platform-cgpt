"""ViralOS Launch v3: bounded, local-only CPU implementation vertical slice.

Manual evidence ≠ verified claim. Render preview ≠ monetization-ready video.
No internet fetch, no YouTube publishing, no AI hallucination fallback.
"""
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit
import hashlib,json, os, shutil, sqlite3, uuid, wave
from typing import Literal

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from . import db
from .renderer import render

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'outputs'
STATIC=ROOT/'app'/'static'

def uid():return str(uuid.uuid4())
def now():return datetime.now(timezone.utc).isoformat(timespec='microseconds')
def sha(s):return hashlib.sha256(s.encode('utf8')).hexdigest()
def j(v):return json.dumps(v,ensure_ascii=False,sort_keys=True)
def must(row,msg='Not found'):
    if not row:raise HTTPException(404,msg)
    return row

def from_project(c,project_id):
    return must(db.one(c,'SELECT p.*,ch.sport_id,ch.locale FROM content_projects p JOIN channels ch ON ch.channel_id=p.channel_id WHERE p.project_id=?',(project_id,)),'Project not found')

def latest_script(c,project_id):
    return db.one(c,'SELECT * FROM scripts WHERE project_id=? ORDER BY revision DESC LIMIT 1',(project_id,))

def latest_scenes(c,project_id,script_id):
    return db.many(c,'SELECT * FROM scenes WHERE project_id=? AND script_version_id=? ORDER BY order_index',(project_id,script_id))

@asynccontextmanager
async def lifespan(app):
    db.initialize();OUT.mkdir(parents=True,exist_ok=True)
    # On process crash, an in-flight local render cannot be resumed frame-by-frame.
    # Mark it FAILED so the operator may explicitly retry with input hashes checked.
    with db.transaction() as c:
        c.execute("UPDATE jobs SET state='FAILED',error_code='INTERRUPTED_ON_STARTUP',updated_at=? "
                  "WHERE state='RUNNING' AND job_type IN ('CPU_PREVIEW','M2_STUDIO_PREVIEW')",(now(),))
    # An interrupted network request could have created a PRIVATE remote video.
    # Mark unknown; NEVER blindly resubmit on restart.
    with db.transaction() as c:
        c.execute("UPDATE m3_private_upload_intents SET state='REMOTE_UNKNOWN',last_error='INTERRUPTED_ON_STARTUP',updated_at=? WHERE state='IN_FLIGHT'",(now(),))
    yield

app=FastAPI(title='ViralOS Launch — CPU Vertical Slice',version='0.7.0',lifespan=lifespan)
app.mount('/static', StaticFiles(directory=str(STATIC)),name='static')

class ChannelIn(BaseModel):
    name:str=Field(min_length=2,max_length=100)
    sport_id:Literal['cricket','nfl']
    locale:str=Field(pattern=r'^[a-z]{2}-[A-Z]{2}$')
    market:str=Field(min_length=2,max_length=80)
    timezone:str=Field(min_length=3,max_length=60)

class ProjectIn(BaseModel):
    channel_id:str
    title:str=Field(min_length=6,max_length=180)
    original_angle:str=Field(min_length=10,max_length=600)
    format:Literal['SHORT','LONG']='SHORT'

class ManualSourceIn(BaseModel):
    url:str=Field(min_length=12,max_length=2000)
    publisher:str=Field(min_length=2,max_length=150)
    excerpt:str=Field(min_length=15,max_length=10000)
    locale:str='en-US'

class ClaimIn(BaseModel):
    proposition:str=Field(min_length=10,max_length=900)
    source_version_id:str
    relation:Literal['SUPPORTS','REFUTES','CONTEXT']='SUPPORTS'
    locator:str=Field(min_length=2,max_length=120)

class ClaimReview(BaseModel):
    status:Literal['SUPPORTED','REFUTED','MIXED','UNVERIFIABLE','OUT_OF_CONTEXT','REQUIRES_HUMAN_REVIEW']
    reviewer:str=Field(min_length=2,max_length=100)
    explanation:str=Field(min_length=12,max_length=800)

class LinkSpan(BaseModel):
    claim_id:str
    exact_quote:str=Field(min_length=4)

class ScriptIn(BaseModel):
    text:str=Field(min_length=25,max_length=15000)
    claim_links:list[LinkSpan]=[]

class SceneIn(BaseModel):
    text:str=Field(min_length=4,max_length=450)
    duration_seconds:float=Field(ge=1,le=15)
    claim_ids:list[str]=[]

@app.get('/')
def index():return FileResponse(STATIC/'index.html')

@app.get('/health')
def health():
    with db.read() as c:
        tables=c.execute("select count(*) from sqlite_master where type='table'").fetchone()[0]
    return {'status':'ok','mode':'LOCAL_CPU','schema_tables':tables,'app_stage':'IMPLEMENTED_VERTICAL_SLICE',
            'publishing_enabled':False,'private_upload_opt_in_available':True,'private_upload_opt_in_enabled':os.getenv('VIRALOS_ENABLE_PRIVATE_UPLOAD')=='1','youtube_connected':False,'ai_autoresearch_enabled':False,
            'video_generation_enabled':False,'note':'All source text is supplied by operator, not independently verified'}

@app.get('/api/capabilities')
def capabilities():
    return {'cpu':True,'ffmpeg':bool(shutil.which('ffmpeg')),'ffprobe':bool(shutil.which('ffprobe')),
            'gpu':{'status':'UNTESTED_UNAVAILABLE','enabled':False},
            'voice':{'owner_wav_import':True,'piper_automatic':False},
            'external_upload':{'enabled':False},'mode':'CPU_ONLY'}

@app.get('/api/channels')
def channels():
    with db.read() as c:return db.many(c,'SELECT * FROM channels ORDER BY created_at DESC')

@app.post('/api/channels')
def create_channel(b:ChannelIn):
    x=uid();t=now()
    with db.transaction() as c:
        c.execute('INSERT INTO channels(channel_id,domain_id,sport_id,name,locale,market,timezone,risk_policy_id,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?)',
                  (x,'sports',b.sport_id,b.name,b.locale,b.market,b.timezone,'MANUAL_EDITORIAL',t,t))
    return {'channel_id':x,'name':b.name,'sport_id':b.sport_id}

@app.get('/api/projects')
def projects():
    with db.read() as c:
        return db.many(c,'SELECT p.*,c.name AS channel_name FROM content_projects p JOIN channels c ON c.channel_id=p.channel_id ORDER BY p.created_at DESC')

@app.post('/api/projects')
def create_project(b:ProjectIn):
    p=uid();topic=uid();plan=uid();t=now();key=sha(b.title.casefold())
    with db.transaction() as c:
        ch=must(db.one(c,'SELECT * FROM channels WHERE channel_id=?',(b.channel_id,)),'Channel not found')
        existing=db.one(c,'SELECT topic_id FROM topics WHERE domain_id=? AND canonical_key=?',('sports',key))
        if existing: topic=existing['topic_id']
        else:c.execute('INSERT INTO topics(topic_id,domain_id,canonical_key,first_observed_at) VALUES (?,?,?,?)',(topic,'sports',key,t))
        duplicate=db.one(c,'SELECT project_id FROM content_projects WHERE channel_id=? AND topic_id=? AND angle_sha256=? AND format=?',(b.channel_id,topic,sha(b.original_angle),b.format))
        if duplicate:raise HTTPException(409,'An identical project already exists; open it or change the editorial angle')
        c.execute('INSERT INTO content_projects(project_id,channel_id,topic_id,domain_id,editorial_angle,angle_sha256,format,status,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?)',
                  (p,b.channel_id,topic,'sports',b.original_angle,sha(b.original_angle),b.format,'DRAFT',t,t))
        c.execute('INSERT INTO research_plans(research_plan_id,channel_id,topic_id,domain_id,depth,plan_json,status,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?)',
                  (plan,b.channel_id,topic,'sports','QUICK_VERIFIED_BRIEF',j({'project_id':p,'mode':'MANUAL_EVIDENCE_FIRST','title':b.title,'question':b.original_angle,'completeness':'NOT_EVALUATED'}),'DRAFT',t,t))
    return {'project_id':p,'research_plan_id':plan,'topic_id':topic,'title':b.title}

@app.get('/api/projects/{project_id}')
def get_project(project_id:str):
    with db.read() as c:
        p=from_project(c,project_id)
        plan=_plan(c,p)
        claims=db.many(c,'SELECT cl.* FROM claims cl WHERE research_plan_id=? ORDER BY created_at',(plan['research_plan_id'],))
        evid=db.many(c,'SELECT e.*,s.canonical_url,sv.text_excerpt FROM evidence_edges e JOIN source_versions sv ON sv.source_version_id=e.source_version_id JOIN sources s ON s.source_id=sv.source_id WHERE e.claim_id IN (SELECT claim_id FROM claims WHERE research_plan_id=?)',(plan['research_plan_id'],))
        script=latest_script(c,project_id)
        scenes=latest_scenes(c,project_id,script['script_version_id']) if script else []
        renders=db.many(c,'SELECT * FROM render_attempts WHERE project_id=? ORDER BY started_at DESC LIMIT 4',(project_id,))
        return {'project':p,'plan':plan,'claims':claims,'evidence':evid,'script':script,'scenes':[dict(s, spec=json.loads(s['spec_json'])) for s in scenes],
                'renders':renders,'voice_imported':(OUT/project_id/'voice.wav').exists(),
                'report':_review_report(c,project_id,plan,script,scenes)}

def _review_report(c,project_id,plan,script,scenes):
    claims=db.many(c,'SELECT * FROM claims WHERE research_plan_id=?',(plan['research_plan_id'],))
    unsupported=[cl['claim_id'] for cl in claims if cl['verification_status']!='SUPPORTED']
    unlinked=[]
    if script:
        linked={r['claim_id'] for r in db.many(c,'SELECT claim_id FROM script_claim_links WHERE script_version_id=?',(script['script_version_id'],))}
        unlinked=[cl['claim_id'] for cl in claims if cl['claim_id'] not in linked]
    voice=(OUT/project_id/'voice.wav').exists()
    return {'research':'MANUAL_NOT_INDEPENDENTLY_VERIFIED','unsupported_claims':unsupported,'claims_missing_script_links':unlinked,
            'scenes':len(scenes),'has_narration':voice,'full_watchthrough':'NOT_COMPLETED',
            'upload_status':'DISABLED','publish_ready':False}

def _plan(c,p):
    return must(db.one(c,"SELECT * FROM research_plans WHERE channel_id=? AND json_extract(plan_json,'$.project_id')=?",(p['channel_id'],p['project_id'])), 'Project research plan missing')

@app.post('/api/projects/{project_id}/sources')
def add_source(project_id:str,b:ManualSourceIn):
    parsed=urlsplit(b.url)
    if parsed.scheme not in ('https','http') or not parsed.hostname or parsed.username or parsed.password:
        raise HTTPException(422,'Only public http(s) URL metadata accepted; service does not fetch remote content')
    now_time=now();source_id=uid();version_id=uid();content_hash=sha(b.excerpt)
    with db.transaction() as c:
        from_project(c,project_id)
        existing=db.one(c,'SELECT * FROM sources WHERE canonical_url=?',(b.url,))
        if existing:source_id=existing['source_id']
        else:c.execute('INSERT INTO sources(source_id,canonical_url,original_publisher,source_class,created_at) VALUES(?,?,?,?,?)',(source_id,b.url,b.publisher,'MANUAL_SUPPLIED',now_time))
        c.execute('INSERT INTO source_versions(source_version_id,source_id,retrieved_at,content_sha256,original_language,rights_policy_id,access_status,text_excerpt,metadata_json) VALUES(?,?,?,?,?,?,?,?,?)',
                  (version_id,source_id,now_time,content_hash,b.locale,'UNKNOWN_RIGHTS_NOT_FOR_MEDIA','METADATA_ONLY',b.excerpt,j({'intake':'OWNER_SUPPLIED','verification':'NOT_AUTOMATED','not_downloaded':True})))
        c.execute('INSERT OR IGNORE INTO m1_project_sources(project_id,source_version_id,bound_at) VALUES (?,?,?)',(project_id,version_id,now_time))
    return {'source_version_id':version_id,'verification':'UNVERIFIED_MANUAL_SOURCE','fetched':False}

@app.post('/api/projects/{project_id}/claims')
def add_claim(project_id:str,b:ClaimIn):
    cid=uid();eid=uid();t=now()
    with db.transaction() as c:
        p=from_project(c,project_id);plan=_plan(c,p)
        sv=must(db.one(c,'SELECT * FROM source_versions WHERE source_version_id=?',(b.source_version_id,)),'Source version not found')
        if not db.one(c,'SELECT project_id FROM m1_project_sources WHERE project_id=? AND source_version_id=?',(project_id,b.source_version_id)):
            raise HTTPException(409,'Source version is not bound to this project; attach source first')
        c.execute('INSERT INTO claims(claim_id,research_plan_id,proposition,claim_type,verification_status,created_at,updated_at) VALUES (?,?,?,?,?,?,?)',
                  (cid,plan['research_plan_id'],b.proposition,'FACT','UNREVIEWED',t,t))
        c.execute('INSERT INTO evidence_edges(evidence_edge_id,claim_id,source_version_id,relation,locator,excerpt_or_value,human_review_required) VALUES (?,?,?,?,?,?,?)',
                  (eid,cid,b.source_version_id,b.relation,b.locator,sv['text_excerpt'] or '',1))
    return {'claim_id':cid,'verification_status':'UNREVIEWED','review_required':True}

@app.post('/api/claims/{claim_id}/review')
def review_claim(claim_id:str,b:ClaimReview):
    with db.transaction() as c:
        claim=must(db.one(c,'SELECT * FROM claims WHERE claim_id=?',(claim_id,)),'Claim not found')
        if b.status=='SUPPORTED':
            link=c.execute("SELECT count(*) FROM evidence_edges WHERE claim_id=? AND relation='SUPPORTS'",(claim_id,)).fetchone()[0]
            if not link:raise HTTPException(409,'Cannot mark supported without supporting source link')
        c.execute('UPDATE claims SET verification_status=?,reviewer_id=?,review_reason=?,updated_at=? WHERE claim_id=?',
                  (b.status,b.reviewer,b.explanation,now(),claim_id))
    return {'claim_id':claim_id,'status':b.status,'review_type':'HUMAN_ATTESTATION_ONLY'}

@app.post('/api/projects/{project_id}/script')
def save_script(project_id:str,b:ScriptIn):
    with db.transaction() as c:
        p=from_project(c,project_id);plan=_plan(c,p)
        prev=latest_script(c,project_id);rev=(prev['revision'] if prev else 0)+1
        sid=uid()
        c.execute('INSERT INTO scripts(script_version_id,project_id,revision,original_language,script_text,narrative_plan_json,content_sha256,created_at) VALUES (?,?,?,?,?,?,?,?)',
                  (sid,project_id,rev,p['locale'],b.text,j({'origin':'MANUAL_SCRIPT','claim_linking':'MANUAL','professional_video_plan':'NOT_YET_VERIFIED'}),sha(b.text),now()))
        for link in b.claim_links:
            cl=must(db.one(c,'SELECT * FROM claims WHERE claim_id=? AND research_plan_id=?',(link.claim_id,plan['research_plan_id'])),'Claim not in this project')
            offset=b.text.find(link.exact_quote)
            if offset<0:raise HTTPException(422,f'Exact claim quote not present in script: {link.claim_id}')
            c.execute('INSERT INTO script_claim_links(script_version_id,claim_id,span_start,span_end) VALUES (?,?,?,?)',
                      (sid,link.claim_id,offset,offset+len(link.exact_quote)))
        c.execute("UPDATE content_projects SET status='SCRIPTING',revision=revision+1,updated_at=? WHERE project_id=?",(now(),project_id))
    return {'script_version_id':sid,'revision':rev,'links':len(b.claim_links),'source_audit':'HUMAN_REVIEW_REQUIRED'}

@app.post('/api/projects/{project_id}/scenes')
def add_scene(project_id:str,b:SceneIn):
    with db.transaction() as c:
        p=from_project(c,project_id);script=must(latest_script(c,project_id),'Write a script first')
        for clid in b.claim_ids:
            valid=db.one(c,'SELECT claim_id FROM script_claim_links WHERE script_version_id=? AND claim_id=?',(script['script_version_id'],clid))
            if not valid:raise HTTPException(409,'Scene claim must be linked to latest script')
        count=c.execute('SELECT count(*) FROM scenes WHERE script_version_id=?',(script['script_version_id'],)).fetchone()[0]
        if count>=20:raise HTTPException(422,'Preview limit is 20 scenes')
        scene=uid();spec={'prototype_type':'MANUAL_ORIGINAL_TEXT_SCENE','text':b.text,'duration_seconds':b.duration_seconds,'claim_ids':b.claim_ids,'visual_type':'TEXT_MOTION','rights':'ORIGINAL_ONLY','not_a_complete_v3_ShotPlan':True}
        c.execute('INSERT INTO scenes(scene_id,project_id,script_version_id,order_index,spec_json,spec_sha256,status) VALUES (?,?,?,?,?,?,?)',
                  (scene,project_id,script['script_version_id'],count,j(spec),sha(j(spec)),'DRAFT'))
        c.execute("UPDATE content_projects SET status='PRODUCING',revision=revision+1,updated_at=? WHERE project_id=?",(now(),project_id))
    return {'scene_id':scene,'order':count,'status':'DRAFT'}

@app.post('/api/projects/{project_id}/voice')
async def upload_voice(project_id:str,file:UploadFile=File(...)):
    if not file.filename or not file.filename.lower().endswith('.wav'):raise HTTPException(422,'Only owner-supplied WAV narration accepted')
    with db.read() as c:from_project(c,project_id)
    data=await file.read(16*1024*1024+1)
    if len(data)>16*1024*1024:raise HTTPException(413,'Narration max 16 MB in this prototype')
    folder=OUT/project_id;folder.mkdir(parents=True,exist_ok=True)
    target=folder/'voice.wav'
    temp=folder/'voice.tmp'
    try:
        temp.write_bytes(data)
        with wave.open(str(temp),'rb') as w:
            if w.getnchannels() not in (1,2) or w.getframerate()<8000:raise ValueError('Unsupported audio format')
            duration=w.getnframes()/w.getframerate()
            if duration<0.25 or duration>600:raise ValueError('Audio must be between 0.25 and 600 seconds')
        os.replace(temp,target)
        with db.transaction() as c:
            c.execute('DELETE FROM m2_voice_provenance WHERE project_id=?',(project_id,))
    except Exception:
        temp.unlink(missing_ok=True)
        raise HTTPException(422,'Invalid WAV or out-of-range duration')
    return {'uploaded':True,'duration_seconds':round(duration,2),'source':'OWNER_SUPPLIED','speech_alignment':'NOT_MEASURED'}

@app.post('/api/projects/{project_id}/queue-preview')
def queue_preview(project_id:str):
    with db.transaction() as c:
        p=from_project(c,project_id);script=must(latest_script(c,project_id),'Script required')
        scenes=latest_scenes(c,project_id,script['script_version_id'])
        if not scenes:raise HTTPException(409,'Storyboard scenes required')
        voice=OUT/project_id/'voice.wav'
        generated_voice=db.one(c,'SELECT * FROM m2_voice_provenance WHERE project_id=?',(project_id,))
        if voice.exists() and generated_voice and generated_voice['script_version_id']!=script['script_version_id']:
            raise HTTPException(409,'Piper narration generated for older script; regenerate or import a new owner WAV')
        content_hash=sha(script['content_sha256']+''.join(s['spec_sha256'] for s in scenes)+(hashlib.sha256(voice.read_bytes()).hexdigest() if voice.exists() else 'NO_VOICE'))
        existing=db.one(c,'SELECT job_id,state FROM jobs WHERE channel_id=? AND job_type=? AND idempotency_key=?',(p['channel_id'],'CPU_PREVIEW',sha(project_id+':'+content_hash)))
        if existing:return dict(existing,already_exists=True)
        job=uid();t=now()
        c.execute('INSERT INTO jobs(job_id,channel_id,domain_id,job_type,input_sha256,idempotency_key,state,progress_json,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?)',
                  (job,p['channel_id'],'sports','CPU_PREVIEW',content_hash,sha(project_id+':'+content_hash),'QUEUED',j({'project_id':project_id,'script_version_id':script['script_version_id']}),t,t))
    return {'job_id':job,'state':'QUEUED','already_exists':False}

@app.get('/api/jobs')
def list_jobs():
    with db.read() as c:return db.many(c,'SELECT job_id,job_type,state,error_code,progress_json,updated_at FROM jobs ORDER BY created_at DESC LIMIT 40')

@app.post('/api/jobs/run-next')
def run_next():
    with db.transaction() as c:
        job=db.one(c,"SELECT * FROM jobs WHERE state='QUEUED' AND job_type='CPU_PREVIEW' ORDER BY created_at LIMIT 1")
        if not job:return {'state':'EMPTY','message':'No queued preview jobs'}
        c.execute("UPDATE jobs SET state='RUNNING',attempt_count=attempt_count+1,updated_at=? WHERE job_id=?",(now(),job['job_id']))
    jid=job['job_id'];p_id=json.loads(job['progress_json'])['project_id'];outdir=OUT/p_id/jid
    try:
        with db.read() as c:
            p=from_project(c,p_id);script=must(latest_script(c,p_id))
            if script['script_version_id']!=json.loads(job['progress_json'])['script_version_id']:
                raise RuntimeError('Script changed since queued; cancel and requeue revised project')
            scenes=latest_scenes(c,p_id,script['script_version_id'])
            raw=[json.loads(s['spec_json']) for s in scenes]
        voice=OUT/p_id/'voice.wav'
        actual_input_hash=sha(script['content_sha256']+''.join(s['spec_sha256'] for s in scenes)+(hashlib.sha256(voice.read_bytes()).hexdigest() if voice.exists() else 'NO_VOICE'))
        if actual_input_hash!=job['input_sha256']:
            raise RuntimeError('Project input changed after queueing; requeue after refreshing input')
        output,manifest=render(p_id,script['revision'],raw,outdir,format_name=p['format'],sport=p['sport_id'],voice=voice if voice.is_file() else None)
        r_id=uid();t=now();rel=str(output.relative_to(OUT));file_hash=hashlib.sha256(output.read_bytes()).hexdigest()
        with db.transaction() as c:
            c.execute('INSERT INTO render_attempts(render_attempt_id,project_id,project_revision,manifest_json,output_relpath,output_sha256,status,started_at,finished_at) VALUES (?,?,?,?,?,?,?,?,?)',
                      (r_id,p_id,p['revision'],j(manifest),rel,file_hash,'TECHNICAL_PREVIEW',t,t))
            c.execute("UPDATE jobs SET state='SUCCEEDED',progress_json=?,updated_at=? WHERE job_id=?",(j({'project_id':p_id,'render_attempt_id':r_id,'file':rel,'has_voice':bool(voice.exists())}),t,jid))
        return {'job_id':jid,'state':'SUCCEEDED','preview_url':f'/api/previews/{r_id}','has_voice':bool(voice.exists()),'publish_ready':False}
    except Exception as ex:
        with db.transaction() as c:
            c.execute("UPDATE jobs SET state='FAILED',error_code=?,updated_at=? WHERE job_id=?",(str(ex)[:200],now(),jid))
        return {'job_id':jid,'state':'FAILED','error':str(ex)[:500]}

@app.get('/api/previews/{render_id}')
def preview(render_id:str):
    with db.read() as c:
        r=must(db.one(c,'SELECT output_relpath FROM render_attempts WHERE render_attempt_id=?',(render_id,)),'Preview not found')
    p=(OUT/r['output_relpath']).resolve()
    if OUT.resolve() not in p.parents or not p.is_file():raise HTTPException(404,'File not found')
    return FileResponse(p,media_type='video/mp4',filename='viralos_technical_preview.mp4')


@app.post('/api/jobs/{job_id}/retry')
def retry_failed_job(job_id:str):
    with db.transaction() as c:
        record=must(db.one(c,'SELECT * FROM jobs WHERE job_id=?',(job_id,)),'Job not found')
        if record['state']!='FAILED':raise HTTPException(409,'Only FAILED jobs can be manually requeued')
        c.execute("UPDATE jobs SET state='QUEUED',error_code=NULL,updated_at=? WHERE job_id=?",(now(),job_id))
    return {'job_id':job_id,'state':'QUEUED','note':'Retry only succeeds if current inputs still match originally queued hash'}

@app.get('/api/editions')
def editions():
    return {'active':'LAUNCH_VERTICAL_SLICE','source_spec':'ViralOS Launch v3.0','ultimate_enabled':False,
            'combined_reference':'ViralOS Combined v3.0','published_release':False}

# Additive feature surface: research assistance, creative timing, secure review/export.
from .expansion import register as register_extensions
register_extensions(app)

# Additive, typed CPU Professional Studio prototype; no external upload authorization.
from .studio_routes import register_studio
register_studio(app)

from .director_m21 import register_director
register_director(app)

from .creative_m22 import register_creative_m22
register_creative_m22(app)
from .youtube_private import register_youtube_private
register_youtube_private(app)

# M2.3 additive evidence-to-screen and opt-in offline speech timing proposals.
from .production_m23 import register_m23
register_m23(app)

from .analytics_m31 import register_m31
register_m31(app)

# M2.4 locale-specific, owner-reviewed narration and graphics (technical preview only).
from .multilingual_m24 import register_m24
register_m24(app)
# M3.2 non-destructive real-account acceptance preflight.
from .acceptance_m32 import register_m32
register_m32(app)
