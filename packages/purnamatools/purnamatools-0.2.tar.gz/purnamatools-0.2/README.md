# PurnamaTools

**PurnamaTools** adalah paket Python yang dibuat untuk **mempermudah tahap awal pembuatan model sebelum analisis lebih lanjut**.  
Paket ini menyediakan utilitas untuk manipulasi data, visualisasi awal, dan seleksi fitur menggunakan library populer.

## Fitur Utama
- Seleksi fitur dengan **RFE** (`sklearn.feature_selection.RFE`)
- Seleksi fitur dengan **Sequential Feature Selector** (`sklearn.feature_selection.SequentialFeatureSelector`)
- Standardisasi data menggunakan `StandardScaler`
- Penggunaan estimator: `RandomForestClassifier`, `RandomForestRegressor`, `LassoCV`
- Visualisasi data awal dengan `seaborn` dan `matplotlib`

## Instalasi
Install langsung dari PyPI (nanti setelah diupload):
```bash
pip install purnamatools
