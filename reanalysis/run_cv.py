import sys, json, numpy as np, pandas as pd
from sklearn.model_selection import KFold
from scipy.stats import wilcoxon
sys.path.insert(0, sys.argv[2])
from common import *

df, X, R, EEG = load(sys.argv[1])
Y = rank_to_score(R)
n = len(X)
SETS = {'all': list(X.columns), 'psych': GARDNER + MBTI, 'eeg': EEG}
MODELS = ['baseline', 'ridge', 'rf', 'gb', 'lgbm']
REPS = int(sys.argv[3]) if len(sys.argv) > 3 else 20

records = []  # rep, model, fs, respondent, metrics
for rep in range(REPS):
    kf = KFold(5, shuffle=True, random_state=rep)
    for tr, te in kf.split(X):
        Xtr, Xte = prep(X.iloc[tr], X.iloc[te])
        for fs, cols in SETS.items():
            for mname in MODELS:
                if fs != 'all' and mname in ('gb', 'lgbm', 'baseline'):
                    continue
                P = fit_predict(mname, Xtr[cols], Y[tr], Xte[cols], seed=rep)
                m = metrics_rows(R[te], scores_to_rank(P))
                for i, idx in enumerate(te):
                    records.append(dict(rep=rep, model=mname, fs=fs, resp=int(idx), **m.iloc[i].to_dict()))
    print('rep', rep, file=sys.stderr)

D = pd.DataFrame(records)
D.to_csv(sys.argv[4] if len(sys.argv) > 4 else 'cv_records.csv', index=False)
