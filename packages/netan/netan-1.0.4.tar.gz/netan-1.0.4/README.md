# Netan — Multilayer Network Builder for Rodin‑like Objects

**Netan** builds multilayer networks from omics matrices and gives you clean APIs to analyze, visualize, and export them. It supports Spearman, CLR (MI‑z), ExtraTrees‑RF, and Graphical Lasso; both *samples* and *features* node modes; stacked or multilayer graphs (with optional `consensus` edges); cross‑omics links; an interactive Plotly viewer; and Cytoscape‑ready CSV export.

Web App: **netan.io**

> **Works with any *Rodin‑like* object** exposing:
> - `r.X`: `pandas.DataFrame` (**features × samples**)
> - `r.samples`: `pandas.DataFrame` (first column = sample IDs; order matches `r.X.columns`)
> - `r.features` *(optional)*: `pandas.DataFrame` (index = feature IDs; used for tooltips/colors in *features* mode)
>
> See also: https://github.com/BM-Boris/rodin

---

## Installation

```bash
pip install netan
```

> Requires Python ≥ 3.10. Installs dependencies automatically: `rodin` (recent), `numpy`, `pandas`, `networkx`, `scikit-learn`, `joblib`, `tqdm`, `plotly`.

---

## Quick Start (Rodin-based)

Below is a **ready‑to‑run example** using two omics tables that share the same samples.

```python
import rodin
import netan

# 1) Create one or multiple Rodin objects from data + metadata
r1 = rodin.create("metabolomics.txt", "meta.csv")
r2 = rodin.create("transcriptomics.csv", "meta.csv")

# 2) Preprocess (Rodin handles normalization/log/scale etc.)
r1.transform()
r2.transform()

# 3) Build a multilayer network across shared samples
nt = netan.create([r1, r2])
nt.build(
    method="spearman",        # inference: 'spearman'|'clr'|'rf'|'glasso'
    edge_threshold=0.75,       # method-specific threshold
    layer_mode="multilayer",  # 'stack' or 'multilayer'
    node_mode="samples",      # 'samples' or 'features'
    weights=True,
)

# 4) Interactive Plotly graph (FigureWidget)
fig = nt.plot(
    title="Netan • Samples × Multilayer (Spearman, thr=0.75)",
    color="pGroup",           # column from r.samples to color nodes (optional)
    node_size=12,
    width=950,
    height=650,
)

# 5) Export an edge table compatible with Cytoscape
edges = nt.to_csv("edges.csv")
```

---

## Concepts at a Glance

- **Node mode**
  - `samples`: nodes are samples; edges reflect sample–sample similarity.
  - `features`: nodes are features; feature IDs are prefixed per input to avoid collisions; optional cross‑omics edges are added in multilayer mode.

- **Layer mode**
  - `stack`: combine all inputs into a single layer named `"Entire"`.
  - `multilayer`: keep per‑input layers; edges store a `layers` set (always includes `"Entire"`; adds `"consensus"` if present in *all* inputs).

- **Methods & thresholds**
  - `spearman`: absolute Spearman correlation; threshold ∈ **[0,1]**.
  - `clr`: Context Likelihood of Relatedness (MI‑based symmetric Z); typical thresholds ~ **2–5**.
  - `rf`: ExtraTrees‑based symmetric importance; threshold on **[0,1]**.
  - `glasso`: Graphical Lasso; threshold on |partial correlation| ∈ **[0,1]**.

- **Cross‑omics links** *(features+multilayer)*
  - Adds edges between layers using the chosen method; labeled as `cross_<method>`.

---

## Layouts (computed at plot time)

`plot()` computes node positions **after** applying UI filters (layer, `weight_min/weight_max`, `hide_isolated`). That means the layout reflects exactly what you visualize.

- Supported: `{ "force-directed", "spring", "circular", "kamada_kawai", "random" }`.
- `"force-directed"` is an alias for NetworkX `spring_layout`.
- Edge weights (when present) are passed to spring/force-directed, so stronger edges pull nodes closer.
- Use `layout_seed` for reproducibility in stochastic layouts.

---

## API Overview

### `create(rodins, names=None) -> Netan`
Builds a container from one or multiple Rodin‑like objects by aligning them to shared samples. Prints concise pre/post stats.

- **Parameters**
  - `rodins`: one object or a list of objects exposing `.X` and `.samples` (optionally `.features`, `.uns`).
  - `names`: optional list of human‑readable layer names (defaults to `r.uns['file_name']` or `layer{i}`).

- **Returns**: `Netan` (with `.G` unset until you call `.build`).

---

### `Netan.build(method='spearman', node_mode='samples', layer_mode='stack', edge_threshold=0.75, weights=True, combine='mean', n_jobs=1, **kwargs) -> self`
Constructs the network into `self.G` and stores a 2D layout on nodes.

- **Common parameters**
  - `method`: `'spearman' | 'clr' | 'rf' | 'glasso'`.
  - `node_mode`: `'samples' | 'features'`.
  - `layer_mode`: `'stack' | 'multilayer'`.
  - `edge_threshold`: float — threshold on the method‑specific weight matrix.
  - `weights`: bool — attach edge weights as `G[u][v]['weight']`.
  - `combine`: `'mean'|'median'|'max'` — fusion rule in `samples+multilayer` mode.
  - `n_jobs`: int — parallelism for CLR/RF computations.

- **Method‑specific `**kwargs`**
  - `clr`: `n_neighbors=int`.
  - `rf`: `n_estimators=int`, `max_depth=int|None` (0/''/None ⇒ `None`).
  - `glasso`: `alpha=float`, `max_iter=int`, `tol=float` (default `1e-4`).

- **Returns**: `self`. After the call, `self.G` is a `networkx.Graph` where edges carry `weight`, `layer`, `layers`; nodes have `display_id`, `community` (and in *features* mode: `object`, `file`, `type`, `compound` when metadata is available).

---

### `Netan.plot(color=None, shape=None, layer=None, hide_isolated=False, weight_min=None, weight_max=None, node_size=10, width=None, height=None, title=None, continuous_colorscale='Viridis', layout='force-directed', layout_seed=777) -> plotly.graph_objs.FigureWidget`
Creates an interactive Plotly network.

- **Color/shape**
  - *Categorical* color/shape: nodes split into legend groups; toggling legend hides incident edges live.
  - *Continuous* color: shows a colorbar; legend toggles are disabled.

- **Layer/weight filters**
  - `layer`: keep an edge if this label is present in its `layers` set.
  - `weight_min/max`: numeric bounds to prune edges.
  - `hide_isolated`: optionally drop nodes with no edges after filtering.

- **Layout**
  - `{ 'force-directed','spring','circular','kamada_kawai','random' }`; set `layout_seed` for reproducibility.

- **Returns**: a `FigureWidget` suitable for notebooks/dashboards.

---

### `Netan.to_csv(path=None, sep=',', index=False, float_format=None) -> pandas.DataFrame`
Exports a flat edge list.

- **Columns**: `source, target, weight, layer, layers`.
- *Features* mode adds: `source_compound, target_compound` (when available).
- **Cytoscape tip**: set **Import → Advanced → List delimiter = `|`** so `layers` parses as a list.

---

## Threshold Tips

- **Spearman**: `0.7–0.9` (higher → sparser).
- **CLR**: `2–5` (start at `≈3`).
- **RF (ExtraTrees)**: `0.02–0.10`.
- **Glasso**: `edge_threshold 0.1–0.3`; if convergence is tricky, increase `alpha` (e.g., `0.1–0.2`).

---

## Performance & Limits

- Soft **density guard** around ~10,000 edges (`MAX_EDGES`): warnings suggest raising thresholds or reducing variables.
- Complexity (roughly):
  - `spearman/CLR/RF` ~ O(p²) in the number of nodes per layer.
  - `glasso` ~ O(p³); consider increasing `alpha` or reducing dimensionality.
- Use `n_jobs` to parallelize CLR/RF.

---

## Troubleshooting

- **Graph too dense** → raise `edge_threshold`, switch to a stricter method (`glasso`), or reduce variables.
- **`GraphicalLasso failed`** → increase `alpha` (e.g., `0.1–0.2`), relax `tol`, ensure scaling is appropriate.
- **Empty plot** → check `layer`/`weight_min/max` filters and that inputs share sample IDs.
- **Too many categories for `shape`** → map values to fewer categories (limited symbol set).

---

## License

MIT (see `LICENSE`).

