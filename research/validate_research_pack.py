from pathlib import Path
import json,csv,collections,re,sys
p=Path(__file__).parent
rows=list(csv.DictReader((p/'120_channel_benchmarks.csv').open(encoding='utf-8-sig',newline='')))
assert len(rows)==120,len(rows)
assert len({(r['domain'],r['channel']) for r in rows})==120
counts=collections.Counter(r['domain'] for r in rows)
assert len(counts)==12 and set(counts.values())=={10}, counts
for r in rows:
    for col in ['archetype','hook','visuals_audio','why_it_works','viral_os_implementation','limits']:
        assert len(r[col])>=15, (r['channel'],col)
raw=json.loads((p/'channel_data.json').read_text(encoding='utf-8'))
assert len(raw)==120
assert all(x==y for x,y in zip(rows,raw))
report=(p/'02_120_CHANNEL_CONTENT_BENCHMARK.md').read_text(encoding='utf-8')
for r in rows: assert f'**' not in r['channel'] and f'. {r["channel"]}' in report, r['channel']
for f in ['README_START_HERE.md','01_PLATFORM_COMPETITOR_STUDY.md','02_120_CHANNEL_CONTENT_BENCHMARK.md','03_FINAL_ARCHITECTURE_DECISION_ADR-001.md','04_IMPLEMENTATION_AND_VALIDATION_PLAN.md']:
    s=(p/f).read_text(encoding='utf-8'); assert len(s)>300
print('PACK VALIDATION PASS: 120 profiles / 12 domains / 10 each / CSV-JSON-report parity / core docs present. This is NOT a media-content or executable-product quality test.')
