"""Deterministic, source-aware *assistance*, never invented fact verification."""
import hashlib, json, re, xml.etree.ElementTree as ET
from datetime import datetime, timezone
from urllib.parse import urlsplit

MAX_FEED_BYTES=262144

def parse_owner_rss(xml_text: str, max_items: int=20):
    """Parse owner-provided RSS/Atom; no hidden network requests or remote entity expansion."""
    data=xml_text.encode('utf-8')
    if len(data)>MAX_FEED_BYTES:raise ValueError('RSS XML exceeds 256 KiB limit')
    if '<!DOCTYPE' in xml_text.upper() or '<!ENTITY' in xml_text.upper():
        raise ValueError('XML DTD and external entities are forbidden')
    root=ET.fromstring(data)
    if root.tag not in ('rss','{http://www.w3.org/2005/Atom}feed'):
        raise ValueError('Requires RSS 2.0 or Atom feed')
    items=[]
    if root.tag=='rss':
        for node in root.findall('./channel/item')[:max_items]:
            entry={'title':(node.findtext('title') or '').strip()[:240], 'url':(node.findtext('link') or '').strip(),
                   'published_at':(node.findtext('pubDate') or '').strip()[:100]}
            items.append(entry)
    else:
        ns='{http://www.w3.org/2005/Atom}'
        for node in root.findall(ns+'entry')[:max_items]:
            link=node.find(ns+'link');url=link.attrib.get('href','') if link is not None else ''
            items.append({'title':(node.findtext(ns+'title') or '').strip()[:240],
                          'url':url,'published_at':(node.findtext(ns+'updated') or '').strip()[:100]})
    result=[];seen=set()
    for item in items:
        u=urlsplit(item['url'])
        if not item['title'] or u.scheme not in ('https','http') or not u.hostname or u.username or u.password:continue
        if item['url'] in seen:continue
        seen.add(item['url']);result.append(item)
    return result

def research_audit(claims, edges, script, source_bindings):
    """Returns evidence coverage and *review requirements*, not truth assertions."""
    claim_map={c['claim_id']:c for c in claims}
    supported={e['claim_id'] for e in edges if e['relation']=='SUPPORTS' and e['source_version_id'] in source_bindings}
    statuses={cl['verification_status'] for cl in claims}
    gaps=[]
    if not source_bindings:gaps.append('No project-bound source versions')
    if not claims:gaps.append('No atomic factual claims recorded; factual script may still be unreviewed')
    for cl in claims:
        if cl['claim_id'] not in supported:gaps.append('Claim has no project-bound supporting evidence: '+cl['claim_id'])
        if cl['verification_status']!='SUPPORTED':gaps.append('Claim requires human verification: '+cl['claim_id'])
    if not script:gaps.append('No current script')
    if not edges and claims:gaps.append('No evidence edges')
    return {'sources_bound':len(source_bindings),'claims_total':len(claims),
            'supported_by_owner_attestation':sum(1 for cl in claims if cl['verification_status']=='SUPPORTED' and cl['claim_id'] in supported),
            'script_exists':bool(script),'gaps':gaps,
            'independent_verification':'NOT_PERFORMED','fact_assurance':'NO_AUTOMATIC_TRUTH_CLAIM',
            'publish_gate':'OWNER_REVIEW_REQUIRED'}

def story_plan(script, scenes, locale, format_name, sport):
    if not script or not scenes:raise ValueError('Script and scenes required')
    duration=0;beats=[]
    tags=['HOOK','CONTEXT','EVIDENCE','EXPLANATION','PAYOFF']
    for n,scene in enumerate(scenes):
        spec=json.loads(scene['spec_json'])
        ms=round(float(spec['duration_seconds'])*1000)
        role='HOOK' if n==0 else 'PAYOFF' if n==len(scenes)-1 else (tags[min(n,3)])
        beats.append({'index':n,'role':role,'start_ms':duration,'end_ms':duration+ms,
                      'spoken_segment':'NOT_ALIGNED','text_overlay':{'text':spec['text'],'safe_area_pct':[7,18,86,64],
                      'style':'MAIN_TITLE','native_locale':locale},
                      'visual':{'type':'ORIGINAL_DIAGRAM_OR_TEXT','domain':sport,'rights':'ORIGINAL_ONLY'},
                      'music':{'mode':'NONE_UNTIL_RIGHTS_APPROVED'},'source_claim_ids':spec.get('claim_ids',[]),
                      'human_director_review':'REQUIRED'})
        duration+=ms
    return {'version':'1.0','source_script_id':script['script_version_id'],'locale':locale,'format':format_name,
            'total_duration_ms':duration,'beat_count':len(beats),'beats':beats,
            'voice_direction':{'source':'OWNER_WAV_OR_CONFIGURED_LOCAL_TTS','alignment':'NOT_MEASURED',
                               'pronunciation_review':'REQUIRED'},
            'audience_promise':'OWNER_MUST_REVIEW','creative_quality':'UNTESTED','publish_ready':False}

def srt_from_plan(plan, locale_texts=None):
    def timestamp(ms):
        h,ms=divmod(int(ms),3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000)
        return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'
    result=[]
    for n,beat in enumerate(plan['beats']):
        text=(locale_texts[n] if locale_texts else beat['text_overlay']['text']).strip().replace('-->','- >')
        result.append(f'{n+1}\n{timestamp(beat["start_ms"])} --> {timestamp(beat["end_ms"])}\n{text}\n')
    return '\n'.join(result)
