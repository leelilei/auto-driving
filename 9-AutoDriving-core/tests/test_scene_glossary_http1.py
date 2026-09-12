import json
from pathlib import Path
from types import SimpleNamespace
import pytest
from src.llm_client import LLMConfig
from scripts import scene_glossary_http1 as h

def test_http1_preserves_anthropic_payload_and_keeps_key_off_command(monkeypatch):
    config=LLMConfig(model='test-model',base_url='https://example.invalid',max_output_tokens=1600,temperature=0)
    response={'model':'test-model','content':[{'type':'text','text':'{}'}],'usage':{'input_tokens':10,'output_tokens':1}}
    def fake_run(cmd,**kwargs):
        assert '--http1.1' in cmd
        assert not any('test-secret' in arg for arg in cmd)
        assert 'test-secret' in kwargs['input']
        payload=json.loads(Path(cmd[cmd.index('--data-binary')+1][1:]).read_text())
        assert payload==dict(model='test-model',max_tokens=1600,temperature=0,system='system',messages=[{'role':'user','content':'user'}])
        Path(cmd[cmd.index('--output')+1]).write_text(json.dumps(response))
        return SimpleNamespace(returncode=0,stdout='200',stderr='')
    monkeypatch.setattr(h.subprocess,'run',fake_run)
    client=h.CurlMessages(config,'test-secret')
    assert client.complete({'system_prompt':'system','user_prompt':'user'})=='{}'
    assert client.last_response==response

def test_transport_error_redacts_key(monkeypatch):
    monkeypatch.setattr(h.subprocess,'run',lambda *a,**k:SimpleNamespace(returncode=35,stdout='',stderr='failure test-secret'))
    with pytest.raises(RuntimeError) as exc:
        h.CurlMessages(LLMConfig(),'test-secret').complete({'system_prompt':'s','user_prompt':'u'})
    assert 'test-secret' not in str(exc.value)
