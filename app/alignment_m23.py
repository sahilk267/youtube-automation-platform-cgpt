"""Offline, optional, *ASR-derived* word timestamps. NOT forced transcript alignment.

Models and licenses are supplied by the operator.  No model downloads, web services,
or synthetic transcript rewriting.  ASR proposals require independent owner review.
"""
import os
from pathlib import Path


def model_config():
    raw=os.getenv('VIRALOS_FASTER_WHISPER_MODEL_DIR','').strip()
    model=Path(raw).expanduser().resolve() if raw else None
    return {'configured':bool(model and model.is_dir()),'model_dir':str(model) if model else None,
            'owner_model_license_attested':os.getenv('VIRALOS_WHISPER_MODEL_RIGHTS_OK')=='1',
            'backend':'OPTIONAL_FASTER_WHISPER_CPU_INT8','automatic_downloads':False}


def transcribe_local(audio_path,language):
    cfg=model_config()
    if not cfg['configured'] or not cfg['owner_model_license_attested']:
        raise RuntimeError('Install an existing local faster-whisper model and attest model rights first')
    if language not in ('en','hi'):
        raise RuntimeError('Only individually reviewed English/Hindi language models are permitted in this checkpoint')
    if os.getenv('VIRALOS_OFFLINE_ASR_OPT_IN')!='1':
        raise RuntimeError('Set VIRALOS_OFFLINE_ASR_OPT_IN=1 to explicitly enable local inference')
    # Prevent implicit Hugging Face network fallback; only pass a checked local directory.
    os.environ['HF_HUB_OFFLINE']='1'
    os.environ['TRANSFORMERS_OFFLINE']='1'
    try:
        from faster_whisper import WhisperModel
    except ImportError as e:
        raise RuntimeError('Install optional faster-whisper package in your local environment') from e
    model=WhisperModel(cfg['model_dir'],device='cpu',compute_type='int8',local_files_only=True,
                       cpu_threads=min(8,max(1,os.cpu_count() or 1)))
    segments,_=model.transcribe(str(audio_path),language=language,word_timestamps=True,
                                beam_size=2,vad_filter=False,condition_on_previous_text=False)
    words=[]
    for segment in segments:
        for w in (segment.words or []):
            token=w.word.strip()
            if token and w.start is not None and w.end is not None:
                words.append({'token':token,'start_ms':max(0,round(w.start*1000)),
                              'end_ms':max(1,round(w.end*1000))})
    return words


def config_for_public():
    cfg=model_config()
    return {k:v for k,v in cfg.items() if k!='model_dir'} | {
        'model_file_path_exposed':False,'supported_languages':['en','hi'],
        'word_timestamps':'ASR_ESTIMATED_NOT_FORCED_ALIGNMENT',
        'live_model_tested_in_package':False,
        'human_transcript_and_timing_review_required':True}
