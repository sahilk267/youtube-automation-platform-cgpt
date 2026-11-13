"""Offline technical-video demo, synthetic/fictional illustrative source. Not verified real-world content.

Run from project root: python examples/create_m23_demo.py
Requires eSpeak, FFmpeg & FFprobe installed.  No network or YouTube calls.
"""
from pathlib import Path
import subprocess, json, sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.production_m23 import make_card
from app.studio_render import render_studio
from app.studio_routes import sha_file

root=Path(__file__).resolve().parent
card=root/'m23_demo_original_card.png'
make_card(card,'DEMO EXAMPLE: Show reviewed source context on screen.',
          'Fictional example — demonstration only','https://example.org/fictional', 'en-US')
spoken=root/'m23_demo_raw_espeak.wav';voice=root/'m23_demo_voice.wav'
subprocess.run(['espeak','-s','126','-w',str(spoken),
                'Before publishing, always check the original source. '
                'Show a clear graphic with readable attribution. '
                'This is a technical demonstration, not a real sporting event.'],check=True)
subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error','-i',str(spoken),
               '-af','apad','-t','12.000','-ar','16000','-ac','1',str(voice)],check=True)
plan={'locale':'en-US','shots':[
 {'role':'HOOK','duration_ms':4000,'headline':'Where does this claim come from?',
  'visual':{'kind':'ORIGINAL_DIAGRAM','motion':'ILLUSTRATIVE_ROUTE'},'overlays':[], 'claim_ids':[]},
 {'role':'EVIDENCE','duration_ms':4000,'headline':'Original illustration + clear source',
  'visual':{'kind':'RIGHTS_APPROVED_STILL','asset_id':'LOCAL_ORIGINAL_CARD'},'overlays':[], 'claim_ids':[]},
 {'role':'PAYOFF','duration_ms':4000,'headline':'Review context before publication',
  'visual':{'kind':'ORIGINAL_DIAGRAM','motion':'ILLUSTRATIVE_ROUTE'},'overlays':[], 'claim_ids':[]}
 ],'captions':[{'start_ms':0,'end_ms':3900,'text':'Check the original source before publishing.'},
               {'start_ms':4000,'end_ms':7800,'text':'Keep evidence and attribution visible.'},
               {'start_ms':8000,'end_ms':11800,'text':'Human review is still required.'}],
    'captions_provenance':'OWNER_TIMED','locale_reviewed':True}
assets={'LOCAL_ORIGINAL_CARD':{'path':card,'kind':'STILL','content_sha256':sha_file(card),
          'origin':'ViralOS ORIGINAL TEXT GRAPHIC • FICTIONAL DEMO'}}
outdir=root/'m23_demo_render'
video,qc,manifest=render_studio(plan,'cricket','SHORT',assets,voice,outdir)
report=root/'m23_demo_qc.json';report.write_text(json.dumps(qc,indent=2),encoding='utf8')
print(json.dumps({'video':str(video),'original_card':str(card),
                  'quality_status':qc['status'],'render_wall_seconds':qc['render_wall_seconds'],
                  'actual_user_source_verified':False,'professionally_reviewed':False},indent=2))
