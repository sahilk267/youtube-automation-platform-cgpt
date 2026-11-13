"""Optional, consent-based YouTube *read-only analytics* integration.

Not a publishing client. No plaintext OAuth token storage, no fabricated metrics.
Requires Google APIs, google-auth-oauthlib and OS-backed `keyring` installed by owner.
"""
import json
from datetime import date,timedelta

SCOPES=['https://www.googleapis.com/auth/youtube.readonly',
        'https://www.googleapis.com/auth/yt-analytics.readonly']
SERVICE_NAME='ViralOS_Local_YouTube_OAuth'

def _keyring():
    try:import keyring
    except ImportError as ex:raise RuntimeError('Install optional YouTube authentication dependencies') from ex
    backend=keyring.get_keyring()
    if getattr(backend,'priority',0)<1 or 'fail' in backend.__class__.__module__.lower():
        raise RuntimeError('No secure OS credential store found; plaintext OAuth token fallback forbidden')
    return keyring

def store_credentials(local_channel_id,credentials):
    _keyring().set_password(SERVICE_NAME,local_channel_id,credentials.to_json())

def credentials_for(local_channel_id):
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    keyring=_keyring()
    raw=keyring.get_password(SERVICE_NAME,local_channel_id)
    if not raw:raise RuntimeError('No OAuth credentials for this local channel; connect from CLI first')
    credentials=Credentials.from_authorized_user_info(json.loads(raw),scopes=SCOPES)
    if credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
        store_credentials(local_channel_id,credentials)
    if not credentials.valid:raise RuntimeError('OAuth token expired or revoked; reconnect the channel')
    return credentials

def verify_channel(credentials,expected_remote_id):
    from googleapiclient.discovery import build
    service=build('youtube','v3',credentials=credentials,cache_discovery=False)
    data=service.channels().list(part='id,snippet',mine=True).execute()
    items=data.get('items',[])
    matches=[x for x in items if x.get('id')==expected_remote_id]
    if len(matches)!=1:raise RuntimeError('Authenticated YouTube channel does not match explicitly selected channel ID')
    return {'id':matches[0]['id'],'title':matches[0].get('snippet',{}).get('title','')}

def fetch_daily_report(credentials,start_date,end_date):
    """No revenue unless separate monetary scope + account permission is obtained."""
    from googleapiclient.discovery import build
    service=build('youtubeAnalytics','v2',credentials=credentials,cache_discovery=False)
    return service.reports().query(ids='channel==MINE',startDate=start_date,endDate=end_date,
                                   metrics='views,estimatedMinutesWatched,subscribersGained',
                                   dimensions='day',sort='day').execute()

def normalize_report(report):
    headers=[x.get('name') for x in report.get('columnHeaders',[])]
    wanted=['day','views','estimatedMinutesWatched','subscribersGained']
    if not all(k in headers for k in wanted):raise ValueError('Analytics report missing required columns')
    output=[]
    for row in report.get('rows',[]):
        if len(row)!=len(headers):raise ValueError('Analytics report column count mismatch')
        v=dict(zip(headers,row));date.fromisoformat(str(v['day']))
        views=int(v['views']);watch=float(v['estimatedMinutesWatched']);subs=int(v['subscribersGained'])
        if views<0 or watch<0:raise ValueError('Invalid negative analytics value')
        output.append({'report_date':str(v['day']),'views':views,'watch_hours':round(watch/60,4),
                       'subscribers_gained':subs})
    return output

def environment():
    try:
        import googleapiclient,google_auth_oauthlib
        return {'api_client_installed':True,'os_keyring_available':_keyring() is not None}
    except Exception:return {'api_client_installed':False,'os_keyring_available':False}
