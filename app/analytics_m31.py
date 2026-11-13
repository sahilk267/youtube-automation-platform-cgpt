"""M3.1 optional owner-authorized revenue estimates & remote-unknown reconciliation.

No credentials are stored in SQLite; no profit or RPM assumptions are fabricated.
All real Google network operations require separately installed dependencies, scopes
and owner opt-in.  Mock-only in packaged verification.
"""
import json,os,hashlib
from datetime import date
from typing import Literal
from fastapi import HTTPException
from pydantic import BaseModel,ConfigDict,Field,model_validator
from . import db

MONETARY_SCOPES=['https://www.googleapis.com/auth/youtube.readonly',
                 'https://www.googleapis.com/auth/yt-analytics-monetary.readonly']
MONETARY_SERVICE='ViralOS_Local_YouTube_RevenueReadOnly'

class Strict(BaseModel):model_config=ConfigDict(extra='forbid')
class RevenueRequest(Strict):
    channel_id:str
    start_date:date
    end_date:date
    currency:Literal['USD','INR']='USD'
    owner_authorized_sync:bool
    @model_validator(mode='after')
    def dates_ok(self):
        if self.end_date<self.start_date or (self.end_date-self.start_date).days>90:raise ValueError('Revenue window must be between 0 and 90 days')
        if self.end_date>=date.today():raise ValueError('Only completed past reporting days are permitted')
        return self

class RetentionRequest(Strict):
    export_id:str
    start_date:date
    end_date:date
    owner_authorized_sync:bool
    @model_validator(mode='after')
    def valid_window(self):
        if self.end_date<self.start_date or (self.end_date-self.start_date).days>90 or self.end_date>=date.today():
            raise ValueError('Select completed historical retention days within 90 days')
        return self

class Reconcile(Strict):
    remote_video_id:str=Field(min_length=5,max_length=64,pattern=r'^[A-Za-z0-9_-]+$')
    owner_checked_studio_video_matches:bool
    confirmation:Literal['RECONCILE_EXISTING_PRIVATE_VIDEO_ONLY']


def store_monetary_credentials(channel_id,credential):
    from .youtube_analytics import _keyring
    _keyring().set_password(MONETARY_SERVICE,channel_id,credential.to_json())


def monetary_credentials(channel_id):
    from .youtube_analytics import _keyring
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    raw=_keyring().get_password(MONETARY_SERVICE,channel_id)
    if not raw:raise RuntimeError('Monetary OAuth not connected for selected channel')
    cred=Credentials.from_authorized_user_info(json.loads(raw),scopes=MONETARY_SCOPES)
    if cred.expired and cred.refresh_token:
        cred.refresh(Request());store_monetary_credentials(channel_id,cred)
    if not cred.valid:raise RuntimeError('Monetary OAuth expired or revoked')
    return cred


def fetch_monetary(credentials,start,end,currency):
    from googleapiclient.discovery import build
    service=build('youtubeAnalytics','v2',credentials=credentials,cache_discovery=False)
    return service.reports().query(ids='channel==MINE',startDate=start,endDate=end,
                                   metrics='estimatedRevenue,estimatedAdRevenue',dimensions='day',
                                   sort='day',currency=currency).execute()


def normalized_monetary(report):
    fields=[h.get('name') for h in report.get('columnHeaders',[])]
    required={'day','estimatedRevenue','estimatedAdRevenue'}
    if not required.issubset(fields):raise ValueError('Revenue report missing required fields')
    result=[];seen=set()
    for row in report.get('rows',[]):
        if len(row)!=len(fields):raise ValueError('Malformed revenue row')
        x=dict(zip(fields,row));day=date.fromisoformat(str(x['day']))
        rev=float(x['estimatedRevenue']);ad=float(x['estimatedAdRevenue'])
        if any(not __import__('math').isfinite(a) or a<0 for a in (rev,ad)):
            raise ValueError('Negative or non-finite estimated revenue')
        if day.isoformat() in seen:raise ValueError('Duplicated day in API response')
        seen.add(day.isoformat())
        result.append({'day':day.isoformat(),'estimated_revenue':rev,'estimated_ad_revenue':ad})
    return result


def fetch_remote_video(credentials,video_id):
    from googleapiclient.discovery import build
    service=build('youtube','v3',credentials=credentials,cache_discovery=False)
    response=service.videos().list(part='id,snippet,status',id=video_id).execute()
    return response.get('items',[])


def fetch_retention(credentials,video_id,start,end):
    from googleapiclient.discovery import build
    service=build('youtubeAnalytics','v2',credentials=credentials,cache_discovery=False)
    return service.reports().query(ids='channel==MINE',startDate=start,endDate=end,
                metrics='audienceWatchRatio,relativeRetentionPerformance',
                dimensions='elapsedVideoTimeRatio',filters='video=='+video_id,
                sort='elapsedVideoTimeRatio').execute()


def normalize_retention(report):
    import math
    fields=[h.get('name') for h in report.get('columnHeaders',[])]
    names={'elapsedVideoTimeRatio','audienceWatchRatio','relativeRetentionPerformance'}
    if not names.issubset(fields):raise ValueError('Audience retention response missing expected fields')
    rows=[];last=-1.0
    for raw in report.get('rows',[]):
        if len(raw)!=len(fields):raise ValueError('Retention row length mismatch')
        item=dict(zip(fields,raw))
        fraction=float(item['elapsedVideoTimeRatio']);abswatch=float(item['audienceWatchRatio'])
        relative=float(item['relativeRetentionPerformance'])
        if not all(math.isfinite(v) for v in (fraction,abswatch,relative)):
            raise ValueError('Non-finite retention response')
        if not (0<fraction<=1) or fraction<=last or abswatch<0 or not 0<=relative<=1:
            raise ValueError('Invalid or unordered audience retention response')
        rows.append({'elapsed_video_ratio':fraction,'audience_watch_ratio':abswatch,
                     'relative_retention_performance':relative})
        last=fraction
    if len(rows)>200:raise ValueError('Unexpectedly large retention response')
    return rows


def map_retention_to_shots(shots,rows):
    """Associative descriptive mapping only, NOT causal inference."""
    total=sum(s['duration_ms'] for s in shots)
    summary=[];offset=0
    for index,shot in enumerate(shots):
        end=offset+shot['duration_ms']
        samples=[r for r in rows if offset<r['elapsed_video_ratio']*total<=end]
        summary.append({'index':index,'role':shot['role'],'headline':shot['headline'],
                        'from_ms':offset,'to_ms':end,'sample_count':len(samples),
                        'first_audience_watch_ratio':samples[0]['audience_watch_ratio'] if samples else None,
                        'last_audience_watch_ratio':samples[-1]['audience_watch_ratio'] if samples else None,
                        'observed_delta':round(samples[-1]['audience_watch_ratio']-samples[0]['audience_watch_ratio'],5) if len(samples)>1 else None})
        offset=end
    return {'scene_summaries':summary,'data_points':len(rows),
            'observed_retention_not_causal_explanation':True,
            'audience_watch_ratio_can_exceed_one_due_to_rewatches':True}

def register_m31(app):
    from . import main as m
    from . import youtube_private

    @app.get('/api/m31/capabilities')
    def capabilities():
        return {'monetary_revenue_sync_opt_in':os.getenv('VIRALOS_ENABLE_MONETARY_SYNC')=='1',
                'monetary_scope_required':True,'source':'YOUTUBE_ANALYTICS_API_ESTIMATES',
                'net_profit_calculated':False,'real_account_tested':False,'retention_sync_opt_in':os.getenv('VIRALOS_ENABLE_RETENTION_SYNC')=='1',
                'private_upload_reconciliation':'OWNER_CONFIRMATION_AND_REMOTE_ID_VERIFICATION_ONLY'}

    @app.post('/api/m31/retention/sync')
    def sync_retention(body:RetentionRequest):
        if not body.owner_authorized_sync:raise HTTPException(409,'Owner authorization required')
        if os.getenv('VIRALOS_ENABLE_RETENTION_SYNC')!='1':
            raise HTTPException(403,'Retention API sync is disabled by default')
        with db.read() as c:
            export=db.one(c,'SELECT * FROM m22_final_exports WHERE export_id=?',(body.export_id,))
            if not export:raise HTTPException(404,'Export missing')
            intent=db.one(c,"SELECT * FROM m3_private_upload_intents WHERE export_id=? AND state='UPLOADED_PRIVATE'",(body.export_id,))
            if not intent or not intent['remote_video_id']:
                raise HTTPException(409,'Owner-verified remotely uploaded private video required')
            account=db.one(c,'SELECT remote_channel_id FROM m3_youtube_accounts WHERE local_channel_id=?',(intent['local_channel_id'],))
            if not account or account['remote_channel_id']!=intent['remote_channel_id']:
                raise HTTPException(409,'Read-only Analytics account does not match the owner upload channel')
            plan=db.one(c,'SELECT plan_json FROM m2_studio_plans WHERE plan_id=?',(export['plan_id'],))
            if not plan:raise HTTPException(409,'Stored video timeline unavailable')
            shots=json.loads(plan['plan_json'])['shots']
        try:
            from . import youtube_analytics
            creds=youtube_analytics.credentials_for(intent['local_channel_id'])
            youtube_analytics.verify_channel(creds,intent['remote_channel_id'])
            remote=fetch_retention(creds,intent['remote_video_id'],body.start_date.isoformat(),body.end_date.isoformat())
            rows=normalize_retention(remote)
        except Exception as ex:
            raise HTTPException(503,'Retention API failed: '+type(ex).__name__[:45]) from ex
        scene_report=map_retention_to_shots(shots,rows)
        with db.transaction() as c:
            actual=db.one(c,"SELECT remote_video_id FROM m3_private_upload_intents WHERE export_id=? AND state='UPLOADED_PRIVATE'",(body.export_id,))
            if not actual or actual['remote_video_id']!=intent['remote_video_id']:
                raise HTTPException(409,'Remote video association changed during retention sync')
            c.execute('INSERT INTO m31_retention_snapshots(snapshot_id,export_id,remote_video_id,start_date,end_date,raw_json,scene_json,source,retrieved_at) VALUES (?,?,?,?,?,?,?,?,?) '
                      'ON CONFLICT(export_id,start_date,end_date) DO UPDATE SET raw_json=excluded.raw_json,scene_json=excluded.scene_json,retrieved_at=excluded.retrieved_at',
                      (m.uid(),body.export_id,intent['remote_video_id'],body.start_date.isoformat(),body.end_date.isoformat(),
                       m.j(rows),m.j(scene_report),'OWNER_AUTHORIZED_YOUTUBE_ANALYTICS',m.now()))
        return {'export_id':body.export_id,'source':'OWNER_AUTHORIZED_YOUTUBE_ANALYTICS',
                'data_available':bool(rows),'samples':len(rows),'report':scene_report,
                'causal_interpretation':False,'network_live_tested_in_delivery':False}

    @app.get('/api/m31/exports/{export_id}/retention')
    def retention_cached(export_id:str):
        with db.read() as c:
            if not db.one(c,'SELECT export_id FROM m22_final_exports WHERE export_id=?',(export_id,)):
                raise HTTPException(404,'Export missing')
            rec=db.one(c,'SELECT * FROM m31_retention_snapshots WHERE export_id=? ORDER BY retrieved_at DESC',(export_id,))
            if not rec:return {'export_id':export_id,'data_available':False,'source':'NOT_AVAILABLE','report':None}
            return {'export_id':export_id,'data_available':bool(json.loads(rec['raw_json'])),
                    'source':rec['source'],'start_date':rec['start_date'],'end_date':rec['end_date'],
                    'report':json.loads(rec['scene_json'])}

    @app.get('/api/m31/channels/{channel_id}/earnings')
    def earnings(channel_id:str):
        with db.read() as c:
            ch=db.one(c,'SELECT channel_id FROM channels WHERE channel_id=?',(channel_id,))
            if not ch:raise HTTPException(404,'Local channel not found')
            rows=db.many(c,'SELECT report_date,currency,estimated_revenue,estimated_ad_revenue,retrieved_at,source FROM m31_monetary_daily WHERE local_channel_id=? ORDER BY report_date',(channel_id,))
            currencies=sorted(set(x['currency'] for x in rows))
            totals={currency:round(sum(x['estimated_revenue'] for x in rows if x['currency']==currency),4) for currency in currencies}
            return {'channel_id':channel_id,'rows':rows,'totals_by_currency':totals,
                    'currency_conversion':False,'costs_accounted':False,'profit_calculated':False,
                    'metric':'ESTIMATED_YOUTUBE_REVENUE_NOT_FINAL_SETTLEMENT','data_if_empty':'NOT_AVAILABLE'}

    @app.post('/api/m31/monetary/sync')
    def sync(body:RevenueRequest):
        if not body.owner_authorized_sync:raise HTTPException(409,'Explicit owner authorization required')
        if os.getenv('VIRALOS_ENABLE_MONETARY_SYNC')!='1':raise HTTPException(403,'Monetary sync disabled by default')
        with db.read() as c:
            ch=db.one(c,'SELECT channel_id FROM channels WHERE channel_id=?',(body.channel_id,))
            acct=db.one(c,'SELECT remote_channel_id FROM m31_monetary_accounts WHERE local_channel_id=?',(body.channel_id,))
            if not ch or not acct:raise HTTPException(409,'Connect and verify exact owner channel first')
            upload_acct=db.one(c,'SELECT remote_channel_id FROM m3_upload_accounts WHERE local_channel_id=?',(body.channel_id,))
            if upload_acct and upload_acct['remote_channel_id']!=acct['remote_channel_id']:
                raise HTTPException(409,'Monetary and upload account channel IDs do not match')
        try:
            cred=monetary_credentials(body.channel_id)
            youtube_private.verify_owned_channel(cred,acct['remote_channel_id'])
            report=fetch_monetary(cred,body.start_date.isoformat(),body.end_date.isoformat(),body.currency)
            rows=normalized_monetary(report)
        except Exception as ex:
            raise HTTPException(503,'OAuth/Analytics unavailable: '+type(ex).__name__[:45]) from ex
        for row in rows:
            if not body.start_date<=date.fromisoformat(row['day'])<=body.end_date:
                raise HTTPException(422,'Provider returned day outside requested period')
        response_hash=m.sha(m.j({'currency':body.currency,'rows':rows}))
        with db.transaction() as c:
            checked=db.one(c,'SELECT remote_channel_id FROM m31_monetary_accounts WHERE local_channel_id=?',(body.channel_id,))
            if not checked or checked['remote_channel_id']!=acct['remote_channel_id']:
                raise HTTPException(409,'Connected channel changed during sync')
            for row in rows:
                existing=db.one(c,'SELECT snapshot_id FROM m31_monetary_daily WHERE local_channel_id=? AND report_date=? AND currency=?',(body.channel_id,row['day'],body.currency))
                if existing:
                    c.execute('UPDATE m31_monetary_daily SET estimated_revenue=?,estimated_ad_revenue=?,retrieved_at=?,response_digest=?,remote_channel_id=? WHERE snapshot_id=?',
                              (row['estimated_revenue'],row['estimated_ad_revenue'],m.now(),response_hash,acct['remote_channel_id'],existing['snapshot_id']))
                else:
                    c.execute('INSERT INTO m31_monetary_daily(snapshot_id,local_channel_id,remote_channel_id,report_date,currency,estimated_revenue,estimated_ad_revenue,source,retrieved_at,response_digest) VALUES(?,?,?,?,?,?,?,?,?,?)',
                              (m.uid(),body.channel_id,acct['remote_channel_id'],row['day'],body.currency,row['estimated_revenue'],row['estimated_ad_revenue'],'YOUTUBE_ANALYTICS_MONETARY_OAUTH',m.now(),response_hash))
        return {'rows_imported':len(rows),'currency':body.currency,'data_source':'LIVE_AUTHORIZED_YOUTUBE_ANALYTICS',
                'revenue_is_estimate':True,'profit_calculated':False,'storage_has_no_oauth_secrets':True}

    @app.post('/api/m31/private-upload/intents/{intent_id}/reconcile')
    def reconcile(intent_id:str,body:Reconcile):
        if not body.owner_checked_studio_video_matches:
            raise HTTPException(409,'Owner must inspect exact uploaded video in YouTube Studio')
        if os.getenv('VIRALOS_ENABLE_REMOTE_RECONCILE')!='1':
            raise HTTPException(403,'Remote reconciliation disabled by default')
        with db.read() as c:
            intent=db.one(c,'SELECT * FROM m3_private_upload_intents WHERE intent_id=?',(intent_id,))
            if not intent:raise HTTPException(404,'Upload intent missing')
            if intent['state']!='REMOTE_UNKNOWN':raise HTTPException(409,'Only unknown remote uploads can be reconciled')
            linked=db.one(c,'SELECT intent_id FROM m3_private_upload_intents WHERE remote_video_id=?',(body.remote_video_id,))
            if linked:raise HTTPException(409,'Remote video ID already attached to another intent')
        try:
            credentials=youtube_private.upload_credentials(intent['local_channel_id'])
            youtube_private.verify_owned_channel(credentials,intent['remote_channel_id'])
            results=fetch_remote_video(credentials,body.remote_video_id)
        except Exception as ex:
            raise HTTPException(503,'Remote verification unavailable; state unchanged') from ex
        if len(results)!=1:
            raise HTTPException(409,'Video not visible to authenticated account; check ID manually')
        remote=results[0]
        if (remote.get('id')!=body.remote_video_id or remote.get('snippet',{}).get('channelId')!=intent['remote_channel_id']
            or remote.get('status',{}).get('privacyStatus')!='private'):
            raise HTTPException(409,'Remote video, channel or privacy did not match exactly')
        with db.transaction() as c:
            cur=db.one(c,'SELECT state FROM m3_private_upload_intents WHERE intent_id=?',(intent_id,))
            if not cur or cur['state']!='REMOTE_UNKNOWN':raise HTTPException(409,'Upload state changed during verification')
            c.execute("UPDATE m3_private_upload_intents SET state='UPLOADED_PRIVATE',remote_video_id=?,receipt_json=?,updated_at=? WHERE intent_id=? AND state='REMOTE_UNKNOWN'",
                     (body.remote_video_id,m.j({'id':body.remote_video_id,'privacyStatus':'private','reconciled_by_owner':True}),m.now(),intent_id))
        return {'intent_id':intent_id,'state':'UPLOADED_PRIVATE','privacy':'private',
                'owner_attested_local_file_matches_remote':True,'remote_bytes_independently_compared':False,
                'automatic_retry_performed':False}
