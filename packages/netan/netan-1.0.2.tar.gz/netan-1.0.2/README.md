# Netan — Multilayer Network Builder for Rodin‑like Objects

**Netan** builds multilayer networks from omics matrices and gives you clean APIs to analyze, visualize, and export them. It supports Spearman, CLR (MI‑z), ExtraTrees‑RF, and Graphical Lasso; both *samples* and *features* node modes; stacked or multilayer graphs (with `consensus` edges); cross‑omics links; an interactive Plotly viewer; and Cytoscape‑ready CSV export.

Web App: [netan.io](https://netan.io)

> **Works with any *Rodin‑like* object** exposing:
> - `r.X`: `pandas.DataFrame` (features × samples)
> - `r.samples`: `pandas.DataFrame` (first column = sample IDs; order = `r.X.columns`)
> - `r.features`: `pandas.DataFrame` (index = feature IDs)

> - check https://github.com/BM-Boris/rodin

---

## Installation

```bash
pip install netan
```

> Requires Python ≥ 3.10. Dependencies (installed automatically): `rodin>=1.9.10`, `numpy`, `pandas`, `networkx`, `scikit-learn`, `joblib`, `tqdm`, `plotly`.

---

## Quick Start (with Rodin)

Below is a **ready‑to‑run** .

```python
import rodin
import netan

# 1) Create one or multiple Rodin objects from omics data + metadata
r1 = rodin.create( 'metabolomics.txt', 'meta.csv'
    )

r2 = rodin.create( 'transcriptomics.csv', 'meta.csv'
    )

# 2) Apply your preprocessing (Rodin handles normalization/log/scale etc.)
r1.transform()
r2.transform()

# 3) Build a multilayer network across shared samples
nt = netan.create([r1, r2])
nt.build(
    method='spearman',        # network inference method
    edge_threshold=0.75,       # threshold on method-specific weights
    layer_mode='multilayer',  # 'stack' or 'multilayer'
)

# 4) Interactive Plotly graph (FigureWidget)
fig = nt.plot(
    title='Netan: Samples × Multilayer (Spearman, threshold=0.75)',
    node_size=12,
    width=950,
    height=650
)

# 5) Export an edge table compatible with Cytoscape
nt.to_csv()
```


---

## What Netan Does

- **Aligns samples** across inputs.
- **Infers networks** per method:
  - `spearman`: absolute Spearman correlation, threshold ∈ [0,1].
  - `clr`: Context Likelihood of Relatedness (MI‑based symmetric Z). Typical thresholds ~2–5.
  - `rf`: ExtraTrees‑based symmetric importance; threshold on [0,1].
  - `glasso`: Graphical Lasso; threshold on |partial correlation| ∈ [0,1].
- **Combines layers**:
  - `layer_mode='stack'`: single layer `"Entire"`.
  - `layer_mode='multilayer'`: per‑input graphs; edges carry a `layers` set (includes `"Entire"`; adds `"consensus"` if present in all inputs).
  - In *features*+multilayer mode: adds cross‑omics edges labeled `cross_<method>`.
- **Layouts & communities**: assigns 2D coordinates (`x`,`y`) and lightweight component labels for easy plotting.
- **Interactive Plotly**: legend‑driven node group toggles dynamically rebuild edge polylines; continuous color shows a colorbar.
- **CSV export**: `source,target,weight,layer,layers` (Cytoscape‑friendly; set `List delimiter = "|"`).

---

### `create(rodins, names=None) -> Netan`
Builds a `Netan` container from one or multiple Rodin‑like objects by aligning them to shared samples. Prints concise pre/post stats.

- **Parameters**
  - `rodins`: a single object or a list of objects exposing `.X` and `.samples` (optionally `.features`, `.uns`).
  - `names`: optional list of human‑readable layer names (defaults to `r.uns['file_name']` or `layer{i}`).

- **Returns**: `Netan` (with `.G` unset until you call `.build`).

### `Netan.build(method='rf', node_mode='samples', layer_mode='multilayer', edge_threshold=0.025, weights=True, layout='force-directed', combine='mean', n_jobs=-1, **kwargs) -> self`
Constructs the network in `self.G` and stores a 2D layout on nodes.

- **Common parameters**
  - `method`: `'spearman' | 'clr' | 'rf' | 'glasso'`.
  - `node_mode`: `'samples' | 'features'` — whether nodes represent samples or features.
  - `layer_mode`: `'stack' | 'multilayer'` — combine inputs into one layer or keep them separate with fusion.
  - `edge_threshold`: float — threshold applied to the method‑specific weight matrix.
  - `weights`: bool — store edge weights as `G[u][v]['weight']`.
  - `layout`: `'force-directed'|'spring'|'circular'|'kamada_kawai'|'random'` — determines `x`,`y`.
  - `combine`: `'mean'|'median'|'max'` — fusion rule in `samples+multilayer` mode.
  - `n_jobs`: int — parallelism for CLR/RF.

- **Method‑specific `**kwargs`**
  - `clr`: `n_neighbors=int`.
  - `rf`: `n_estimators=int`, `max_depth=int|None` (0/''/None ⇒ `None`).
  - `glasso`: `alpha=float`, `max_iter=int`, `tol=float` (default 1e‑4).

- **Returns**: `self`. After the call, `self.G` is a `networkx.Graph` with edge attributes `weight`, `layer`, `layers`; nodes have `x`,`y`,`display_id`,`community` (and in features mode: `object`,`file`,`type`,`compound` when metadata is available).

### `Netan.plot(color=None, shape=None, layer=None, hide_isolated=False, weight_min=None, weight_max=None, node_size=10, width=None, height=None, title='Network Plot', continuous_colorscale='Viridis') -> plotly.graph_objs.FigureWidget`
Creates an interactive Plotly network figure.

- **Color/shape**
  - *Categorical* color/shape splits nodes into legend groups; hiding a group removes its incident edges on the fly.
  - *Continuous* color shows a colorbar (legend toggling disabled).

- **Layer/weight filters**
  - `layer`: keep an edge if that layer label is present in its `layers` set.
  - `weight_min/max`: numeric bounds for pruning edges by weight.

- **Display**: returns a `FigureWidget` suitable for notebooks/dashboards.

### `Netan.to_csv(path=None, sep=',', index=False, float_format=None) -> pandas.DataFrame`
Exports a flat edge list. Columns: `source, target, weight, layer, layers`.

- In *features* node mode: adds `source_compound, target_compound` if known.
- **Cytoscape tip**: set **Advanced → List delimiter = `|`** so `layers` parses as list.

---

## Threshold Tips

- **Spearman**: `0.7–0.9` (use higher for sparser graphs).
- **CLR**: `2–5` (start at `3`).
- **RF (ExtraTrees)**: `0.02–0.10`.
- **Glasso**: `0.1–0.3` for `edge_threshold`; increase `alpha` (`0.1–0.2`) if convergence is hard.

---

## Performance & Limits

- Soft **density guard** around ~10,000 edges (`MAX_EDGES`); warnings suggest raising thresholds or reducing nodes.
- Complexity:
  - `spearman/CLR/RF`: ~O(p²) in the number of nodes per layer.
  - `glasso`: ~O(p³)`; consider increasing `alpha` or reducing dimensionality.
- Use `n_jobs` to parallelize CLR/RF.

---

## Troubleshooting

- **Graph too dense** → raise `edge_threshold`, use a stricter method (`glasso`), or reduce variables.
- **`GraphicalLasso failed`** → increase `alpha` (e.g., `0.1–0.2`), relax `tol`, ensure proper scaling.
- **Empty plot** → check `layer` and `weight_min/max` filters and that inputs share sample IDs.
- **Too many categories for `shape`** → map values to fewer categories (limited symbol set).

---

## License

MIT (see `LICENSE`).

