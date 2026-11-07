import sys,csv,numpy as np
D=sys.argv[1]
sox={};spx={}
for r in csv.reader(open(D+"/sox_c.csv")):
    if r and r[0][:2] in("19","20"): sox[r[0]]=float(r[1])
for r in list(csv.reader(open(D+"/h1.csv")))[1:]: spx[r[0]]=float(r[1])
for r in list(csv.reader(open(D+"/g_c.csv")))[2:]:
    if r[0]>="2015": spx[r[0]]=float(r[5])
dates=[k for k in sorted(sox) if k in spx]
lr=np.log(np.array([sox[k]/spx[k] for k in dates]))
i0=dates.index("2025-06-20"); ip=dates.index("2026-06-22"); ie=dates.index("2026-10-28")
L=ip-i0; P=ie-ip
tgt=lr[i0:ie+1]-lr[ip]
print("dates",dates[0],dates[-1],"L",L,"P",P)
res=[]
for c in range(L,len(dates)-P):
    if dates[c]>="2025-01-01": break
    w=lr[c-L:c+P+1]-lr[c]
    rmse=np.sqrt(np.mean((np.exp(w)-np.exp(tgt))**2))*100
    rpre=np.sqrt(np.mean((np.exp(w[:L])-np.exp(tgt[:L]))**2))*100
    rpost=np.sqrt(np.mean((np.exp(w[L:])-np.exp(tgt[L:]))**2))*100
    corr=np.corrcoef(w,tgt)[0,1]
    res.append((rmse,dates[c],corr,rpre,rpost))
res.sort()
picked=[]
for r in res:
    if all(abs((np.datetime64(r[1])-np.datetime64(p[1])).astype(int))>120 for p in picked): picked.append(r)
    if len(picked)==10: break
print("top analogs by RMSE (index points, peak=100 scale):")
for r in picked: print(f"{r[1]}  RMSE {r[0]:5.1f}  pre {r[3]:5.1f}  post {r[4]:5.1f}  corr {r[2]:.3f}")
allr=np.array([r[0] for r in res]); print("percentile of 2000-03-10:", [ (i,r) for i,r in enumerate(res) if r[1]=="2000-03-10"][0][0], "of", len(res))
print("median RMSE all", np.median(allr))
# what followed top analogs: ratio change from c+P to c+P+126, +252 trading days
for r in picked[:6]:
    c=dates.index(r[1]); 
    def chg(n): return (np.exp(lr[c+P+n]-lr[c+P])-1)*100 if c+P+n<len(dates) else None
    print(r[1], "relative SOX/SPX after equivalent date: +6m", None if chg(126) is None else round(chg(126),1), "+12m", None if chg(252) is None else round(chg(252),1), " equiv date", dates[c+P])
