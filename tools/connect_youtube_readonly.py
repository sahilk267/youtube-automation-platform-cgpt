"""Connect user's own YouTube account read-only, with explicit channel confirmation.

Run locally on the owner's computer, not on a server. OAuth tokens go only to
OS credential store; never into the repository or console output.
"""
import argparse
from pathlib import Path
from app import db
from app.youtube_analytics import SCOPES,store_credentials,verify_channel

def main():
    a=argparse.ArgumentParser()
    a.add_argument('--local-channel-id',required=True)
    a.add_argument('--expected-youtube-channel-id',required=True,
                   help='Exact owned YouTube channel ID, not a display name')
    a.add_argument('--client-secrets',required=True,help='Google OAuth Desktop client JSON')
    b=a.parse_args()
    if not Path(b.client_secrets).is_file():raise SystemExit('Client secrets file not found')
    with db.read() as c:
        row=c.execute('SELECT channel_id FROM channels WHERE channel_id=?',(b.local_channel_id,)).fetchone()
        if not row:raise SystemExit('Create the local ViralOS channel first')
    from google_auth_oauthlib.flow import InstalledAppFlow
    flow=InstalledAppFlow.from_client_secrets_file(b.client_secrets,SCOPES)
    credentials=flow.run_local_server(host='localhost',port=0,open_browser=True,access_type='offline',prompt='consent')
    ch=verify_channel(credentials,b.expected_youtube_channel_id)
    store_credentials(b.local_channel_id,credentials)
    db.initialize()
    with db.transaction() as c:
        c.execute('INSERT OR REPLACE INTO m3_youtube_accounts(local_channel_id,remote_channel_id,remote_title,connected_at,verification,oauth_scope_text) VALUES (?,?,?,?,?,?)',
                  (b.local_channel_id,ch['id'],ch['title'],__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),
                   'OAUTH_CHANNELS_MINE',','.join(SCOPES)))
    print('Connected: ',ch['title'],' / ',ch['id'],' (READ ONLY; uploads remain DISABLED)')

if __name__=='__main__':main()
