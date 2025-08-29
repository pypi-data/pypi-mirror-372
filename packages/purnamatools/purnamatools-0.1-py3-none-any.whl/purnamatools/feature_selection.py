import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.feature_selection import RFE
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LassoCV, Lasso
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import SequentialFeatureSelector
from sklearn.ensemble import  RandomForestRegressor


def correlation_analysis(df, target, method='pearson', threshold=0.4):
    """
    Perform correlation analysis for dataset.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe containing features + target
    target : str
        Target column name
    method : str
        Correlation method ('pearson', 'spearman', 'kendall')
    threshold : float
        Threshold to determine strong correlation (default=0.4)
    """

    # Hanya numeric
    df_num = df.select_dtypes(include=[np.number]).dropna()
    if target not in df_num.columns:
        raise ValueError(f"Target '{target}' not found or not numeric.")

    corr_matrix = df_num.corr(method=method)

    # --- 1. Heatmap untuk semua variabel dengan target ---
    plt.figure(figsize=(10, 6))
    sns.heatmap(corr_matrix[[target]].sort_values(by=target, ascending=False),
                annot=True, cmap="coolwarm", vmin=-1, vmax=1)
    plt.title(f"Correlation with {target} ({method})")
    plt.show()

    # --- 2. Fitur dengan korelasi kuat ---
    strong_corr = corr_matrix[target][(corr_matrix[target].abs() >= threshold) & (corr_matrix.index != target)]
    if not strong_corr.empty:
        print("\n📌 Strong correlations with target:")
        print(strong_corr.sort_values(ascending=False))
    else:
        print(f"\n⚠️ No strong correlations with {target} using method '{method}'.")
        print("👉 Try using another method (pearson/spearman/kendall) or feature engineering.")

    # --- 3. Cari fitur yang duplikat (multikolinearitas) ---
    corr_features = corr_matrix.drop(target, axis=0).drop(target, axis=1)
    duplicated_pairs = []
    for col in corr_features.columns:
        for row in corr_features.index:
            if col != row and abs(corr_features.loc[row, col]) > 0.9:
                duplicated_pairs.append((row, col, corr_features.loc[row, col]))

    if duplicated_pairs:
        print("\n⚠️ Potential duplicated/redundant features (high correlation > 0.9):")
        for f1, f2, val in duplicated_pairs:
            print(f"   {f1} <-> {f2} | corr={val:.2f}")
        print("👉 Consider removing one of them to avoid multicollinearity.")
    else:
        print("\n✅ No highly duplicated features found.")

    return strong_corr

def m1_score_analysis(df, target, method="pearson", threshold_corr=0.4, show_plot=True):
    """
    Perform correlation and M1 Score analysis for feature selection.
    
    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe with features and target.
    target : str
        Target column name.
    method : str
        Correlation method: 'pearson', 'spearman', 'kendall'
    threshold_corr : float
        Threshold for reporting "strong correlation"
    show_plot : bool
        Whether to show heatmap correlation
    
    Returns
    -------
    pd.DataFrame : DataFrame with features, corr_to_target, redundancy, m1_score
    """
    if target not in df.columns:
        raise ValueError(f"Target column '{target}' not found in DataFrame")
    
    # Drop non-numeric
    num_df = df.select_dtypes(include=[np.number])
    if target not in num_df.columns:
        raise ValueError("Target must be numeric for correlation analysis")
    
    corr = num_df.corr(method=method)
    
    # Correlation with target
    corr_target = corr[target].drop(target)
    
    results = []
    for col in corr_target.index:
        rel = abs(corr_target[col])  # relevance to target
        redund = np.mean([abs(corr[col][c]) for c in corr.index if c != col and c != target])  # redundancy
        m1 = rel / (redund + 1e-8)  # avoid div 0
        results.append({
            "feature": col,
            "corr_to_target": corr_target[col],
            "redundancy": redund,
            "m1_score": m1
        })
    
    res_df = pd.DataFrame(results).sort_values("m1_score", ascending=False).reset_index(drop=True)
    
    # Strong correlation features
    strong = res_df[(res_df['corr_to_target'] >= threshold_corr) | (res_df['corr_to_target'] <= -threshold_corr)]
    
    # Print Summary
    print("="*50)
    print(f" M1 Score Analysis (method={method})")
    print("="*50)
    print("\nTop features by M1 Score:")
    print(res_df[['feature', 'corr_to_target', 'redundancy', 'm1_score']].head(10))
    
    if strong.empty:
        print("\n⚠️ No strong correlations found with target.")
        print("   Consider trying another correlation method or feature engineering.")
    else:
        print("\n✅ Features with strong correlation to target:")
        print(strong[['feature','corr_to_target']])
    
    if show_plot:
        plt.figure(figsize=(10,6))
        sns.heatmap(corr, annot=False, cmap="coolwarm", center=0)
        plt.title(f"Correlation Heatmap ({method})")
        plt.show()
    
    return res_df

def batch_rfe_feature_selection(X, y, 
                                base_estimator=None, 
                                n_features_to_select=2, 
                                batch_size=10, 
                                final_top=10):
    """
    RFE dengan batch agar scalable untuk banyak fitur.
    
    Parameters
    ----------
    X : pd.DataFrame
        Dataframe fitur
    y : array-like
        Target
    base_estimator : sklearn estimator
        Model dasar untuk RFE, default RandomForestClassifier
    n_features_to_select : int
        Jumlah fitur terbaik yang dipilih tiap batch
    batch_size : int
        Jumlah fitur per batch
    final_top : int
        Jumlah fitur final setelah RFE tahap 2
    
    Returns
    -------
    selected_features : list
        List nama fitur terpilih
    """
    if base_estimator is None:
        base_estimator = RandomForestClassifier(random_state=42, n_jobs=-1)
    
    feature_names = X.columns.tolist()
    n_features = len(feature_names)
    selected_features = []

    # Step 1: Batch processing
    for i in range(0, n_features, batch_size):
        batch_features = feature_names[i:i+batch_size]
        X_batch = X[batch_features]

        rfe = RFE(base_estimator, n_features_to_select=n_features_to_select)
        rfe.fit(X_batch, y)

        batch_selected = [f for f, s in zip(batch_features, rfe.support_) if s]
        selected_features.extend(batch_selected)
        print(f"Batch {i//batch_size+1}: terpilih {batch_selected}")

    # Step 2: Final RFE di gabungan hasil batch
    X_final = X[selected_features]
    rfe_final = RFE(base_estimator, n_features_to_select=final_top)
    rfe_final.fit(X_final, y)
    final_selected = [f for f, s in zip(selected_features, rfe_final.support_) if s]

    print("\n=== Fitur Final Terpilih ===")
    print(final_selected)

    return final_selected

def sfs_feature_selection(
    X, y, 
    base_estimator=None, 
    n_features_to_select=5, 
    direction="forward", 
    scoring=None, 
    cv=5,
    random_state=42
):
    """
    Sequential Feature Selection (SFS) for feature selection.
    
    Parameters
    ----------
    X : pd.DataFrame
        Feature matrix.
    y : pd.Series or np.ndarray
        Target values.
    base_estimator : sklearn estimator, optional
        Model to evaluate features. If None, defaults to:
        - RandomForestClassifier for classification
    n_features_to_select : int, default=5
        Number of features to select.
    direction : {"forward", "backward"}, default="forward"
        - "forward": start with 0 features and add one by one
        - "backward": start with all features and remove one by one
    scoring : str or callable, optional
        Scoring metric (e.g., "accuracy", "r2", "f1"). If None, uses default of estimator.
    cv : int, default=5
        Number of cross-validation folds.
    random_state : int, default=42
        Random seed for reproducibility.
    
    Returns
    -------
    selected_features : list
        List of selected feature names.
    support_mask : np.ndarray
        Boolean mask of selected features.
    """
    # Default estimator
    if base_estimator is None:       
            base_estimator = RandomForestClassifier(random_state=random_state, n_jobs=-1)

    # SFS
    sfs = SequentialFeatureSelector(
        base_estimator,
        n_features_to_select=n_features_to_select,
        direction=direction,
        scoring=scoring,
        cv=cv,
        n_jobs=-1
    )
    sfs.fit(X, y)

    # hasil
    support_mask = sfs.get_support()
    selected_features = X.columns[support_mask].tolist()

    print(f"Selected {len(selected_features)} features using SFS ({direction}):")
    print(selected_features)

    return selected_features, support_mask

def lasso_feature_selection(X, y, alphas=None, cv=5, top_k=None, random_state=42):
    """
    Lasso-based feature selection with automatic alpha search.
    
    Parameters
    ----------
    X : pd.DataFrame or np.ndarray
        Feature matrix.
    y : pd.Series or np.ndarray
        Target values.
    alphas : list or np.ndarray, optional
        Range of alpha values to search. If None, uses np.logspace(-3, 1, 50).
    cv : int, default=5
        Number of cross-validation folds.
    top_k : int, optional
        Number of top features to keep (ranked by absolute coefficient).
        If None, keep all non-zero features.
    random_state : int, default=42
        Random seed for reproducibility.

    Returns
    -------
    selected_features : list
        List of selected feature names.
    best_alpha : float
        Best alpha chosen by cross-validation.
    coef_df : pd.DataFrame
        DataFrame with features and their coefficients.
    """

    if alphas is None:
        alphas = np.logspace(-3, 1, 50)  # rentang alpha otomatis
    
    # scaling penting buat Lasso
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # cari alpha terbaik dengan cross-validation
    lasso_cv = LassoCV(alphas=alphas, cv=cv, random_state=random_state, n_jobs=-1)
    lasso_cv.fit(X_scaled, y)
    
    best_alpha = lasso_cv.alpha_
    
    # fit ulang dengan alpha terbaik
    lasso = Lasso(alpha=best_alpha, random_state=random_state)
    lasso.fit(X_scaled, y)
    
    # ambil koefisien
    coef = lasso.coef_
    feature_names = X.columns if isinstance(X, pd.DataFrame) else [f"f{i}" for i in range(X.shape[1])]
    
    coef_df = pd.DataFrame({
        "feature": feature_names,
        "coef": coef,
        "abs_coef": np.abs(coef)
    }).sort_values("abs_coef", ascending=False)
    
    # pilih fitur
    if top_k is not None:
        selected_features = coef_df.head(top_k)["feature"].tolist()
    else:
        selected_features = coef_df[coef_df["coef"] != 0]["feature"].tolist()
    
    return selected_features, best_alpha, coef_df
