"""Explicit desktop OAuth for PRIVATE upload capability (requires user action)."""
import argparse
from datetime import datetime,timezone
from pathlib import Path
from app import db
from app.youtube_private import SCOPES,store_upload_credentials,verify_owned_channel

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--local-channel-id',required=True)
    parser.add_argument('--expected-youtube-channel-id',required=True)
    parser.add_argument('--client-secrets',required=True)
    args=parser.parse_args()
    if not Path(args.client_secrets).is_file():raise SystemExit('OAuth client secrets file missing')
    db.initialize()
    with db.read() as c:
        row=db.one(c,'SELECT channel_id FROM channels WHERE channel_id=?',(args.local_channel_id,))
        if not row:raise SystemExit('Create ViralOS channel first')
    from google_auth_oauthlib.flow import InstalledAppFlow
    flow=InstalledAppFlow.from_client_secrets_file(args.client_secrets,SCOPES)
    creds=flow.run_local_server(host='localhost',port=0,open_browser=True,access_type='offline',prompt='consent')
    verified=verify_owned_channel(creds,args.expected_youtube_channel_id)
    store_upload_credentials(args.local_channel_id,creds)
    with db.transaction() as c:
        c.execute('INSERT INTO m3_upload_accounts(local_channel_id,remote_channel_id,remote_title,verified_at,scopes_json) VALUES (?,?,?,?,?) '
                  'ON CONFLICT(local_channel_id) DO UPDATE SET remote_channel_id=excluded.remote_channel_id,remote_title=excluded.remote_title,verified_at=excluded.verified_at,scopes_json=excluded.scopes_json',
                  (args.local_channel_id,verified['id'],verified['title'],datetime.now(timezone.utc).isoformat(),__import__('json').dumps(SCOPES)))
    print('Upload OAuth connected for',verified['id'],'— uploads still require explicit per-video approval and private-upload opt-in')

if __name__=='__main__':main()
