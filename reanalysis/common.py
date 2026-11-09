import numpy as np, pandas as pd
from scipy.stats import norm, spearmanr
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
import lightgbm as lgb

GARDNER = ['Натуралистический интеллект','Внутриличностный интеллект','Логико-математический интеллект',
           'Лингвистический интеллект','Телесно-кинестетический интеллект','Пространственно-визуальный интеллект',
           'Музыкальный интеллект','Экзистенциальный интеллект','Межличностный интеллект']
MBTI = ['MBTIЭкстраверт','MBTIИнтуитивные','MBTIЛогика','MBTIПланирующие','MBTIУверенные']
ROLES = ['Focus Expert','Optimist','Brainstormer','Catalyst','Analyst','Winner','Storyteller','Problem Solver',
         'Strategist','Thinker','Believer','Time Keeper','Peace Keeper','Deliverer','Commander','Philomath',
         'Chameleon','Coach','Self-Believer','Empathizer']

def load(path):
    df = pd.read_csv(path)
    eeg = [c for c in df.columns if c.startswith('neiry')]
    assert len(eeg) == 24
    X = df[GARDNER + MBTI + eeg].astype(float).copy()
    R = df[ROLES].astype(int).values
    assert all(sorted(r) == list(range(1, 21)) for r in R)
    return df, X, R, eeg

def winsorize_fit(Xtr, col, q=0.99):
    return np.quantile(Xtr[col], q)

def rank_to_score(R):
    return norm.ppf((20 - R + 0.5) / 20)

def scores_to_rank(S):
    # higher score -> rank 1
    order = np.argsort(-S, axis=1)
    ranks = np.empty_like(order)
    for i in range(S.shape[0]):
        ranks[i, order[i]] = np.arange(1, 21)
    return ranks

def ndcg5(true_rank, pred_rank):
    rel = 21 - true_rank  # graded relevance 20..1
    top = np.argsort(pred_rank)[:5]
    dcg = sum(rel[j] / np.log2(k + 2) for k, j in enumerate(top))
    ideal = np.sort(rel)[::-1][:5]
    idcg = sum(r / np.log2(k + 2) for k, r in enumerate(ideal))
    return dcg / idcg

def metrics_rows(Rtrue, Rpred):
    out = []
    for t, p in zip(Rtrue, Rpred):
        out.append(dict(rho=spearmanr(t, p).correlation, ndcg5=ndcg5(t, p),
                        top1=float(np.argmin(p) == np.argmin(t)), mae=np.mean(np.abs(t - p))))
    return pd.DataFrame(out)

def make_model(name, seed=0):
    if name == 'ridge':
        return make_pipeline(StandardScaler(), Ridge(alpha=1.0))
    if name == 'rf':
        return RandomForestRegressor(n_estimators=300, min_samples_leaf=2, random_state=seed, n_jobs=-1)
    if name == 'gb':
        return MultiOutputRegressor(GradientBoostingRegressor(n_estimators=200, max_depth=3, learning_rate=0.05, random_state=seed))
    if name == 'lgbm':
        return MultiOutputRegressor(lgb.LGBMRegressor(n_estimators=400, learning_rate=0.05, min_child_samples=5, random_state=seed, verbose=-1, n_jobs=1))
    raise ValueError(name)

def fit_predict(name, Xtr, Ytr, Xte, seed=0):
    if name == 'baseline':
        return np.tile(Ytr.mean(axis=0), (len(Xte), 1))
    m = make_model(name, seed)
    m.fit(Xtr, Ytr)
    return m.predict(Xte)

def prep(Xtr, Xte):
    Xtr = Xtr.copy(); Xte = Xte.copy()
    col = 'neiryFatigue score'
    cap = winsorize_fit(Xtr, col)
    Xtr[col] = Xtr[col].clip(upper=cap); Xte[col] = Xte[col].clip(upper=cap)
    return Xtr, Xte

def gaussian_copula_sample(Xtr, n, rng):
    """Fit a Gaussian copula with empirical marginals on Xtr (DataFrame incl. score columns); sample n rows."""
    A = Xtr.values.astype(float)
    m, d = A.shape
    # normal scores of ranks
    ranks = A.argsort(axis=0).argsort(axis=0) + 1
    Z = norm.ppf(ranks / (m + 1))
    C = np.corrcoef(Z, rowvar=False)
    C = C + 1e-6 * np.eye(d)
    Zs = rng.multivariate_normal(np.zeros(d), C, size=n)
    U = norm.cdf(Zs)
    out = np.empty_like(Zs)
    for j in range(d):
        out[:, j] = np.quantile(A[:, j], U[:, j])  # empirical inverse CDF (linear interpolation)
    return pd.DataFrame(out, columns=Xtr.columns)
