"""Opt-in offline Piper CLI driver. Requires owner-installed executable and licensed local model."""
import os,subprocess,wave
from pathlib import Path


def piper_config():
    exe=Path(os.getenv('VIRALOS_PIPER_EXE','')).expanduser() if os.getenv('VIRALOS_PIPER_EXE') else None
    model=Path(os.getenv('VIRALOS_PIPER_MODEL','')).expanduser() if os.getenv('VIRALOS_PIPER_MODEL') else None
    return {'installed':bool(exe and exe.is_file() and model and model.is_file()),
            'licensed_model_reviewed':os.getenv('VIRALOS_PIPER_MODEL_RIGHTS_OK')=='1',
            'voice_type':'LOCAL_TTS_NO_VOICE_CLONING'}


def generate(text,output):
    cfg=piper_config()
    if not cfg['installed'] or not cfg['licensed_model_reviewed']:
        raise ValueError('Configure Piper executable, existing model file and rights confirmation first')
    exe=Path(os.environ['VIRALOS_PIPER_EXE']).expanduser().resolve()
    model=Path(os.environ['VIRALOS_PIPER_MODEL']).expanduser().resolve()
    target=Path(output).resolve();target.parent.mkdir(exist_ok=True,parents=True)
    temp=target.with_suffix('.piper-tmp.wav')
    try:
        cp=subprocess.run([str(exe),'--model',str(model),'--output_file',str(temp)],
                          input=text+'\n',text=True,capture_output=True,timeout=180)
        if cp.returncode:raise ValueError('Piper CLI exited with an error; see local logs')
        with wave.open(str(temp),'rb') as wav:
            if wav.getframerate()<8000 or wav.getnframes()==0 or wav.getnchannels() not in (1,2):
                raise ValueError('Invalid generated audio')
            duration=wav.getnframes()/wav.getframerate()
        if duration>600:raise ValueError('Narration too long for preview')
        temp.replace(target)
        return {'generated':True,'duration_seconds':round(duration,2),'source':'OPT_IN_LOCAL_PIPER',
                'word_level_alignment':'NOT_DONE','phonetic_review':'REQUIRED'}
    finally:temp.unlink(missing_ok=True)
