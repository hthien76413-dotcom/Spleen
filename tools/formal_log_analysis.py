"""Analyse Rayyan's formal-screening export (articles.csv + customizations_log.csv) beyond the conflict list.

Used on 12 Oct 2026 after the formal title/abstract screening of 2,548 records. Prints: user-to-reviewer mapping
(matched on decisions, not on e-mail), AI-prescreen label events, bulk operations (>=5 decision events within one
second), how each reviewer's final decisions were set, pace between first decisions, agreement by phase, default
reasons, labels, and writes a de-identified copy of the event log (reviewer labels R1/R2 and WS ids only).

Usage: python3 -I tools/formal_log_analysis.py RAW_DIR OUT_DIR
  RAW_DIR  folder with articles.csv and customizations_log.csv (these contain e-mail addresses: never commit them)
  OUT_DIR  folder with screening_results_all.csv written by tools/screening_conflicts.py; the de-identified log is written here
R1 = display name '俊', R2 = display name 'Fei' (as printed in the export).
"""
import sys
RAW, OUT = sys.argv[1], sys.argv[2]
import csv, re, collections, json, datetime as dt
csv.field_size_limit(10**9)
log=list(csv.DictReader(open(RAW+'/customizations_log.csv',encoding='utf-8-sig',newline='')))
art=list(csv.DictReader(open(RAW+'/articles.csv',encoding='utf-8-sig',newline='')))
res={r['rayyan_id']:r for r in csv.DictReader(open(OUT+'/screening_results_all.csv',encoding='utf-8-sig',newline=''))}
dec={}
for r in art:
    m=re.search(r'RAYYAN-INCLUSION: (\{.*?\})',r['notes'] or '')
    dec[r['key'].replace('rayyan-','')]=dict(re.findall(r'"([^"]+)"=>"([^"]+)"',m.group(1))) if m else {}
VAL={'1':'Included','0':'Maybe','-1':'Excluded'}
log.sort(key=lambda e:e['created_at'])
last={}
for e in log:
    if e['key']=='included': last[(e['user_id'],e['article_id'])]=VAL.get(e['value'])
score=collections.defaultdict(collections.Counter)
for (u,a),v in last.items():
    for name,val in dec.get(a,{}).items(): score[(u,name)][v==val]+=1
users=sorted({e['user_id'] for e in log}); mp={}
for u in users:
    mp[u]=max(['俊','Fei'],key=lambda n:score[(u,n)][True]); print('log user',len([x for x in mp])+0,'-> reviewer',mp[u],'; decisions matching the export:',score[(u,mp[u])][True],'of',sum(score[(u,mp[u])].values()))
def who(e): return {'俊':'R1','Fei':'R2'}[mp[e['user_id']]]
def ts(e): return dt.datetime.strptime(e['created_at'],'%Y-%m-%dT%H:%M:%S.%fZ')
# --- AI-prescreen
ai=[e for e in log if e['key']=='"AI-prescreen"']
print('\nAI-prescreen events',len(ai), collections.Counter((who(e),e['value']) for e in ai))
print('first/last',ts(ai[0]),ts(ai[-1]))
days=collections.Counter((who(e),ts(e).strftime('%m-%d %H')) for e in ai); print(sorted(days.items())[:30])
# decisions of the AI-prescreen articles
ai_ids={e['article_id'] for e in ai if e['value']=='1'}
print('distinct articles with AI-prescreen set:',len(ai_ids))
c=collections.Counter()
for a in ai_ids:
    r=res.get(a)
    if r: c[(r['R1_JunShu_decision'],r['R2_FeiPeng_decision'])]+=1
print('decisions on those articles (R1,R2):',c.most_common())
# --- order of events for a few AI articles
for a in list(ai_ids)[:3]:
    print(a,[(ts(e).strftime('%m-%d %H:%M:%S'),who(e),e['key'],e['value']) for e in log if e['article_id']==a])

print('\n===== bulk operations (>=5 decision events in the same second, same user) =====')
byk=collections.defaultdict(list)
for e in log:
    if e['key']=='included': byk[(who(e),e['created_at'][:19])].append(e)
bulk=[(k,v) for k,v in byk.items() if len(v)>=5]
print('number of such seconds',len(bulk))
for k,v in sorted(bulk,key=lambda kv:-len(kv[1]))[:15]:
    ws=sorted(int(res[e['article_id']]['ws_id'][2:]) for e in v if e['article_id'] in res)
    print(k,len(v),collections.Counter(e['value'] for e in v),'WS range',ws[0],ws[-1])
tot=sum(len(v) for k,v in bulk); print('decision events inside such bulk seconds:',tot)
print('\n===== per-reviewer timeline =====')
for r in ('R1','R2'):
    ev=[e for e in log if e['key']=='included' and who(e)==r]
    first=min(ts(e) for e in ev); lastt=max(ts(e) for e in ev)
    print(r,'decision events',len(ev),'first',first,'last',lastt)
    # first decision per article
    fd={}
    for e in ev: fd.setdefault(e['article_id'],ts(e))
    d=collections.Counter(x.strftime('%m-%d') for x in fd.values()); print('  first decisions per UTC day',sorted(d.items()))
    print('  distinct articles',len(fd),' articles with >1 decision event',sum(1 for a in fd if sum(1 for e in ev if e['article_id']==a)>1) if False else '')

print('\n===== bulk vs individual: how was each reviewer\'s FINAL decision set =====')
BULK_N=5
cnt=collections.Counter((who(e),e['created_at'][:19]) for e in log if e['key']=='included')
final_ev={}
for e in log:
    if e['key']=='included': final_ev[(who(e),e['article_id'])]=e
out=collections.defaultdict(collections.Counter)
for (r,a),e in final_ev.items():
    bulk=cnt[(r,e['created_at'][:19])]>=BULK_N
    out[r][('bulk' if bulk else 'single', VAL[e['value']])]+=1
for r in out: print(r,dict(out[r]))
# conflicts involving R2 bulk final decisions
print('\n===== the 642 conflicts: how R2 / R1 final decision was set =====')
cc=collections.Counter()
for a,rr in res.items():
    d1,d2=rr['R1_JunShu_decision'],rr['R2_FeiPeng_decision']
    adv1=d1 in('Include','Maybe'); adv2=d2 in('Include','Maybe')
    if adv1!=adv2:
        e1=final_ev[('R1',a)]; e2=final_ev[('R2',a)]
        cc[(d1,d2,'R1bulk' if cnt[('R1',e1['created_at'][:19])]>=BULK_N else 'R1single','R2bulk' if cnt[('R2',e2['created_at'][:19])]>=BULK_N else 'R2single')]+=1
for k,v in sorted(cc.items(),key=lambda kv:-kv[1]): print(v,k)
# R1 reasonless excludes
print('\n===== R1 Excludes without reason =====')
reas=collections.defaultdict(set)
for e in log:
    if e['key'].startswith('"__EXR__') and e['value']=='1': reas[(who(e),e['article_id'])].add(e['key'])
nr=[a for a,rr in res.items() if rr['R1_JunShu_decision']=='Exclude' and not rr['R1_JunShu_reason']]
print(len(nr))
tsn=collections.Counter(final_ev[('R1',a)]['created_at'][:16] for a in nr); print(sorted(tsn.items())[:40])
cnt1=collections.Counter(cnt[('R1',final_ev[('R1',a)]['created_at'][:19])]>=BULK_N for a in nr); print('bulk?',cnt1)
wsn=sorted(int(res[a]['ws_id'][2:]) for a in nr); print('WS range',wsn[0],wsn[-1]); 
print('R1 decision by type for these:',collections.Counter(res[a]['type'] for a in nr))
print('R2 decisions on these 310:',collections.Counter(res[a]['R2_FeiPeng_decision'] for a in nr))

print('\n===== R2 activity 2026-10-10 16:40 - 2026-10-11 01:30 UTC, per minute (key:count) =====')
win=[e for e in log if who(e)=='R2' and '2026-10-10T16:40'<=e['created_at'][:16]<='2026-10-11T01:30']
pm=collections.defaultdict(collections.Counter)
for e in win: pm[e['created_at'][:16]][e['key'].replace('"__EXR__','R:').strip('"')+('='+e['value'] if e['key']=='included' or e['value']=='deleted' else '')]+=1
for m in sorted(pm): print(m,dict(pm[m]))

print('\n===== pace: gaps between consecutive FIRST decisions per article (single events only) =====')
import statistics
for r in ('R1','R2'):
    fe={}
    for e in log:
        if e['key']=='included' and who(e)==r: fe.setdefault(e['article_id'],e)
    ev=sorted(fe.values(),key=lambda e:ts(e))
    gaps=[(ts(b)-ts(a)).total_seconds() for a,b in zip(ev,ev[1:])]
    s=sorted(gaps); n=len(s)
    print(r,'n',n+1,'median gap',statistics.median(gaps),'p10',s[n//10],'p90',s[9*n//10],' gaps<=3s:',sum(1 for g in gaps if g<=3),' gaps<=1s:',sum(1 for g in gaps if g<=1))
    # active time: sum of gaps <=120s
    print('   active time (gaps<=120s) hours',round(sum(g for g in gaps if g<=120)/3600,2),' wall span days',round((ts(ev[-1])-ts(ev[0])).total_seconds()/86400,2))
print('\n===== R2 bulk groups: reasons applied in the same second =====')
reas_ev=collections.defaultdict(list)
for e in log:
    if e['key'].startswith('"__EXR__') and e['value']=='1': reas_ev[(who(e),e['created_at'][:19])].append(e['key'].replace('"__EXR__','').strip('"'))
rg=collections.Counter()
for (r,sec),n in cnt.items():
    if r=='R2' and n>=5: rg[tuple(sorted(collections.Counter(reas_ev.get((r,sec),[])).items()))]+=n
for k,v in rg.most_common(12): print(v,k)
print('R2 bulk seconds time span:',min(s for (r,s),n in cnt.items() if r=='R2' and n>=5),max(s for (r,s),n in cnt.items() if r=='R2' and n>=5))
print('\n===== R2 bulk-excluded articles: R1 decision and language/type =====')
bk={a for (r,a),e in final_ev.items() if r=='R2' and cnt[('R2',e['created_at'][:19])]>=5}
print(len(bk),collections.Counter(res[a]['R1_JunShu_decision'] for a in bk))
print(collections.Counter(res[a]['language'][:3].lower() for a in bk).most_common(6), collections.Counter(res[a]['type'] for a in bk))

print('\n===== R2 first decisions per UTC hour with median gap to previous first decision =====')
def firsts(r):
    fe={}
    for e in log:
        if e['key']=='included' and who(e)==r: fe.setdefault(e['article_id'],e)
    return sorted(fe.values(),key=lambda e:ts(e))
for r in ('R2','R1'):
    ev=firsts(r); prev=None; hh=collections.defaultdict(list)
    for e in ev:
        if prev is not None: hh[ts(e).strftime('%m-%d %H')].append((ts(e)-ts(prev)).total_seconds())
        prev=e
    print(r)
    for h in sorted(hh): print('  ',h,'n',len(hh[h]),'median gap',round(statistics.median(hh[h]),1),'bulk-excluded share' if False else '')
print('\n===== R2 pace by decision type (gap before first decision) =====')
ev=firsts('R2'); byt=collections.defaultdict(list)
for a,b in zip(ev,ev[1:]):
    byt[VAL[b['value']]].append((ts(b)-ts(a)).total_seconds())
for k,v in byt.items(): print(k,len(v),'median',round(statistics.median(v),1))
print('\n===== is R2 working in list order? (WS number of consecutive first decisions) =====')
ws=[int(res[e['article_id']]['ws_id'][2:]) for e in ev]
inc=sum(1 for a,b in zip(ws,ws[1:]) if b==a+1); print('consecutive +1 steps',inc,'of',len(ws)-1)

print('\n===== agreement by phase (R2 careful phase = first 180 list positions vs the rest) =====')
def kappa(pairs,cats):
    n=len(pairs); po=sum(1 for a,b in pairs if a==b)/n
    pe=sum((sum(1 for a,_ in pairs if a==c)/n)*(sum(1 for _,b in pairs if b==c)/n) for c in cats)
    return po,(po-pe)/(1-pe) if pe<1 else float('nan')
rows=sorted(res.values(),key=lambda r:int(r['ws_id'][2:]))
def adv(d): return 'adv' if d in('Include','Maybe') else 'exc'
for name,sub in (('WS0001-0180',rows[:180]),('WS0181-2548',rows[180:])):
    p3=[(r['R1_JunShu_decision'],r['R2_FeiPeng_decision']) for r in sub]
    p2=[(adv(a),adv(b)) for a,b in p3]
    a3,k3=kappa(p3,['Include','Maybe','Exclude']); a2,k2=kappa(p2,['adv','exc'])
    print(name,len(sub),'3-cat agree %.3f kappa %.3f | advance-vs-exclude agree %.3f kappa %.3f'%(a3,k3,a2,k2),
          '| R1 adv share %.2f R2 adv share %.2f'%(sum(1 for a,b in p2 if a=='adv')/len(p2),sum(1 for a,b in p2 if b=='adv')/len(p2)))

print('\n===== default reasons / labels / E5 =====')
for e in log:
    k=e['key']
    if k in ('"__EXR__background article"','"__EXR__wrong publication type"') and e['value']=='1':
        r=res.get(e['article_id']); print('default reason',k,who(e),e['created_at'],r['ws_id'] if r else None,(r['title'][:70] if r else ''), '| R1:',r['R1_JunShu_decision'],'R2:',r['R2_FeiPeng_decision'])
lab=collections.Counter((who(e),e['key'],e['value']) for e in log if not e['key'].startswith('"__EXR__') and e['key']!='included')
for k,v in sorted(lab.items()): print(k,v)
e5=[e for e in log if e['key']=='"__EXR__E5 not a formal article"' and e['value']=='1']
print('E5 first use',who(e5[0]),e5[0]['created_at'],res[e5[0]['article_id']]['ws_id'],' uses by',collections.Counter(who(e) for e in e5))
rs=collections.Counter()
for r in res.values():
    for k,tag in (('R1_JunShu_reason','R1'),('R2_FeiPeng_reason','R2')): 
        if r[k]: rs[(tag,r[k])]+=1
print(sorted(rs.items()))
print('\nfirst formal decision per reviewer (UTC):')
for r in ('R1','R2'):
    ev=[e for e in log if e['key']=='included' and who(e)==r]; print(r,min(e['created_at'] for e in ev),'last',max(e['created_at'] for e in ev))
# de-identified log for the repo
ws_of={a:r['ws_id'] for a,r in res.items()}
with open(OUT+'/formal_decisions_log_deidentified.csv','w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f); w.writerow(['created_at_utc','reviewer','ws_id','key','value'])
    for e in log:
        w.writerow([e['created_at'],who(e),ws_of.get(e['article_id'],''),e['key'].strip('"'),e['value']])
print('wrote de-identified log rows',len(log))
