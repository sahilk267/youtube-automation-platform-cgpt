"""Owner-authorized private-only YouTube uploader. Never assume permissions.

The only network side effect is behind both an exact explicit user action and a
local environment switch. Failure after starting upload is REMOTE_UNKNOWN,
never a blindly retried call that could duplicate the video.
"""
from __future__ import annotations
import json, os
from pathlib import Path
from typing import Literal
from fastapi import HTTPException
from pydantic import BaseModel, Field, ConfigDict
from . import db
from .studio_routes import sha_file

SCOPES=['https://www.googleapis.com/auth/youtube.upload','https://www.googleapis.com/auth/youtube.readonly']
SERVICE_NAME='ViralOS_Local_YouTube_PrivateUpload'


def _keyring():
    from .youtube_analytics import _keyring as kr
    return kr()


def store_upload_credentials(channel_id,credentials):
    _keyring().set_password(SERVICE_NAME,channel_id,credentials.to_json())


def upload_credentials(channel_id):
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    raw=_keyring().get_password(SERVICE_NAME,channel_id)
    if not raw:raise RuntimeError('YouTube upload OAuth not connected to this local channel')
    cred=Credentials.from_authorized_user_info(json.loads(raw),scopes=SCOPES)
    if cred.expired and cred.refresh_token:
        cred.refresh(Request());store_upload_credentials(channel_id,cred)
    if not cred.valid:raise RuntimeError('Upload OAuth expired/revoked; reconnect')
    return cred


def verify_owned_channel(credentials,expected_id):
    from googleapiclient.discovery import build
    service=build('youtube','v3',credentials=credentials,cache_discovery=False)
    result=service.channels().list(part='id,snippet',mine=True).execute()
    matches=[x for x in result.get('items',[]) if x.get('id')==expected_id]
    if len(matches)!=1:raise RuntimeError('Authorized account does not match selected YouTube channel')
    return {'id':matches[0]['id'],'title':matches[0].get('snippet',{}).get('title','')}


def upload_private_video(credentials,path,metadata):
    """Resumable YouTube Data API insert. NEVER auto retry unknown outcome."""
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    service=build('youtube','v3',credentials=credentials,cache_discovery=False)
    body={'snippet':{'title':metadata['title'],'description':metadata['description'],
                     'tags':metadata['tags'],'categoryId':metadata.get('category_id','17'),'defaultLanguage':metadata.get('locale','en-US')},
          'status':{'privacyStatus':'private',
                    'selfDeclaredMadeForKids':metadata['made_for_kids'],
                    'containsSyntheticMedia':metadata['altered_content']}}
    media=MediaFileUpload(str(path),mimetype='video/mp4',resumable=True,chunksize=8*1024*1024)
    request=service.videos().insert(part='snippet,status',body=body,media_body=media,notifySubscribers=False)
    result=None
    for _attempt in range(4096):
        if result is not None:break
        _,result=request.next_chunk()
    if result is None:raise RuntimeError('Resumable upload exceeded safe chunk limit; inspect remotely')
    video_id=result.get('id')
    if not video_id:raise RuntimeError('Upload completed without a video ID; remote status unknown')
    # 'private' is explicitly supplied. Do not make public via any endpoint.
    return {'id':video_id,'privacyStatus':result.get('status',{}).get('privacyStatus','UNKNOWN')}


class Strict(BaseModel):model_config=ConfigDict(extra='forbid')

class PreparePrivate(Strict):
    export_id:str
    title:str=Field(min_length=5,max_length=100)
    description:str=Field(min_length=20,max_length=4500)
    tags:list[str]=Field(default_factory=list,max_length=15)
    altered_content:bool
    made_for_kids:bool
    owner_confirmed_metadata_rights:bool
    @staticmethod
    def validate_tags(tags):
        if any(not x.strip() or len(x)>50 for x in tags):raise ValueError('Invalid tags')

class ExecutePrivate(Strict):
    confirmation:Literal['UPLOAD_PRIVATE_NOW']


def resolve_export(c,export_id):
    from . import main as m
    from .creative_m22 import fingerprint
    e=db.one(c,'SELECT * FROM m22_final_exports WHERE export_id=?',(export_id,))
    if not e or e['status']!='OWNER_APPROVED_FINAL_EXPORT':raise HTTPException(404,'Owner approved final export not found')
    review=db.one(c,'SELECT * FROM m22_studio_reviews WHERE review_id=? AND project_id=?',(e['review_id'],e['project_id']))
    if not review:raise HTTPException(409,'Final export missing human approval')
    digest,p,*_=fingerprint(c,e['project_id'],review['preview_render_id'])
    if digest!=e['fingerprint'] or digest!=review['fingerprint']:
        raise HTTPException(409,'Final export stale after source, voice, script or approval change')
    video=(m.OUT/e['file_relpath']).resolve()
    if m.OUT.resolve() not in video.parents or not video.is_file() or sha_file(video)!=e['file_sha256']:
        raise HTTPException(409,'Final export changed or is unavailable')
    return e,p,video


def register_youtube_private(app):
    from . import main as m

    @app.get('/api/m3/private-upload/capabilities')
    def capabilities():
        return {'private_upload_opt_in':os.getenv('VIRALOS_ENABLE_PRIVATE_UPLOAD')=='1',
                'public_upload':False,'scheduling':False,
                'oauth':'OWNER_DESKTOP_CLI_SECURE_OS_KEYRING',
                'status_on_network_failure':'REMOTE_UNKNOWN_NO_AUTORETRY',
                'actual_youtube_upload_tested':False}

    @app.post('/api/m3/private-upload/intents')
    def prepare(body:PreparePrivate):
        if not body.owner_confirmed_metadata_rights:raise HTTPException(409,'Owner must confirm original metadata, rights and disclosure selections')
        if any(not t.strip() or len(t)>50 for t in body.tags):raise HTTPException(422,'Tags must be 1–50 characters')
        with db.transaction() as c:
            e,p,video=resolve_export(c,body.export_id)
            account=db.one(c,'SELECT * FROM m3_upload_accounts WHERE local_channel_id=?',(p['channel_id'],))
            if not account:raise HTTPException(409,'Connect exact owner YouTube channel with upload OAuth CLI')
            prior=db.one(c,'SELECT * FROM m3_private_upload_intents WHERE export_id=?',(e['export_id'],))
            if prior:
                if (prior['title']!=body.title or prior['description']!=body.description or json.loads(prior['tags_json'])!=body.tags
                        or prior['altered_content']!=int(body.altered_content) or prior['made_for_kids']!=int(body.made_for_kids)):
                    raise HTTPException(409,'Upload intent already prepared with different metadata; no silent replacement')
                return {'intent_id':prior['intent_id'],'state':prior['state'],'already_exists':True}
            iid=m.uid()
            c.execute('INSERT INTO m3_private_upload_intents(intent_id,export_id,local_channel_id,remote_channel_id,title,description,tags_json,altered_content,made_for_kids,owner_confirmed,privacy_status,state,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                (iid,e['export_id'],p['channel_id'],account['remote_channel_id'],body.title,body.description,m.j(body.tags),int(body.altered_content),int(body.made_for_kids),1,'private','PREPARED',m.now(),m.now()))
        return {'intent_id':iid,'state':'PREPARED','privacy':'private','owner_action_required':True,'already_exists':False}

    @app.get('/api/m3/private-upload/intents/{intent_id}')
    def status(intent_id:str):
        with db.read() as c:
            row=db.one(c,'SELECT intent_id,state,remote_video_id,privacy_status,created_at,updated_at FROM m3_private_upload_intents WHERE intent_id=?',(intent_id,))
            if not row:raise HTTPException(404,'Upload intent not found')
            return row

    @app.post('/api/m3/private-upload/intents/{intent_id}/execute')
    def execute(intent_id:str,body:ExecutePrivate):
        if os.getenv('VIRALOS_ENABLE_PRIVATE_UPLOAD')!='1':
            raise HTTPException(403,'Private YouTube uploading disabled. Set local opt-in VIRALOS_ENABLE_PRIVATE_UPLOAD=1')
        with db.transaction() as c:
            row=db.one(c,'SELECT * FROM m3_private_upload_intents WHERE intent_id=?',(intent_id,))
            if not row:raise HTTPException(404,'Intent not found')
            if row['state']!='PREPARED':raise HTTPException(409,'Upload already started/completed; never automatically retry possibly duplicated upload')
            e,p,video=resolve_export(c,row['export_id'])
            acct=db.one(c,'SELECT * FROM m3_upload_accounts WHERE local_channel_id=?',(row['local_channel_id'],))
            if not acct or acct['remote_channel_id']!=row['remote_channel_id'] or p['channel_id']!=row['local_channel_id']:
                raise HTTPException(409,'Wrong account/channel or missing verified upload permission')
            c.execute("UPDATE m3_private_upload_intents SET state='IN_FLIGHT',updated_at=? WHERE intent_id=? AND state='PREPARED'",(m.now(),intent_id))
        try:
            credentials=upload_credentials(row['local_channel_id'])
            verified=verify_owned_channel(credentials,row['remote_channel_id'])
            if verified['id']!=row['remote_channel_id']:raise RuntimeError('Owner channel mismatch')
            metadata={'title':row['title'],'description':row['description'],'tags':json.loads(row['tags_json']),
                      'altered_content':bool(row['altered_content']),'made_for_kids':bool(row['made_for_kids']),'category_id':'17' if p['domain_id']=='sports' else '22','locale':p['locale']}
            receipt=upload_private_video(credentials,video,metadata)
            if receipt['privacyStatus']!='private':raise RuntimeError('Uploaded video did not confirm private status; inspect remotely')
            with db.transaction() as c:
                c.execute("UPDATE m3_private_upload_intents SET state='UPLOADED_PRIVATE',remote_video_id=?,receipt_json=?,updated_at=? WHERE intent_id=? AND state='IN_FLIGHT'",
                          (receipt['id'],m.j(receipt),m.now(),intent_id))
            return {'intent_id':intent_id,'state':'UPLOADED_PRIVATE','video_id':receipt['id'],
                    'privacy':'private','published_public':False}
        except Exception as ex:
            # Even if failure occurs before actual bytes are sent, conservatively mark unknown:
            # no duplicate uploads by blind retry. Secrets and third-party payloads never returned.
            with db.transaction() as c:
                c.execute("UPDATE m3_private_upload_intents SET state='REMOTE_UNKNOWN',last_error=?,updated_at=? WHERE intent_id=? AND state='IN_FLIGHT'",
                          (type(ex).__name__[:50],m.now(),intent_id))
            raise HTTPException(503,'YouTube upload status uncertain. Check YouTube Studio manually before any new attempt; no automatic retry') from ex
