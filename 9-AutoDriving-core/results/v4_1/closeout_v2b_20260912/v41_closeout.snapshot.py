"""Versioned offline joint evaluation. No API clients or original-asset writes."""
import argparse,copy,hashlib,itertools,json,math,random,re,socket,sys
from pathlib import Path
from dataclasses import asdict
from collections import defaultdict
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.intent import Intent
from src.graph import SyntheticGraph
from src.solver import ExactRouteSolver,RouteResult
from src.evaluation import check_route
from src.gating import compute_protection_trigger,compute_cross_utility_delta,calculate_route_utility
RUNS={
'gpt54':'20260906T051339Z_main_test',
'luna':'20260912T074558Z_e2_confirmation_gpt-5_6-luna',
'gemini':'20260912T073141Z_e2_confirmation_gemini-3_1-flash-lite',
'haiku':'20260912T090152Z_e2_claude-haiku-4-5-20251001',
'sonnet':'20260912T092122Z_e2_claude-sonnet-4-6'}
OVERLAP={42,56,325,345,361,369,433,501}
DRIFT={'test_001','test_007','test_020','test_080','test_091','test_100','test_102','test_108','test_112','test_115','test_129','test_141','test_142','test_147'}
def block(*a,**k):raise RuntimeError('OFFLINE_ONLY')
socket.socket=block

def read(p):return json.loads(p.read_text())
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def canonical(v):return json.dumps(v,sort_keys=True,ensure_ascii=False,allow_nan=False)
def mean(xs):return float(np.mean(xs)) if xs else None

def parse_raw(raw,claude):
 text=raw.strip();changes=[]
 if claude:
  m=re.search(r'```(?:json)?\s*(\{.*?\})\s*```',text,re.S) or re.search(r'(\{.*\})',text,re.S)
  if m:text=m.group(1)
 else:
  if text.startswith('```'):
   text=re.sub(r'^```[a-zA-Z]*\n?','',text);text=re.sub(r'\n?```$','',text).strip()
 d=json.loads(text)
 if claude and isinstance(d,dict):
  required={'pois','time_limit','dependencies','quality_weight'}
  if not required<=d.keys():
   for k in ['intent','parsed_intent','extracted_intent','route_intent']:
    if isinstance(d.get(k),dict) and required<=d[k].keys():d=dict(d[k]);changes.append({'type':'unwrap','key':k});break
  if isinstance(d.get('dependencies'),list):
   old=d['dependencies'];new=[list(x) for x in old if isinstance(x,(list,tuple)) and len(x)==2 and all(isinstance(z,str) for z in x)]
   if old!=new:changes.append({'type':'dependency_deletion','before':old,'after':new})
   d['dependencies']=new
 return Intent.parse(d),changes

def make_manifest(out):
 files=set(Path(__file__).parent.parent.joinpath('src').glob('*.py'));files.add(Path(__file__))
 runs={}
 for model,name in RUNS.items():
  d=ROOT/'results/runs'/name
  groups=sorted(p for p in d.glob('*.json') if p.name.startswith(('test_','e2_clean_')) and not p.name.endswith('_graph.json'))
  expected=160 if model=='gpt54' else 40
  if len(groups)!=expected:raise ValueError('group count '+model)
  ids=[];gids=[]
  for p in groups:
   g=read(p);gids.append(g['group_id']);ids += [u['utterance_id'] for u in g['utterances']]
   files.update([p,d/(g['group_id']+'_graph.json')])
  if len(ids)!=expected*4 or len(set(ids))!=len(ids):raise ValueError('ID count')
  runs[model]={'directory':str(d.relative_to(ROOT)),'groups':[str(p.relative_to(ROOT)) for p in groups],'ids':ids,'group_ids':gids}
 for name in ['data/test/test_640_utterances.json','data/e2/e2_strictly_unexposed_utterances.json','data/e2/e2_clean_manifest.json']:
  files.add(ROOT/name)
 m={'version':'v41_closeout_v2','runs':runs,'sources':{str(p.relative_to(ROOT)):sha(p) for p in sorted(files)},'approval':read(out/'human_approval.json'),'scope':'historical and post-hoc migration; no retrospective confirmatory claim','bootstrap_seed':20260912,'bootstrap_n':2000,'random_seeds':list(range(20))}
 write(out/'manifest.json',m);(out/'manifest.sha256').write_text(sha(out/'manifest.json')+'\n')
 return m

def verify_inputs(out):
 if sha(out/'manifest.json')!=(out/'manifest.sha256').read_text().strip():raise ValueError('MANIFEST_CHANGED')
 m=read(out/'manifest.json')
 if read(out/'human_approval.json')!=m['approval']:raise ValueError('APPROVAL_CHANGED')
 for name,digest in m['sources'].items():
  if not (ROOT/name).is_file() or sha(ROOT/name)!=digest:raise ValueError('SOURCE_CHANGED '+name)
 return m

def load(model,spec):
 reference=read(ROOT/('data/test/test_640_utterances.json' if model=='gpt54' else 'data/e2/e2_strictly_unexposed_utterances.json'))
 refs={u['utterance_id']:u for u in reference};items=[];ledger=[];binding=[]
 for name in spec['groups']:
  p=ROOT/name;g=read(p);gid=g['group_id'];graph=SyntheticGraph.load(p.parent/(gid+'_graph.json'));solver=ExactRouteSolver(graph)
  if len(g['utterances'])!=4 or {u['variant_type'] for u in g['utterances']}!={'V0','V1','V2','V3'}:raise ValueError('VARIANTS')
  for u in g['utterances']:
   uid=u['utterance_id'];ref=refs[uid]
   if u['group_id']!=gid or u['text']!=ref['text']:raise ValueError('TEXT_BINDING '+uid)
   gold=Intent.parse(u['gold_intent']);hard=ref['gold_hard']
   if sorted(gold.pois)!=sorted(hard['pois']) or gold.time_limit!=hard['time_limit']:raise ValueError('GOLD_BINDING '+uid)
   from src.intent import closure
   if closure(gold.dependencies)!=closure([tuple(x) for x in hard['dependencies']]):raise ValueError('DEPENDENCIES '+uid)
   cs={};cost={};routes={}
   for method in ['A','B','review']:
    call=u['calls'].get(method)
    if call is None:raise ValueError('MISSING_CALL '+uid)
    c=None;change=[];error=None
    try:c,change=parse_raw(call.get('raw_response',''),model in ('haiku','sonnet'))
    except (ValueError,TypeError,KeyError) as exc:error=type(exc).__name__
    saved=u['candidates'].get(method)
    if canonical(asdict(c) if c else None)!=canonical(saved):
     raise ValueError('RAW_CANDIDATE_BINDING '+model+' '+uid+' '+method)
    cs[method]=c
    if method in ['A','B'] and call['user_prompt']!=u['text']:raise ValueError('DIRECT_PROMPT_BINDING')
    tok=call.get('usage') or call.get('telemetry')
    cost[method]=(tok.get('total_tokens') if tok and tok.get('total_tokens') is not None else (tok.get('prompt_tokens',0)+tok.get('completion_tokens',0) if tok and 'prompt_tokens' in tok else None))
    ledger.append({'model':model,'uid':uid,'method':method,'raw_valid':c is not None,'error':error,'changes':change,'tokens':cost[method],'returned_model':call.get('returned_model',call.get('model'))})
    routes[method]=solver.solve(**c.solver_args()) if c else None
   rq=json.loads(u['calls']['review']['user_prompt'])
   # Historical prompt uses the same serialized candidate keys; reject instruction mismatch.
   if rq.get('instruction')!=u['text']:raise ValueError('REVIEW_TEXT_BINDING '+uid)
   for key,method in [('candidate_A','A'),('candidate_B','B')]:
    qr=asdict(Intent.parse(rq[key])) if rq.get(key) else None
    if canonical(qr)!=canonical(u['candidates'].get(method)):raise ValueError('REVIEW_CANDIDATE_BINDING '+uid)
   for method in ['A','B']:
    cached=u['routes'].get(method);fresh=asdict(routes[method]) if routes[method] else None
    if cached and fresh:
     if tuple(cached['poi_ids'])!=tuple(fresh['poi_ids']) or cached['is_valid']!=fresh['is_valid']:raise ValueError('ROUTE_BINDING '+uid)
    elif bool(cached)!=bool(fresh):raise ValueError('ROUTE_BINDING '+uid)
   a,b=routes['A'],routes['B'];rev=routes['review'] or a or b
   h=compute_protection_trigger(cs['A'],cs['B'],a,b);du=compute_cross_utility_delta(graph,cs['A'],cs['B'],a,b) if not h else None
   oracle=solver.solve(**gold.solver_args());ou=calculate_route_utility(graph,oracle,gold.quality_weight)
   outcomes=[]
   for r,c in [(a,cs['A']),(rev,cs['review'] or cs['A'] or cs['B'])]:
    ok=bool(r and check_route(graph,r,gold)['task_success']);loss=(ou-calculate_route_utility(graph,r,gold.quality_weight))/2 if ok else None
    if loss is not None and loss < -1e-8:raise ValueError('NEGATIVE_REGRET '+uid)
    direction=ref.get('preference_direction');pred=('quality_first' if c.quality_weight>.5 else 'distance_first' if c.quality_weight<.5 else 'balanced') if c else None
    outcomes.append({'success':ok,'route':list(r.poi_ids) if r else [],'loss':max(0.,loss) if loss is not None else None,'direction_correct':pred==direction if direction in ['quality_first','balanced','distance_first'] else None})
   items.append({'uid':uid,'gid':gid,'variant':u['variant_type'],'cluster':ref.get('source_cluster_id'),'h':h,'du':du,'ds':abs(cs['A'].quality_weight-cs['B'].quality_weight) if cs['A'] and cs['B'] else None,'outcomes':outcomes,'cost':cost,'review_fallback':cs['review'] is None})
 if [it['uid'] for it in items]!=spec['ids']:raise ValueError('IDS_CHANGED')
 return items,ledger

def policies(items):
 n=len(items);h={i for i,x in enumerate(items) if x['h']};other=[i for i in range(n) if i not in h]
 p={'B0':set(),'B6':set(range(n)),'DARC_online':h|{i for i in other if items[i]['du']>.02},'B4_online':h|{i for i in other if items[i]['ds']>.1}}
 for q in [.05,.1,.2]:
  k=int(q*n);prefix=f'q{int(q*100)}:'
  if len(h)>k:continue
  p[prefix+'DARC']=h|set(sorted(other,key=lambda i:(-items[i]['du'],i))[:k-len(h)])
  p[prefix+'B4']=h|set(sorted(other,key=lambda i:(-items[i]['ds'],i))[:k-len(h)])
  for s in range(20):
   r=list(other);random.Random(s).shuffle(r);p[prefix+f'B3_{s}']=h|set(r[:k-len(h)])
 return p

def metrics(items,pol,indices=None):
 indices=list(range(len(items))) if indices is None else indices;n=len(indices);pairs=[]
 by=defaultdict(list)
 for i in indices:by[items[i]['gid']].append(i)
 for gid,ii in by.items():pairs.extend((gid,i,j) for i,j in itertools.combinations(ii,2))
 outcomes={m:{i:items[i]['outcomes'][int(i in sel)] for i in indices} for m,sel in pol.items()}
 # Common reference set for utility uses A and review success, identical for all policies.
 common=[i for i in indices if all(o['success'] for o in items[i]['outcomes'])]
 result={}
 for m,sel in pol.items():
  rows=[outcomes[m][i] for i in indices];oks=[r['success'] for r in rows];tok=[]
  for i in indices:
   needed=['A'] if m=='B0' else ['A','B']+(['review'] if i in sel else [])
   ts=[items[i]['cost'][x] for x in needed];tok.append(sum(ts) if all(x is not None for x in ts) else None)
  goodpairs=[p for p in pairs if outcomes[m][p[1]]['success'] and outcomes[m][p[2]]['success']]
  flip=lambda p:outcomes[m][p[1]]['route']!=outcomes[m][p[2]]['route']
  dirs=[r['direction_correct'] for r in rows if r['direction_correct'] is not None]
  result[m]={'n':n,'tsr':mean(oks),'gtsr':mean([all(outcomes[m][i]['success'] for i in ii) for ii in by.values()]),'degraded_ids':[items[i]['uid'] for i in indices if items[i]['outcomes'][0]['success'] and not outcomes[m][i]['success']],'corrected_ids':[items[i]['uid'] for i in indices if not items[i]['outcomes'][0]['success'] and outcomes[m][i]['success']],'common_utility_n':len(common),'common_success_loss':mean([outcomes[m][i]['loss'] for i in common]),'failure_penalized_loss':mean([r['loss'] if r['success'] else 1. for r in rows]),'direction_n':len(dirs),'direction_accuracy':mean(dirs),'own_success_pairs':len(goodpairs),'own_conditional_flip':mean([flip(p) for p in goodpairs]),'all_pair_flip_or_failure':mean([flip(p) or not outcomes[m][p[1]]['success'] or not outcomes[m][p[2]]['success'] for p in pairs]),'review_count':len(set(indices)&sel),'fallback_selected':sum(items[i]['review_fallback'] for i in indices if i in sel),'logical_calls':n if m=='B0' else 2*n+len(set(indices)&sel),'tokens':sum(tok) if all(x is not None for x in tok) else None,'token_missing_requests':sum(t is None for t in tok)}
 comparisons={}
 for q in [5,10,20]:
  names=[f'q{q}:DARC',f'q{q}:B4']+[f'q{q}:B3_{s}' for s in range(20)]
  if names[0] not in pol:continue
  pp=[p for p in pairs if all(outcomes[m][p[1]]['success'] and outcomes[m][p[2]]['success'] for m in names)]
  counts={gid:len([p for p in pp if p[0]==gid]) for gid in by};gids=list(by)
  totals=np.array([counts[g] for g in gids]);diffs=[]
  for comparator in ['B4','B3_mean']:
   vals=[]
   for gid in gids:
    ps=[p for p in pp if p[0]==gid];d=0.
    for _,i,j in ps:
     a=outcomes[names[0]][i]['route']!=outcomes[names[0]][j]['route']
     bs=names[2:] if comparator=='B3_mean' else [names[1]]
     b=np.mean([outcomes[m][i]['route']!=outcomes[m][j]['route'] for m in bs]);d+=a-b
    vals.append(d)
   rng=np.random.default_rng(20260912);ix=rng.integers(0,len(gids),size=(2000,len(gids)));den=totals[ix].sum(axis=1);valid=den>0;boot=np.array(vals)[ix].sum(axis=1)[valid]/den[valid]
   diffs.append({'vs':comparator,'difference':sum(vals)/len(pp) if pp else None,'ci95':np.quantile(boot,[.025,.975]).tolist() if len(boot) else None,'estimable_resamples':int(valid.sum())})
  comparisons[str(q)]={'common_pairs':len(pp),'all_pairs':len(pairs),'pair_weighted_darc_flip':mean([outcomes[names[0]][i]['route']!=outcomes[names[0]][j]['route'] for _,i,j in pp]),'differences':diffs}
 return {'methods':result,'comparisons':comparisons}

def compute(m):
 joint={};strata={};ledger=[];records={};selections={}
 for model,spec in m['runs'].items():
  items,logs=load(model,spec);ledger+=logs;pol=policies(items);records[model]=items;selections[model]={k:[items[i]['uid'] for i in sorted(v)] for k,v in pol.items()}
  joint[model]=metrics(items,pol)
  if model!='gpt54':
   strata[model]={name:metrics(items,pol,[i for i,x in enumerate(items) if (x['cluster'] in OVERLAP)==over]) for name,over in [('overlap8',True),('remaining32',False)]}
  else:strata[model]={'posthoc_excluding14':metrics(items,pol,[i for i,x in enumerate(items) if x['gid'] not in DRIFT])}
 return {'joint_metrics.json':joint,'fixed_policy_strata.json':strata,'parser_change_ledger.json':ledger,'evaluated_records.json':records,'selections.json':selections}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['build','verify']);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();out=a.out.resolve()
 if a.mode=='build':
  if (out/'manifest.json').exists():raise ValueError('NO_OVERWRITE')
  m=make_manifest(out);r=compute(m)
  for n,v in r.items():write(out/n,v)
  write(out/'outputs.sha256.json',{n:sha(out/n) for n in r});print('BUILD OK')
 else:
  m=verify_inputs(out);hashes=read(out/'outputs.sha256.json');required={'joint_metrics.json','fixed_policy_strata.json','parser_change_ledger.json','evaluated_records.json','selections.json'}
  if set(hashes)!=required:raise ValueError('OUTPUT_INVENTORY')
  for n,d in hashes.items():
   if not (out/n).exists() or sha(out/n)!=d:raise ValueError('OUTPUT_CHANGED '+n)
  r=compute(m)
  for n,v in r.items():
   if canonical(v)!=canonical(read(out/n)):raise ValueError('REPLAY_MISMATCH '+n)
  print('VERIFY AND OFFLINE REPLAY PASS')
if __name__=='__main__':main()
