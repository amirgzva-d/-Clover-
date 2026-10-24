"""Persian translation must make a real provider call, not echo the input."""
import pytest
from utils import language_utils as languages

@pytest.mark.asyncio
async def test_persian_to_english_invokes_translation_provider(monkeypatch):
    calls=[]
    class Translation:
        text="Hello, my friend"
    class FakeTranslator:
        async def translate(self,text,src,dest):
            calls.append((text,src,dest))
            return Translation()
    monkeypatch.setattr(languages,"Translator",FakeTranslator)
    monkeypatch.setattr(languages,"GOOGLETRANS_AVAILABLE",True)
    monkeypatch.setattr(languages,"_ensure_googletrans",lambda: True)
    monkeypatch.setattr(languages,"is_china_region",lambda: False)
    monkeypatch.setattr(languages,"_is_google_marked_failed",lambda: False)
    translated,failed=await languages.translate_text("سلام دوست من","en")
    assert translated=="Hello, my friend"
    assert calls==[("سلام دوست من","fa","en")]
    assert not failed

@pytest.mark.asyncio
async def test_english_to_persian_invokes_translation_provider(monkeypatch):
    calls=[]
    class Translation:
        text="صبح بخیر!"
    class FakeTranslator:
        async def translate(self,text,src,dest):
            calls.append((text,src,dest))
            return Translation()
    monkeypatch.setattr(languages,"Translator",FakeTranslator)
    monkeypatch.setattr(languages,"GOOGLETRANS_AVAILABLE",True)
    monkeypatch.setattr(languages,"_ensure_googletrans",lambda: True)
    monkeypatch.setattr(languages,"is_china_region",lambda: False)
    monkeypatch.setattr(languages,"_is_google_marked_failed",lambda: False)
    translated,failed=await languages.translate_text("Good morning!","fa")
    assert translated=="صبح بخیر!"
    assert calls==[("Good morning!","en","fa")]
    assert not failed

@pytest.mark.asyncio
async def test_existing_english_to_english_fast_path(monkeypatch):
    def fail_if_provider_used(): raise AssertionError("must not translate same language")
    monkeypatch.setattr(languages,"_ensure_googletrans",fail_if_provider_used)
    translated,_=await languages.translate_text("Hello","en",source_lang="en")
    assert translated=="Hello"
