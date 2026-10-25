from pathlib import Path
import importlib.util,json
import numpy as np,pandas as pd
p=Path(__file__).parent
spec=importlib.util.spec_from_file_location('cross',p/'analysis_crosscheck.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
d=m.build(p/'synthetic_consensus.xlsx'); d['l2']=np.log2(d.days.where(d.days>0))
fit,cc=m.fit(d,'y',['l2','age','period2015'])
X=fit.model.exog; y=fit.model.endog; prob=fit.predict(); score=X*(y-prob)[:,None]
groups=pd.factorize(cc.report_id)[0]; S=np.stack([score[groups==g].sum(0) for g in np.unique(groups)])
B=np.linalg.inv((X.T*(prob*(1-prob)))@X); n,k=X.shape; G=len(S)
manual=B@S.T@S@B*G/(G-1)*(n-1)/(n-k)
assert np.allclose(manual,fit.cov_params(),rtol=1e-8,atol=1e-10)
assert list(m.category(pd.Series([2,2.5,7,7.1,30,30.1])).cat.codes)==[0,1,1,2,2,3]
assert 'WS0110' in m.omit_overlap_reports(d) and 'WS0105' not in m.omit_overlap_reports(d)
checks={'manual_covariance_max_abs_error':float(np.max(np.abs(manual-fit.cov_params().values))),'n':n,'K':k,'G':G,'boundary_and_overlap_tests':'passed'}
if (p/'r_output'/'primary_precision.csv').exists():
    a=pd.read_csv(p/'python_output'/'primary_precision.csv'); b=pd.read_csv(p/'r_output'/'primary_precision.csv')
    checks['primary_max_abs_difference']=float(np.max(np.abs(a.values-b.values)))
    assert np.allclose(a,b,rtol=1e-6,atol=1e-8)
    a=pd.read_csv(p/'python_output'/'trend_precision.csv'); b=pd.read_csv(p/'r_output'/'trend_precision.csv')
    checks['trend_p_max_abs_difference']=float(np.max(np.abs(a.values-b.values)))
    assert np.allclose(a,b,rtol=1e-6,atol=1e-12)
(p/'verification.json').write_text(json.dumps(checks,indent=2))
print(json.dumps(checks,indent=2))
