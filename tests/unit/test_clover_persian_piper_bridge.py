"""Regression tests for optional Persian Piper bridge."""
from __future__ import annotations
import importlib.util
import json
import math
import struct
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("piper_bridge", ROOT/"scripts/clover_persian_piper_bridge.py")
bridge = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bridge)

class FakeVoice:
    def synthesize_wav(self, text, wav):
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(22050)
        raw = b"".join(struct.pack("<h", int(6000*math.sin(2*math.pi*440*i/22050))) for i in range(2205))
        wav.writeframes(raw)

@pytest.fixture
def url():
    server=ThreadingHTTPServer(("127.0.0.1",0),bridge.build_handler(FakeVoice(),"test-secret"))
    thread=threading.Thread(target=server.serve_forever,daemon=True)
    thread.start()
    yield "http://127.0.0.1:"+str(server.server_address[1])
    server.shutdown()
    server.server_close()
    thread.join(timeout=3)

def _send(url,token="",model="piper-fa"):
    body=json.dumps({"model":model,"voice":"fa_IR-amir-medium","response_format":"pcm","input":"سلام"}).encode("utf8")
    req=urllib.request.Request(url+"/v1/audio/speech",data=body,headers={"Content-Type":"application/json","Authorization":"Bearer "+token})
    return urllib.request.urlopen(req,timeout=8)

def test_pcm_24khz():
    data=bridge.synthesize_pcm(FakeVoice(),"سلام")
    assert len(data)%2==0
    assert abs(len(data)-4800)<10

def test_local_health(url):
    with urllib.request.urlopen(url+"/health",timeout=5) as res:
        assert res.status==200
        assert "secret" not in res.read().decode()

def test_auth_rejects_wrong_token(url):
    with pytest.raises(urllib.error.HTTPError) as exc:
        _send(url,token="invalid")
    assert exc.value.code==401

def test_model_rejects_unsupported(url):
    with pytest.raises(urllib.error.HTTPError) as exc:
        _send(url,token="test-secret",model="unknown")
    assert exc.value.code==400

def test_pcm_openai_compatibility(url):
    with _send(url,token="test-secret") as res:
        assert res.status==200
        assert res.headers["Content-Type"]=="audio/pcm"
        assert len(res.read())>4000
