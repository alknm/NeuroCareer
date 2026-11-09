"""Sensitivity of NeuroCareer profession rankings to matcher weights and to dropping EEG-based inputs.
Re-implements the matcher formulas of core/matcher.py; role ranks are out-of-fold random-forest predictions."""
import sys, json, numpy as np, pandas as pd, yaml
from scipy.stats import spearmanr
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.model_selection import KFold
sys.path.insert(0, sys.argv[3])
from common import *

df, X, R, EEG = load(sys.argv[1])
profs = yaml.safe_load(open(sys.argv[2], encoding='utf-8'))['professions']
assert len(profs) == 64
n = len(df)

# --- clusters exactly as in build_default_matcher ---
Xn = StandardScaler().fit_transform(df[EEG])
km = KMeans(n_clusters=3, n_init=10, random_state=2).fit(Xn)
lab = {2: 'balanced', 1: 'mobilized', 0: 'depleted'}
clusters = np.array([lab[c] for c in km.labels_])
print('cluster sizes', pd.Series(clusters).value_counts().to_dict(), 'R01,R02,R03:', clusters[:3], file=sys.stderr)

# --- out-of-fold role ranks ---
Y = rank_to_score(R)
def oof(cols, seed=0):
    P = np.zeros_like(Y)
    for tr, te in KFold(5, shuffle=True, random_state=seed).split(X):
        Xtr, Xte = prep(X.iloc[tr], X.iloc[te])
        P[te] = fit_predict('rf', Xtr[cols], Y[tr], Xte[cols], seed=seed)
    return scores_to_rank(P)
ranks_all = oof(list(X.columns))
ranks_psy = oof(GARDNER + MBTI)
role_idx = {r: i for i, r in enumerate(ROLES)}
MB = {'extraversion': 'MBTIЭкстраверт', 'intuition': 'MBTIИнтуитивные', 'thinking': 'MBTIЛогика',
      'judging': 'MBTIПланирующие', 'assertive': 'MBTIУверенные'}

def components(i, ranks):
    row = df.iloc[i]; out = np.zeros((64, 4))
    for k, p in enumerate(profs):
        gi = p.get('gardner_ideal') or {}
        out[k, 0] = np.mean([max(0, 100 - abs(row[nm] - v)) for nm, v in gi.items()]) if gi else 50
        mp = p.get('mbti_preference') or {}
        out[k, 1] = np.mean([max(0, 100 - abs((row[MB[d]] - 50) * 2 - v) / 2) for d, v in mp.items()]) if mp else 50
        cp = p.get('cluster_preference', 'any')
        out[k, 2] = 70 if cp == 'any' else (100 if clusters[i] == cp else 40)
        out[k, 3] = np.mean([max(0, (21 - ranks[i, role_idx[r]]) / 20 * 100) for r in p['top_roles']])
    return out

C_all = np.stack([components(i, ranks_all) for i in range(n)])   # n x 64 x 4
C_psy = np.stack([components(i, ranks_psy) for i in range(n)])
W0 = np.array([.30, .20, .10, .40])

def rank_lists(C, w):
    w = np.asarray(w, float); w = w / w.sum()
    S = C @ w                       # n x 64
    return S, np.argsort(-S, axis=1)

S0, O0 = rank_lists(C_all, W0)
def compare(S, O):
    top1 = np.mean(O[:, 0] == O0[:, 0])
    ov5 = np.mean([len(set(O[i, :5]) & set(O0[i, :5])) for i in range(n)])
    rho = np.mean([spearmanr(S[i], S0[i]).correlation for i in range(n)])
    return dict(top1_same=round(top1, 3), top5_overlap=round(ov5, 2), rho64=round(rho, 3),
                distinct_top1=int(len(set(O[:, 0]))), max_top1_share=round(pd.Series(O[:, 0]).value_counts().iloc[0] / n, 3))

rows = {}
rows['default (0.30/0.20/0.10/0.40)'] = compare(S0, O0)
for name, w in {'equal weights': [1, 1, 1, 1], 'no Gardner': [0, .2, .1, .4], 'no MBTI': [.3, 0, .1, .4],
                'no cluster (EEG)': [.3, .2, 0, .4], 'no roles': [.3, .2, .1, 0]}.items():
    rows[name] = compare(*rank_lists(C_all, w))
rows['headset-free: no cluster, roles from self-report model'] = compare(*rank_lists(C_psy, [.3, .2, 0, .4]))

rng = np.random.default_rng(0)
rand = [compare(*rank_lists(C_all, rng.dirichlet(np.ones(4)))) for _ in range(500)]
R_ = pd.DataFrame(rand)
rows['random weights (Dirichlet, 500 draws) mean'] = R_.mean().round(3).to_dict()
rows['random weights 5th percentile'] = R_.quantile(0.05).round(3).to_dict()
# one-at-a-time perturbation +/-0.10 around default
pert = []
for j in range(4):
    for d in (-0.1, 0.1):
        w = W0.copy(); w[j] = max(0, w[j] + d)
        pert.append(compare(*rank_lists(C_all, w)))
rows['single weight +/-0.10 (mean of 8)'] = pd.DataFrame(pert).mean().round(3).to_dict()

out = pd.DataFrame(rows).T
print(out.to_string())
names = [p['name_en'] for p in profs]
print('\nDefault top-1 professions:', pd.Series([names[k] for k in O0[:, 0]]).value_counts().head(8).to_dict())
print('Top-1 fit score mean/sd:', S0.max(1).mean().round(1), S0.max(1).std().round(1))
out.to_csv(sys.argv[4])
