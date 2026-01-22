import os
import glob
import streamlit as st
import numpy as np
from shapely.geometry import Polygon, MultiPolygon

# --- Core import (robust) ---
dxf_analiz_et = None
_import_errors = []
for modname in ("ai_core", "ai_core_v8", "ai_core_v7", "ai_core_son", "ai_core_patched_v5"):
    try:
        mod = __import__(modname)
        if hasattr(mod, "dxf_analiz_et"):
            dxf_analiz_et = getattr(mod, "dxf_analiz_et")
            break
    except Exception as e:
        _import_errors.append(f"{modname}: {e}")

if dxf_analiz_et is None:
    st.error("ai_core modülü yüklenemedi. Denenen modüller:\n" + "\n".join(_import_errors))
    st.stop()


def normalize_outputs(a, b):
    """Return feats(list[float]) and geom(dict) regardless of order."""
    feats, geom = None, None
    if isinstance(a, dict) and isinstance(b, (list, tuple, np.ndarray)):
        geom, feats = a, list(b)
    elif isinstance(b, dict) and isinstance(a, (list, tuple, np.ndarray)):
        geom, feats = b, list(a)
    elif isinstance(a, dict) and b is None:
        geom, feats = a, None
    elif isinstance(b, dict) and a is None:
        geom, feats = b, None
    else:
        # last resort
        if isinstance(a, dict):
            geom = a
        if isinstance(b, dict):
            geom = b
        if isinstance(a, (list, tuple, np.ndarray)):
            feats = list(a)
        if isinstance(b, (list, tuple, np.ndarray)):
            feats = list(b)
    return feats, geom


st.set_page_config(page_title="DXF Analiz", layout="wide")
st.title("DXF Analiz")

uploaded = st.file_uploader("DXF dosyası yükleyin", type=["dxf"])

if uploaded is None:
    st.info("Bir DXF dosyası yükleyin.")
    st.stop()

# Save uploaded to temp
tmp_dir = "tmp_uploads"
os.makedirs(tmp_dir, exist_ok=True)
tmp_path = os.path.join(tmp_dir, uploaded.name)
with open(tmp_path, "wb") as f:
    f.write(uploaded.getbuffer())

out = dxf_analiz_et(tmp_path)
if not isinstance(out, (list, tuple)) or len(out) < 2:
    st.error("dxf_analiz_et beklenen formatta değer döndürmedi.")
    st.stop()

feats, geom = normalize_outputs(out[0], out[1])

if geom is None:
    st.error("Geometri üretilemedi (geom=None).")
    st.stop()

# --- Display key metrics ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Alan", f"{geom.get('alan', 0):.2f}")
col2.metric("Delik sayısı", f"{geom.get('delik_sayisi', len(geom.get('delikler', [])))}")
col3.metric("Büküm sayısı", f"{geom.get('bukum_sayisi', len(geom.get('bukumler', [])))}")
col4.metric("Çevre", f"{geom.get('cevre', 0):.2f}")

# --- Simple plot (matplotlib) ---
import matplotlib.pyplot as plt

fig, ax = plt.subplots()

def plot_poly(p, **kwargs):
    x, y = p.exterior.xy
    ax.plot(x, y, **kwargs)

ana = geom.get("ana_parca")
if ana is not None:
    try:
        if isinstance(ana, Polygon):
            plot_poly(ana)
        elif isinstance(ana, MultiPolygon):
            for g in ana.geoms:
                plot_poly(g)
    except Exception:
        pass

for d in geom.get("delikler", []) or []:
    try:
        plot_poly(d)
    except Exception:
        pass

for l in geom.get("bukumler", []) or []:
    try:
        xs, ys = l.xy
        ax.plot(xs, ys)
    except Exception:
        pass

ax.set_aspect("equal", adjustable="datalim")
st.pyplot(fig)

# --- Features vector (optional) ---
if feats is not None:
    st.subheader("Feature vektörü")
    st.write(feats)
