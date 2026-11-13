"""Reproduce an ORIGINAL abstract NFL-style Studio technical demo.
No broadcast footage, real-player statistics, or copyrighted music.
Requires pre-made narration WAV supplied via --voice (optional); never auto-downloads voices.
"""
import argparse, hashlib, json, sys
from pathlib import Path
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from app.studio_render import render_studio


def build(output:Path,voice:Path|None=None):
    output.mkdir(parents=True,exist_ok=True)
    art=Image.new('RGB',(640,400),(13,78,69));d=ImageDraw.Draw(art)
    for x in (130,255,380,505):d.line((x,45,x,350),fill='#599a87',width=3)
    d.ellipse((120,185,155,220),fill='#f9c978');d.ellipse((485,110,520,145),fill='#f9c978')
    d.line((150,200,505,135),fill='#ffe8a4',width=7)
    origin=output/'original_positioning_diagram.png';art.save(origin)
    digest=hashlib.sha256(origin.read_bytes()).hexdigest()
    assets={'sample_pip':{'path':origin,'kind':'STILL','content_sha256':digest}}
    shots=[
        {'role':'HOOK','duration_ms':3200,'headline':'What opens the passing lane?',
         'visual':{'kind':'ORIGINAL_DIAGRAM','asset_id':None},'claim_ids':[],
         'overlays':[{'text':'Notice the spacing','start_ms':550,'end_ms':2850,'anchor':'CENTER','style':'CALLOUT','image_asset_id':None}]},
        {'role':'CONTEXT','duration_ms':3500,'headline':'The formation changes the angles',
         'visual':{'kind':'ORIGINAL_DIAGRAM','asset_id':None},'claim_ids':[],
         'overlays':[{'text':'Original schematic insert','start_ms':350,'end_ms':3150,'anchor':'CENTER',
                      'style':'IMAGE_INSERT','image_asset_id':'sample_pip'}]},
        {'role':'PAYOFF','duration_ms':3100,'headline':'The key is spacing and timing',
         'visual':{'kind':'ORIGINAL_DIAGRAM','asset_id':None},'claim_ids':[],
         'overlays':[{'text':'An original tactical explanation','start_ms':450,'end_ms':2750,'anchor':'CENTER',
                      'style':'CALLOUT','image_asset_id':None}]},
    ]
    # Timing is manually estimated for demonstration only, not forced aligned.
    plan={'locale':'en-US','locale_reviewed':True,'music_asset_id':None,'shots':shots,
          'captions':[{'start_ms':100,'end_ms':3000,'text':'What causes the passing lane to open?'},
                      {'start_ms':3200,'end_ms':6500,'text':'Watch the players shift their positions.'},
                      {'start_ms':6700,'end_ms':9600,'text':'Spacing and timing create the lane.'}],
          'captions_provenance':'OWNER_TIMED'}
    video,qc,manifest=render_studio(plan,'nfl','SHORT',assets,voice,output)
    (output/'demo_plan.json').write_text(json.dumps(plan,indent=2,ensure_ascii=False))
    print(json.dumps({'video':str(video),'quality':qc['status'],'publish_ready':qc['publish_ready']},indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--out',default=str(ROOT/'examples'/'studio_demo'))
    ap.add_argument('--voice',default=None)
    args=ap.parse_args()
    build(Path(args.out),Path(args.voice) if args.voice else None)
