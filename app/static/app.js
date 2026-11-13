const $=id=>document.getElementById(id);
let channelId='',projectId='',lastSource='';
const opts=(arr,id,label,choice)=>{let el=$(id);el.replaceChildren(new Option(choice||'Select…',''));arr.forEach(x=>el.add(new Option(label(x),x.channel_id||x.project_id)));};
async function request(url,method='GET',data){let init={method};if(data instanceof FormData)init.body=data;else if(data!==undefined){init.headers={'Content-Type':'application/json'};init.body=JSON.stringify(data);}let response=await fetch(url,init);let payload=await response.json();if(!response.ok)throw new Error(payload.detail||JSON.stringify(payload));return payload;}
function log(label,result){$('log').textContent=`${new Date().toLocaleTimeString()} • ${label}\n${typeof result==='string'?result:JSON.stringify(result,null,2)}\n\n`+$('log').textContent.slice(0,2600);}
async function safely(label,fn){try{let v=await fn();log(label,v);return v;}catch(err){log('ERROR: '+label,err.message);return null;}}
function obj(form){return Object.fromEntries(new FormData(form).entries());}
async function refresh(){let c=await request('/api/channels');let old=channelId;opts(c,'channels',x=>`${x.name} (${x.sport_id} / ${x.locale})`,'Select channel…');$('channels').value=old;if(!c.some(x=>x.channel_id===old))channelId='';let p=await request('/api/projects');let oldP=projectId;opts(p,'projects',x=>`${x.editorial_angle.slice(0,38)} (${x.status})`,'Select project…');$('projects').value=oldP;if(!p.some(x=>x.project_id===oldP))projectId='';if(projectId)await inspect();}
async function inspect(){if(!projectId)return;let x=await request('/api/projects/'+projectId),report=x.report;$('summary').textContent=`Status: ${x.project.status} • Research: ${report.research} • Unreviewed/unsupported: ${report.unsupported_claims.length} • Unlinked claims: ${report.claims_missing_script_links.length} • Scenes: ${report.scenes} • Voice: ${report.has_narration?'Imported':'MISSING'} • Publish ready: NO`;
$('claims').replaceChildren();let sl=$('script-claim');sl.replaceChildren(new Option('No claim link for this script',''));x.claims.forEach(z=>sl.add(new Option(z.proposition.slice(0,72),z.claim_id)));x.claims.forEach(c=>{let card=document.createElement('div');card.className='claim';let desc=document.createElement('div');desc.textContent=c.proposition;card.append(desc);let tag=document.createElement('small');tag.textContent=`${c.verification_status} • ${c.claim_id}`;card.append(tag);if(c.verification_status==='UNREVIEWED'){let btn=document.createElement('button');btn.textContent='Record human review';btn.onclick=async()=>{let explanation=prompt('Evidence review explanation (12+ characters). Do not click until you personally verified the claim.');if(!explanation)return;let v=await safely('review',()=>request('/api/claims/'+c.claim_id+'/review','POST',{status:'SUPPORTED',reviewer:'local-owner',explanation}));if(v)inspect();};card.append(btn);} $('claims').append(card);});
if(x.scenes.length){let container=document.createElement('div');x.scenes.forEach(s=>{let v=document.createElement('div');v.className='scene';v.textContent=`${s.order_index+1}. ${s.spec.text} (${s.spec.duration_seconds}s)`;container.append(v);});$('summary').append(container);}
$('preview').replaceChildren();if(x.renders.length){let label=document.createElement('p');label.className='small';label.textContent='Technical preview only — no owner full watch-through or publishing approval';$('preview').append(label);let a=document.createElement('a');a.textContent='Open latest video preview';a.style.color='#78ddbf';let job=await request('/api/jobs');let found=job.find(j=>JSON.parse(j.progress_json||'{}').render_attempt_id===x.renders[0].render_attempt_id);if(found){a.href='/api/previews/'+x.renders[0].render_attempt_id;a.target='_blank';$('preview').append(a);let v=document.createElement('video');v.controls=true;v.src=a.href;$('preview').append(v);}}}
$('channel-form').addEventListener('submit',async e=>{e.preventDefault();let x=await safely('create channel',()=>request('/api/channels','POST',obj(e.target)));if(x){channelId=x.channel_id;await refresh();}});
$('project-form').addEventListener('submit',async e=>{e.preventDefault();if(!channelId)return log('BLOCKED','Select a channel first');let x=await safely('create project',()=>request('/api/projects','POST',{...obj(e.target),channel_id:channelId}));if(x){projectId=x.project_id;await refresh();}});
$('source-form').addEventListener('submit',async e=>{e.preventDefault();if(!projectId)return log('BLOCKED','Select project');let v=await safely('record manual source',()=>request(`/api/projects/${projectId}/sources`,'POST',obj(e.target)));if(v){lastSource=v.source_version_id;$('source-id').textContent=lastSource;$('source-input').value=lastSource;inspect();}});
$('claim-form').addEventListener('submit',async e=>{e.preventDefault();if(!projectId)return log('BLOCKED','Select project');let v=await safely('record claim',()=>request(`/api/projects/${projectId}/claims`,'POST',{...obj(e.target),relation:'SUPPORTS'}));if(v)inspect();});
$('script-form').addEventListener('submit',async e=>{e.preventDefault();if(!projectId)return log('BLOCKED','Select project');let v=await safely('save manual script',()=>request(`/api/projects/${projectId}/script`,'POST',{text:obj(e.target).text,claim_links:($('script-claim').value&&obj(e.target).exact_quote)?[{claim_id:$('script-claim').value,exact_quote:obj(e.target).exact_quote}]:[]}));if(v)inspect();});
$('scene-form').addEventListener('submit',async e=>{e.preventDefault();if(!projectId)return log('BLOCKED','Select project');let f=obj(e.target);let v=await safely('add scene',()=>request(`/api/projects/${projectId}/scenes`,'POST',{text:f.text,duration_seconds:Number(f.duration_seconds),claim_ids:f.claim_ids.split(',').map(s=>s.trim()).filter(Boolean)}));if(v)inspect();});
$('voice-form').addEventListener('submit',async e=>{e.preventDefault();if(!projectId)return log('BLOCKED','Select project');let v=await safely('voice import',()=>request(`/api/projects/${projectId}/voice`,'POST',new FormData(e.target)));if(v)inspect();});
$('channels').addEventListener('change',e=>channelId=e.target.value);
$('projects').addEventListener('change',e=>{projectId=e.target.value;inspect();});
$('queue').onclick=async()=>{if(!projectId)return log('BLOCKED','Select project');await safely('queue preview',()=>request(`/api/projects/${projectId}/queue-preview`,'POST'));};
$('run').onclick=async()=>{await safely('run worker',()=>request('/api/jobs/run-next','POST'));if(projectId)inspect();};
request('/api/capabilities').then(c=>{$('capabilities').replaceChildren();['CPU available',`FFmpeg ${c.ffmpeg?'installed':'MISSING'}`,'No GPU required','PUBLIC publishing disabled','Human evidence review'].forEach(t=>{let x=document.createElement('span');x.className='pill';x.textContent=t;$('capabilities').append(x);});});
refresh().catch(err=>log('Initialize error',err.message));

// M1–M3 development extensions. No external upload, no implicit factual verification.
const needProject=()=>{if(!projectId){log('BLOCKED','Select project first');return false;}return true;};
$('audit-research').onclick=async()=>{if(!needProject())return;await safely('source/evidence audit',()=>request(`/api/projects/${projectId}/research-audit`));};
$('rss-form').addEventListener('submit',async e=>{e.preventDefault();if(!needProject())return;await safely('parse owner RSS',()=>request(`/api/projects/${projectId}/rss-import`,'POST',obj(e.target)));});
$('plan-story').onclick=async()=>{if(!needProject())return;await safely('timed story plan',()=>request(`/api/projects/${projectId}/story-plan`,'POST',{}));};
$('caption-base').onclick=()=>{if(!needProject())return;window.open(`/api/projects/${projectId}/captions/${$('channel-form').elements.locale.value || 'hi-IN'}`,'_blank','noopener');};
$('locale-form').addEventListener('submit',async e=>{e.preventDefault();if(!needProject())return;let b=obj(e.target);await safely('localized on-screen text',()=>request(`/api/projects/${projectId}/locales`,'POST',{locale:b.locale,localized_scenes:b.localized_scenes.split('\n').map(x=>x.trim()).filter(Boolean),owner_checked:$('locale-form').elements.owner_checked.checked}));});
$('review-form').addEventListener('submit',async e=>{e.preventDefault();if(!needProject())return;let data=await safely('project state',()=>request(`/api/projects/${projectId}`));if(!data||!data.renders.length)return log('BLOCKED','Render a preview first');let b=obj(e.target);await safely('private preview review',()=>request(`/api/projects/${projectId}/review-video`,'POST',{render_attempt_id:data.renders[0].render_attempt_id,reviewer:b.reviewer,notes:b.notes,rights_attested:!!b.rights_attested,claims_attested:!!b.claims_attested,watched_full_video:!!b.watched_full_video}));});
$('export-private').onclick=async()=>{if(!needProject())return;let x=await safely('private review ZIP',()=>request(`/api/projects/${projectId}/export-review-packet`,'POST',{}));if(x){let a=document.createElement('a');a.href=x.download_url;a.textContent='Download private review ZIP (NOT publish ready)';a.style.color='#78ddbf';a.download='ViralOS_Private_Review_Packet.zip';$('preview').append(a);}};
$('analytics-form').addEventListener('submit',async e=>{e.preventDefault();if(!channelId)return log('BLOCKED','Select channel');let b=obj(e.target);await safely('owner-entered analytics',()=>request('/api/analytics/owner-entry','POST',{channel_id:channelId,report_date:b.report_date,format:b.format,views:Number(b.views),watch_hours:b.watch_hours?Number(b.watch_hours):null}));});
$('analytics-view').onclick=async()=>{if(!channelId)return log('BLOCKED','Select channel');await safely('owner observations',()=>request(`/api/analytics/${channelId}`));};
$('analytics-form').elements.report_date.value = new Date().toISOString().slice(0,10);


// M2 Studio v0.3: operator-authored typed timeline and real CPU-rendered preview.
$('studio-example').onclick=async()=>{if(!needProject())return;let v=await safely('Studio example timeline',()=>request(`/api/projects/${projectId}/studio/example`));if(v)$('studio-json').value=JSON.stringify(v,null,2);};
$('studio-plan-form').addEventListener('submit',async e=>{e.preventDefault();if(!needProject())return;let b;try{b=JSON.parse($('studio-json').value);}catch(err){return log('INVALID JSON',err.message);}await safely('save typed Studio plan',()=>request(`/api/projects/${projectId}/studio/plans`,'POST',b));});
$('studio-queue').onclick=async()=>{if(!needProject())return;await safely('queue M2 Studio',()=>request(`/api/projects/${projectId}/studio/queue`,'POST',{}));};
$('studio-run').onclick=async()=>{let result=await safely('M2 Studio CPU render',()=>request('/api/studio/run-next','POST',{}));if(!result||result.state!=='SUCCEEDED')return;let holder=$('studio-result');holder.replaceChildren();let p=document.createElement('p');p.textContent='Technical Studio preview (NOT PUBLISH READY)';holder.append(p);let a=document.createElement('a');a.href=result.preview_url;a.target='_blank';a.rel='noopener';a.textContent='Open MP4';a.style.color='#7cdeb9';holder.append(a);let v=document.createElement('video');v.controls=true;v.src=result.preview_url;holder.append(v);let b=document.createElement('button');b.type='button';b.textContent='View detailed QC report';b.className='outline';b.onclick=async()=>await safely('Studio technical QC',()=>request(result.report_url));holder.append(b);};
for(const [id,kind] of [['studio-still-form','still'],['studio-music-form','music']]){
  $(id).addEventListener('submit',async e=>{e.preventDefault();if(!needProject())return;let body=new FormData(e.target);let v=await safely('owner-approved '+kind,()=>request(`/api/projects/${projectId}/studio/assets/${kind}`,'POST',body));if(v)log('Copy asset_id into your Studio plan',v.asset_id);});
}


// M2.1: deterministic creative draft + measured per-shot narration (NO auto translation/ASR).
let directorDraftId=null;
function showDirectorSegments(data){
  const holder=$('director-segments');holder.replaceChildren();
  let intro=document.createElement('p');intro.textContent=`Draft ${data.draft_id}: ${data.segments.length} narration segments. Record each sentence and upload WAV or use configured Piper.`;holder.append(intro);
  data.segments.forEach((seg,i)=>{
    let panel=document.createElement('div');panel.className='scene';
    let text=document.createElement('p');text.textContent=`${i+1}. ${typeof seg==='string'?seg:seg.text}`;panel.append(text);
    let file=document.createElement('input');file.type='file';file.accept='.wav,audio/wav';file.setAttribute('aria-label',`Narration WAV for scene ${i+1}`);
    let btn=document.createElement('button');btn.type='button';btn.textContent=`Upload scene ${i+1} WAV`;btn.className='outline';
    btn.onclick=async()=>{
      if(!file.files||!file.files[0]){log('BLOCKED',`Select narration WAV for scene ${i+1}`);return;}
      let form=new FormData();form.append('file',file.files[0]);
      let response=await safely('Voice segment '+(i+1),()=>request(`/api/projects/${projectId}/director/drafts/${directorDraftId}/voice/${i}`,'POST',form));
      if(response){btn.textContent=`Scene ${i+1}: measured ${response.duration_ms} ms`;}
    };panel.append(file,btn);holder.append(panel);
  });
}
$('director-draft-form').addEventListener('submit',async e=>{
  e.preventDefault();if(!needProject())return;
  let f=e.target;let values=obj(f);
  let payload={locale:values.locale,locale_reviewed:f.elements.locale_reviewed.checked};
  if(values.translated_script.trim())payload.translated_script=values.translated_script.trim();
  let x=await safely('M2.1 creative draft',()=>request(`/api/projects/${projectId}/director/drafts`,'POST',payload));
  if(x){directorDraftId=x.draft_id;showDirectorSegments(x);}
});
$('director-piper').onclick=async()=>{
  if(!directorDraftId||!needProject())return log('BLOCKED','Generate a Director draft first');
  let x=await safely('Local Piper segments',()=>request(`/api/projects/${projectId}/director/drafts/${directorDraftId}/synthesize-piper`,'POST',{}));
  if(x)log('Piper segments created: human pronunciation check still required',x.generated_segments);
};
$('director-assemble').onclick=async()=>{
  if(!directorDraftId||!needProject())return log('BLOCKED','Generate a Director draft first');
  let x=await safely('Measured M2.1 assembly',()=>request(`/api/projects/${projectId}/director/drafts/${directorDraftId}/assemble`,'POST',{}));
  if(x){log('Director timeline ready: queue it through M2 Studio',x);$('studio-json').value=JSON.stringify((await request(`/api/projects/${projectId}/studio/plan`)).plan,null,2);}
};
$('projects').addEventListener('change',async()=>{directorDraftId=null;$('director-segments').textContent='Generate a new draft for this project.';if(!projectId)return;try{let x=await request(`/api/projects/${projectId}`);$('director-locale').value=x.project.locale;}catch(e){log('Locale load',e.message);}});

// M2.2: objective creative audit, explicit human review and original final export.
let latestM22RenderId=null, latestM22ReviewId=null, latestM22ExportId=null, latestPrivateIntentId=null;
async function getM22Render(){
  if(!needProject())return null;
  const arr=await request(`/api/projects/${projectId}/studio/renders`);
  if(!arr.length)throw new Error('No Studio MP4 preview yet: create M2.1 plan, then render through M2 Studio');
  latestM22RenderId=arr[0].studio_render_id;return latestM22RenderId;
}
$('m22-policies').onclick=async()=>await safely('domain creative policies',()=>request('/api/m22/creative-policies'));
$('m22-audit').onclick=async()=>{
  if(!needProject())return;
  await safely('creative QA audit',async()=>request(`/api/projects/${projectId}/m22/creative-audit/${await getM22Render()}`));
};
$('m22-review-form').addEventListener('submit',async e=>{
  e.preventDefault();if(!needProject())return;
  const b=obj(e.target);
  const payload={reviewer:b.reviewer,notes:b.notes,watched_full_video:!!b.watched_full_video,
    original_or_rights_reviewed:!!b.original_or_rights_reviewed,facts_sources_reviewed:!!b.facts_sources_reviewed,
    narration_and_captions_reviewed:!!b.narration_and_captions_reviewed};
  const result=await safely('human final Studio review',async()=>request(`/api/projects/${projectId}/m22/studio/renders/${await getM22Render()}/review-final`,'POST',payload));
  if(result){latestM22ReviewId=result.review_id;$('m22-result').textContent='Full-video owner approval recorded. Export final MP4 to continue.';}
});
$('m22-export').onclick=async()=>{
  if(!needProject()||!latestM22ReviewId)return log('BLOCKED','Complete M2.2 full-video approval first');
  const result=await safely('owner reviewed final MP4',()=>request(`/api/projects/${projectId}/m22/reviews/${latestM22ReviewId}/export-final`,'POST',{}));
  if(result){latestM22ExportId=result.export_id;const box=$('m22-result');box.replaceChildren();
    const a=document.createElement('a');a.href=result.download_url||`/api/m22/final-exports/${result.export_id}/download`;
    a.textContent='Download owner-reviewed final MP4';a.style.color='#8addc3';a.target='_blank';a.rel='noopener';box.append(a);
    const p=document.createElement('p');p.textContent='YouTube monetization/copyright approval remains unverified.';box.append(p);
  }
};
$('m3-private-form').addEventListener('submit',async e=>{
  e.preventDefault();if(!latestM22ExportId)return log('BLOCKED','Create owner-reviewed final MP4 first');
  const b=obj(e.target);
  const payload={export_id:latestM22ExportId,title:b.title,description:b.description,
    tags:b.tags.split(',').map(x=>x.trim()).filter(Boolean),altered_content:!!b.altered_content,
    made_for_kids:!!b.made_for_kids,owner_confirmed_metadata_rights:!!b.owner_confirmed_metadata_rights};
  const result=await safely('prepare PRIVATE upload',()=>request('/api/m3/private-upload/intents','POST',payload));
  if(result){latestPrivateIntentId=result.intent_id;$('m3-result').textContent='PRIVATE upload prepared, not sent. Confirm separately to execute.';}
});
$('m3-execute').onclick=async()=>{
  if(!latestPrivateIntentId)return log('BLOCKED','Prepare an upload intent first');
  if(!window.confirm('This will send the approved MP4 to your linked YouTube channel as PRIVATE. Continue?'))return;
  const typed=window.prompt('To authorize this PRIVATE upload, type exactly: UPLOAD_PRIVATE_NOW');
  if(typed!=='UPLOAD_PRIVATE_NOW')return log('BLOCKED','Confirmation did not match');
  const r=await safely('PRIVATE YouTube upload',()=>request(`/api/m3/private-upload/intents/${latestPrivateIntentId}/execute`,'POST',{confirmation:typed}));
  $('m3-result').textContent=r?.state==='UPLOADED_PRIVATE'?'Uploaded as PRIVATE: '+r.video_id:'Check YouTube Studio. Never retry a remote-unknown upload blindly.';
};
$('projects').addEventListener('change',()=>{latestM22RenderId=null;latestM22ReviewId=null;latestM22ExportId=null;latestPrivateIntentId=null;
  $('m22-result').textContent='No final export has been created for this project.';
  $('m3-result').textContent='PRIVATE upload requires fresh per-project approval.';});

// M2.3 / M3.1: optional workbench helpers. Never start external account access by default.
let m23Edges=[],m23DraftId=null,m23EvidenceAssetId=null;
$('m23-load-edges').onclick=async()=>{
  if(!needProject())return;
  let list=await safely('source/locator edges',()=>request(`/api/projects/${projectId}/m23/evidence-edges`));
  if(!list)return;
  m23Edges=list;
  let choice=$('m23-edges');choice.replaceChildren(new Option('Select an evidence link…',''));
  list.forEach(x=>choice.add(new Option(`${x.verification_status} • ${x.proposition.slice(0,55)} (${x.locator})`,x.evidence_edge_id)));
};
$('m23-edge-review').addEventListener('submit',async e=>{
  e.preventDefault();if(!needProject())return;
  let selected=$('m23-edges').value;if(!selected)return log('BLOCKED','Select an evidence link first');
  let data=obj(e.target);
  let result=await safely('manual source/locator review',()=>request(`/api/projects/${projectId}/m23/evidence-edges/${selected}/review`,'POST',
    {reviewer:data.reviewer,explanation:data.explanation,source_and_locator_checked:!!data.source_and_locator_checked}));
  if(result)await $('m23-load-edges').onclick();
});
$('m23-generate-card').onclick=async()=>{
  if(!needProject())return;
  let edge=m23Edges.find(e=>e.evidence_edge_id===$('m23-edges').value);
  if(!edge)return log('BLOCKED','Select a valid supporting evidence link');
  if(!confirm('Have you checked this claim, source attribution and the right to use an original text card?'))return;
  let data=await safely('original evidence graphic',()=>request(`/api/projects/${projectId}/m23/evidence-cards`,'POST',
     {claim_id:edge.claim_id,source_version_id:edge.source_version_id,attribution_and_rights_reviewed:true}));
  if(!data)return;
  m23EvidenceAssetId=data.asset_id;
  const holder=$('m23-evidence-result');holder.replaceChildren();
  const para=document.createElement('p');para.textContent='Created asset_id: '+data.asset_id+' • Owner reviewed, not independently verified.';holder.append(para);
  const image=document.createElement('img');image.src=`/api/projects/${projectId}/m23/evidence-cards/${data.asset_id}/image`;
  image.alt='Owner-reviewed original evidence graphic';image.style.maxWidth='100%';image.style.borderRadius='10px';holder.append(image);
  const btn=document.createElement('button');btn.type='button';btn.className='outline';btn.textContent='Insert as editable image overlay in Studio JSON';
  btn.onclick=()=>{
    try{
      const plan=JSON.parse($('studio-json').value);
      let target=plan.shots.find(s=>s.role==='EVIDENCE')||plan.shots[1];if(!target)throw Error('Load a Studio plan first');
      let start=100,end=Math.min(target.duration_ms-80,1500);if(end<start+150)throw Error('Shot too short');
      const anchors=['LOWER_THIRD','CENTER','TOP'];
      const anchor=anchors.find(a=>!(target.overlays||[]).some(o=>o.anchor===a&&o.start_ms<end&&start<o.end_ms));
      if(!anchor)throw Error('No non-overlapping overlay anchor; edit timing manually');
      target.overlays=target.overlays||[];
      target.overlays.push({text:'Reviewed source context',start_ms:start,end_ms:end,anchor,style:'IMAGE_INSERT',image_asset_id:data.asset_id});
      $('studio-json').value=JSON.stringify(plan,null,2);
      log('Evidence insert draft','Review text/timing and then save Studio plan. Prior audio-bound plan must be reassembled/relinked if you changed its revision.');
    }catch(err){log('Evidence Studio insertion',err.message);}
  };holder.append(btn);
};
$('m23-asr').onclick=async()=>{
  if(!needProject())return;
  let raw=await safely('current Studio plan',()=>request(`/api/projects/${projectId}/studio/plan`));if(!raw)return;
  let result=await safely('offline word-timing proposal',()=>request(`/api/projects/${projectId}/m23/plans/${raw.plan_id}/asr-proposal`,'POST',{}));
  if(result){m23DraftId=result.draft_id;let words=result.words;
    if(!words){let detail=await request(`/api/projects/${projectId}/m23/alignment-drafts/${m23DraftId}`);words=detail.words;}
    $('m23-words').value=JSON.stringify(words,null,2);$('m23-checked').checked=false;
    log('Review ASR draft',result.transcript_matches?'Exact transcript sequence matched; timings STILL require listening':'ASR transcript mismatch; correct every word and timing before approval');
  }
};
$('m23-approve').onclick=async()=>{
  if(!needProject()||!m23DraftId)return log('BLOCKED','Generate a timing proposal first');
  let words;try{words=JSON.parse($('m23-words').value);}catch(err){return log('INVALID WORD JSON',err.message);}
  await safely('owner-reviewed captions',()=>request(`/api/projects/${projectId}/m23/alignment-drafts/${m23DraftId}/approve`,'POST',
    {owner_checked_audio_and_words:$('m23-checked').checked,words}));
};
$('m23-locale').onclick=async()=>{
  if(!needProject())return;
  let x=await safely('Studio plan',()=>request(`/api/projects/${projectId}/studio/plan`));
  if(x)await safely('locale/narration review',()=>request(`/api/projects/${projectId}/m23/plans/${x.plan_id}/locale-audit`));
};
$('m31-revenue').addEventListener('submit',async e=>{
  e.preventDefault();if(!channelId)return log('BLOCKED','Select a channel');
  const values=obj(e.target);await safely('owner-authorized monetary sync',()=>request('/api/m31/monetary/sync','POST',
      {channel_id:channelId,start_date:values.start_date,end_date:values.end_date,
       currency:values.currency,owner_authorized_sync:!!values.owner_authorized_sync}));
});
$('m31-earnings').onclick=async()=>{
  if(!channelId)return log('BLOCKED','Select channel');
  const result=await safely('verified-account revenue estimates',()=>request(`/api/m31/channels/${channelId}/earnings`));
  if(result)$('m31-observed').textContent=JSON.stringify(result,null,2);
};
$('m31-retention').addEventListener('submit',async e=>{
  e.preventDefault();let f=obj(e.target);
  const result=await safely('owner authorized retention sample',()=>request('/api/m31/retention/sync','POST',
      {export_id:f.export_id,start_date:f.start_date,end_date:f.end_date,owner_authorized_sync:!!f.owner_authorized_sync}));
  if(result)$('m31-observed').textContent=JSON.stringify(result.report,null,2);
});
$('m31-reconcile').addEventListener('submit',async e=>{
  e.preventDefault();const b=obj(e.target);
  if(!window.confirm('You personally verified the uploaded PRIVATE video in YouTube Studio? No new upload will occur.'))return;
  await safely('REMOTE_UNKNOWN verification',()=>request(`/api/m31/private-upload/intents/${b.intent_id}/reconcile`,'POST',
    {remote_video_id:b.remote_video_id,owner_checked_studio_video_matches:!!b.owner_checked_studio_video_matches,
     confirmation:'RECONCILE_EXISTING_PRIVATE_VIDEO_ONLY'}));
});
$('projects').addEventListener('change',()=>{m23Edges=[];m23DraftId=null;m23EvidenceAssetId=null;
  $('m23-words').value='';$('m23-evidence-result').textContent='Select a source, review it, then generate a new evidence card.';
  $('m23-edges').replaceChildren(new Option('Select an evidence link…',''));
});

// M2.4 / M3.2: these controls cannot auto-publish or silently download models.
let selectedM24VariantId=null;
$('m24-variant-form').addEventListener('submit',async e=>{
  e.preventDefault();if(!needProject())return;const b=obj(e.target);
  const response=await safely('reviewed language variant',()=>request(`/api/projects/${projectId}/m24/variants`,'POST',{
    locale:b.locale,reviewed_script:b.reviewed_script,reviewer:b.reviewer,regional_notes:b.regional_notes,
    words_names_numbers_and_meaning_reviewed:!!b.words_names_numbers_and_meaning_reviewed,
    on_screen_language_reviewed:!!b.on_screen_language_reviewed}));
  if(!response)return;selectedM24VariantId=response.variant_id;
  const detail=await safely('locale scene list',()=>request(`/api/projects/${projectId}/m24/variants/${selectedM24VariantId}`));
  if(!detail)return;
  let box=$('m24-segments');box.replaceChildren();
  const title=document.createElement('p');title.textContent=`${detail.locale} · ${detail.segments.length} segments. Record one WAV per segment.`;box.append(title);
  detail.segments.forEach(segment=>{
    let row=document.createElement('div');row.className='scene';
    let label=document.createElement('p');label.textContent=`${segment.index+1}: ${segment.text}`;row.append(label);
    const picker=document.createElement('input');picker.type='file';picker.accept='.wav,audio/wav';row.append(picker);
    const button=document.createElement('button');button.type='button';button.className='outline';button.textContent='Upload this voice segment';
    button.onclick=async()=>{if(!picker.files[0])return log('BLOCKED','Select a WAV');
      const data=new FormData();data.append('file',picker.files[0]);
      await safely('localized voice segment',()=>request(`/api/projects/${projectId}/m24/variants/${selectedM24VariantId}/voice/${segment.index}`,'POST',data));
    };row.append(button);box.append(row);
  });
});
$('m24-synthesize').onclick=async()=>{
  if(!selectedM24VariantId)return log('BLOCKED','Create reviewed locale variant first');
  if(!window.confirm('Only use a locally installed, legally reviewed model matching the locale. Pronunciation and voice still need listening review. Continue?'))return;
  await safely('opt-in offline voice',()=>request(`/api/projects/${projectId}/m24/variants/${selectedM24VariantId}/synthesize-piper`,'POST',{
    owner_approved_model_license:true,owner_approved_pronunciation:true}));
};
$('m24-render').onclick=async()=>{
  if(!selectedM24VariantId||!needProject())return log('BLOCKED','Create reviewed locale variant first');
  const x=await safely('localized technical preview',()=>request(`/api/projects/${projectId}/m24/variants/${selectedM24VariantId}/render`,'POST',{}));
  if(x){const div=$('m24-segments');const p=document.createElement('p');p.textContent='TECHNICAL PREVIEW ONLY — full listen/watch required.';div.append(p);
    const a=document.createElement('a');a.href=x.preview_url;a.target='_blank';a.rel='noopener';a.textContent=`Open ${x.locale} MP4`;div.append(a);
    const b=document.createElement('a');b.href=x.captions_url;b.target='_blank';b.rel='noopener';b.textContent=' · Get captions (.srt)';div.append(b);}
};
$('m32-preflight').onclick=async()=>{
  if(!latestM22ExportId)return log('BLOCKED','Create and human-review M2.2 final export first');
  const remote=$('m32-live').checked;
  const result=await safely('M3.2 non-destructive acceptance',()=>request('/api/m32/acceptance/preflight','POST',{
    export_id:latestM22ExportId,
    owner_confirmed_local_video_and_rights:$('m32-owner-local').checked,
    owner_confirmed_target_channel:$('m32-owner-channel').checked,
    perform_remote_read_only_check:remote,owner_consented_network_access:remote}));
  if(result)$('m32-result').textContent=JSON.stringify({status:result.status,blockers:result.blockers,remote_upload_verified:result.remote_upload_verified});
};
$('projects').addEventListener('change',()=>{selectedM24VariantId=null;
  $('m24-segments').textContent='Choose a project and create a variant first.';
  $('m32-result').textContent='New project: acceptance not checked.';});
