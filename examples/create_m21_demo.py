from pathlib import Path
import os,json,subprocess,sys,shutil
from fastapi.testclient import TestClient
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from app.main import app
import app.main as main
from app import db
RUNTIME=ROOT/'scratch_m21_demo_runtime'
if RUNTIME.exists():shutil.rmtree(RUNTIME)
RUNTIME.mkdir(parents=True)
os.environ['VIRALOS_DB']=str(RUNTIME/'test.db')
main.OUT=RUNTIME/'outputs'

def post(c,url,body):
 r=c.post(url,json=body)
 if r.status_code!=200:raise RuntimeError((url,r.status_code,r.text))
 return r.json()

with TestClient(app) as client:
 ch=post(client,'/api/channels',{'name':'ViralOS Football Analysis Demo','sport_id':'nfl','locale':'en-US','market':'USA','timezone':'America/New_York'})
 p=post(client,'/api/projects',{'channel_id':ch['channel_id'],'title':'An original field positioning illustration','original_angle':'Demonstrate field positions using original graphic; no actual game footage','format':'SHORT'})
 pid=p['project_id']
 script=('Look closely at this original field diagram. '
         'These arrows show how a defender might react to movement on the field. '
         'This is a teaching illustration, not real match footage.')
 post(client,f'/api/projects/{pid}/script',{'text':script,'claim_links':[]})
 draft=post(client,f'/api/projects/{pid}/director/drafts',{'locale':'en-US'})
 print('Draft count',len(draft['segments']),'segments:',draft['segments'])
 for i,segment in enumerate(draft['segments']):
  voice=RUNTIME/f'voice_{i}.wav'
  subprocess.run(['espeak','-s','146','-w',str(voice),segment],check=True,timeout=25)
  res=client.post(f"/api/projects/{pid}/director/drafts/{draft['draft_id']}/voice/{i}",files={'file':('recorded.wav',voice.read_bytes(),'audio/wav')})
  print('Segment',i,res.status_code,res.text[:160]);assert res.status_code==200
 result=post(client,f"/api/projects/{pid}/director/drafts/{draft['draft_id']}/assemble",{})
 print('Assembled',result)
 srt=client.get(f"/api/projects/{pid}/director/plans/{result['plan_id']}/captions.srt")
 assert srt.status_code==200
 (ROOT/'examples'/'m21_spoken_captions.srt').write_text(srt.text,encoding='utf8')
 timeline=client.get(f'/api/projects/{pid}/studio/plan').json()['plan']
 (ROOT/'examples'/'m21_spoken_timeline.json').write_text(json.dumps(timeline,ensure_ascii=False,indent=2),encoding='utf8')
 post(client,f'/api/projects/{pid}/studio/queue',{})
 done=client.post('/api/studio/run-next').json();print('render',done);assert done['state']=='SUCCEEDED',done
 file=client.get(done['preview_url']).content
 (ROOT/'examples'/'m21_spoken_demo.mp4').write_bytes(file)
 report=client.get(done['report_url']).json()
 (ROOT/'examples'/'m21_spoken_qc.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf8')
 print('QC',report['quality']['status'],len(file))
subprocess.run(['ffmpeg','-y','-v','error','-ss','2.3','-i',str(ROOT/'examples'/'m21_spoken_demo.mp4'),'-frames:v','1',str(ROOT/'examples'/'m21_spoken_frame.png')],check=True)
