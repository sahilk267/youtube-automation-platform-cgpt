#!/usr/bin/env python3
"""ViralOS v3 specification integrity validator. Not a functional media or legal test."""
from pathlib import Path
import sys, csv, json, sqlite3, re, collections
P=Path(__file__).resolve().parents[1]
errors=[]
def require(ok,msg):
 if not ok:errors.append(msg)
def load(p):
 try:return json.loads((P/p).read_text(encoding='utf-8'))
 except Exception as e:errors.append(f'cannot read JSON {p}: {e}');return {}
try:
 from jsonschema import Draft202012Validator
except ImportError:
 print('ERROR: jsonschema>=4.20 required for full v3 contract validation. Install in an isolated env.');sys.exit(1)
manifest=load('PACK_MANIFEST.json');profile=manifest.get('profile')
require(profile in ('LAUNCH','ULTIMATE','COMBINED'),'invalid profile')
require(manifest.get('pack_format_version')=='3.0','incorrect manifest spec version')
require(manifest.get('contract_version')=='2.0.0','v2 backward compatibility drift')
require(manifest.get('creative_contract_version')=='3.0.0','v3 artifact version drift')
expected={'sports','technology'} if profile=='LAUNCH' else {'sports','newsroom','science','technology','business','gaming','history','space','learning','career','productivity','culture'}
actual={p.stem for p in (P/'creative/directors').glob('*.json')}
require(actual==expected,f'director scope mismatch {actual^expected}')
fmts={p.stem for p in (P/'creative/formats').glob('*.md')}
require(len(fmts)==9,'format playbook count mismatch')
SC={p.stem.removesuffix('.schema'):json.loads(p.read_text(encoding='utf-8')) for p in (P/'contracts/v3').glob('*.schema.json')}
require(len(SC)==15,'missing v3 schemas')
for name,doc in SC.items():
 try: Draft202012Validator.check_schema(doc)
 except Exception as e:errors.append(f'bad schema {name}: {e}')
 require(doc.get('additionalProperties') is False, f'{name} must be strict')
 require(doc.get('properties',{}).get('contract_version',{}).get('const')=='3.0.0', f'{name}: wrong contract version')
 fixture=P/'tests/v3_fixtures'/f'{name}.json'
 if fixture.exists():
  try:
   value=json.loads(fixture.read_text(encoding='utf-8'))
   errs=list(Draft202012Validator(doc).iter_errors(value))
   if errs:errors.append(f'fixture {name} fails schema: {errs[0].message}')
  except Exception as e:errors.append(f'fixture {name}: {e}')
 elif name!='DomainCreativeProfile':errors.append(f'missing positive test fixture for {name}')
for d in actual:
 p=P/'creative/directors'/f'{d}.json';j=json.loads(p.read_text())
 require(not list(Draft202012Validator(SC['DomainCreativeProfile']).iter_errors(j)),f'invalid director profile {d}')
 require((P/j.get('director_document','x')).is_file(),f'missing director doc {d}')
 require(set(j['allowed_format_ids'])<=fmts,f'director {d} references unknown format')
 require(j.get('implementation_status')=='SPECIFIED_NOT_IMPLEMENTED','director falsely implemented '+d)
 require(len((P/j['director_document']).read_text())>1700,'under-detailed director '+d)
ops=load('configs/creative_operation_registry_v3.json').get('operations',[])
require(len(ops)==18,'operation count is not 18')
ids=[x.get('id') for x in ops];require(len(set(ids))==len(ids),'duplicate operation ids')
old=load('configs/engine_registry.json').get('engines',[])
require(not set(ids)&{x['engine_id'] for x in old},'colliding old/new engine IDs')
for op in ops:
 require(op.get('implementation_status')=='SPECIFIED_NOT_IMPLEMENTED','operation falsely implemented '+str(op.get('id')))
 require(op.get('owner_service'),'missing owner '+str(op.get('id')))
 require(op.get('input_contract') and op.get('output_contract'),'missing I/O '+str(op.get('id')))
 require(op.get('failure_code') and op.get('gate'),'missing failure/gate '+str(op.get('id')))
 require(set(op.get('depends_on',[]))<=set(ids),'unknown op dependency '+str(op.get('id')))
 if op.get('conditional_on')!='ALWAYS':require(op['short_name']=='SOURCE_CLIP_REVIEW','unapproved optional operation')
seen=set();active=set();graph={x['id']:x.get('depends_on',[]) for x in ops}
require('CV3-07' in graph.get('CV3-08',[]),'asset build can bypass source clip rights review')
def dfs(n):
 if n in active:errors.append('cycle '+n);return
 if n in seen:return
 active.add(n)
 for a in graph.get(n,[]):dfs(a)
 active.remove(n);seen.add(n)
for id in ids:dfs(id)
with (P/'tests/V3_REQUIREMENTS.csv').open(encoding='utf-8-sig',newline='') as f:req=list(csv.DictReader(f))
require(len(req)==len(ops),'v3 requirement count mismatch')
require({x['operation_id'] for x in req}==set(ids),'v3 requirements do not cover operations')
require(all(x['status']=='SPECIFIED_NOT_IMPLEMENTED' for x in req),'tests preclaimed implemented')
with (P/'tests/V3_CREATIVE_GOLDEN_CASES.csv').open(encoding='utf-8-sig',newline='') as f:gold=list(csv.DictReader(f))
require(all(x['status']=='NOT_RUN' for x in gold),'golden tests preclaimed passed')
for d in actual:
 for kind in ('SHORT','LONG'):
  require(any(x['domain_id']==d and x['format']==kind for x in gold), f'missing {kind} golden test {d}')
neg=load('tests/V3_NEGATIVE_CASES.json').get('cases',[])
require(len(neg)>=25,'missing negative cases')
require(len({x['id'] for x in neg})==len(neg),'duplicate negative IDs')
require(all(x['status']=='NOT_RUN' for x in neg),'negative tests preclaimed passed')
require(all(x['stage'] in {o['short_name'] for o in ops} for x in neg),'negative test unknown stage')
# Temporal and risk invariants are application logic, not covered by JSON schema shapes.
beat=load('tests/v3_fixtures/TimedBeatGraph.json');shots=load('tests/v3_fixtures/ShotPlan.json');tl=load('tests/v3_fixtures/VideoTimeline.json')
def check_intervals(items,duration,label):
 for o in items:require(0<=o['start_ms']<o['end_ms']<=duration,f'bad {label} half-open interval')
check_intervals(beat['beats'],beat['duration_ms'],'beat')
require(beat['beats'][0]['start_ms']==0 and beat['beats'][-1]['end_ms']==beat['duration_ms'],'beats lack full duration')
require(all(a['end_ms']==b['start_ms'] for a,b in zip(beat['beats'],beat['beats'][1:])), 'gapped / overlapped beat sequence')
check_intervals(shots['shots'],shots['duration_ms'],'shot')
require({x['beat_id'] for x in shots['shots']}=={x['beat_id'] for x in beat['beats']},'shots not mapped to beat IDs')
check_intervals(tl['segments'],tl['duration_ms'],'timeline segment')
pri=sorted((x for x in tl['segments'] if x['lane']=='PRIMARY_VISUAL'),key=lambda x:x['start_ms'])
require(all(a['end_ms']<=b['start_ms'] for a,b in zip(pri,pri[1:])), 'overlapping primary visuals')
reaction=load('tests/v3_fixtures/ReactionClipMap.json')
if reaction['source_category'] in ('UNKNOWN_OR_DENIED','LEGAL_EXCEPTION_REVIEW'):
 require(not reaction['auto_download_allowed'],'unknown/legal-review source auto-download allowed')
 if reaction['source_category']=='UNKNOWN_OR_DENIED':require(not reaction['excerpts'],'unknown source clips in production')
qc=load('tests/v3_fixtures/CreativeQualityReport.json')
if qc['human_watchthrough']!='APPROVED':require(qc['final_status']!='PASS','unreviewed QC marked PASS')
obs=load('tests/v3_fixtures/CreatorVideoObservation.json')
require(obs['private_retention'] is None,'competitor private analytics invented')
# Research inventory is a benchmark, not falsely labelled ranked/video-observed list.
with (P/'research/120_channel_benchmarks.csv').open(encoding='utf-8-sig',newline='') as f:channels=list(csv.DictReader(f))
counts=collections.Counter(x['domain'] for x in channels)
require(len(channels)==120 and len(counts)==12 and all(x==10 for x in counts.values()),'benchmark 120/12x10 broken')
require(len({(x['domain'],x['channel']) for x in channels})==120,'duplicate channel benchmark records')
require('desk-research' in (P/'core/24_COMPETITOR_ADR_V3.md').read_text().lower(),'missing benchmark limitations')
# Additive SQL migration smoke test (not an installed DB migration).
try:
 db=sqlite3.connect(':memory:');db.execute('PRAGMA foreign_keys=ON')
 for s in ['database/schema.sql','database/002_operational_controls.sql','database/003_content_production_v3.sql']:
  db.executescript((P/s).read_text(encoding='utf-8'))
 require(db.execute('PRAGMA integrity_check').fetchone()[0]=='ok','sqlite integrity failure')
 require(db.execute('PRAGMA foreign_key_check').fetchall()==[],'sqlite FK failure')
 tables={x[0] for x in db.execute('SELECT name FROM sqlite_master WHERE type="table"')}
 for t in ('creative_briefs','creative_story_versions','creative_shot_plans','creative_locale_variants','creative_timeline_versions','creative_quality_reports','creative_asset_dependencies','creative_rights_source_clip_maps'):
  require(t in tables,'missing SQL table '+t)
 try:
  db.execute("INSERT INTO creative_briefs(brief_id,project_id,domain_id,contract_version,brief_json,brief_sha256,status,created_at) VALUES('x','x','x','3.0.0','{}','"+'0'*64+"','FAKE','x')")
  errors.append('SQLite accepted invalid v3 status / missing project foreign key')
 except sqlite3.IntegrityError:pass
 db.close()
except Exception as e:errors.append('sqlite v3 migration: '+str(e))
# This validator deliberately checks only specs and synthetic fixtures.
print('PROFILE',profile,'V3_SCHEMAS',len(SC),'DIRECTORS',len(actual),'FORMAT_PACKS',len(fmts),'OPERATIONS',len(ops),'GOLDENS',len(gold),'NEGATIVE_CASES',len(neg),'CHANNEL_REFERENCES',len(channels))
for e in errors:print('ERROR',e)
print('V3 SPEC VALIDATION','PASS' if not errors else f'FAIL ({len(errors)})')
print('NOT A TEST OF REAL VIDEO GENERATION, FACTUAL CORRECTNESS, COPYRIGHT RIGHTS, WINDOWS PERFORMANCE OR YOUTUBE INCOME')
sys.exit(1 if errors else 0)
