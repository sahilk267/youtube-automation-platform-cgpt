"""Small deterministic waveform diagnostics, not subjective voice assessment."""
from __future__ import annotations
import array,math,sys,wave

def inspect_pcm16_mono(path):
    with wave.open(str(path),'rb') as f:
        if f.getnchannels()!=1 or f.getsampwidth()!=2 or f.getframerate()!=16000:
            raise ValueError('Local voice QA requires 16kHz mono PCM16')
        frames=f.getnframes()
        samples=array.array('h');samples.frombytes(f.readframes(frames))
    if sys.byteorder!='little':samples.byteswap()
    if len(samples)!=frames or not samples:raise ValueError('Voice file truncated or empty')
    step=max(1,len(samples)//75000)
    reduced=samples[::step]
    peak=max(abs(x) for x in reduced)/32768
    rms=math.sqrt(sum(x*x for x in reduced)/len(reduced))/32768
    clipped=sum(1 for x in reduced if abs(x)>=32680)/len(reduced)
    # Objective thresholds only. A quiet sample and a synthetic voice may still sound bad.
    blockers=[];warnings=[]
    if rms<0.007:blockers.append('VERY_LOW_NARRATION_ENERGY')
    if clipped>0.015:blockers.append('EXCESSIVE_WAVEFORM_CLIPPING')
    if peak>0.99:warnings.append('AUDIO_NEAR_FULL_SCALE_REVIEW_LIMITER')
    if rms>0.25:warnings.append('HIGH_VOICE_RMS_REVIEW_LEVELS')
    return {'sample_rate_hz':16000,'duration_seconds':round(frames/16000,3),
            'peak_fraction':round(peak,5),'rms_fraction':round(rms,5),
            'clipping_ratio':round(clipped,6),
            'blockers':blockers,'warnings':warnings,
            'loudness_standard_measured':False,'professional_naturalness_measured':False}
