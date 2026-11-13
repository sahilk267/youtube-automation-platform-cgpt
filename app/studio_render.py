"""CPU-only M2 scene compositor: original diagram/still + timed layers + owner timing.
No downloaded fonts/models, no automatic sourcing, no fabricated speech alignment.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageStat
import hashlib, json, math, os, shutil, subprocess, wave, array

FPS=20
SHORT=(540,960)
LONG=(960,540)
BG=(12,25,40,255)
ACCENT=(88,212,172,255)


def font_file(locale):
    import shutil as _shutil
    paths=[]
    if locale.startswith('hi'):
        paths += ['C:/Windows/Fonts/Nirmala.ttf','/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf']
    paths += ['C:/Windows/Fonts/arial.ttf','C:/Windows/Fonts/segoeui.ttf',
              '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']
    for p in paths:
        if Path(p).is_file():return p
    if os.name!='nt':
        q=subprocess.run(['fc-match','-f','%{file}', 'Noto Sans Devanagari' if locale.startswith('hi') else 'DejaVu Sans'],capture_output=True,text=True)
        if q.returncode==0 and Path(q.stdout.strip()).is_file():return q.stdout.strip()
    raise RuntimeError('No suitable font installed; install a locale-compatible font')


def font(locale, size):return ImageFont.truetype(font_file(locale),size)


def wrap(draw, text, fnt, width, limit=5):
    words=text.split(); result=[];line=''
    for word in words:
        trial=(line+' '+word).strip()
        if line and draw.textbbox((0,0),trial,font=fnt)[2]>width:
            result.append(line);line=word
        else:line=trial
    if line:result.append(line)
    if len(result)>limit or any(draw.textbbox((0,0),s,font=fnt)[2]>width for s in result):
        raise ValueError('Text cannot fit safe area; shorten text or split shot')
    return result


def rounded_text(text,locale,size,maxwidth,kind='label'):
    """Return an independent alpha text card with native-script font fallback."""
    f=font(locale,size); margin=int(size*.72)
    temp=Image.new('RGBA',(maxwidth,max(size*9,80)),(0,0,0,0));d=ImageDraw.Draw(temp)
    lines=wrap(d,text,f,maxwidth-margin*2,4)
    lineh=int(size*1.32);w=max(int(d.textbbox((0,0),line,font=f)[2]) for line in lines)+margin*2
    h=lineh*len(lines)+margin*2
    img=Image.new('RGBA',(min(maxwidth,w),h),(0,0,0,0));draw=ImageDraw.Draw(img)
    fill=(7,18,30,228) if kind!='caption' else (5,10,20,224)
    draw.rounded_rectangle((0,0,img.width-1,h-1),radius=max(10,int(size*.35)),fill=fill,
                           outline=(111,227,194,230) if kind=='stat' else (51,76,95,200),width=2)
    y=margin
    for l in lines:
        draw.text((margin,y),l,font=f,fill=(255,255,255,255),stroke_width=0)
        y+=lineh
    return img


def base_frame(shot,fmt,domain,assets,locale,release=False):
    w,h=SHORT if fmt=='SHORT' else LONG
    kind=shot['visual']['kind'];img=Image.new('RGBA',(w,h),BG)
    if kind=='RIGHTS_APPROVED_STILL':
        asset=assets[shot['visual']['asset_id']]
        src=Image.open(asset['path']);src.load();src=ImageOps.exif_transpose(src).convert('RGB')
        # Original cited evidence cards must remain fully visible; cropping can
        # remove the exact source attribution. Other approved stills keep cover-fit.
        if asset.get('origin','').startswith('ViralOS ORIGINAL TEXT GRAPHIC'):
            fitted=ImageOps.contain(src,(int(w*.93),int(h*.63)),method=Image.Resampling.LANCZOS)
            canvas=Image.new('RGB',(w,h),BG[:3])
            canvas.paste(fitted,((w-fitted.width)//2,(h-fitted.height)//2))
            img=canvas.convert('RGBA')
        else:
            fitted=ImageOps.fit(src,(w,h),method=Image.Resampling.LANCZOS)
            img=Image.blend(Image.new('RGB',(w,h),BG[:3]),fitted,0.57).convert('RGBA')
    d=ImageDraw.Draw(img,'RGBA')
    # Expressive original sport visualization; never represents actual tracked match data.
    if kind=='ORIGINAL_DIAGRAM':
        left,right=int(w*.13),int(w*.87)
        top,bottom=int(h*.29),int(h*.70)
        if domain=='cricket':
            d.ellipse((left,top,right,bottom),fill=(12,67,53,255),outline=(113,179,152,245),width=3)
            d.rectangle((int(w*.468),int(h*.36),int(w*.532),int(h*.63)),fill=(156,125,84,235))
            for px,py in [(0.2,.49),(.78,.46),(.65,.32),(.33,.64),(.4,.37),(.64,.62)]:
                x,y=int(w*px),int(h*py);d.ellipse((x-8,y-8,x+8,y+8),fill=(244,209,118,245))
            d.line((int(w*.50),int(h*.51),int(w*.70),int(h*.36)),fill=(252,221,139,255),width=5)
        elif domain=='nfl':
            d.rounded_rectangle((left,top,right,bottom),radius=15,fill=(17,62,63,255),outline=(126,188,190,245),width=3)
            for i in range(1,9):
                x=left+int((right-left)*i/9);d.line((x,top+8,x,bottom-8),fill=(112,164,167,180),width=2)
            for px,py in [(.23,.51),(.34,.49),(.44,.54),(.65,.44),(.73,.54)]:
                x,y=int(w*px),int(h*py);d.ellipse((x-8,y-8,x+8,y+8),fill=(244,215,121,255))
            d.line((int(w*.33),int(h*.53),int(w*.69),int(h*.40)),fill=(244,215,121,255),width=5)
        else:
            for i in range(4):
                d.rounded_rectangle((int(w*(.16+i*.075)),int(h*(.42-i*.05)),int(w*(.25+i*.075)),int(h*.67)),radius=8,fill=(36,90+i*14,109+i*10,230))
    # Quiet brand system; title and overlay remain distinct timed layers.
    d.rounded_rectangle((int(w*.06),int(h*.04),int(w*.14),int(h*.05)),radius=3,fill=ACCENT)
    f=font(locale,max(13,int(w*.027)))
    if locale.startswith('hi'):
        # The Devanagari font need not contain Latin glyphs; render brand independently.
        d.text((int(w*.06),int(h*.075)),'VIRALOS',font=font('en-US',max(13,int(w*.027))),fill=(213,242,232,255))
        d.text((int(w*.27),int(h*.075)),'मूल विश्लेषण',font=f,fill=(213,242,232,255))
        role={'HOOK':'शुरुआत','CONTEXT':'संदर्भ','EVIDENCE':'साक्ष्य','EXPLANATION':'व्याख्या','PAYOFF':'निष्कर्ष','CTA':'अगला कदम'}.get(shot['role'],'व्याख्या')
        d.text((int(w*.06),int(h*.13)),role,font=f,fill=(129,225,197,255))
    else:
        d.text((int(w*.06),int(h*.075)),'VIRALOS  |  ORIGINAL EXPLAINER',font=f,fill=(213,242,232,255))
        d.text((int(w*.06),int(h*.13)),shot['role'],font=f,fill=(129,225,197,255))
    d.line((int(w*.06),int(h*.91),int(w*.94),int(h*.91)),fill=(77,113,132,255),width=2)
    disclaimer=('OWNER-ATTESTED STILL  •  NOT MATCH FOOTAGE' if kind=='RIGHTS_APPROVED_STILL'
                else 'ILLUSTRATIVE DIAGRAM  •  NOT MATCH FOOTAGE')
    if locale.startswith('hi'):
        disclaimer='स्वीकृत चित्र  •  असली मैच नहीं' if kind=='RIGHTS_APPROVED_STILL' else 'उदाहरण चित्र  •  असली मैच नहीं'
    fsmall=font(locale,max(11,int(w*.020)))
    d.text((int(w*.06),int(h*.917)),disclaimer,font=fsmall,fill=(215,229,236,255))
    if not release:
        d.text((int(w*.06),int(h*.952)),('तकनीकी पूर्वावलोकन  •  प्रकाशित न करें' if locale.startswith('hi') else 'TECHNICAL STUDIO PREVIEW  •  NOT PUBLISH READY'),font=fsmall,fill=(255,202,149,255))
    return img


def animate_tactical_motion(canvas,shot,domain,local_ms):
    """Original, clearly illustrative moving marker; never real player tracking."""
    if (shot['visual']['kind']!='ORIGINAL_DIAGRAM' or
            shot['visual'].get('motion','STATIC')!='ILLUSTRATIVE_ROUTE'):
        return
    w,h=canvas.size
    if domain=='cricket':
        points=[(0.50,0.51),(0.55,0.47),(0.63,0.41),(0.70,0.36)]
    elif domain=='nfl':
        points=[(0.33,0.53),(0.45,0.49),(0.56,0.45),(0.69,0.40)]
    else:
        return
    # Progress is bounded by the shot's actual duration, not an invented game clock.
    phase=max(0.0,min(1.0,local_ms/max(1,shot['duration_ms'])))
    d=ImageDraw.Draw(canvas,'RGBA')
    for i in range(len(points)-1):
        start=points[i];end=points[i+1]
        d.line((int(w*start[0]),int(h*start[1]),int(w*end[0]),int(h*end[1])),
               fill=(220,240,213,110),width=max(2,int(w*.004)))
    progress=phase*(len(points)-1)
    idx=min(len(points)-2,int(progress));mix=progress-idx
    x=round(w*(points[idx][0]*(1-mix)+points[idx+1][0]*mix))
    y=round(h*(points[idx][1]*(1-mix)+points[idx+1][1]*mix))
    radius=max(6,int(w*.015))
    d.ellipse((x-radius-5,y-radius-5,x+radius+5,y+radius+5),outline=(255,245,195,135),width=3)
    d.ellipse((x-radius,y-radius,x+radius,y+radius),fill=(255,242,169,255))

def picture_layer(overlay,assets,locale,w,h):
    """Owner-attested image insert with label; no remote footage downloading."""
    entry=assets[overlay['image_asset_id']]
    if entry['kind']!='STILL':raise ValueError('Image insert requires STILL asset')
    tw=int(w*.68);th=int(h*.24)
    src=Image.open(entry['path']);src.load()
    src=ImageOps.exif_transpose(src).convert('RGB')
    thumb=ImageOps.fit(src,(tw,th),method=Image.Resampling.LANCZOS).convert('RGBA')
    caption=rounded_text(overlay['text'],locale,max(13,int(w*.030)),tw,'label')
    result=Image.new('RGBA',(tw+12,th+caption.height+14),(0,0,0,0))
    d=ImageDraw.Draw(result)
    d.rounded_rectangle((1,1,tw+10,th+caption.height+12),radius=12,fill=(4,18,28,242),outline=(101,216,182,255),width=3)
    result.alpha_composite(thumb,(6,6))
    result.alpha_composite(caption,(6,th+7))
    return result


def make_title_layer(shot,fmt,locale):
    w,h=SHORT if fmt=='SHORT' else LONG
    return rounded_text(shot['headline'],locale,max(20,int(w*.056)),int(w*.88),'stat')


def animate_layer(canvas,layer,x,y,local_ms,start_ms,end_ms,animated=True):
    if not start_ms<=local_ms<end_ms:return
    into=local_ms-start_ms;remaining=end_ms-local_ms
    alpha=min(1,into/210,remaining/190) if animated else 1
    if alpha<=0:return
    delta=int((1-min(1,into/250))*20) if animated else 0
    x=max(0,min(canvas.width-layer.width,x))
    y=max(0,min(canvas.height-layer.height,y+delta))
    if alpha<1:
        crop=layer.copy();crop.putalpha(layer.getchannel('A').point(lambda v:int(v*alpha)))
    else:crop=layer
    canvas.alpha_composite(crop,(x,y))


def locate(layer,anchor,w,h,caption=False):
    if caption:return (int((w-layer.width)/2),max(int(h*.55),int(h*.90)-layer.height-int(h*.022)))
    if anchor=='TOP':y=int(h*.19)
    elif anchor=='CENTER':y=int(h*.49)
    else:y=int(h*.63)
    return (int((w-layer.width)/2),min(y,int(h*.87)-layer.height))


def probe_file(path):
    cp=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-show_entries','stream=codec_type,width,height,r_frame_rate',
                       '-of','json',str(path)],capture_output=True,text=True,check=True,timeout=25)
    return json.loads(cp.stdout)


def wav_duration(path):
    with wave.open(str(path),'rb') as f:
        if f.getnchannels() not in (1,2) or f.getsampwidth() not in (1,2,3,4):
            raise ValueError('Unsupported WAV channels/sample width')
        return f.getnframes()/f.getframerate()


def narration_energy(path):
    """Bounded diagnostic for mono/stereo 16-bit PCM; NOT ASR/speech-quality verification."""
    with wave.open(str(path),'rb') as f:
        if f.getsampwidth()!=2:return None
        size=min(f.getnframes(),f.getframerate()*25)
        samples=array.array('h');samples.frombytes(f.readframes(size))
        if not samples:return 0
        step=max(1,len(samples)//30000)
        subset=samples[::step]
        return round(math.sqrt(sum((v/32768.0)**2 for v in subset)/len(subset)),5)


def render_studio(plan,domain,fmt,assets,voice_path,outdir,release=False):
    """Stream pixels to FFmpeg, mux only verified owner audio. No silent audio truncation."""
    if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):raise RuntimeError('FFmpeg and FFprobe required')
    import time
    render_t0=time.perf_counter()
    locale=plan['locale'];shots=plan['shots']; w,h=SHORT if fmt=='SHORT' else LONG
    total_ms=sum(s['duration_ms'] for s in shots)
    has_voice=voice_path is not None
    if has_voice and abs(wav_duration(voice_path)-total_ms/1000)>.45:
        raise ValueError('Narration WAV must match timeline within 450 ms; adjust shot durations or supply aligned narration')
    music=assets.get(plan.get('music_asset_id'))
    if music and music['kind']!='MUSIC':raise ValueError('Music asset must have kind MUSIC')
    outdir=Path(outdir);outdir.mkdir(parents=True,exist_ok=True)
    silent=outdir/'studio_silent.mp4';result=outdir/'studio_preview.mp4'
    cmd=['ffmpeg','-y','-hide_banner','-loglevel','error','-f','rawvideo','-vcodec','rawvideo',
         '-pix_fmt','rgb24','-s',f'{w}x{h}','-r',str(FPS),'-i','pipe:0',
         '-an','-c:v','libx264','-preset','ultrafast','-crf','28','-pix_fmt','yuv420p',str(silent)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    offset=0;frames_written=0;sampled_variance=[]
    try:
        for shot in shots:
            base=base_frame(shot,fmt,domain,assets,locale,release=release)
            title=make_title_layer(shot,fmt,locale)
            overlays=[]
            for o in shot['overlays']:
                size=max(19,int(w*(.044 if o['style']=='LABEL' else .052)))
                layer=(picture_layer(o,assets,locale,w,h) if o['style']=='IMAGE_INSERT' else
                       rounded_text(o['text'],locale,size,int(w*.84),o['style'].lower()))
                overlays.append((o,layer))
            cues=[]
            for cue in plan['captions']:
                if cue['end_ms']>offset and cue['start_ms']<offset+shot['duration_ms']:
                    layer=rounded_text(cue['text'],locale,max(17,int(w*.040)),int(w*.90),'caption')
                    # Captions are absolute timeline; restrict at shot edges.
                    cues.append((cue,layer))
            count=round(shot['duration_ms']*FPS/1000)
            if count<1:raise ValueError('Shot too short for selected frame rate')
            for frame_idx in range(count):
                local_ms=frame_idx*1000/FPS; global_ms=offset+local_ms
                fr=base.copy()
                animate_tactical_motion(fr,shot,domain,local_ms)
                x,y=locate(title,'TOP',w,h)
                animate_layer(fr,title,x,y,local_ms,0,shot['duration_ms'],animated=True)
                for ov,layer in overlays:
                    x,y=locate(layer,ov['anchor'],w,h)
                    animate_layer(fr,layer,x,y,local_ms,ov['start_ms'],ov['end_ms'])
                for cue,layer in cues:
                    x,y=locate(layer,'BOTTOM',w,h,caption=True)
                    animate_layer(fr,layer,x,y,global_ms,cue['start_ms'],cue['end_ms'])
                if frames_written%max(1,FPS*2)==0:
                    sampled_variance.append(round(ImageStat.Stat(fr.convert('L')).var[0],2))
                proc.stdin.write(fr.convert('RGB').tobytes())
                frames_written+=1
            offset+=shot['duration_ms']
        proc.stdin.close()
        rc=proc.wait(timeout=180)
        if rc:
            err=proc.stderr.read().decode('utf8',errors='replace')[-1000:]
            raise RuntimeError('FFmpeg studio stream failed: '+err)
    except Exception:
        if proc.poll() is None:
            proc.kill();proc.wait(timeout=10)
        raise
    finally:
        proc.stderr.close()
    ff=['ffmpeg','-y','-hide_banner','-loglevel','error','-i',str(silent)]
    streams=[]
    if has_voice:
        ff+=['-i',str(voice_path)]
        streams.append('1:a')
    if music:
        ff+=['-stream_loop','-1','-i',str(music['path'])]
        streams.append(f'{2 if has_voice else 1}:a')
    total=total_ms/1000
    if has_voice and music:
        filt='[1:a]volume=1.0[v];[2:a]volume=0.08[m];[v][m]amix=inputs=2:duration=first:dropout_transition=0[a]'
        ff+=['-filter_complex',filt,'-map','0:v:0','-map','[a]']
    elif has_voice:
        ff+=['-map','0:v:0','-map','1:a:0']
    elif music:
        ff+=['-map','0:v:0','-map','1:a:0','-af','volume=0.08']
    else:ff+=['-map','0:v:0']
    ff+=['-c:v','copy']
    if streams:ff+=['-c:a','aac','-b:a','128k']
    ff+=['-t',f'{total:.3f}','-movflags','+faststart',str(result)]
    cp=subprocess.run(ff,capture_output=True,text=True,timeout=180)
    if cp.returncode:raise RuntimeError('Audio mix/mux failed: '+cp.stderr[-1000:])
    info=probe_file(result)
    types=[s['codec_type'] for s in info['streams']]
    actual=float(info['format']['duration'])
    if not any(s.get('codec_type')=='video' and s.get('width')==w and s.get('height')==h for s in info['streams']):
        raise RuntimeError('Studio output video stream/dimensions invalid')
    if (has_voice or music) and 'audio' not in types:raise RuntimeError('Studio expected audio missing')
    if abs(actual-total)>.4:raise RuntimeError('Studio output duration differs from timeline')
    if not sampled_variance or min(sampled_variance)<45:raise RuntimeError('Studio generated blank/flat frames')
    warnings=['Human full-video watch-through required','Claims not automatically verified','No copyright or YouTube monetization clearance']
    energy=narration_energy(voice_path) if has_voice else None
    if not has_voice:warnings.append('No narration supplied; scene cards are NOT a spoken audio track')
    if energy is not None and energy < .007:warnings.append('Owner WAV energy is extremely low; audio may be silent')
    if not plan['captions']:warnings.append('No speech-aligned caption cues supplied')
    if plan['captions'] and has_voice:
        warnings.append('Captions are segment-timed by measured WAV durations, NOT word-level ASR' if plan['captions_provenance']=='SEGMENT_TIMED_MEASURED' else 'Caption timing is OWNER_TIMED; not verified by forced aligner')
    if music:warnings.append('Licensed music owner attestation recorded; legal validity not automatically established')
    wall_seconds=round(time.perf_counter()-render_t0,3)
    report={'render_wall_seconds':wall_seconds,'status':'TECHNICAL_QC_PASSED_HUMAN_REVIEW_REQUIRED','publish_ready':False,
            'automated_checks':{'video_stream':True,'duration_within_400ms':True,'sampled_frame_variance':True,
                                'rights_asset_records_present':True,'voice_duration_checked':has_voice},
            'caption_alignment':('MEASURED_SEGMENT_LEVEL_NOT_WORD_LEVEL' if plan['captions_provenance']=='SEGMENT_TIMED_MEASURED' else 'OWNER_TIMED_NOT_MEASURED') if plan['captions'] else 'MISSING',
            'audio_track_present':'audio' in types,'voice_present':has_voice,'narration_rms':energy,
            'warnings':warnings,'ffprobe':info}
    manifest={'render_wall_seconds':wall_seconds,'renderer':'viralos_cpu_studio_v0.3','domain':domain,'format':fmt,'locale':locale,
              'total_duration_ms':total_ms,'shots':shots,'captions':plan['captions'],
              'asset_sha256':{k:v['content_sha256'] for k,v in assets.items()},
              'voice_sha256':hashlib.sha256(Path(voice_path).read_bytes()).hexdigest() if has_voice else None,
              'sampled_luma_variance':sampled_variance,'publish_ready':False,'render_profile':'OWNER_REVIEWED_FINAL' if release else 'TECHNICAL_PREVIEW'}
    (outdir/'studio_render_manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding='utf8')
    (outdir/'studio_qc_report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf8')
    return result,report,manifest
