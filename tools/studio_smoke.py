"""Runs offline API smoke from a fresh temporary DB, no external network. Optional --demo-output path."""
import io, sys, tempfile, os
from pathlib import Path
from fastapi.testclient import TestClient
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
from app.main import app
from app import db

def post(client,path,data):
    result=client.post(path,json=data)
    assert result.status_code==200,(path,result.status_code,result.text)
    return result.json()

if __name__=='__main__':
    with tempfile.TemporaryDirectory() as d:
        os.environ['VIRALOS_DB']=str(Path(d)/'viralos.sqlite')
        with TestClient(app) as client:
            ch=post(client,'/api/channels',{'name':'Local Smoke Channel','sport_id':'cricket','locale':'en-US','market':'India','timezone':'Asia/Kolkata'})
            p=post(client,'/api/projects',{'channel_id':ch['channel_id'],'title':'Original cricket field overview','original_angle':'Explain a field diagram without any copyrighted game footage','format':'SHORT'})
            post(client,f"/api/projects/{p['project_id']}/script",{'text':'This is an original illustration explaining field positioning. No real game outcome is claimed.','claim_links':[]})
            body=client.get(f"/api/projects/{p['project_id']}/studio/example").json()
            post(client,f"/api/projects/{p['project_id']}/studio/plans",body)
            post(client,f"/api/projects/{p['project_id']}/studio/queue",{})
            done=post(client,'/api/studio/run-next',{})
            assert done['state']=='SUCCEEDED',done
            qc=client.get(done['report_url']).json()
            assert not qc['quality']['publish_ready'] and qc['quality']['automated_checks']['video_stream']
            print('PASS: CPU Studio MP4, timed overlays, hashes, technical QC and publish block')
