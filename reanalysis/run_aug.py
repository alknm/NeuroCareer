"""Synthetic augmentation: leaky (copula fitted on all 47, test on same 47) vs honest (copula fitted inside each training fold)."""
import sys, numpy as np, pandas as pd
from sklearn.model_selection import KFold
sys.path.insert(0, sys.argv[2])
from common import *

df, X, R, EEG = load(sys.argv[1])
Y = rank_to_score(R)
cols = list(X.columns)
ycols = [f'y_{r}' for r in ROLES]
REPS = int(sys.argv[3])
NSYN = 500
rec = []

def synth(Xr, Yr, rng):
    full = pd.concat([Xr.reset_index(drop=True), pd.DataFrame(Yr, columns=ycols)], axis=1)
    S = gaussian_copula_sample(full, NSYN, rng)
    Ys = S[ycols].values
    # re-rank synthetic role scores into valid permutation, then back to scores
    Ys = rank_to_score(scores_to_rank(Ys))
    return S[cols], Ys

for rep in range(REPS):
    rng = np.random.default_rng(rep)
    # leaky: generator sees everyone, test on everyone
    Xall, _ = prep(X, X)
    Xs, Ys = synth(Xall, Y, rng)
    for mname in ['baseline', 'ridge', 'rf']:
        P = fit_predict(mname, Xs, Ys, Xall, seed=rep)
        m = metrics_rows(R, scores_to_rank(P))
        for i in range(len(X)):
            rec.append(dict(rep=rep, regime='leaky_synth', model=mname, resp=i, **m.iloc[i].to_dict()))
    # honest: generator fitted within the training fold only
    kf = KFold(5, shuffle=True, random_state=rep)
    for tr, te in kf.split(X):
        Xtr, Xte = prep(X.iloc[tr], X.iloc[te])
        Xs, Ys = synth(Xtr, Y[tr], rng)
        for regime, (XT, YT) in {'fold_synth': (Xs, Ys),
                                 'fold_real_plus_synth': (pd.concat([Xtr.reset_index(drop=True), Xs]), np.vstack([Y[tr], Ys]))}.items():
            for mname in ['ridge', 'rf']:
                P = fit_predict(mname, XT, YT, Xte, seed=rep)
                m = metrics_rows(R[te], scores_to_rank(P))
                for i, idx in enumerate(te):
                    rec.append(dict(rep=rep, regime=regime, model=mname, resp=int(idx), **m.iloc[i].to_dict()))
    print('rep', rep, file=sys.stderr)

pd.DataFrame(rec).to_csv(sys.argv[4], index=False)
