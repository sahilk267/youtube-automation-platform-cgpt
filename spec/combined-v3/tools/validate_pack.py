#!/usr/bin/env python3
"""ViralOS v2.1 specification-package structural & SQLite behavior validation.
This NEVER verifies software implementation, legal rights, live APIs or YouTube monetization.
"""
from pathlib import Path
import json,csv,sqlite3,hashlib,re,sys,ast
P=Path(__file__).resolve().parents[1]
errors=[];warn=[]
def check(cond,msg):
 if not cond:errors.append(msg)
def load(rel):
 try:return json.loads((P/rel).read_text(encoding='utf-8'))
 except Exception as e: errors.append('JSON invalid '+rel+' '+str(e));return {}
manifest=load('PACK_MANIFEST.json');profile=manifest.get('profile');check(profile in {'LAUNCH','ULTIMATE','COMBINED'},'unknown pack profile')
all_domains={'newsroom','science','technology','business','gaming','history','space','learning','sports','career','productivity','culture'}
expected= {'sports','technology'} if profile=='LAUNCH' else all_domains
registry=load('configs/domain_registry.json');ids={x['domain_id'] for x in registry.get('domains',[])}
check(ids==expected,'domain registry differs from pack scope')
check(set(x.stem for x in (P/'domains').glob('*.md'))==ids,'domain dossiers missing or unexpectedly added')
check(set(x.stem for x in (P/'playbooks').glob('*.md'))==ids,'domain playbooks missing or unexpectedly added')
check(manifest.get('domain_dossier_count')==len(ids),'manifest dossier count mismatch')
for d in ids:check((P/f'domains/{d}.md').exists(),'missing domain '+d)
engine=load('configs/engine_registry.json');eng=engine.get('engines',[]);engineids={x['engine_id'] for x in eng}
check(len(engineids)==len(eng),'duplicate engine identifiers');check(len(eng)==manifest.get('engine_count'),'engine count mismatch')
execs=load('configs/engine_execution_registry.json');entries=execs.get('engines',[])
check(set(x['engine_id'] for x in entries)==engineids,'execution registry missing/extra engine')
for x in entries:
 check(x['domain_id'] is None or x['domain_id'] in ids,'execution engine points to missing domain '+x['engine_id'])
 check((P/x['source_dossier']).is_file(),'execution dossier missing '+x['engine_id'])
 check(x['input_contract']=='ExecutionRequest.schema.json' and x['output_contract']=='ExecutionResult.schema.json','execution envelope mismatch '+x['engine_id'])
 check(len(x.get('execution_steps',[]))>=3,'missing execution steps '+x['engine_id'])
 check(x.get('implementation_status')=='NOT_IMPLEMENTED_IN_SPEC_PACK','fake implemented engine '+x['engine_id'])
for item in ['SPEC_PRECEDENCE.md','GAP_AUDIT.md','AGENT_START_HERE.md','README_FIRST.md', 'database/schema.sql','database/002_operational_controls.sql','tests/GAP_ACCEPTANCE.csv','tests/OPERATOR_RELEASE_CHECKLIST.md','configs/provider_acceptance.json']:
 check((P/item).exists(),'missing '+item)
for f in (P/'contracts').glob('*.schema.json'):
 s=load(str(f.relative_to(P)));check(s.get('additionalProperties') is False,'not strict JSON contract '+f.name)
 check(s.get('properties',{}).get('contract_version',{}).get('const')=='2.0.0','contract version drift '+f.name)
 try:
  from jsonschema.validators import Draft202012Validator
  Draft202012Validator.check_schema(s)
 except ImportError: warn.append('jsonschema unavailable: full schema compliance not checked');break
 except Exception as e:errors.append('invalid schema '+f.name+' '+str(e))
try:
 import yaml
 y=yaml.safe_load((P/'contracts/openapi.yaml').read_text(encoding='utf-8'))
 check(len(y.get('paths',{}))>=30,'API route loss')
except ImportError:warn.append('PyYAML unavailable: OpenAPI YAML not parsed')
except Exception as e:errors.append('OpenAPI parse '+str(e))
# All test references must exist. Future U- tests in Launch are deferred, not active blockers.
with (P/'tests/REQUIREMENTS.csv').open(newline='',encoding='utf-8') as f:req=list(csv.DictReader(f))
with (P/'tests/ACCEPTANCE_MATRIX.csv').open(newline='',encoding='utf-8') as f:acc=list(csv.DictReader(f))
reqs={x['req_id'] for x in req}; tests={x['test_id'] for x in acc}
check(len(reqs)==len(req),'duplicate requirement IDs');check(len(tests)==len(acc),'duplicate test IDs')
for x in entries: check(x['evaluation_test_ref'] in tests,'unknown engine test '+x['engine_id'])
for x in req:check(x['test_ids'] in tests,'req missing test '+x['req_id'])
with (P/'tests/GAP_ACCEPTANCE.csv').open(newline='',encoding='utf-8') as f:rows=list(csv.DictReader(f))
check(len(rows)>=25 and len({x['gap_id'] for x in rows})==len(rows),'gap audit tests incomplete')
check(all(x['status']=='NOT_RUN' for x in rows),'gap tests pre-claimed pass')
check(all(x['status']=='SPECIFIED' for x in req),'baseline requirements pre-claimed passed')
# SQL baseline + additive migration + idempotency + invalid statuses + foreign key checks
try:
 db=sqlite3.connect(':memory:');db.execute('PRAGMA foreign_keys=ON')
 db.executescript((P/'database/schema.sql').read_text(encoding='utf-8'))
 db.executescript((P/'database/002_operational_controls.sql').read_text(encoding='utf-8'))
 checks={x[0] for x in db.execute("select name from sqlite_master where type='table'")}
 for nm in ['outbound_action_intents','review_revision_snapshots','connector_qualification','research_coverage_reports','model_execution_audit']:
  check(nm in checks,'migration missing '+nm)
 check(db.execute('PRAGMA integrity_check').fetchone()[0]=='ok','SQLite integrity check failed')
 check(db.execute('PRAGMA foreign_key_check').fetchall()==[],'SQLite foreign key problems')
 try:
  db.execute("insert into outbound_action_intents(intent_id,job_id,action_type,payload_sha256,idempotency_key,status,created_at,updated_at) VALUES ('x','bad','UPLOAD','bad','key','FAKE','2026-11-09','2026-11-09')")
  errors.append('DB accepts invalid external action state/FK')
 except sqlite3.IntegrityError:pass
 db.close()
except Exception as e:errors.append('migration SQL failed '+str(e))
# v2.1 additional coverage checks
with (P/'tests/ENGINE_OPERATION_CASES.csv').open(newline='',encoding='utf-8') as f:engine_cases=list(csv.DictReader(f))
check(len(engine_cases)==len(entries),'every engine needs unique concrete negative test')
check(len({x['engine_id'] for x in engine_cases})==len(entries),'duplicate engine test registration')
for x in entries:check(x['case_id'] in {c['test_id'] for c in engine_cases},'engine case missing '+x['engine_id'])
api=load('configs/api_operation_registry.json')
try:
 import yaml
 oa=yaml.safe_load((P/'contracts/openapi.yaml').read_text(encoding='utf-8'))
 ops=[o for pp in oa['paths'].values() for method,o in pp.items() if method not in ('parameters','summary','description')]
 check(len(ops)==api['operation_count'],'API operation registry mismatch')
 for o in ops:
  for st,resp in o.get('responses',{}).items():
   link=resp.get('content',{}).get('application/json',{}).get('schema',{}).get('$ref')
   check(bool(link) and (P/'contracts'/link.removeprefix('./')).is_file(),'untyped API response '+o['operationId']+' '+st)
except ImportError:pass
except Exception as e:errors.append('typed API validation '+str(e))
wf=load('configs/workflow_dag.json');steps=wf.get('pipeline_steps',[]);all_step_ids={x['id'] for x in steps}
check(len(steps)==len(all_step_ids),'duplicate workflow step')
for x in steps:check(set(x['depends_on'])<=all_step_ids,'missing workflow dep for '+x['id'])
# recursive cycle detector
edges={x['id']:x['depends_on'] for x in steps}
def visit(n,active,seen):
 if n in active:return True
 if n in seen:return False
 active.add(n)
 for k in edges.get(n,[]):
  if visit(k,active,seen):return True
 active.remove(n);seen.add(n);return False
seen=set();check(not any(visit(k,set(),seen) for k in edges),'workflow cycle')
if profile=='LAUNCH':
 check(all(x['req_id'].startswith('L-') for x in req),'Launch package contains non-launch requirements')
 check(len(req)==22 and len(acc)==22,'Launch scope not isolated to 22 L- requirements')
if profile=='COMBINED':
 check(all(e.get('release_state')=='DEFERRED_UNTIL_ULTIMATE_PROFILE_ENABLED' for e in entries if e['domain_id'] not in (None,'sports','technology')),'Combined future domains incorrectly enabled')

# Resolve ALL local schema file references (root and nested API DTO files)
for schema_path in (P/'contracts').rglob('*.schema.json'):
 try:doc=json.loads(schema_path.read_text(encoding='utf-8'))
 except Exception as e:errors.append('schema parse failed '+str(schema_path)+' '+str(e));continue
 def walk(x):
  if isinstance(x,dict):
   for key,val in x.items():
    if key=='$ref' and isinstance(val,str) and (val.startswith('./') or val.startswith('../')):
     check((schema_path.parent/val.split('#')[0]).resolve().is_file(),'broken local $ref '+str(schema_path.relative_to(P))+' '+val)
    else:walk(val)
  elif isinstance(x,list):
   for v in x:walk(v)
 walk(doc)

# Check file checksums against manifest (excluding hashes and mutable debug)
h=load('FILE_HASHES.json').get('sha256',{})
for rel,digest in h.items():
 f=P/rel
 check(f.is_file(),'hash file missing '+rel)
 if f.is_file():check(hashlib.sha256(f.read_bytes()).hexdigest()==digest,'checksum failed '+rel)
actual={str(x.relative_to(P)) for x in P.rglob('*') if x.is_file() and str(x.relative_to(P))!='FILE_HASHES.json'}
check(set(h)==actual,'missing or extra files vs FILE_HASHES inventory')
print('PACK',profile,'DOMAINS',len(ids),'ENGINES',len(eng),'SCHEMAS',len(list((P/'contracts').glob('*.schema.json'))),'GAP_CHECKS',len(rows))
for x in warn:print('WARNING',x)
for x in errors:print('ERROR',x)
print('VALIDATION', 'PASS' if not errors else 'FAIL: '+str(len(errors))+' errors')
print('NOTE: only structural/document integrity, NOT running app/source/API/hardware/license validation')
sys.exit(1 if errors else 0)
