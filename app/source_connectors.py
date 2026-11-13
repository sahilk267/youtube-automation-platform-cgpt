"""Opt-in allowlisted HTTPS RSS fetch (discovery only, never factual verification).

Registry is an operator-owned local JSON file. Unconfigured network access is disabled.
No arbitrary URL input, redirects, private IP literals or ambient proxy trust.
"""
import ipaddress,json,os,socket
from pathlib import Path
from urllib.parse import urlsplit
import httpx
from .intelligence import MAX_FEED_BYTES, parse_owner_rss


def registry():
    path=os.getenv('VIRALOS_APPROVED_FEEDS_FILE','').strip()
    if not path:return {}
    p=Path(path).resolve()
    if not p.is_file():return {}
    data=json.loads(p.read_text('utf-8'))
    if not isinstance(data,dict):raise ValueError('Feed registry must be JSON object')
    validated={}
    for key, entry in data.items():
        if not isinstance(key,str) or not isinstance(entry,dict) or not key.replace('_','').isalnum():continue
        url=entry.get('url',''); u=urlsplit(url)
        if u.scheme!='https' or not u.hostname or u.username or u.password or u.port not in (None,443):continue
        try:ipaddress.ip_address(u.hostname);continue
        except ValueError:pass
        validated[key]={'url':url,'name':str(entry.get('name',key))[:120],
                        'permission_reviewed':entry.get('permission_reviewed') is True,
                        'notes':str(entry.get('notes',''))[:240]}
    return validated


def assert_public_dns(host):
    # DNS preflight is defense-in-depth, not an assurance against DNS rebinding.
    resolved=socket.getaddrinfo(host,443,type=socket.SOCK_STREAM)
    if not resolved:raise ValueError('No public DNS response for configured source')
    for result in resolved:
        ip=ipaddress.ip_address(result[4][0])
        if not ip.is_global:raise ValueError('Feed resolved to a non-public address')


def fetch_approved(key):
    feeds=registry()
    if key not in feeds:raise ValueError('Feed not in local approved registry')
    entry=feeds[key]
    if not entry['permission_reviewed']:raise ValueError('Feed permission/ToS review must be recorded')
    url=entry['url'];host=urlsplit(url).hostname
    assert_public_dns(host)
    with httpx.Client(timeout=httpx.Timeout(12.0,connect=5),follow_redirects=False,trust_env=False) as c:
        with c.stream('GET',url,headers={'Accept':'application/rss+xml,application/atom+xml,application/xml,text/xml',
                                        'User-Agent':'ViralOS-LocalResearch/0.2 (+owner-provided contact not embedded)'}) as res:
            if res.status_code!=200:raise ValueError('Feed HTTP status '+str(res.status_code))
            content=bytearray()
            for piece in res.iter_bytes():
                content.extend(piece)
                if len(content)>MAX_FEED_BYTES:raise ValueError('Feed exceeds maximum safe size')
            xml=bytes(content).decode('utf-8-sig')
    return entry,parse_owner_rss(xml)
