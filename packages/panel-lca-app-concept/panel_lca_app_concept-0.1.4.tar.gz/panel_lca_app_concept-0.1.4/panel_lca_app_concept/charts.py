import plotly.graph_objects as go
import pandas as pd
from panel_lca_app_concept.data import STAGES, PRODUCTS, REACTANTS, PROCESSES, PRODUCT_MAT_SHARES, MAT_PROC_SHARES
from panel_lca_app_concept.theming import current_bg_color

def _prep(df: pd.DataFrame, norm: bool) -> pd.DataFrame:
    if not norm: return df
    g = df.groupby("product")["value"].transform("sum")
    out = df.copy(); out["value"] = out["value"] / g
    return out

def plot_stacked_bars(df, norm=False, colors=None) -> go.Figure:
    df = _prep(df, norm)
    wide = df.pivot(index="product", columns="stage", values="value").fillna(0)
    bg = current_bg_color()
    fig = go.Figure()
    for i, stage in enumerate(STAGES):
        if stage not in wide.columns: continue
        fig.add_trace(go.Bar(
            name=stage, x=wide.index, y=wide[stage],
            hovertemplate=("%{x}<br>Stage: "+stage+"<br>"+
                           ("Value: %{y:.1f} kg CO₂e" if not norm else "Share: %{y:.0%}")+
                           "<extra></extra>"),
            marker={"color": (colors[i] if colors else None),
                    "line":{"width":2,"color":bg}, "cornerradius":8}
        ))
    fig.update_layout(barmode="stack", xaxis_title="", yaxis_title=("kg CO₂e" if not norm else "Share"),
                      hovermode="closest", legend_title_text="Stage",
                      margin=dict(l=10,r=10,t=40,b=10), uirevision="keep",
                      paper_bgcolor=bg, plot_bgcolor=bg)
    return fig

def update_stacked_bars(fig, df, norm=False, colors=None):
    df = _prep(df, norm)
    wide = df.pivot(index="product", columns="stage", values="value").fillna(0)
    bg = current_bg_color()
    for i, stage in enumerate(STAGES):
        if stage not in wide.columns: continue
        fig.data[i].x = wide.index; fig.data[i].y = wide[stage]
        fig.data[i].hovertemplate = ("%{x}<br>Stage: "+stage+"<br>"+
                                     ("Value: %{y:.1f} kg CO₂e" if not norm else "Share: %{y:.0%}")+
                                     "<extra></extra>")
        fig.data[i].marker.line.color = bg
        if colors: fig.data[i].marker.color = colors[i]
    fig.update_layout(yaxis_title=("kg CO₂e" if not norm else "Share"))

def plot_sankey(df) -> go.Figure:
    import numpy as np
    # totals and flows
    prod_totals = df.groupby("product")["value"].sum().reindex(PRODUCTS, fill_value=0)
    pm = PRODUCT_MAT_SHARES.mul(prod_totals, axis=0)
    mat_totals = pm.sum(axis=0).reindex(REACTANTS, fill_value=0)
    mp = MAT_PROC_SHARES.mul(mat_totals, axis=0)
    # nodes / indices
    nodes = ["Total footprint"] + PRODUCTS + REACTANTS + PROCESSES
    idx_total = 0
    idx_prod = {p: i+1 for i,p in enumerate(PRODUCTS)}
    off_mat = 1+len(PRODUCTS)
    idx_mat = {m: off_mat+i for i,m in enumerate(REACTANTS)}
    off_proc = off_mat + len(REACTANTS)
    idx_proc = {r: off_proc+i for i,r in enumerate(PROCESSES)}
    # links
    src,tgt,val=[],[],[]
    for p in PRODUCTS: src+= [idx_total]; tgt+= [idx_prod[p]]; val+= [float(prod_totals[p])]
    for p in PRODUCTS:
        for m in REACTANTS: src+= [idx_prod[p]]; tgt+= [idx_mat[m]]; val+= [float(pm.loc[p,m])]
    for m in REACTANTS:
        for r in PROCESSES: src+= [idx_mat[m]]; tgt+= [idx_proc[r]]; val+= [float(mp.loc[m,r])]
    # colors
    rng = np.random.default_rng(0)
    node_cols = [f"rgba({50+rng.integers(0,205)},{50+rng.integers(0,205)},{50+rng.integers(0,205)},1.0)" for _ in nodes]
    link_cols = [node_cols[s].replace(",1.0)",",0.5)") for s in src]
    return go.Figure([go.Sankey(arrangement="snap",
        node=dict(label=nodes, pad=15, thickness=20, color=node_cols),
        link=dict(source=src, target=tgt, value=val, color=link_cols)
    )])

def update_sankey(fig, df):
    prod_totals = df.groupby("product")["value"].sum().reindex(PRODUCTS, fill_value=0)
    pm = PRODUCT_MAT_SHARES.mul(prod_totals, axis=0)
    mat_totals = pm.sum(axis=0).reindex(REACTANTS, fill_value=0)
    mp = MAT_PROC_SHARES.mul(mat_totals, axis=0)
    vals=[]
    for p in PRODUCTS: vals.append(float(prod_totals[p]))
    for p in PRODUCTS:
        for m in REACTANTS: vals.append(float(pm.loc[p,m]))
    for m in REACTANTS:
        for r in PROCESSES: vals.append(float(mp.loc[m,r]))
    fig.data[0].link.value = vals