import os
import pickle
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

CSV_PATH = "egitim_verisi.csv"
MODEL_PATH = "uretim_ai.pkl"

if not os.path.exists(CSV_PATH):
    raise SystemExit(f"CSV bulunamadı: {CSV_PATH}")

df = pd.read_csv(CSV_PATH)

# Etiket sütununu otomatik bul
candidate_labels = ["durum", "label", "class", "y", "target"]
label_col = next((c for c in candidate_labels if c in df.columns), None)

if label_col is None:
    # Son sütunu etiket kabul et
    label_col = df.columns[-1]

# X/y ayır
y = df[label_col]
X = df.drop(columns=[label_col])

# Feature'ları sayısala zorla (string vb. varsa)
for c in X.columns:
    X[c] = pd.to_numeric(X[c], errors="coerce")

# NaN doldur
X = X.fillna(0)

# Model
clf = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    class_weight="balanced",
    random_state=42
)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y if y.nunique() > 1 else None
)

clf.fit(X_train, y_train)

acc = accuracy_score(y_test, clf.predict(X_test)) * 100
print(f"Etiket sütunu: {label_col}")
print(f"Model Başarısı: %{acc:.2f}")

with open(MODEL_PATH, "wb") as f:
    pickle.dump(clf, f)

print(f"Model kaydedildi: {MODEL_PATH}")
