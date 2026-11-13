"""M2 Studio routes. No remote media acquisition, unattended publishing, or fake AI."""
from pathlib import Path
import hashlib, io, json, os, shutil, wave
from fastapi import UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from PIL import Image, ImageOps, UnidentifiedImageError
from .studio_contracts import StudioPlanIn
from .studio_render import render_studio, wav_duration
from . import db

MAX_STILL_BYTES=8*1024*1024
MAX_MUSIC_BYTES=20*1024*1024
Image.MAX_IMAGE_PIXELS=14_000_000


def sha_file(p):
    with Path(p).open('rb') as f:
        h=hashlib.sha256()
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
        return h.hexdigest()


def register_studio(app):
    from . import main as m

    def latest(c,pid):
        p=m.from_project(c,pid)
        script=m.must(m.latest_script(c,pid),'Script required before studio planning')
        return p,script

    def assets_for(c,pid,plan):
        aids=set()
        for shot in plan['shots']:
            if shot['visual']['asset_id']:aids.add(shot['visual']['asset_id'])
            for ov in shot['overlays']:
                if ov.get('image_asset_id'):aids.add(ov['image_asset_id'])
        if plan.get('music_asset_id'):aids.add(plan['music_asset_id'])
        assets={}
        for aid in aids:
            row=db.one(c,'SELECT * FROM m2_studio_assets WHERE asset_id=? AND project_id=?',(aid,pid))
            if not row:raise HTTPException(422,'Asset not found in this project or rights record missing: '+aid)
            if row['rights_attested']!=1:raise HTTPException(409,'Asset rights not attested')
            p=(m.OUT/row['local_relpath']).resolve()
            if m.OUT.resolve() not in p.parents or not p.is_file():raise HTTPException(409,'Asset unavailable')
            if sha_file(p)!=row['content_sha256']:raise HTTPException(409,'Asset file changed since intake')
            assets[aid]=dict(row,path=p)
        return assets

    def latest_studio_plan(c,pid):
        rec=db.one(c,'SELECT * FROM m2_studio_plans WHERE project_id=? ORDER BY created_at DESC, rowid DESC LIMIT 1',(pid,))
        if not rec:raise HTTPException(404,'No Studio plan for project')
        return rec,json.loads(rec['plan_json'])

    def fingerprint(c,pid,rec,plan):
        p,script=latest(c,pid)
        if rec['script_version_id']!=script['script_version_id'] or rec['project_revision']!=p['revision']:
            raise HTTPException(409,'Studio plan is stale after project/script revision; create a new Studio plan')
        assets=assets_for(c,pid,plan)
        voice=m.OUT/pid/'voice.wav'
        bound=db.one(c,'SELECT * FROM m21_plan_audio WHERE plan_id=? AND project_id=?',(rec['plan_id'],pid))
        if bound:
            if bound['script_version_id']!=script['script_version_id']:raise HTTPException(409,'Director voice bound to old script')
            voice=(m.OUT/bound['voice_relpath']).resolve()
            if m.OUT.resolve() not in voice.parents or not voice.is_file() or sha_file(voice)!=bound['voice_sha256']:
                raise HTTPException(409,'Director voice asset missing or modified')
        v=db.one(c,'SELECT * FROM m2_voice_provenance WHERE project_id=?',(pid,))
        if not bound and voice.exists() and v and v['script_version_id']!=script['script_version_id']:
            raise HTTPException(409,'Piper narration belongs to old script; regenerate')
        hashes={'plan':rec['plan_sha256'],'script':script['content_sha256'],
                'voice':sha_file(voice) if voice.is_file() else None,
                'assets':{k:assets[k]['content_sha256'] for k in sorted(assets)},'project_revision':p['revision']}
        return m.sha(m.j(hashes)),p,script,assets,voice if voice.is_file() else None

    @app.get('/api/studio/capabilities')
    def studio_capabilities():
        return {'renderer':'CPU_STUDIO_V0.3','supported_formats':['SHORT','LONG'],
                'ffmpeg':bool(shutil.which('ffmpeg')),'ffprobe':bool(shutil.which('ffprobe')),
                'timed_overlays':True,'owner_timed_captions':True,'approved_local_stills':True,
                'approved_music_wav':True,'auto_translation':False,'forced_alignment':False,'measured_segment_alignment':True,'automatic_director_draft':True,
                'ai_video_generation':False,'youtube_upload':False,'publish_ready':False}

    @app.post('/api/projects/{project_id}/studio/assets/still')
    async def studio_still(project_id:str,file:UploadFile=File(...),origin:str=Form(...),
                           license_note:str=Form(...),rights_attested:bool=Form(...)):
        if not rights_attested or len(origin.strip())<8 or len(license_note.strip())<12:
            raise HTTPException(422,'Owner must attest rights, origin and documented permission')
        with db.read() as c:latest(c,project_id)
        data=await file.read(MAX_STILL_BYTES+1)
        if not data or len(data)>MAX_STILL_BYTES:raise HTTPException(413,'Still images max 8MB')
        try:
            im=Image.open(io.BytesIO(data));im.verify()
            im=Image.open(io.BytesIO(data))
            if im.format not in ('PNG','JPEG'):raise ValueError('PNG or JPEG only')
            if im.width*im.height>12_000_000 or im.width<64 or im.height<64:raise ValueError('Image dimensions unsupported')
            im=ImageOps.exif_transpose(im).convert('RGB')
        except (ValueError,UnidentifiedImageError,OSError,Image.DecompressionBombError) as ex:
            raise HTTPException(422,'Invalid/unsafe image: '+str(ex)[:100])
        aid=m.uid();folder=m.OUT/project_id/'studio_assets';folder.mkdir(parents=True,exist_ok=True)
        dest=folder/f'{aid}.png';im.save(dest,format='PNG',optimize=True)
        rel=str(dest.relative_to(m.OUT));digest=sha_file(dest)
        with db.transaction() as c:
            latest(c,project_id)
            c.execute('INSERT INTO m2_studio_assets(asset_id,project_id,kind,local_relpath,origin,license_note,rights_attested,content_sha256,mime,duration_ms,created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)',
                      (aid,project_id,'STILL',rel,origin.strip(),license_note.strip(),1,digest,'image/png',None,m.now()))
        return {'asset_id':aid,'kind':'STILL','sha256':digest,'rights_status':'OWNER_ATTESTED_NOT_INDEPENDENTLY_VERIFIED'}

    @app.post('/api/projects/{project_id}/studio/assets/music')
    async def studio_music(project_id:str,file:UploadFile=File(...),origin:str=Form(...),
                           license_note:str=Form(...),rights_attested:bool=Form(...)):
        if not rights_attested or len(origin.strip())<8 or len(license_note.strip())<12:
            raise HTTPException(422,'Owner must attest sound rights and origin')
        with db.read() as c:latest(c,project_id)
        data=await file.read(MAX_MUSIC_BYTES+1)
        if not data or len(data)>MAX_MUSIC_BYTES:raise HTTPException(413,'Music WAV max 20MB')
        aid=m.uid();folder=m.OUT/project_id/'studio_assets';folder.mkdir(parents=True,exist_ok=True)
        dest=folder/f'{aid}.wav';dest.write_bytes(data)
        try:
            duration=wav_duration(dest)
            if duration<.5 or duration>600:raise ValueError('WAV must be between 0.5 and 600 seconds')
        except Exception:
            dest.unlink(missing_ok=True);raise HTTPException(422,'Invalid WAV audio')
        digest=sha_file(dest);rel=str(dest.relative_to(m.OUT))
        with db.transaction() as c:
            latest(c,project_id)
            c.execute('INSERT INTO m2_studio_assets(asset_id,project_id,kind,local_relpath,origin,license_note,rights_attested,content_sha256,mime,duration_ms,created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)',
                      (aid,project_id,'MUSIC',rel,origin.strip(),license_note.strip(),1,digest,'audio/wav',int(duration*1000),m.now()))
        return {'asset_id':aid,'kind':'MUSIC','sha256':digest,'rights_status':'OWNER_ATTESTED_NOT_INDEPENDENTLY_VERIFIED'}

    @app.get('/api/projects/{project_id}/studio/assets')
    def list_assets(project_id:str):
        with db.read() as c:
            latest(c,project_id)
            rows=db.many(c,'SELECT asset_id,kind,origin,license_note,content_sha256,duration_ms,created_at FROM m2_studio_assets WHERE project_id=? ORDER BY created_at',(project_id,))
        return {'assets':rows}

    @app.get('/api/projects/{project_id}/studio/example')
    def studio_example(project_id:str):
        with db.read() as c:p,script=latest(c,project_id)
        return {'locale':p['locale'],'locale_reviewed':False,'music_asset_id':None,
                'shots':[
                  {'role':'HOOK','duration_ms':3500,'headline':'What changed the play?',
                   'visual':{'kind':'ORIGINAL_DIAGRAM','motion':'ILLUSTRATIVE_ROUTE'},'claim_ids':[],
                   'overlays':[{'text':'A tactical question','start_ms':450,'end_ms':3050,'anchor':'CENTER','style':'CALLOUT'}]},
                  {'role':'PAYOFF','duration_ms':3500,'headline':'How the positioning works',
                   'visual':{'kind':'ORIGINAL_DIAGRAM','motion':'ILLUSTRATIVE_ROUTE'},'claim_ids':[],
                   'overlays':[{'text':'Original illustrative diagram','start_ms':550,'end_ms':3000,'anchor':'CENTER','style':'STAT'}]}
                ],'captions':[],'captions_provenance':'NOT_PROVIDED'}

    @app.post('/api/projects/{project_id}/studio/plans')
    def studio_plan(project_id:str,body:StudioPlanIn):
        plan=body.model_dump(mode='json')
        with db.transaction() as c:
            p,script=latest(c,project_id)
            if body.locale!=p['locale'] and not body.locale_reviewed:
                raise HTTPException(409,'New locale requires owner translation/pronunciation review attestation')
            assets=assets_for(c,project_id,plan)
            if body.music_asset_id and assets[body.music_asset_id]['kind']!='MUSIC':
                raise HTTPException(422,'music_asset_id must reference approved WAV')
            for shot in body.shots:
                if shot.visual.asset_id and assets[shot.visual.asset_id]['kind']!='STILL':
                    raise HTTPException(422,'Visual asset must be still image')
                for ov in shot.overlays:
                    if ov.image_asset_id and assets[ov.image_asset_id]['kind']!='STILL':raise HTTPException(422,'Timed insert requires approved STILL asset')
                for cl in shot.claim_ids:
                    if not db.one(c,'SELECT claim_id FROM script_claim_links WHERE script_version_id=? AND claim_id=?',(script['script_version_id'],cl)):
                        raise HTTPException(409,'Studio shot claim must link to current script')
            # Idempotent on an unchanged current revision; permits fresh identical
            # creative plans after a new script/project revision.
            previous=db.one(c,'SELECT * FROM m2_studio_plans WHERE project_id=? ORDER BY created_at DESC,rowid DESC LIMIT 1',(project_id,))
            if (previous and previous['project_revision']==p['revision']
                    and previous['script_version_id']==script['script_version_id']
                    and previous['plan_json']==m.j(plan)):
                return {'plan_id':previous['plan_id'],'already_exists':True,'status':'DRAFT'}
            revised=p['revision']+1;pid=m.uid()
            plan_hash=m.sha(m.j(plan)+'|script:'+script['script_version_id']+'|revision:'+str(revised))
            c.execute('UPDATE content_projects SET revision=?,updated_at=? WHERE project_id=?',(revised,m.now(),project_id))
            c.execute('INSERT INTO m2_studio_plans(plan_id,project_id,script_version_id,project_revision,locale,plan_json,plan_sha256,status,created_at) VALUES (?,?,?,?,?,?,?,?,?)',
                      (pid,project_id,script['script_version_id'],revised,body.locale,m.j(plan),plan_hash,'DRAFT',m.now()))
        return {'plan_id':pid,'already_exists':False,'status':'DRAFT','publish_ready':False}

    @app.get('/api/projects/{project_id}/studio/plan')
    def get_studio_plan(project_id:str):
        with db.read() as c:
            latest(c,project_id)
            rec,plan=latest_studio_plan(c,project_id)
        return {'plan_id':rec['plan_id'],'project_revision':rec['project_revision'],'plan':plan,'status':rec['status']}

    @app.post('/api/projects/{project_id}/studio/queue')
    def studio_queue(project_id:str):
        with db.transaction() as c:
            rec,plan=latest_studio_plan(c,project_id)
            content_hash,p,script,assets,voice=fingerprint(c,project_id,rec,plan)
            key=m.sha(project_id+':studio:'+content_hash)
            old=db.one(c,'SELECT job_id,state FROM jobs WHERE channel_id=? AND job_type=? AND idempotency_key=?',(p['channel_id'],'M2_STUDIO_PREVIEW',key))
            if old:return dict(old,already_exists=True)
            jid=m.uid()
            c.execute('INSERT INTO jobs(job_id,channel_id,domain_id,job_type,input_sha256,idempotency_key,state,progress_json,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?)',
                      (jid,p['channel_id'],p['domain_id'],'M2_STUDIO_PREVIEW',content_hash,key,'QUEUED',m.j({'project_id':project_id,'plan_id':rec['plan_id']}),m.now(),m.now()))
        return {'job_id':jid,'state':'QUEUED','already_exists':False}

    @app.post('/api/studio/run-next')
    def studio_run_next():
        with db.transaction() as c:
            job=db.one(c,"SELECT * FROM jobs WHERE state='QUEUED' AND job_type='M2_STUDIO_PREVIEW' ORDER BY created_at LIMIT 1")
            if not job:return {'state':'EMPTY','message':'No queued Studio jobs'}
            c.execute("UPDATE jobs SET state='RUNNING',attempt_count=attempt_count+1,updated_at=? WHERE job_id=?",(m.now(),job['job_id']))
        data=json.loads(job['progress_json']);project_id=data['project_id'];jid=job['job_id']
        try:
            with db.read() as c:
                rec=db.one(c,'SELECT * FROM m2_studio_plans WHERE plan_id=? AND project_id=?',(data['plan_id'],project_id))
                if not rec:raise ValueError('Studio plan missing')
                plan=json.loads(rec['plan_json'])
                digest,p,script,assets,voice=fingerprint(c,project_id,rec,plan)
                if digest!=job['input_sha256']:raise ValueError('Studio inputs changed since queue; requeue a fresh job')
            folder=m.OUT/project_id/'studio'/jid
            file,report,manifest=render_studio(plan,p['sport_id'],p['format'],assets,voice,folder)
            output_hash=sha_file(file);rid=m.uid()
            with db.transaction() as c:
                c.execute('INSERT INTO m2_studio_renders(studio_render_id,plan_id,project_id,job_id,output_relpath,output_sha256,quality_report_json,render_manifest_json,status,created_at) VALUES (?,?,?,?,?,?,?,?,?,?)',
                          (rid,rec['plan_id'],project_id,jid,str(file.relative_to(m.OUT)),output_hash,m.j(report),m.j(manifest),'TECHNICAL_STUDIO_PREVIEW',m.now()))
                c.execute("UPDATE jobs SET state='SUCCEEDED',progress_json=?,updated_at=? WHERE job_id=?",
                          (m.j({'project_id':project_id,'studio_render_id':rid}),m.now(),jid))
            return {'job_id':jid,'state':'SUCCEEDED','studio_render_id':rid,
                    'preview_url':f'/api/studio/previews/{rid}','report_url':f'/api/studio/reports/{rid}',
                    'publish_ready':False,'qc_status':report['status']}
        except Exception as e:
            with db.transaction() as c:
                c.execute("UPDATE jobs SET state='FAILED',error_code=?,updated_at=? WHERE job_id=?",(str(e)[:200],m.now(),jid))
            return {'job_id':jid,'state':'FAILED','error':str(e)[:500]}

    @app.get('/api/studio/reports/{render_id}')
    def studio_report(render_id:str):
        with db.read() as c:
            row=m.must(db.one(c,'SELECT * FROM m2_studio_renders WHERE studio_render_id=?',(render_id,)),'Studio render not found')
            return {'render_id':render_id,'quality':json.loads(row['quality_report_json']),
                    'manifest':json.loads(row['render_manifest_json']),'status':row['status']}

    @app.get('/api/studio/previews/{render_id}')
    def studio_preview(render_id:str):
        with db.read() as c:
            row=m.must(db.one(c,'SELECT * FROM m2_studio_renders WHERE studio_render_id=?',(render_id,)),'Studio render not found')
        path=(m.OUT/row['output_relpath']).resolve()
        if m.OUT.resolve() not in path.parents or not path.is_file():raise HTTPException(404,'Studio preview missing')
        return FileResponse(path,media_type='video/mp4',filename='ViralOS_CPU_Studio_Technical_Preview.mp4')

    @app.get('/api/projects/{project_id}/studio/renders')
    def studio_renders(project_id:str):
        with db.read() as c:
            latest(c,project_id)
            return db.many(c,'SELECT studio_render_id,plan_id,output_sha256,status,created_at FROM m2_studio_renders WHERE project_id=? ORDER BY created_at DESC',(project_id,))
