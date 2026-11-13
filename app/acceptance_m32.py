"""M3.2 supervised acceptance preflight: offline approval and opt-in READ-ONLY
YouTube channel/privacy verification. Never publishes or modifies remote videos.
"""
from __future__ import annotations
import os,json
from fastapi import HTTPException
from pydantic import BaseModel,ConfigDict
from . import db
from .youtube_private import resolve_export

class Strict(BaseModel):model_config=ConfigDict(extra='forbid')
class PreflightIn(Strict):
    export_id:str
    owner_confirmed_local_video_and_rights:bool
    owner_confirmed_target_channel:bool
    perform_remote_read_only_check:bool=False
    owner_consented_network_access:bool=False


def inspect_remote(credentials,channel_id,video_id=None):
    """Read only: validate owner identity, optional uploaded video privacy.
    Channel metadata is fetched with authenticated YouTube Data API.
    """
    from . import youtube_private
    from .analytics_m31 import fetch_remote_video
    owner=youtube_private.verify_owned_channel(credentials,channel_id)
    result={'verified_channel_id':owner['id'],'remote_video_privacy':None,'remote_video_verified':False}
    if video_id:
        videos=fetch_remote_video(credentials,video_id)
        if len(videos)!=1 or videos[0].get('id')!=video_id or videos[0].get('snippet',{}).get('channelId')!=channel_id:
            raise RuntimeError('Remote video is not owned by the selected OAuth account')
        privacy=videos[0].get('status',{}).get('privacyStatus')
        if privacy!='private':raise RuntimeError('Remote video privacy must be confirmed PRIVATE')
        result.update(remote_video_privacy=privacy,remote_video_verified=True)
    return result


def register_m32(app):
    from . import main as m
    from . import youtube_private

    @app.get('/api/m32/capabilities')
    def capabilities():
        return {'offline_preflight':True,
                'remote_read_only_preflight_opt_in':os.getenv('VIRALOS_ENABLE_M32_REMOTE_READ')=='1',
                'real_account_test_performed_in_delivery':False,
                'private_upload_requires_separate_approval':True,
                'remote_writes_during_preflight':False,
                'public_upload':False,
                'metrics_monetary_scope_separate':True}

    @app.post('/api/m32/acceptance/preflight')
    def preflight(b:PreflightIn):
        blockers=[];report={}
        if not (b.owner_confirmed_local_video_and_rights and b.owner_confirmed_target_channel):
            raise HTTPException(409,'Owner must confirm final file, rights, selected channel and metadata')
        if b.perform_remote_read_only_check and not b.owner_consented_network_access:
            raise HTTPException(409,'Remote account access requires explicit owner consent')
        if b.perform_remote_read_only_check and os.getenv('VIRALOS_ENABLE_M32_REMOTE_READ')!='1':
            raise HTTPException(403,'Remote read-only preflight is disabled by default')
        with db.read() as c:
            e,p,video=resolve_export(c,b.export_id)
            acct=db.one(c,'SELECT * FROM m3_upload_accounts WHERE local_channel_id=?',(p['channel_id'],))
            analytics=db.one(c,'SELECT remote_channel_id FROM m3_youtube_accounts WHERE local_channel_id=?',(p['channel_id'],))
            monetary=db.one(c,'SELECT remote_channel_id FROM m31_monetary_accounts WHERE local_channel_id=?',(p['channel_id'],))
            existing=db.one(c,"SELECT remote_video_id,state,remote_channel_id FROM m3_private_upload_intents WHERE export_id=?",(e['export_id'],))
            if not acct:blockers.append('UPLOAD_OAUTH_CHANNEL_NOT_CONNECTED')
            if acct and analytics and analytics['remote_channel_id']!=acct['remote_channel_id']:
                blockers.append('ANALYTICS_ACCOUNT_MISMATCH')
            if acct and monetary and monetary['remote_channel_id']!=acct['remote_channel_id']:
                blockers.append('MONETARY_ACCOUNT_MISMATCH')
            if existing and acct and existing['remote_channel_id']!=acct['remote_channel_id']:
                blockers.append('UPLOAD_INTENT_CHANNEL_MISMATCH')
            if existing and existing['state']=='REMOTE_UNKNOWN':blockers.append('UNRESOLVED_REMOTE_UNKNOWN_UPLOAD')
            remote_id=acct['remote_channel_id'] if acct else None
            report={'export_id':b.export_id,'local_channel_id':p['channel_id'],
                    'local_export_sha256':e['file_sha256'],
                    'local_export_unchanged':True,'owner_review_bound_to_current_fingerprint':True,
                    'remote_channel_id':remote_id,'analytics_connected':bool(analytics),
                    'monetary_connected':bool(monetary),
                    'upload_intent_state':existing['state'] if existing else 'NOT_STARTED',
                    'upload_privacy':'PRIVATE_EXPLICIT_ONLY','remote_access_performed':False,
                    'youtube_revenue_available':False if not monetary else 'NOT_TESTED',
                    'blockers':blockers}
        if b.perform_remote_read_only_check:
            if blockers:raise HTTPException(409,'Preflight blocked by local account/intent mismatch: '+', '.join(blockers))
            try:
                creds=youtube_private.upload_credentials(p['channel_id'])
                remote=inspect_remote(creds,remote_id,existing['remote_video_id'] if existing and existing['state']=='UPLOADED_PRIVATE' else None)
            except Exception as ex:
                raise HTTPException(503,'Owner OAuth/remote read-only validation failed; no upload attempted: '+type(ex).__name__) from ex
            report['remote_access_performed']=True
            report['remote_read_back']=remote
            status='REMOTE_CHANNEL_VERIFIED'
        else:
            status='BLOCKED' if blockers else 'LOCAL_READY'
        report['status']=status
        report['live_private_upload_executed_by_preflight']=False
        report['remote_upload_verified']=report.get('remote_read_back',{}).get('remote_video_verified',False)
        with db.transaction() as c:
            e,p,video=resolve_export(c,b.export_id)
            c.execute('INSERT INTO m32_acceptance_checks(check_id,export_id,local_channel_id,remote_channel_id,mode,report_json,status,created_at) VALUES(?,?,?,?,?,?,?,?)',
                      (m.uid(),b.export_id,p['channel_id'],remote_id,'OWNER_AUTHORIZED_READ_ONLY' if b.perform_remote_read_only_check else 'OFFLINE',m.j(report),status,m.now()))
        return report

    @app.get('/api/m32/acceptance/exports/{export_id}')
    def history(export_id:str):
        with db.read() as c:
            e=db.one(c,'SELECT export_id FROM m22_final_exports WHERE export_id=?',(export_id,))
            if not e:raise HTTPException(404,'Owner-approved export not found')
            rows=db.many(c,'SELECT check_id,mode,status,report_json,created_at FROM m32_acceptance_checks WHERE export_id=? ORDER BY created_at DESC',(export_id,))
        return {'export_id':export_id,'checks':[{'check_id':r['check_id'],'mode':r['mode'],'status':r['status'],'created_at':r['created_at'],'report':json.loads(r['report_json'])} for r in rows]}
