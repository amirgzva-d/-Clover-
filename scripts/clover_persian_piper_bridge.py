"""Optional loopback-only OpenAI-compatible PCM TTS adapter for Piper Persian.

Run with a local Piper model and use only via explicitly configured Custom TTS.
Does not modify or replace the original N.E.K.O. UI or existing Chinese voice.
"""
from __future__ import annotations
import argparse
import io
import json
import os
import threading
import wave
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

_MAX_BYTES=8192
_MAX_TEXT=900
_MODEL_NAME='piper-fa'
_VOICE_NAME='fa_IR-amir-medium'

def synthesize_pcm(model, text: str) -> bytes:
    """Synthesize Piper 22.05kHz WAV, resample to OpenAI PCM s16le mono 24kHz."""
    import numpy as np
    import soxr
    buf=io.BytesIO()
    with wave.open(buf,'wb') as wav:
        model.synthesize_wav(text,wav)
    buf.seek(0)
    with wave.open(buf,'rb') as wav:
        channels,rate,sw=wav.getnchannels(),wav.getframerate(),wav.getsampwidth()
        if channels!=1 or sw!=2: raise RuntimeError("Piper output must be PCM16 mono")
        audio=np.frombuffer(wav.readframes(wav.getnframes()),dtype='<i2').astype('float32')
    if rate!=24000: audio=soxr.resample(audio,rate,24000)
    return np.clip(audio,-32768,32767).astype('<i2').tobytes()

def build_handler(model,secret):
    model_lock=threading.Lock()
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def response(self,status: int,body: bytes,kind='application/json'):
            self.send_response(status)
            self.send_header('Content-Type',kind)
            self.send_header('Content-Length',str(len(body)))
            self.send_header('Cache-Control','no-store')
            self.send_header('X-Content-Type-Options','nosniff')
            self.end_headers()
            self.wfile.write(body)
        def fail(self,status,reason):
            self.response(status,json.dumps({'error':{'message':reason,'type':'invalid_request_error'}}).encode('utf8'))
        def do_GET(self):
            if self.path=='/health':
                return self.response(200,b'{"status":"ok","model":"piper-fa"}')
            return self.fail(404,'not found')
        def do_POST(self):
            if self.path.rstrip('/')!='/v1/audio/speech':return self.fail(404,'not found')
            if secret and self.headers.get('Authorization')!='Bearer '+secret:
                return self.fail(401,'unauthorized')
            size=int(self.headers.get('Content-Length','0') or '0')
            if size<2 or size>_MAX_BYTES:return self.fail(413,'invalid size')
            try:
                request=json.loads(self.rfile.read(size))
                if not isinstance(request,dict):raise ValueError("invalid request")
                text=request.get('input','')
                if not isinstance(text,str) or not 1<=len(text.strip())<=_MAX_TEXT:raise ValueError("invalid input")
                if request.get('model')!=_MODEL_NAME:raise ValueError("unsupported model")
                if request.get('voice') not in (_VOICE_NAME, 'default'):raise ValueError("unsupported voice")
                if request.get('response_format','pcm')!='pcm':raise ValueError("PCM is required")
                with model_lock:
                    pcm=synthesize_pcm(model,text.strip())
                self.response(200,pcm,'audio/pcm')
            except (ValueError,TypeError,json.JSONDecodeError) as ex:
                self.fail(400,str(ex))
            except Exception:
                self.fail(503,'speech synthesis temporarily unavailable')
    return Handler

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--model',type=Path,required=True)
    p.add_argument('--port',type=int,default=48919)
    p.add_argument('--token-file',type=Path,required=True)
    a=p.parse_args()
    if not a.model.is_file():raise SystemExit('Missing Persian Piper ONNX file')
    if not 1024<=a.port<=65535:raise SystemExit('Invalid port')
    if not a.token_file.is_file():raise SystemExit('Missing local auth file')
    secret=a.token_file.read_text(encoding='utf8').strip()
    if len(secret)<32:raise SystemExit('Local TTS token must have >=32 characters')
    from piper import PiperVoice
    model=PiperVoice.load(str(a.model))
    server=ThreadingHTTPServer(('127.0.0.1',a.port),build_handler(model,secret))
    print('PERSIAN_TTS_READY',a.port,flush=True)
    try:server.serve_forever(poll_interval=.5)
    finally:server.server_close()
if __name__=='__main__':main()
