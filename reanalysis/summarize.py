import sys, numpy as np, pandas as pd
from scipy.stats import wilcoxon

def boot_ci(v, B=10000, seed=0):
    rng = np.random.default_rng(seed)
    v = np.asarray(v)
    bs = rng.choice(v, (B, len(v))).mean(axis=1)
    return np.percentile(bs, [2.5, 97.5])

def summarize(path, keys):
    D = pd.read_csv(path)
    out = []
    per_resp = D.groupby(keys + ['resp'])[['rho', 'ndcg5', 'top1', 'mae']].mean().reset_index()
    rep_means = D.groupby(keys + ['rep'])[['rho', 'ndcg5', 'top1', 'mae']].mean().reset_index()
    for k, g in per_resp.groupby(keys):
        k = k if isinstance(k, tuple) else (k,)
        r = rep_means
        for kk, vv in zip(keys, k):
            r = r[r[kk] == vv]
        row = dict(zip(keys, k))
        for met in ['rho', 'ndcg5', 'top1', 'mae']:
            lo, hi = boot_ci(g[met].values)
            row[met] = g[met].mean(); row[met + '_ci'] = f'[{lo:.3f}, {hi:.3f}]'
            row[met + '_rep_range'] = f'[{r[met].quantile(.025):.3f}, {r[met].quantile(.975):.3f}]'
        out.append(row)
    return pd.DataFrame(out), per_resp

def paired(per_resp, keys, a, b, met='rho'):
    def sel(spec):
        s = per_resp
        for kk, vv in zip(keys, spec):
            s = s[s[kk] == vv]
        return s.set_index('resp')[met].sort_index()
    x, y = sel(a), sel(b)
    d = (x - y).values
    lo, hi = boot_ci(d)
    p = wilcoxon(d).pvalue
    return dict(a=a, b=b, metric=met, mean_diff=d.mean(), ci=f'[{lo:.3f}, {hi:.3f}]', wilcoxon_p=p, n_better=int((d > 0).sum()))

if __name__ == '__main__':
    pd.set_option('display.width', 250); pd.set_option('display.max_columns', 30)
    cv, pr = summarize(sys.argv[1], ['fs', 'model'])
    print(cv.round(3).to_string()); print()
    for a, b in [(('all', 'rf'), ('all', 'baseline')), (('psych', 'rf'), ('all', 'baseline')), (('eeg', 'rf'), ('all', 'baseline')),
                 (('psych', 'rf'), ('all', 'rf')), (('eeg', 'rf'), ('psych', 'rf')), (('all', 'ridge'), ('all', 'baseline')),
                 (('psych', 'ridge'), ('all', 'ridge'))]:
        for met in ['rho', 'ndcg5', 'top1']:
            print(paired(pr, ['fs', 'model'], a, b, met))
    if len(sys.argv) > 2:
        print()
        ag, pa = summarize(sys.argv[2], ['regime', 'model'])
        print(ag.round(3).to_string())
        print(paired(pa, ['regime', 'model'], ('fold_synth', 'rf'), ('fold_real_plus_synth', 'rf')))
