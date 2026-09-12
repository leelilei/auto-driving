"""Independent xcode Luna run after the FHL preflight failed; no response mixing."""
import argparse
import json
import os
import subprocess
from pathlib import Path
import luna_mechanism_ablation as l

l.a.RUN=l.a.m.ROOT/'results/v5/diagnostic/20260910_xcode_luna_mechanism_ablation24'
l.a.m.CONFIG=l.a.m.ROOT/'configs/v5/xcode_gpt56_luna_120s.json'

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','collect','analyze','audit'])
    args=p.parse_args()
    if args.action=='prepare':
        l.prepare()
        path=l.a.RUN/'manifest.json'; manifest=json.loads(path.read_text())
        manifest.update(provider='xcode',launcher_sha256=l.a.m.digest(Path(__file__)),
                        switch_reason='FHL first real request returned HTTP502 twice; no FHL model output used.',
                        decoding_note='xcode Luna omits temperature; DeepSeek used temperature=0. Same cases, prompts, output cap; not pure model ability comparison.')
        l.a.m.dump(path,manifest)
    elif args.action=='collect':
        key=subprocess.run(['security','find-generic-password','-s','XCODE_API_KEY','-w'],capture_output=True,text=True,check=True)
        os.environ['XCODE_API_KEY']=key.stdout.strip()
        l.collect()
    elif args.action=='audit':l.audit()
    else:l.verify();l.a.analyze()
