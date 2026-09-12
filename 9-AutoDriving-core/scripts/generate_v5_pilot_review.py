#!/usr/bin/env python3
"""Generate a local, human-operated review workspace for the first v5.1 groups.

This script never changes annotation status. A reviewer must inspect every row,
enter an identity, and export the resulting JSON as a separate evidence file.
"""
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path


def select_groups(records: list[dict], count: int) -> list[dict]:
    group_ids = sorted({str(item["group_id"]) for item in records})[:count]
    selected = [item for item in records if str(item["group_id"]) in group_ids]
    if len(selected) != count * 4:
        raise ValueError("review workspace requires exactly four utterances per group")
    return sorted(selected, key=lambda item: str(item["utterance_id"]))


def render(records: list[dict], source_path: Path) -> str:
    safe_records = json.dumps(records, ensure_ascii=False).replace("</", "<\\/")
    source = html.escape(str(source_path.resolve()))
    return f"""<!doctype html>
<html lang=\"zh-CN\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">
<title>DARC-Route v5.1 前8组人工审核</title>
<style>
body{{font-family:-apple-system,BlinkMacSystemFont,\"Segoe UI\",sans-serif;margin:0;background:#f4f6f8;color:#17202a}}
header{{position:sticky;top:0;background:#17202a;color:white;padding:16px 24px;z-index:2}}
main{{max-width:1100px;margin:24px auto;padding:0 18px}} .meta,.card{{background:white;border:1px solid #dfe5eb;border-radius:10px;padding:18px;margin-bottom:16px}}
.group{{border-left:5px solid #346beb}} .utterance{{border-top:1px solid #e7ebef;padding:16px 0}}
.utterance:first-of-type{{border-top:0}} .v0{{background:#eef5ff;padding:12px;border-radius:6px}}
.label{{font-weight:700;color:#34495e}} .target{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:8px;background:#f8fafc;padding:10px;margin:8px 0}}
.checks{{display:grid;grid-template-columns:1fr 1fr;gap:12px}} fieldset{{border:1px solid #ccd5df;border-radius:6px}}
textarea,input[type=text]{{box-sizing:border-box;width:100%;padding:8px;border:1px solid #aeb9c4;border-radius:5px}}
button{{background:#2457d6;color:white;border:0;border-radius:6px;padding:10px 16px;font-weight:700;cursor:pointer}}
.warn{{color:#a23b19}} #progress{{font-weight:700}}
</style></head><body>
<header><div>DARC-Route v5.1 · 前8组人工语义审核</div><div id=\"progress\">0 / {len(records)} 条已裁定</div></header>
<main><section class=\"meta\"><p><strong>审核目标：</strong>逐条判断改写是否保持V0含义，以及显示的目标标签是否被当前文本支持。不要依据模型输出或路线好坏修改语义。</p>
<p><strong>源文件：</strong><code>{source}</code>。本页不会改写数据集，也不会自动签名。</p>
<label>审核人真实姓名/标识 <input id=\"reviewer\" type=\"text\" placeholder=\"导出前必填\"></label><br><br>
<button id=\"export\">导出审核JSON</button> <span class=\"warn\" id=\"message\"></span></section><div id=\"cards\"></div></main>
<script>
const rows={safe_records}; const key='darc-v5.1-pilot8-human-review';
let state=JSON.parse(localStorage.getItem(key)||'{{}}');
const esc=s=>String(s).replace(/[&<>\"']/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#39;'}}[c]));
function radio(uid,name,value){{return `<label><input type=\"radio\" name=\"${{uid}}_${{name}}\" value=\"${{value}}\" ${{state[uid]?.[name]===value?'checked':''}}> ${{value}}</label>`}}
function updateProgress(){{let n=rows.filter(r=>state[r.utterance_id]?.equivalence&&state[r.utterance_id]?.label_support).length;document.getElementById('progress').textContent=`${{n}} / ${{rows.length}} 条已裁定`;}}
function render(){{const groups={{}};for(const r of rows)(groups[r.group_id]??=[]).push(r);let out='';for(const [gid,items] of Object.entries(groups)){{let v0=items.find(x=>x.variant_type==='V0').text;out+=`<section class=\"card group\"><h2>${{esc(gid)}}</h2><div class=\"v0\"><span class=\"label\">V0母句：</span>${{esc(v0)}}</div>`;for(const r of items){{let hard=r.gold_hard;out+=`<article class=\"utterance\" data-uid=\"${{esc(r.utterance_id)}}\"><h3>${{esc(r.utterance_id)}} · ${{esc(r.variant_type)}}</h3><p>${{esc(r.text)}}</p><div class=\"target\"><div><b>POI</b>: ${{esc(JSON.stringify(hard.pois))}}</div><div><b>截止</b>: ${{esc(hard.time_limit)}}</div><div><b>依赖</b>: ${{esc(JSON.stringify(hard.dependencies))}}</div><div><b>偏好</b>: ${{esc(r.preference_direction)}}</div></div><div class=\"checks\"><fieldset><legend>与V0语义等价</legend>${{radio(r.utterance_id,'equivalence','yes')}} ${{radio(r.utterance_id,'equivalence','no')}} ${{radio(r.utterance_id,'equivalence','unclear')}}</fieldset><fieldset><legend>目标标签受文本支持</legend>${{radio(r.utterance_id,'label_support','yes')}} ${{radio(r.utterance_id,'label_support','no')}} ${{radio(r.utterance_id,'label_support','unclear')}}</fieldset></div><label>证据/问题说明<textarea data-note=\"${{esc(r.utterance_id)}}\">${{esc(state[r.utterance_id]?.note||'')}}</textarea></label></article>`}}out+='</section>'}}document.getElementById('cards').innerHTML=out;updateProgress();}}
document.addEventListener('change',e=>{{if(e.target.type==='radio'){{let [uid,...parts]=e.target.name.split('_');while(!rows.some(r=>r.utterance_id===uid)&&parts.length)uid+='_'+parts.shift();let name=parts.join('_');state[uid]={{...(state[uid]||{{}}),[name]:e.target.value}};localStorage.setItem(key,JSON.stringify(state));updateProgress();}}}});
document.addEventListener('input',e=>{{if(e.target.dataset.note){{let uid=e.target.dataset.note;state[uid]={{...(state[uid]||{{}}),note:e.target.value}};localStorage.setItem(key,JSON.stringify(state));}}}});
document.getElementById('export').onclick=()=>{{const reviewer=document.getElementById('reviewer').value.trim();const done=rows.filter(r=>state[r.utterance_id]?.equivalence&&state[r.utterance_id]?.label_support).length;if(!reviewer){{message.textContent='请填写真实审核人。';return}}if(done!==rows.length){{message.textContent=`仍有${{rows.length-done}}条未裁定。`;return}}const payload={{protocol_version:'darc-v5.1-human-review-1',reviewer,reviewed_at:new Date().toISOString(),source:'{source}',scope_groups:[...new Set(rows.map(r=>r.group_id))],records:rows.map(r=>({{group_id:r.group_id,utterance_id:r.utterance_id,equivalence:state[r.utterance_id].equivalence,label_support:state[r.utterance_id].label_support,note:state[r.utterance_id].note||''}}))}};const blob=new Blob([JSON.stringify(payload,null,2)],{{type:'application/json'}});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='pilot8_human_review_'+new Date().toISOString().replace(/[:.]/g,'')+'.json';a.click();message.textContent='已导出；请将文件作为独立审核证据归档。';}};render();
</script></body></html>"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--groups", type=int, default=8)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    records = json.loads(args.dataset.read_text(encoding="utf-8"))
    selected = select_groups(records, args.groups)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(render(selected, args.dataset), encoding="utf-8")
    print(json.dumps({"status": "PASS", "groups": args.groups, "utterances": len(selected), "out": str(args.out)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
