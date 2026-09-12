import json,sys,subprocess,shutil,hashlib
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import v41_closeout as audit
BUNDLE=ROOT/'results/v4_1/closeout_v2c_20260912'

def call(p):
 return subprocess.run([sys.executable,str(ROOT/'scripts/v41_closeout.py'),'verify','--out',str(p)],capture_output=True,text=True)

def clone(tmp_path):
 p=tmp_path/'bundle';shutil.copytree(BUNDLE,p);return p

def clone_with_current_client_hash(tmp_path):
 p=clone(tmp_path)
 m=audit.read(p/'manifest.json')
 # v2c is a sealed historical bundle. The production client legitimately
 # changed after its freeze, so tests that need to reach output validation
 # re-anchor only their private copy to the current client source.
 name='src/llm_client.py'
 m['sources'][name]=audit.sha(ROOT/name)
 audit.write(p/'manifest.json',m)
 (p/'manifest.sha256').write_text(audit.sha(p/'manifest.json'))
 return p

def test_historical_bundle_rejects_changed_source():
 r=call(BUNDLE);assert r.returncode!=0 and 'SOURCE_CHANGED src/llm_client.py' in r.stderr

@pytest.mark.parametrize('target',['joint_metrics.json','selections.json','evaluated_records.json','fixed_policy_strata.json'])
def test_output_tamper_rejected(tmp_path,target):
 p=clone_with_current_client_hash(tmp_path);(p/target).write_text('{}');r=call(p);assert r.returncode!=0 and 'OUTPUT_CHANGED' in r.stderr

def test_deleted_output_rejected(tmp_path):
 p=clone_with_current_client_hash(tmp_path);(p/'joint_metrics.json').unlink();assert call(p).returncode!=0

@pytest.mark.parametrize('change',['delete','text','T','graph','duplicate'])
def test_source_changes_rejected(tmp_path,monkeypatch,change):
 p=clone(tmp_path);m=audit.read(p/'manifest.json');src=tmp_path/'root';src.mkdir()
 # Keep a single required source in this isolated fixture; use production validator.
 name=next(n for n in m['sources'] if n.endswith('_graph.json') if change=='graph') if change=='graph' else m['runs']['luna']['groups'][0]
 f=src/name;f.parent.mkdir(parents=True);shutil.copyfile(ROOT/name,f)
 expected=audit.sha(f);m['sources']={name:expected};audit.write(p/'manifest.json',m);(p/'manifest.sha256').write_text(audit.sha(p/'manifest.json'))
 if change=='delete':f.unlink()
 else:
  d=audit.read(f)
  if change=='text':d['utterances'][0]['calls']['review']['user_prompt']='changed'
  elif change=='T':d['utterances'][0]['gold_intent']['time_limit']=100
  elif change=='duplicate':d['utterances'][1]['utterance_id']=d['utterances'][0]['utterance_id']
  else:d['tampered']=True
  audit.write(f,d)
 monkeypatch.setattr(audit,'ROOT',src)
 with pytest.raises(ValueError,match='SOURCE_CHANGED'):audit.verify_inputs(p)

def test_manifest_changed_rejected(tmp_path):
 p=clone(tmp_path);m=audit.read(p/'manifest.json');m['runs']['luna']['ids']=[];audit.write(p/'manifest.json',m);assert call(p).returncode!=0
