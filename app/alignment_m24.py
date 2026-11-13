"""Opt-in genuine local CTC forced alignment from supplied exact transcript.
Requires a local compatible WhisperX aligner/model, with network forced offline.
A model-derived proposal is NEVER accepted without human review. No voice cloning.
"""
import os
from pathlib import Path

def config():
    raw=os.getenv('VIRALOS_WHISPERX_ALIGN_MODEL_DIR','')
    model=Path(raw).expanduser().resolve() if raw else None
    return {'model_installed':bool(model and model.is_dir()),
            'owner_attested_model_rights':os.getenv('VIRALOS_WHISPERX_MODEL_RIGHTS_OK')=='1',
            'opt_in':os.getenv('VIRALOS_OFFLINE_FORCED_ALIGN_OPT_IN')=='1',
            'model_downloads_allowed':False,
            'requires_human_word_review':True,
            'real_model_execution_tested_in_delivery':False}

def align_transcript(voice_path,plan):
    cfg=config()
    if not (cfg['model_installed'] and cfg['owner_attested_model_rights'] and cfg['opt_in']):
        raise RuntimeError('Set up an existing compatible local WhisperX align model and explicit offline rights/opt-in')
    lang=plan['locale'].split('-')[0]
    if lang not in ('hi','en'):raise RuntimeError('Only en/hi selected for local alignment in this release')
    os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1'
    os.environ['HF_HUB_DISABLE_TELEMETRY']='1'
    try:import whisperx
    except ImportError as ex:raise RuntimeError('Optional whisperx module is not installed') from ex
    model,metadata=whisperx.load_align_model(language_code=lang,device='cpu',
                                             model_name=str(Path(os.environ['VIRALOS_WHISPERX_ALIGN_MODEL_DIR']).resolve()))
    transcript=[{'text':c['text'],'start':c['start_ms']/1000,'end':c['end_ms']/1000}
                for c in plan['captions']]
    if not transcript:raise RuntimeError('Cannot force-align without timed human-script captions')
    audio=whisperx.load_audio(str(voice_path))
    result=whisperx.align(transcript,model,metadata,audio,'cpu',return_char_alignments=False)
    out=[]
    for w in result.get('word_segments',[]):
        if w.get('word') and w.get('start') is not None and w.get('end') is not None:
            out.append({'token':w['word'].strip(), 'start_ms':round(w['start']*1000),
                        'end_ms':round(w['end']*1000)})
    if not out:raise RuntimeError('Forced aligner returned no words: missing phonetic/model coverage')
    return out
