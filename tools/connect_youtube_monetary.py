"""Owner-run desktop OAuth: separate read-only monetary scope, no upload privileges."""
import argparse,json
from datetime import datetime,timezone
from pathlib import Path
from app import db
from app.analytics_m31 import MONETARY_SCOPES,store_monetary_credentials
from app.youtube_analytics import verify_channel

def main():
    p=argparse.ArgumentParser(description='Connect separately authorized revenue read-only scope')
    p.add_argument('--local-channel-id',required=True)
    p.add_argument('--expected-youtube-channel-id',required=True)
    p.add_argument('--client-secrets',required=True)
    args=p.parse_args()
    if not Path(args.client_secrets).is_file():raise SystemExit('Desktop OAuth JSON not found')
    db.initialize()
    with db.read() as c:
        ch=db.one(c,'SELECT channel_id FROM channels WHERE channel_id=?',(args.local_channel_id,))
        if not ch:raise SystemExit('Local ViralOS channel not found')
        existing=db.one(c,'SELECT remote_channel_id FROM m3_upload_accounts WHERE local_channel_id=?',(args.local_channel_id,))
        if existing and existing['remote_channel_id']!=args.expected_youtube_channel_id:
            raise SystemExit('Owner-selected channel differs from linked YouTube account')
    from google_auth_oauthlib.flow import InstalledAppFlow
    flow=InstalledAppFlow.from_client_secrets_file(args.client_secrets,MONETARY_SCOPES)
    credentials=flow.run_local_server(host='localhost',port=0,open_browser=True,access_type='offline',prompt='consent')
    verified=verify_channel(credentials,args.expected_youtube_channel_id)
    store_monetary_credentials(args.local_channel_id,credentials)
    # Register exact owner account for authorized read-only monetary reporting.
    with db.transaction() as c:
        c.execute('INSERT INTO m31_monetary_accounts(local_channel_id,remote_channel_id,remote_title,verified_at,scopes_json) VALUES (?,?,?,?,?) '
                  'ON CONFLICT(local_channel_id) DO UPDATE SET remote_channel_id=excluded.remote_channel_id,remote_title=excluded.remote_title,verified_at=excluded.verified_at',
                  (args.local_channel_id,verified['id'],verified['title'],datetime.now(timezone.utc).isoformat(),json.dumps(MONETARY_SCOPES)))
    print('Monetary READ-ONLY OAuth connected to',verified['id'],'. Enable sync separately; no upload is performed.')

if __name__=='__main__':main()
