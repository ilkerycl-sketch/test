import os
import pandas as pd

# Core import (ai_core.py veya ai_core_v7/v8 uyumlu)
try:
    from ai_core import dxf_analiz_et
except Exception:
    from ai_core import dxf_analiz_et  # gerekirse ai_core_v8 de eklenebilir

# SINIFLAR – sizin tanımınız
paths = {
    0: r"veri\sorunsuz",
    1: r"veri\sorunlu"
}

data = []

def normalize_core_output(result):
    """
    dxf_analiz_et() -> (feats, geom) veya (geom, feats)
    Hangisi gelirse gelsin ayır.
    """
    if not isinstance(result, (list, tuple)) or len(result) != 2:
        raise ValueError("dxf_analiz_et beklenmeyen çıktı verdi")

    a, b = result
    if isinstance(a, dict):
        return b, a
    return a, b


for label, folder in paths.items():
    if not os.path.isdir(folder):
        print(f"Klasör bulunamadı: {folder}")
        continue

    for fname in os.listdir(folder):
        if not fname.lower().endswith(".dxf"):
            continue

        fpath = os.path.join(folder, fname)
        try:
            feats, geom = normalize_core_output(dxf_analiz_et(fpath))
            row = list(feats) + [label]
            data.append(row)
        except Exception as e:
            print(f"Hata ({fname}): {e}")

# CSV yaz
if data:
    col_count = len(data[0])
    columns = [f"f{i}" for i in range(col_count - 1)] + ["label"]
    df = pd.DataFrame(data, columns=columns)
    df.to_csv("egitim_verisi.csv", index=False)
    print("CSV üretildi: egitim_verisi.csv")
else:
    print("Hiç veri toplanamadı")
