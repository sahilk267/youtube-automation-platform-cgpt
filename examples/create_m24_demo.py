"""OPTIONAL Linux engineering demo (uses eSpeak only as synthetic audio fixture).
NOT a professional voice, factual match story or YouTube-ready video.
Run: PYTHONPATH=. python examples/create_m24_demo.py
"""
import io,json,os,shutil,subprocess,tempfile
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app
import app.main as main

root=Path(__file__).resolve().parent
if not shutil.which('espeak'):
    raise SystemExit('eSpeak required for synthetic demo fixture. Owner supplied WAV needed otherwise.')

def post(c,url,data):
    r=c.post(url,json=data)
    if r.status_code!=200:raise RuntimeError(f'{url}: {r.status_code} {r.text[:900]}')
    return r.json()

with tempfile.TemporaryDirectory(prefix='viralos_m24_demo_') as tmp:
    os.environ['VIRALOS_DB']=str(Path(tmp)/'local.db')
    main.OUT=Path(tmp)/'outputs'
    with TestClient(app) as c:
        ch=post(c,'/api/channels',{'name':'Fictional educational cricket','sport_id':'cricket',
            'locale':'en-US','market':'Demonstration','timezone':'Asia/Kolkata'})['channel_id']
        pid=post(c,'/api/projects',{'channel_id':ch,'title':'Original cricket field diagram demo',
            'original_angle':'Compare hypothetical positions in an illustrative educational scene, not an actual cricket match.',
            'format':'SHORT'})['project_id']
        english='This original diagram shows two cricket field positions. It is a fictional educational example, not actual match footage.'
        hindi='यह चित्र क्रिकेट की दो फील्ड स्थितियों को समझाता है। यह केवल काल्पनिक शैक्षिक उदाहरण है, वास्तविक मैच की फुटेज नहीं।'
        post(c,f'/api/projects/{pid}/script',{'text':english,'claim_links':[]})
        for locale,reviewed,voice in [('en-US',english,'en-us'),('hi-IN',hindi,'hi')]:
            variant=post(c,f'/api/projects/{pid}/m24/variants',{'locale':locale,
                'reviewed_script':reviewed,'reviewer':'Synthetic demo fixture reviewer',
                'regional_notes':'Fictional cricket illustration; not a claim of a real play, match or athlete.',
                'words_names_numbers_and_meaning_reviewed':True,'on_screen_language_reviewed':True})
            vid=variant['variant_id']
            detail=c.get(f'/api/projects/{pid}/m24/variants/{vid}').json()
            for x in detail['segments']:
                tone=Path(tmp)/f'{locale}_{x["index"]}.wav'
                cp=subprocess.run(['espeak','-v',voice,'-s','175','-w',str(tone),x['text']],capture_output=True,text=True,timeout=20)
                if cp.returncode:raise RuntimeError('eSpeak fixture failed')
                response=c.post(f'/api/projects/{pid}/m24/variants/{vid}/voice/{x["index"]}',
                    files={'file':('synthetic_demo.wav',tone.read_bytes(),'audio/wav')})
                if response.status_code!=200:raise RuntimeError(response.text)
            result=post(c,f'/api/projects/{pid}/m24/variants/{vid}/render',{})
            mp4=c.get(result['preview_url'])
            srt=c.get(result['captions_url'])
            qc=c.get(f'/api/projects/{pid}/m24/previews/{result["preview_id"]}/qc')
            assert mp4.status_code==srt.status_code==qc.status_code==200
            (root/f'm24_{locale}_demo.mp4').write_bytes(mp4.content)
            (root/f'm24_{locale}_captions.srt').write_text(srt.text,encoding='utf8')
            (root/f'm24_{locale}_qc.json').write_text(json.dumps(qc.json(),indent=2,ensure_ascii=False),encoding='utf8')
            print(locale,'length',len(mp4.content),'qc',result['technical_qc'])
for locale in ('en-US','hi-IN'):
    source=root/f'm24_{locale}_demo.mp4'
    frame=root/f'm24_{locale}_frame.png'
    subprocess.run(['ffmpeg','-y','-loglevel','error','-ss','1.2','-i',str(source),'-frames:v','1',str(frame)],check=True,timeout=30)
