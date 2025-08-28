# netan.py
from __future__ import annotations

"""
Netan — network builder around Rodin-like objects (no external progress/callbacks).

Public API
----------
- create(rodins, names=None) -> Netan
    Validate Rodin objects and return a Netan container.

- class Netan:
    .build(method="spearman", node_mode="samples", layer_mode="stack",
           edge_threshold=0.75, weights=True, layout="force-directed",
           combine="mean", n_jobs=1, **kwargs) -> self
        Build the network (Spearman/CLR/RF/Glasso). Heavy builders show tqdm progress
        *inside* themselves. Graph is stored in self.G. After build, concise network
        stats are printed (overall + per-edge-layer, including 'Entire' and 'consensus').

        Per-method params (via **kwargs):
          * CLR:     n_neighbors=int
          * RF:      n_estimators=int, max_depth=int|None (0/""/None ⇒ None)
          * GLASSO:  alpha=float, max_iter=int, tol=float (default 1e-4)

    .plot(...)
        Interactive Plotly visualization with legend-driven edge pruning.

    .to_csv(path=None, sep=',', index=False)
        Export an edge table with columns:
          source, target, weight, layer, layers
        (suitable for Cityscape/Cytoscape-style uploads)

Assumptions about Rodin-like objects:
- r.X:        pd.DataFrame (features x samples)
- r.samples:  pd.DataFrame (first column = sample IDs, same order as r.X.columns)
- r.features: pd.DataFrame (feature metadata; index aligns with r.X.index)  [optional]
- r.uns:      dict-like with optional {'file_name': str, 'file_type': str}  [optional]
"""

import itertools
import threading
import time
import warnings
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple, Union

import networkx as nx
import numpy as np
import pandas as pd
# keep import to avoid breaking environments that import rodin alongside
import rodin  # noqa: F401
from joblib import Parallel, delayed
from sklearn.covariance import GraphicalLasso
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.feature_selection import mutual_info_regression
from sklearn.exceptions import ConvergenceWarning
from tqdm.auto import tqdm
import plotly.graph_objects as go
from plotly.graph_objs import FigureWidget


# ─────────────────────────────────────────────────────────────────────────────
# Constants / guards
# ─────────────────────────────────────────────────────────────────────────────
MAX_EDGES = 10_000  # UI performance guard

def _ensure_df(x, name: str) -> pd.DataFrame:
    if not isinstance(x, pd.DataFrame):
        raise TypeError(f"{name} must be a pandas.DataFrame")
    return x

# ─────────────────────────────────────────────────────────────────────────────
# Builders (tqdm progress internal)
# ─────────────────────────────────────────────────────────────────────────────
def _corr(df, thr, weight_flag, _guard=True):  
    cor = df.corr("spearman")
    adj = (cor.abs() >= thr).astype(int)
    np.fill_diagonal(adj.values, 0)
    G = nx.from_pandas_adjacency(adj)
    if weight_flag == "on":
        for u, v in G.edges():
            G[u][v]["weight"] = float(abs(cor.loc[u, v]))
    return G, cor.values



def _clr(
    df: pd.DataFrame,
    thr: float,
    weights: bool,
    *,
    n_jobs: int,
    n_neighbors: int = 2,
    _guard: bool = True,
) -> Tuple[nx.Graph, np.ndarray]:
    """Fast CLR (symmetric MI z-scores)."""
    X = df.values.astype("float32", copy=False)
    ids = df.columns.to_list()
    p = X.shape[1]
    MI = np.zeros((p, p), dtype=np.float32)
    edge_count = 0

    def mi_column(j: int):
        return mutual_info_regression(
            X, X[:, j],
            discrete_features=False,
            n_neighbors=n_neighbors,
            random_state=0
        )

    chunk = max(1, min(8, p))
    with tqdm(total=p, desc="CLR", leave=False) as bar:
        for start in range(0, p, chunk):
            cols = range(start, min(start + chunk, p))
            res = Parallel(n_jobs=n_jobs, prefer="threads")(
                delayed(mi_column)(j) for j in cols
            )
            MI[:, cols] = np.column_stack(res)
            for j in cols:
                edge_count += int(np.sum(MI[:j, j] >= thr))
                if _guard and edge_count > MAX_EDGES:
                    warnings.warn(
                        f"Network too dense (limit ≈ {MAX_EDGES}). Increase edgeThreshold."
                    )
            bar.update(len(list(cols)))

    MI = (MI + MI.T) * 0.5
    mu = MI.mean(1, keepdims=True)
    sig = MI.std(1, keepdims=True) + 1e-9
    S = np.sqrt(((MI - mu) / sig) ** 2 + (((MI - mu) / sig).T) ** 2)

    adj = (S >= thr).astype(np.uint8)
    np.fill_diagonal(adj, 0)
    if _guard and int(adj.sum()) // 2 > MAX_EDGES:
        warnings.warn("too many edges")

    G = nx.from_pandas_adjacency(pd.DataFrame(adj, index=ids, columns=ids))
    if weights:
        idx = {v: i for i, v in enumerate(ids)}
        for u, v in G.edges():
            G[u][v]["weight"] = float(abs(S[idx[u], idx[v]]))
    return G, S


def _rf(
    df: pd.DataFrame,
    thr: float,
    weights: bool,
    *,
    n_jobs: int,
    n_estimators: int = 160,
    max_depth: Optional[int] = None,
    _guard: bool = True,
) -> Tuple[nx.Graph, np.ndarray]:
    """ExtraTrees-based symmetric importance matrix."""
    X = df.values.astype("float32", copy=False)
    ids = df.columns.to_list()
    p = len(ids)
    W = np.zeros((p, p), dtype=np.float32)
    edge_count = 0
    if max_depth in (0, "0", ""):
        max_depth = None

    def fit_target(t: int):
        y = X[:, t]
        Xo = np.delete(X, t, axis=1)
        mdl = ExtraTreesRegressor(
            n_estimators=int(n_estimators),
            max_depth=(None if max_depth is None else int(max_depth)),
            random_state=1,
            max_features="sqrt"
        )
        mdl.fit(Xo, y)
        row = np.zeros(p, dtype=np.float32)
        row[np.arange(p) != t] = mdl.feature_importances_
        return t, row

    chunk = max(1, min(4, p))
    with tqdm(total=p, desc="RF", leave=False) as bar:
        for start in range(0, p, chunk):
            idxs = range(start, min(start + chunk, p))

            rows = Parallel(n_jobs=n_jobs, prefer="threads")(
                delayed(fit_target)(t) for t in idxs
            )
            for t, row in rows:
                W[t] = row
                edge_count += int(np.sum(row[:t] >= thr))
                if _guard and edge_count > MAX_EDGES:
                    warnings.warn(
                        f"Network too dense (limit ≈ {MAX_EDGES}). Increase edgeThreshold."
                    )
            bar.update(len(list(idxs)))

    W = (W + W.T) * 0.5
    if thr is None:
        off = W[~np.eye(p, dtype=bool)]
        thr = float(np.nanpercentile(off, 95))

    adj = (W >= float(thr)).astype(np.uint8)
    np.fill_diagonal(adj, 0)
    if _guard and int(adj.sum()) // 2 > MAX_EDGES:
        warnings.warn("too many edges")

    G = nx.from_pandas_adjacency(pd.DataFrame(adj, index=ids, columns=ids))
    if weights:
        idx = {v: i for i, v in enumerate(ids)}
        for u, v in G.edges():
            G[u][v]["weight"] = float(W[idx[u], idx[v]])
    return G, W


def _glasso(
    df: pd.DataFrame,
    thr: float,
    weights: bool,
    *,
    alpha: float = 0.05,
    max_iter: int = 200,
    tol: float = 1e-4,
    ridge_factor: float = 10.0,
    max_ridge_tries: int = 8,
    _guard: bool = True,
) -> Tuple[nx.Graph, np.ndarray]:
    """Graphical Lasso with ETA calibration and density guard."""
    X = df.values.astype("float32", copy=False)
    ids = df.columns.to_list()
    p = X.shape[1]

    CALIB_P = 30
    MIN_T_PRED = 0.5

    def _estimate_runtime_and_edges() -> Tuple[float, int]:
        p_sub = min(p, CALIB_P)
        Xsub = X[:, :p_sub]
        t0 = time.perf_counter()
        mdl = GraphicalLasso(alpha=alpha, max_iter=max(1, max_iter // 4), tol=1e-3).fit(Xsub)
        dt = max(time.perf_counter() - t0, 1e-3)
        k = dt / (p_sub ** 3 * max(1, max_iter // 4))
        t_pred = max(k * p ** 3 * max_iter, MIN_T_PRED)

        prec = mdl.precision_
        d_inv = 1.0 / np.sqrt(np.diag(prec))
        Psub = -prec * d_inv[:, None] * d_inv[None, :]
        np.fill_diagonal(Psub, 0)
        edges_sub = int(np.count_nonzero(np.triu(np.abs(Psub) >= thr, k=1)))
        coeff = (p * (p - 1)) / max(1, (p_sub * (p_sub - 1)))
        edges_pred = int(round(edges_sub * coeff)) / 100
        return t_pred, edges_pred

    t_pred, edges_pred = _estimate_runtime_and_edges()
    if _guard and edges_pred > MAX_EDGES:
        warnings.warn(
            f"Network too dense (limit ≈ {MAX_EDGES}). Increase edgeThreshold."
        )

    result: Dict[str, object] = {}

    def _run_fit():
        cur_alpha = float(alpha)
        last_exc = None
        for _ in range(int(max_ridge_tries)):
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", category=ConvergenceWarning)
                    mdl = GraphicalLasso(alpha=cur_alpha, max_iter=int(max_iter), tol=float(tol))
                    mdl.fit(X)
                result["model"] = mdl
                return
            except (FloatingPointError, np.linalg.LinAlgError, ValueError) as e:
                last_exc = e
                cur_alpha *= float(ridge_factor)
        result["exc"] = last_exc

    th = threading.Thread(target=_run_fit, daemon=True)
    th.start()

    with tqdm(total=100, desc="Glasso", leave=False) as bar:
        t0 = time.perf_counter()
        while th.is_alive():
            frac = min((time.perf_counter() - t0) / max(1e-6, t_pred), 0.99)
            bar.n = int(frac * 100)
            bar.refresh()
            time.sleep(0.2)
        th.join()
        bar.n = 100
        bar.refresh()

    if "exc" in result:
        raise RuntimeError(
            f"GraphicalLasso failed: {result['exc']}\n"
            "Try increasing alpha or preprocessing data."
        )

    model: GraphicalLasso = result["model"]  # type: ignore[assignment]
    if model.precision_ is None:
        raise RuntimeError("glasso failed to converge")

    prec = model.precision_
    d_inv = 1.0 / np.sqrt(np.diag(prec))
    P = -prec * d_inv[:, None] * d_inv[None, :]
    np.fill_diagonal(P, 0.0)

    adj = (np.abs(P) >= thr).astype(np.uint8)
    np.fill_diagonal(adj, 0)
    edge_cnt = int(np.count_nonzero(np.triu(adj, k=1)))
    if _guard and edge_cnt > MAX_EDGES:
        warnings.warn(
            f"Network too dense (limit ≈ {MAX_EDGES}). Increase edgeThreshold."
        )

    G = nx.from_pandas_adjacency(pd.DataFrame(adj, index=ids, columns=ids))
    if weights:
        idx = {v: i for i, v in enumerate(ids)}
        for u, v in G.edges():
            G[u][v]["weight"] = float(abs(P[idx[u], idx[v]]))
    return G, P


BUILDERS = {
    "spearman": _corr,
    "clr": _clr,
    "rf": _rf,
    "glasso": _glasso,
}


# ─────────────────────────────────────────────────────────────────────────────
# Multilayer helpers
# ─────────────────────────────────────────────────────────────────────────────
def _fuse(mats: List[np.ndarray], thr: float, how: str = "mean") -> np.ndarray:
    """Element-wise fuse (mean / median / max) after masking by threshold."""
    masked = [np.where(np.abs(m) >= thr, m, np.nan) for m in mats]
    stack = np.stack(masked, axis=0)
    if how == "mean":
        return np.nanmean(stack, 0)
    if how == "median":
        return np.nanmedian(stack, 0)
    if how == "max":
        return np.nanmax(stack, 0)
    raise ValueError("Unknown fuse mode.")


def _add_cross(Gm, A: pd.DataFrame, B: pd.DataFrame, method: str, thr: float, *, n_jobs: int):
    """
    Add cross-omics edges between two feature matrices A and B.
    Layer name: 'cross_<method>' (e.g., 'cross_spearman', 'cross_glasso').
    """
    shared = list(set(A.columns) & set(B.columns))
    if not shared:
        return
    ia, ib = A.index.to_list(), B.index.to_list()
    expr = pd.concat([A.loc[ia, shared], B.loc[ib, shared]], axis=0)

    if method == "clr":
        _, S = _clr(expr.T[ia + ib], 0.0, False, n_jobs=n_jobs, n_neighbors=2, _guard=False)
    elif method == "rf":
        _, S = _rf(expr.T[ia + ib], 0.0, False, n_jobs=n_jobs, n_estimators=80, max_depth=None, _guard=False)
    elif method == "glasso":
        _, S = _glasso(expr.T[ia + ib], 0.0, False, alpha=0.05, max_iter=200, _guard=False)
    else:
        _, S = _corr(expr.T[ia + ib], 0.0, False)

    block = S[: len(ia), len(ia):]
    for i, u in enumerate(ia):
        for j, v in enumerate(ib):
            w = float(abs(block[i, j]))
            if w >= thr:
                Gm.add_edge(u, v, layer=f"cross_{method}", weight=w)


# ─────────────────────────────────────────────────────────────────────────────
# Container
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class Netan:
    """
    Container for network building.

    Attributes
    ----------
    rodins : list
        Rodin-like objects (must expose .X and .samples).
    names : list[str]
        Human-readable object/layer names per input (same length as rodins).
    samples : list[str]
        Common sample order across all rodins.
    G : nx.Graph | None
        Built graph.
    fig : plotly.graph_objs.FigureWidget | None
        Last interactive plot.
    """
    rodins: List[object]
    names: List[str]
    samples: List[str] = field(repr=False)
    G: Optional[nx.Graph] = None
    fig: Optional[FigureWidget] = field(default=None, repr=False)

    _meta: Dict = None  # last build params

    # ── repr / rich display ──────────────────────────────────────────────────
    def __repr__(self) -> str:
        n_objects = len(self.names)
        built = self.G is not None
        n = self.G.number_of_nodes() if built else 0
        e = self.G.number_of_edges() if built else 0
        nm = (self._meta or {}).get("nodeMode", "?")
        lm = (self._meta or {}).get("layerMode", "?")
        # Collect all edge layers including 'Entire'
        edge_layers = []
        if built:
            s = set()
            for _, _, d in self.G.edges(data=True):
                lays = d.get("layers") or {d.get("layer", "Entire")}
                for L in lays:
                    s.add(str(L))
            edge_layers = sorted(s)
        return (
            "Netan("
            f"rodins={n_objects}:{self.names}, "
            f"node_mode={nm}, layer_mode={lm}, "
            f"nodes={n}, edges={e}, "
            f"edge_layers={edge_layers}"
            ")"
        )

    # Avoid auto-rendering in notebooks when printing the object
    def _repr_mimebundle_(self, *args, **kwargs):
        return None

    def available_layers(self) -> List[str]:
        """Unique edge-layer labels observed on edges (incl. 'Entire', 'consensus' when present)."""
        if self.G is None:
            return list(map(str, self.names))
        s = set()
        for _, _, d in self.G.edges(data=True):
            lays = d.get("layers") or {d.get("layer", "Entire")}
            for L in lays:
                s.add(str(L))
        return sorted(s)

    # ─────────────────────────────────────────────────────────────────────────
    # Build
    # ─────────────────────────────────────────────────────────────────────────
    def build(
        self,
        *,
        method: str = "spearman",
        node_mode: str = "samples",      # "samples" | "features"
        layer_mode: str = "stack",       # "stack" | "multilayer"
        edge_threshold: float = 0.75,
        weights: bool = True,
        layout: str = "force-directed",  # "force-directed"|"spring"|"circular"|"kamada_kawai"|"random"
        combine: str = "mean",           # "mean"|"median"|"max" for multilayer fuse (samples mode)
        n_jobs: int = 1,
        **kwargs,
    ) -> "Netan":
        """
        Build the network and store it in `self.G`. Also assigns a 2D layout
        (node attrs "x","y") and lightweight community labels.

        Parameters
        ----------
        method : {"spearman","clr","rf","glasso"}, default "spearman"
            Network inference method.
            - "spearman": absolute Spearman correlation thresholding.
                          edge_threshold ∈ [0,1].
            - "clr"     : Context Likelihood of Relatedness (MI-based, symmetric Z).
                          Typical thresholds ~2–5 (method-specific scale).
            - "rf"      : ExtraTrees-based symmetric importance matrix.
                          edge_threshold is on [0,1] importance scale.
            - "glasso"  : Graphical Lasso, thresholding absolute partial correlations.
                          edge_threshold ∈ [0,1].

        node_mode : {"samples","features"}, default "samples"
            What nodes represent.
            - "samples": nodes are samples; edges capture sample-sample similarity.
            - "features": nodes are features (prefixed per input to avoid collisions).

        layer_mode : {"stack","multilayer"}, default "stack"
            How to combine multiple inputs.
            - "stack": combine all inputs into one layer ("Entire").
            - "multilayer": build per-input graphs and fuse if needed;
                            edges carry a `layers` set (e.g., {"Entire","Lipidomics"}).
                            In features+multilayer mode, cross-omics edges are added
                            with layer name "cross_<method>".

        edge_threshold : float, default 0.75
            Threshold applied to the method-specific weight matrix before
            converting to edges (see `method` notes).

        weights : bool, default True
            If True, store edge weights in `G[u][v]["weight"]` (method-specific).

        layout : {"force-directed","spring","circular","kamada_kawai","random"}, default "force-directed"
            Layout algorithm used to assign 2D coordinates.

        combine : {"mean","median","max"}, default "mean"
            Fusion rule for multilayer ("samples" mode) when aggregating per-layer matrices.

        n_jobs : int, default 1
            Parallelism for CLR/RF computations.

        **kwargs :
            Extra method-specific parameters:
              - method="clr"    : n_neighbors:int=2
              - method="rf"     : n_estimators:int=160, max_depth:int|None (0/""/None ⇒ None)
              - method="glasso" : alpha:float=0.05, max_iter:int=200, tol:float=1e-4

        Returns
        -------
        self : Netan
            Built container; `self.G` is an undirected graph. Node attrs include:
              - "x","y" (layout), "display_id", "community".
              - (features mode) "object","file","type","compound" for coloring/tooltip.
            Edge attrs include:
              - "weight" (if weights=True), "layer" (string summary),
                "layers" (set of layer names; includes "Entire", may include "consensus").

        Raises
        ------
        ValueError
            If arguments are invalid or Rodin objects fail validation.
        RuntimeError
            If the chosen builder fails to converge (e.g., Graphical Lasso).

        Notes
        -----
        A soft guard of MAX_EDGES is used; if exceeded, warnings are emitted.
        """
        method = method.lower()
        node_mode = node_mode.lower()
        layer_mode = layer_mode.lower()
        combine = combine.lower()
        if len(self.rodins)<2 and layer_mode=="multilayer":
            raise ValueError("For multilayer mode -> multiple rodins should be provided.")
            

        if method not in BUILDERS:
            raise ValueError(f"Unknown method '{method}'. Allowed: {list(BUILDERS)}.")
        if node_mode not in ("samples", "features"):
            raise ValueError("node_mode must be 'samples' or 'features'.")
        if layer_mode not in ("stack", "multilayer"):
            raise ValueError("layer_mode must be 'stack' or 'multilayer'.")
        if layout not in {"force-directed", "spring", "circular", "kamada_kawai", "random"}:
            raise ValueError("layout must be one of "
                             "{'force-directed','spring','circular','kamada_kawai','random'}.")

        frames = [r.X for r in self.rodins]
        weights_flag = bool(weights)

        # ── nodes = samples
        if node_mode == "samples":
            if layer_mode == "stack":
                df = pd.concat(frames, axis=0)
                G, _ = _dispatch_build(method, df, edge_threshold, weights_flag, n_jobs, **kwargs)
                for u, v in G.edges():
                    G[u][v]["layer"] = "Entire"
                    G[u][v]["layers"] = {"Entire"}
            else:
                mats = []
                per_layer_edges: Dict[str, set] = {}
                for nm, r in zip(self.names, self.rodins):
                    Gl, W = _dispatch_build(method, r.X, edge_threshold, weights_flag, n_jobs, **kwargs)
                    mats.append(W)
                    per_layer_edges[nm] = {frozenset((u, v)) for u, v in Gl.edges()}
                fused = _fuse(mats, edge_threshold, combine)
                ids = frames[0].columns.to_list()
                adj = (np.abs(fused) >= edge_threshold).astype(np.uint8)
                np.fill_diagonal(adj, 0)
                G = nx.from_pandas_adjacency(pd.DataFrame(adj, index=ids, columns=ids))
                for i, u in enumerate(ids):
                    for j in range(i + 1, len(ids)):
                        v = ids[j]
                        if not G.has_edge(u, v):
                            continue
                        if weights_flag:
                            G[u][v]["weight"] = float(abs(fused[i, j]))
                        layers = {"Entire"}
                        present = [nm for nm, s in per_layer_edges.items() if frozenset((u, v)) in s]
                        if len(present) == len(self.rodins):
                            layers.add("consensus")
                        layers.update(present)
                        G[u][v]["layers"] = set(layers)
                        G[u][v]["layer"] = ",".join(sorted(layers))

        # ── nodes = features
        else:
            # Tag feature IDs by input name to avoid collisions; keep display_id clean
            tagged: List[pd.DataFrame] = []
            tag_map: Dict[str, str] = {}
            for nm, r in zip(self.names, self.rodins):
                tag = (nm or "layer").replace(".", "_")
                tag_map[tag] = nm
                X = r.X.copy()
                X.index = [f"{tag}__{fid}" for fid in X.index]
                tagged.append(X)

            if layer_mode == "stack":
                df = pd.concat(tagged, axis=0)
                G, _ = _dispatch_build(method, df.T, edge_threshold, weights_flag, n_jobs, **kwargs)
                for u, v in G.edges():
                    G[u][v]["layer"] = "Entire"
                    G[u][v]["layers"] = {"Entire"}
            else:
                Gm = nx.MultiGraph()
                for nm, Xtag in zip(self.names, tagged):
                    Gl, _ = _dispatch_build(method, Xtag.T, edge_threshold, weights_flag, n_jobs, **kwargs)
                    for u, v, d in Gl.edges(data=True):
                        Gm.add_edge(u, v, layer=nm, weight=float(d.get("weight", 1.0)))
                    Gm.add_nodes_from(Gl.nodes(data=True))
                if len(tagged) >= 2:
                    for a, b in itertools.combinations(tagged, 2):
                        _add_cross(Gm, a, b, method, edge_threshold, n_jobs=n_jobs)

                G = nx.Graph()
                for u, v, d in Gm.edges(data=True):
                    if G.has_edge(u, v):
                        if d["weight"] > G[u][v].get("weight", 0.0):
                            G[u][v]["weight"] = d["weight"]
                        G[u][v]["layers"].add(d["layer"])
                    else:
                        G.add_edge(u, v, weight=float(d.get("weight", 1.0)), layers={d["layer"]})
                for u, v in G.edges():
                    G[u][v]["layers"].add("Entire")
                    G[u][v]["layer"] = ",".join(sorted(G[u][v]["layers"]))

        # ── postprocess: cleanups, layout, node attrs
        G.remove_edges_from(nx.selfloop_edges(G))
        if G.number_of_edges() > MAX_EDGES:
            warnings.warn(
                f"Network too dense: {G.number_of_edges()} edges (> {MAX_EDGES})."
            )

        layouts = {
            "force-directed": nx.spring_layout,
            "spring": nx.spring_layout,
            "circular": nx.circular_layout,
            "kamada_kawai": nx.kamada_kawai_layout,
            "random": nx.random_layout,
        }
        key = "force-directed" if layout == "force-directed" else layout

        if key in ("force-directed", "spring"):
            pos = nx.spring_layout(G, seed=777)
        elif key in layouts:
            pos = layouts[key](G)
        else:
            pos = nx.spring_layout(G, seed=777)
            
        for n in G.nodes():
            G.nodes[n]["x"], G.nodes[n]["y"] = map(float, pos[n])
            if "__" in str(n) and node_mode == "features":
                G.nodes[n]["display_id"] = str(n).split("__", 1)[1]
            else:
                G.nodes[n]["display_id"] = str(n)

        # Communities (simple connected-components labeling)
        comps = list(nx.connected_components(G))
        label = 2
        for comp in comps:
            comp = list(comp)
            if len(comp) == 1:
                G.nodes[comp[0]]["community"] = "Group_I"
            else:
                for v in comp:
                    G.nodes[v]["community"] = f"Group_{label}"
                label += 1

        # Features-mode: attach per-node metadata to enable coloring by origin
        if node_mode == "features":
            # Build helpers from rodins to populate object/file/type/compound
            ft_by_tag: Dict[str, str] = {}
            comp_by_id: Dict[str, str] = {}
            for nm, r in zip(self.names, self.rodins):
                tag = (nm or "layer").replace(".", "_")
                ft_by_tag[tag] = str(_uns_get(r, "file_type", ""))

                F = getattr(r, "features", None)
                if F is not None and not F.empty:
                    F = _ensure_df(F, "r.features")
                    F.index = F.index.astype(str)
                    # Leading columns: 2 for metabolomics, else 1
                    lead = 2 if str(_uns_get(r, "file_type", "")).lower() == "metabolomics" else 1
                    for fid in F.index:
                        vals = list(F.loc[fid].iloc[:min(lead, F.shape[1])].astype(str))
                        comp_by_id[f"{tag}__{fid}"] = "_".join(vals) if vals else str(fid)

            # Assign attributes
            for nid in list(G.nodes()):
                if "__" in str(nid):
                    tag = str(nid).split("__", 1)[0]
                    obj = (tag_map.get(tag) if 'tag_map' in locals() else tag)
                    G.nodes[nid]["object"] = obj
                    G.nodes[nid]["file"] = obj
                    if tag in ft_by_tag:
                        G.nodes[nid]["type"] = ft_by_tag[tag]
                    if nid in comp_by_id:
                        G.nodes[nid]["compound"] = comp_by_id[nid]

        self.G = G
        self._meta = dict(
            networkMethod=method,
            edgeThreshold=float(edge_threshold),
            layout=str(layout),
            layerMode=layer_mode,
            nodeMode=node_mode,
            combine=combine,
            weights=bool(weights_flag),
        )

        # ── network stats (overall + per-layer)
        stats = _network_stats(G)
        _print_stats(stats)

        return

    # ─────────────────────────────────────────────────────────────────────────
    # Interactive Plotly plot
    # ─────────────────────────────────────────────────────────────────────────
    def plot(
        self,
        *,
        color: Optional[str] = None,          # column to color nodes by (categorical or continuous)
        shape: Optional[str] = None,          # column to shape nodes by (categorical)
        layer: Optional[str] = None,          # edge-layer filter; edge is kept if the layer is present
        hide_isolated: bool = False,          # drop nodes with no edges after filtering
        weight_min: Optional[float] = None,   # edge weight lower bound
        weight_max: Optional[float] = None,   # edge weight upper bound
        node_size: int = 10,                  # node marker size
        width: Optional[int] = None,          # figure width in pixels
        height: Optional[int] = None,         # figure height in pixels
        title: str = None,
        continuous_colorscale: str = "Viridis"
    ) -> FigureWidget:
        """
        Build an interactive Plotly network.

        Behavior
        --------
        - Categorical color/shape: nodes are split into legend groups; when a group is
          hidden via legend, edges incident to its nodes disappear dynamically.
        - Continuous color: colorbar is shown; legend-based filtering is disabled.

        Returns
        -------
        plotly.graph_objs.FigureWidget

        Raises
        ------
        RuntimeError
            If model is not built yet (self.G is None).
        ValueError
            If provided 'layer', 'color', 'shape', 'node_size', 'width', 'height',
            or 'weight_min/max' are invalid / out of range.
        """
        if self.G is None:
            raise RuntimeError("Build the network first (.build).")

        # Validate numeric inputs early
        if not isinstance(node_size, int) or node_size <= 0:
            raise ValueError("node_size must be a positive integer.")
        if width is not None and (not isinstance(width, int) or width <= 0):
            raise ValueError("width must be a positive integer.")
        if height is not None and (not isinstance(height, int) or height <= 0):
            raise ValueError("height must be a positive integer.")

        def _is_number(x):
            try:
                float(x)
                return True
            except Exception:
                return False

        def _col_type(values: pd.Series) -> str:
            vals = [v for v in values if v is not None and v == v]
            if not vals:
                return "categorical"
            if all(_is_number(v) for v in vals) and len(set(map(float, vals))) >= 6:
                return "continuous"
            return "categorical"

        # ---- Build node dataframe (coords + metadata) ----
        node_rows = []
        for n, d in self.G.nodes(data=True):
            row = {"id": str(n)}
            row.update(d)
            node_rows.append(row)
        nodes_df = pd.DataFrame(node_rows).set_index("id", drop=False)
        for c in ("x", "y", "display_id"):
            if c not in nodes_df.columns:
                nodes_df[c] = None

        node_mode = (self._meta or {}).get("nodeMode", "samples")

        # Join sample/feature metadata for coloring/shaping
        if node_mode == "samples":
            try:
                S = self.rodins[0].samples.copy()
                S = _ensure_df(S, "r.samples")
                S = S.rename(columns={S.columns[0]: "id"})
                S["id"] = S["id"].astype(str)
                S = S.set_index("id", drop=False)
                extra = [c for c in S.columns if c not in ("id",)]
                nodes_df = nodes_df.join(S[extra], how="left")
            except Exception:
                pass
        else:
            # features: map id "<tag>__<featureId>" to r.features by featureId within tag
            tag_to_feat = {}
            for nm, r in zip(self.names, self.rodins):
                tag = (nm or "layer").replace(".", "_")
                F = getattr(r, "features", None)
                if F is not None and not F.empty:
                    F = _ensure_df(F, "r.features").copy()
                    F.index = F.index.astype(str)
                    tag_to_feat[tag] = F
            split = nodes_df["id"].str.split("__", n=1, expand=True)
            if split.shape[1] == 2:
                nodes_df["_tag"] = split[0]
                nodes_df["_fid"] = split[1]
                blocks = []
                for tag, sub in nodes_df.groupby("_tag"):
                    F = tag_to_feat.get(tag)
                    if F is None:
                        continue
                    join_df = sub.merge(
                        F.reset_index().rename(columns={"index": "_fid"}),
                        on="_fid", how="left"
                    )
                    blocks.append(join_df.set_index("id", drop=False))
                if blocks:
                    meta_all = pd.concat(blocks, axis=0)
                    extra_cols = [c for c in meta_all.columns if c not in nodes_df.columns]
                    nodes_df = nodes_df.join(meta_all[extra_cols], how="left")
                for c in ("_tag", "_fid"):
                    if c in nodes_df.columns:
                        nodes_df.drop(columns=c, inplace=True)

            # default color = originating object if not specified
            if not color and "object" in nodes_df.columns:
                color = "object"

        # Validate requested color/shape columns
        available_cols = set(nodes_df.columns)
        if color and color not in available_cols:
            raise ValueError(f"Column '{color}' not found in node metadata. "
                             f"Available columns include: {sorted(available_cols)}")
        if shape and shape not in available_cols:
            raise ValueError(f"Column '{shape}' not found in node metadata. "
                             f"Available columns include: {sorted(available_cols)}")

        # ---- Edge dataframe with layer/weight filters ----
        edge_rows = []
        for u, v, d in self.G.edges(data=True):
            lays = d.get("layers")
            if lays is None:
                lays = {d.get("layer", "Entire")}
            elif not isinstance(lays, (set, list, tuple)):
                lays = {lays}
            edge_rows.append({
                "source": str(u),
                "target": str(v),
                "weight": float(d.get("weight", 1.0)),
                "layers": set(lays)
            })
        edges_df = pd.DataFrame(edge_rows)
        if edges_df.empty:
            fig = FigureWidget(data=[], layout=go.Layout(title=title, width=width, height=height))
            self.fig = fig
            return fig

        # Validate 'layer'
        if layer:
            allowed_layers = self.available_layers()
            if layer not in allowed_layers:
                raise ValueError(f"Unknown layer '{layer}'. Allowed layers: {allowed_layers}")

        # default weight bounds
        wmin = float(edges_df["weight"].min())
        wmax = float(edges_df["weight"].max())
        if weight_min is None:
            weight_min = wmin
        if weight_max is None:
            weight_max = wmax
        if weight_min > weight_max:
            raise ValueError(f"weight_min ({weight_min}) cannot be greater than weight_max ({weight_max}).")
        if weight_min < wmin or weight_max > wmax:
            raise ValueError(f"weight_min/max must lie within [{wmin:.6g}, {wmax:.6g}].")

        # layer filter
        if layer:
            edges_df = edges_df[edges_df["layers"].apply(lambda s: layer in s)].copy()

        # weight filter
        edges_df = edges_df[(edges_df["weight"] >= float(weight_min)) &
                            (edges_df["weight"] <= float(weight_max))].copy()

        # optional: drop isolated nodes after filtering
        if hide_isolated:
            keep_ids = set(edges_df["source"]).union(set(edges_df["target"]))
            nodes_df = nodes_df[nodes_df["id"].isin(keep_ids)].copy()

        # ---- Build traces ----
        # We keep ONE edge trace that we recompute live when legend toggles change.
        pos = nodes_df.set_index("id")[["x", "y"]].astype(float).to_dict(orient="index")

        def build_edge_xy(visible_node_ids: set[str]):
            ex, ey = [], []
            for _, r in edges_df.iterrows():
                s, t = r["source"], r["target"]
                if s in visible_node_ids and t in visible_node_ids:
                    ps, pt = pos.get(s), pos.get(t)
                    if ps and pt:
                        ex += [ps["x"], pt["x"], None]
                        ey += [ps["y"], pt["y"], None]
            return ex, ey

        # Initial visible nodes = all currently plotted nodes
        initial_visible_ids = set(nodes_df["id"].astype(str).tolist())
        ex0, ey0 = build_edge_xy(initial_visible_ids)

        # Edge width ~ mean normalized weight (single width for the polyline)
        denom = max(wmax - wmin, 1e-12)
        widths = 0.75 + 3.0 * ((edges_df["weight"] - wmin) / denom)
        mean_width = float(widths.mean()) if len(widths) else 1.0
        edge_trace = go.Scatter(
            x=ex0, y=ey0, mode="lines", hoverinfo="none",
            line=dict(color="#888", width=mean_width),
            showlegend=False, name="edges"
        )

        traces = [edge_trace]

        # Node groups: build by (color, shape) for categorical behavior
        def _series(name: Optional[str]) -> pd.Series:
            if not name or name not in nodes_df.columns:
                return pd.Series([None] * len(nodes_df), index=nodes_df.index)
            return nodes_df[name]

        color_s = _series(color)
        shape_s = _series(shape)
        color_kind = _col_type(color_s.dropna()) if color else "categorical"

        symbols = ["circle","square","diamond","triangle-up","triangle-down","cross","x","star"]

        # If too many categories for shape → error
        if shape:
            n_shapes = len(pd.Series(shape_s.fillna("all")).astype(str).unique())
            if n_shapes > len(symbols):
                raise ValueError(
                    f"'shape' column '{shape}' has {n_shapes} unique values; "
                    f"this exceeds available symbols ({len(symbols)}). "
                    f"Reduce categories or map to fewer values."
                )

        if color and color_kind == "continuous":
            # Ensure column is actually numeric after coercion
            if pd.to_numeric(nodes_df[color], errors="coerce").notna().sum() == 0:
                raise ValueError(f"Column '{color}' cannot be interpreted as numeric for continuous coloring.")
            # Shape must be categorical
            if shape and _col_type(shape_s.dropna()) == "continuous":
                raise ValueError(f"Column '{shape}' looks continuous, but 'shape' expects a categorical variable.")

            shp_vals = shape_s.fillna("all").astype(str).unique().tolist()
            shp_map = {v: symbols[i % len(symbols)] for i, v in enumerate(sorted(shp_vals))}
            for i, sv in enumerate(sorted(shp_vals)):
                sub = nodes_df[shape_s.fillna("all").astype(str) == sv]
                hover = [
                    f"ID: {r.get('display_id', r['id'])}"
                    + (f"<br>{color}: {r[color]}" if color else "")
                    + (f"<br>{shape}: {sv}" if shape else "")
                    for _, r in sub.iterrows()
                ]
                traces.append(go.Scatter(
                    x=sub["x"].astype(float), y=sub["y"].astype(float),
                    mode="markers", name=str(sv), hoverinfo="text", text=hover,
                    showlegend=False,  # continuous: legend toggles are off
                    customdata=sub["id"].astype(str),
                    marker=dict(
                        color=pd.to_numeric(sub[color], errors="coerce"),
                        colorscale=continuous_colorscale,
                        showscale=(i == 0),
                        colorbar=(dict(title=color) if i == 0 else None),
                        symbol=shp_map.get(sv, "circle"),
                        size=node_size,
                        line=dict(width=1, color="#333")
                    )
                ))
        else:
            # Categorical color/shape
            palette = [
                "#c0392b","#2980b9","#27ae60","#e67e22","#8e44ad","#8d6e63",
                "#d81b60","#7f8c8d","#f4c20d","#00acc1","#ad1457",
                "#afc52f","#556b2f","#6d214f","#303f9f","#bdc3c7","#9b59b6",
                "#3f51b5","#ff7043","#c0b283","#40e0d0"
            ]
            color_vals = sorted(map(str, pd.Series(color_s.fillna("all")).unique().tolist()))
            shape_vals = sorted(map(str, pd.Series(shape_s.fillna("all")).unique().tolist()))
            c_map = {v: palette[i % len(palette)] for i, v in enumerate(color_vals)}
            s_map = {v: symbols[i % len(symbols)] for i, v in enumerate(shape_vals)}

            key = (pd.Series(color_s.fillna("all").astype(str).values, index=nodes_df.index)
                   + "||" +
                   pd.Series(shape_s.fillna("all").astype(str).values, index=nodes_df.index))
            nodes_df["_grp"] = key

            for grp, sub in nodes_df.groupby("_grp"):
                c_val, s_val = grp.split("||", 1)
                name = c_val if (color and not shape) else (s_val if (shape and not color) else f"{c_val} | {s_val}")
                hover = [
                    f"ID: {r.get('display_id', r['id'])}"
                    + (f"<br>{color}: {c_val}" if color else "")
                    + (f"<br>{shape}: {s_val}" if shape else "")
                    + (f"<br>compound: {r.get('compound','')}" if 'compound' in r and r.get('compound') else "")
                    for _, r in sub.iterrows()
                ]
                traces.append(go.Scatter(
                    x=sub["x"].astype(float), y=sub["y"].astype(float),
                    mode="markers", name=name, legendgroup=name,
                    hoverinfo="text", text=hover,
                    customdata=sub["id"].astype(str),  # for legend-driven edge rebuilds
                    marker=dict(
                        color=c_map.get(c_val, "#000"),
                        symbol=s_map.get(s_val, "circle"),
                        size=node_size,
                        line=dict(width=1, color="#333")
                    )
                ))
            nodes_df.drop(columns=["_grp"], inplace=True)

        layout = go.Layout(
            title=title, hovermode="closest", showlegend=True,
            margin=dict(l=20, r=60, t=50, b=20),
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            width=width, height=height,
            uirevision="netan"  # keep zoom when rebuilding edges
        )

        fig = FigureWidget(data=traces, layout=layout)

        # ---- Legend-aware edge rebuilding (categorical mode) ----
        def _visible_node_ids() -> set[str]:
            ids = set()
            # data[0] is the edge polyline; node traces start from index 1
            for tr in fig.data[1:]:
                vis = tr.visible
                if vis in (True, None):  # None == default visible
                    cd = getattr(tr, "customdata", None)
                    if cd is not None:
                        ids.update(map(str, cd))
            return ids

        def _rebuild_edges(*_args):
            ids = _visible_node_ids()
            ex, ey = build_edge_xy(ids)
            with fig.batch_update():
                fig.data[0].x = ex
                fig.data[0].y = ey

        # Wire callbacks only for node traces (skip edges trace at index 0)
        for tr in fig.data[1:]:
            tr.on_change(_rebuild_edges, "visible")

        self.fig = fig
        try:
            get_ipython  # есть IPython -> показываем как виджет/фигуру
            from IPython.display import display
            display(fig)
        except Exception:
            fig.show()
            
        return fig

    # ─────────────────────────────────────────────────────────────────────────
    # CSV export (Cityscape/Cytoscape-style edge table)
    # ─────────────────────────────────────────────────────────────────────────
    def to_csv(
        self,
        path: Optional[str] = None,
        *,
        sep: str = ",",
        index: bool = False,
        float_format: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Export the edge list as a flat table suitable for Cytoscape import.
    
        Columns:
          - source, target : node IDs (strings)
          - weight         : edge weight (float; 1.0 if missing)
          - layer          : compact summary of layers
          - layers         : all layers joined with "|" so Cytoscape parses a list
          - source_compound, target_compound : ONLY in 'features' node mode;
                                               omitted in 'samples' mode.
    
        Notes
        -----
        * In Cytoscape Import Wizard, set Advanced → List delimiter to "|"
          so 'layers' is recognized as a List of String.
        """
        if self.G is None:
            raise RuntimeError("Build the network first (.build).")
    
        node_mode = (self._meta or {}).get("nodeMode", "samples")
        nodes = dict(self.G.nodes(data=True))
        rows = []
    
        for u, v in self.G.edges():
            d = self.G[u][v]
            weight = float(d.get("weight", 1.0))
    
            # Collect layers robustly and join with pipe for Cytoscape
            lays = d.get("layers", None)
            if lays is None:
                lays = {d.get("layer", "Entire")}
            elif not isinstance(lays, (set, list, tuple)):
                lays = {lays}
            layers_list = sorted(map(str, list(lays)))
            layers_str = "|".join(layers_list)
            layer_str = d.get("layer") or ",".join(layers_list)
    
            row = {
                "source": str(u),
                "target": str(v),
                "weight": weight,
                "layer": layer_str,
                "layers": layers_str,
            }
    
            if node_mode == "features":
                su = nodes.get(u, {})
                sv = nodes.get(v, {})
                row["source_compound"] = su.get("compound", "") or ""
                row["target_compound"] = sv.get("compound", "") or ""
    
            rows.append(row)
    
        cols = ["source", "target", "weight", "layer", "layers"]
        if node_mode == "features":
            cols += ["source_compound", "target_compound"]
    
        df = pd.DataFrame(rows, columns=cols)
        if path:
            df.to_csv(path, sep=sep, index=index, float_format=float_format)
        return df




# ─────────────────────────────────────────────────────────────────────────────
# Stats helpers
# ─────────────────────────────────────────────────────────────────────────────
def _network_stats(G: nx.Graph) -> Dict:
    """Return overall stats plus per-layer stats (incl. 'Entire' and 'consensus' if present)."""
    deg = dict(G.degree())
    active_nodes = [n for n, d in deg.items() if d > 0]
    out: Dict[str, Union[int, float, dict]] = {
        "numNodes": G.number_of_nodes(),
        "numEdges": G.number_of_edges(),
        "nodesWithEdges": len(active_nodes),
        "densityActive": round(nx.density(G.subgraph(active_nodes)), 4) if len(active_nodes) > 1 else 0.0,
        "densityAll": round(nx.density(G), 4),
        "numComponents": nx.number_connected_components(G),
        "numCommunities": nx.number_connected_components(G) - sum(1 for d in deg.values() if d < 1),
    }

    # Per-layer edges and nodes — include 'Entire' and any others on edges
    layer_stats: Dict[str, Dict[str, Union[int, float]]] = {}
    all_layers = set()
    for _, _, d in G.edges(data=True):
        lays = d.get("layers") or {d.get("layer", "Entire")}
        for L in lays:
            all_layers.add(str(L))
    for L in sorted(all_layers):
        layer_edges = [(u, v) for u, v, d in G.edges(data=True)
                       if L in (d.get("layers") or {d.get("layer", "Entire")})]
        Gl = G.edge_subgraph(layer_edges).copy()
        n_nodes = Gl.number_of_nodes()
        n_edges = Gl.number_of_edges()
        dens = round(nx.density(Gl), 4) if n_nodes > 1 else 0.0
        layer_stats[L] = {"nodes": n_nodes, "edges": n_edges, "density": dens}

    out["layerStats"] = layer_stats
    return out


def _print_stats(stats: Dict):
    core = (
        f"[Netan] nodes={stats['numNodes']} | edges={stats['numEdges']} | "
        f"active_nodes={stats['nodesWithEdges']} | "
        f"density_all={stats['densityAll']} | density_active={stats['densityActive']} | "
        f"components={stats['numComponents']} | communities={stats['numCommunities']}"
    )
    print(core)
    ls = stats.get("layerStats", {})
    if ls:
        for L in sorted(k for k in ls.keys() if k and k != "Entire"):
            s = ls[L]
            print(f"  [Layer {L}] nodes={s['nodes']} | edges={s['edges']} | density={s['density']}")


# ─────────────────────────────────────────────────────────────────────────────
# Dispatch
# ─────────────────────────────────────────────────────────────────────────────
def _dispatch_build(
    method: str,
    df: pd.DataFrame,
    thr: float,
    weights: bool,
    n_jobs: int,
    **kwargs,
):
    method = method.lower()

    if method == "clr":
        return _clr(df, thr, weights, n_jobs=n_jobs, n_neighbors=int(kwargs.get("n_neighbors", 2)))
    if method == "rf":
        md = kwargs.get("max_depth", None)
        return _rf(
            df, thr, weights,
            n_jobs=n_jobs,
            n_estimators=int(kwargs.get("n_estimators", 80)),
            max_depth=(None if md in (None, "", 0, "0") else int(md)),
        )
    if method == "glasso":
        return _glasso(
            df, thr, weights,
            alpha=float(kwargs.get("alpha", kwargs.get("glassoAlpha", 0.05))),
            max_iter=int(kwargs.get("max_iter", kwargs.get("glassoMaxIter", 200))),
            tol=float(kwargs.get("tol", 1e-4)),
        )
    # default
    return _corr(df, thr, weights)


# ─────────────────────────────────────────────────────────────────────────────
# Factory
# ─────────────────────────────────────────────────────────────────────────────
def common_samples(objs) -> List[str]:
    """
    Return sample IDs present in every object's `.samples` table.

    Definition
    ----------
    A "sample ID" is taken from the FIRST column of `r.samples`. Values are
    coerced to `str`. The returned order preserves the order from the first
    object, with duplicates removed if any.

    Parameters
    ----------
    objs : object or Sequence[object]
        A single Rodin-like object (with `.samples: pd.DataFrame`) or a
        sequence of such objects.

    Returns
    -------
    List[str]
        Sample IDs that appear in the first column of `.samples` for every
        object, ordered as in the first object's `.samples`.

    Raises
    ------
    ValueError
        If no objects are provided, or an object has a missing/malformed
        `samples` table (e.g., not a DataFrame or has no columns).
    """
    
    if not isinstance(objs, (list, tuple)):
        objs = [objs]
    if not objs:
        raise ValueError("Provide at least one object.")

    first = list(map(str, objs[0].X.columns))
    common = set(first)
    for r in objs[1:]:
        common &= set(map(str, r.X.columns))

    # Preserve first-object order; drop duplicates while keeping first occurrence
    seen = set()
    ordered = []
    for s in first:
        if s in common and s not in seen:
            seen.add(s)
            ordered.append(s)
    return ordered


def _uns_get(r, key: str, default=None):
    uns = getattr(r, "uns", None)
    if isinstance(uns, dict):
        return uns.get(key, default)
    if uns is None:
        return default
    # dict-like objects without .get() or attr-style objects
    return getattr(uns, key, default)



def create(
    rodins: Union[object, Sequence[object]],
    names: Optional[Sequence[str]] = None,
) -> "Netan":
    """
    Build a Netan container from one or multiple Rodin-like objects by
    aligning them to a shared set of samples.
    """
    objs = [rodins] if not isinstance(rodins, (list, tuple)) else list(rodins)
    if not objs:
        raise ValueError("Provide at least one Rodin-like object.")

    # --- capture pre-stats (for concise prints) ---
    orig_ids_list = []
    orig_shapes = []
    for r in objs:
        try:
            orig_ids_list.append(list(map(str, r.samples.iloc[:, 0])))
        except Exception:
            orig_ids_list.append([])
        try:
            orig_shapes.append(tuple(getattr(r, "X").shape))
        except Exception:
            orig_shapes.append((None, None))

    ids = common_samples(objs)
    if not ids:
        raise ValueError("No common samples across provided objects.")

    # what gets excluded in each object (vs common)
    excluded_per_obj = []
    ids_set = set(ids)
    for orig_ids in orig_ids_list:
        excluded_per_obj.append([s for s in orig_ids if s not in ids_set])

    # Reorder/trim each object to the shared order (logic unchanged)
    objs = [r[r.X.loc[:, ids]] for r in objs]
    [r.samples.reset_index(drop=True, inplace=True) for r in objs]

    # --- post-stats ---
    final_shapes = []
    for r in objs:
        try:
            final_shapes.append(tuple(getattr(r, "X").shape))
        except Exception:
            final_shapes.append((None, None))

    # Names (logic unchanged)
    if names is None:
        names = [str(_uns_get(r, "file_name") or f"layer{i}") for i, r in enumerate(objs, 1)]
    else:
        if len(names) != len(objs):
            raise ValueError("Length of 'names' must match number of rodin objects.")
        names = list(map(str, names))

    # --- concise prints ---
    def _preview(lst, n=8):
        if not lst:
            return "-"
        return ", ".join(lst[:n]) + (f", … (+{len(lst)-n})" if len(lst) > n else "")

    if len(objs)>1:
        print(f"[Netan] common samples: {len(ids)} -> {_preview(ids)}")
        for i, (nm, os, fs, excl) in enumerate(zip(names, orig_shapes, final_shapes, excluded_per_obj), start=1):
            os_str = f"{os[0]}x{os[1]}" if os[0] is not None else "N/A"
            fs_str = f"{fs[0]}x{fs[1]}" if fs[0] is not None else "N/A"
            if len(excl)>0:
                print(f"[Netan] {nm}: X {os_str} -> {fs_str}; dropped {len(excl)}: {_preview(excl)}")
            else:
                print(f"[Netan] {nm}: X {os_str}")
    else:
        print(f"[Netan] {names[0]}: X {objs[0].X.shape[0]}x{objs[0].X.shape[1]}")
        

    return Netan(rodins=objs, names=names, samples=ids)
