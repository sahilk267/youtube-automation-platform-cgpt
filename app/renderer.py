"""CPU-only deterministic ORIGINAL diagram/text preview. Never a publishing approval."""
from pathlib import Path
import hashlib, json, math, os, shutil, subprocess, textwrap
from PIL import Image, ImageDraw, ImageFont

COLORS={'cricket':('#102F30','#E6B65B'), 'nfl':('#1B2840','#71B6FB'), 'technology':('#222B38','#9DCD8E')}

def _font(sz):
    paths=[os.getenv('VIRALOS_FONT',''), 'C:/Windows/Fonts/Nirmala.ttf','C:/Windows/Fonts/arial.ttf',
           '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']
    for p in paths:
        if p and Path(p).is_file():return ImageFont.truetype(p,sz)
    return ImageFont.load_default()

def _lines(draw, text, fnt, max_width):
    res=[];line=''
    for word in text.split():
        trial=(line+' '+word).strip()
        if line and draw.textbbox((0,0),trial,font=fnt)[2]>max_width:
            res.append(line);line=word
        else:line=trial
    if line:res.append(line)
    for entry in res:
        if draw.textbbox((0,0),entry,font=fnt)[2]>max_width:
            raise ValueError('Unwrappable long word in scene; shorten or insert spaces')
    return res

def image_for_scene(text, index, total, dest, width, height, category, no_voice):
    bg,accent=COLORS.get(category,COLORS['technology'])
    image=Image.new('RGB',(width,height),bg);d=ImageDraw.Draw(image)
    pad=max(18,int(width*.065)); title_font=_font(max(17,int(width*.06)));mini=_font(max(12,int(width*.028)))
    # Low-contrast ORIGINAL, sport-specific visual geometry. Not real match footage or statistics.
    if category=='cricket':
        d.ellipse((int(width*.17),int(height*.24),int(width*.83),int(height*.79)),outline='#345C57',width=4)
        d.rectangle((int(width*.47),int(height*.35),int(width*.53),int(height*.65)),outline='#3A6560',width=3)
        d.line((int(width*.5),int(height*.66),int(width*.66),int(height*.55)),fill='#4D7770',width=3)
    elif category=='nfl':
        for x in range(int(width*.1),int(width*.91),max(1,int(width*.16))):
            d.line((x,int(height*.24),x,int(height*.79)),fill='#314764',width=2)
        for y in range(int(height*.24),int(height*.79),max(1,int(height*.1))):
            d.line((int(width*.1),y,int(width*.9),y),fill='#2E3E55',width=2)
        d.line((int(width*.26),int(height*.7),int(width*.69),int(height*.44)),fill='#395875',width=4)
    d.rectangle((pad,pad,pad+max(15,int(width*.09)),pad+5),fill=accent)
    d.text((pad,pad+23),'VIRALOS • ORIGINAL ANALYSIS',font=mini,fill='#D8E7F0')
    d.text((pad,pad+53),f'SCENE {index+1} / {total}',font=mini,fill=accent)
    lines=_lines(d,text,title_font,width-2*pad)
    if len(lines)>10:raise ValueError('Scene text too long for readable layout; split scene')
    bbox=d.textbbox((0,0),'Hg',font=title_font);dy=max(24,(bbox[3]-bbox[1])+13)
    start=max(125,int(height/2-len(lines)*dy/2))
    for l in lines:
        d.text((pad,start),l,font=title_font,fill='#FFFFFF');start+=dy
    d.line((pad,height-84,width-pad,height-84),fill=accent,width=2)
    footer1='ILLUSTRATIVE • NOT MATCH FOOTAGE'
    footer2='SILENT PREVIEW • NOT PUBLISH READY' if no_voice else 'TECHNICAL PREVIEW • NOT PUBLISH READY'
    for value,y,color in [(footer1,height-72,'#CAD9E1'),(footer2,height-46,'#FFCF9C')]:
        font_size=max(9,int(width*.028))
        fnt=_font(font_size)
        while font_size>8 and d.textbbox((0,0),value,font=fnt)[2]>(width-2*pad):
            font_size-=1;fnt=_font(font_size)
        d.text((pad,y),value,font=fnt,fill=color)
    dest.parent.mkdir(parents=True,exist_ok=True);image.save(dest)

def run(command,timeout=240):
    cp=subprocess.run(command,text=True,capture_output=True,timeout=timeout)
    if cp.returncode:raise RuntimeError((cp.stderr or cp.stdout)[-900:])

def render(project_id, script_revision, scenes, outdir, format_name='SHORT', sport='cricket', voice=None):
    if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):raise RuntimeError('FFmpeg and FFprobe required')
    outdir=Path(outdir);outdir.mkdir(parents=True,exist_ok=True)
    # CPU-friendly PREVIEW resolution; not 1080p production grading.
    width,height=(360,640) if format_name=='SHORT' else (640,360)
    parts=[];manifest=[];no_voice=not voice
    for ix,scene in enumerate(scenes):
        d=float(scene['duration_seconds']);
        if not 1<=d<=15:raise ValueError('Scene duration must be between 1 and 15 seconds')
        p=outdir/f'scene_{ix:02d}.png';clip=outdir/f'segment_{ix:02d}.mp4'
        image_for_scene(scene['text'],ix,len(scenes),p,width,height,sport,no_voice)
        # Small original motion: slow zoom on the scene. None of the visuals claim real footage.
        frames=int(round(d*24))
        vf=f"zoompan=z='min(zoom+0.00055,1.04)':d={frames}:s={width}x{height}:fps=24,format=yuv420p"
        run(['ffmpeg','-y','-hide_banner','-loglevel','error','-loop','1','-framerate','24','-i',str(p),
             '-vf',vf,'-frames:v',str(frames),'-an','-c:v','libx264','-preset','ultrafast','-crf','29',str(clip)])
        parts.append(clip)
        manifest.append({'order':ix,'scene_text':scene['text'],'duration_seconds':d,'claim_ids':scene.get('claim_ids',[]),'visual_type':'ORIGINAL_TEXT_MOTION','source_file':p.name})
    # ffconcat avoids shell escaping and arbitrary user-specified paths.
    concat=outdir/'concat.ffconcat'
    concat.write_text('ffconcat version 1.0\n'+''.join(f"file 'segment_{i:02d}.mp4'\n" for i in range(len(parts))),encoding='utf8')
    silent=outdir/'assembled_silent.mp4'
    run(['ffmpeg','-y','-hide_banner','-loglevel','error','-safe','0','-f','concat','-i',str(concat),'-c','copy',str(silent)])
    output=outdir/'preview.mp4'
    if voice:
        # A narration asset must be OWNER supplied and WAV. Do not invent synthesized speech.
        run(['ffmpeg','-y','-hide_banner','-loglevel','error','-i',str(silent),'-i',str(voice),
             '-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','128k','-af','apad',
             '-t',str(sum(s['duration_seconds'] for s in scenes)),'-movflags','+faststart',str(output)])
    else:shutil.copy2(silent,output)
    metadata=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-show_entries','stream=codec_type',
                            '-of','json',str(output)],capture_output=True,text=True,check=True)
    probe=json.loads(metadata.stdout)
    stream_types=[s['codec_type'] for s in probe['streams']]
    if 'video' not in stream_types or (voice and 'audio' not in stream_types):raise RuntimeError('Render stream QC failed')
    obj={'project_id':project_id,'script_revision':script_revision,'format':format_name,'resolution':[width,height],
         'scenes':manifest,'voice_supplied':bool(voice),'rights':'ORIGINAL_GRAPHICS_ONLY','ffprobe':probe,
         'publish_ready':False,'human_reviewed':False,'renderer':'cpu_ffmpeg_original_text_v0.1'}
    (outdir/'render_manifest.json').write_text(json.dumps(obj,indent=2,ensure_ascii=False),encoding='utf8')
    return output,obj
