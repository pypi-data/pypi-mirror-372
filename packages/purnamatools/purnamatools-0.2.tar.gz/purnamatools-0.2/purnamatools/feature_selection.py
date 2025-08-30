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
from sklearn.feature_selection import mutual_info_classif, mutual_info_regression


def correlation_analysis(df, target, method='pearson', threshold=0.4, top_n=20, save_to=None):
    """
    Perform correlation analysis with better visualization.
    
    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe containing features + target
    target : str
        Target column name
    method : str
        Correlation method ('pearson', 'spearman', 'kendall')
    threshold : float
        Threshold to determine strong correlation (default=0.4)
    top_n : int
        Show top N features by correlation strength
    save_to : str or None
        If provided, save correlation results to CSV/Excel
    """

    # Hanya numeric
    df_num = df.select_dtypes(include=[np.number]).dropna()
    if target not in df_num.columns:
        raise ValueError(f"Target '{target}' not found or not numeric.")

    corr_matrix = df_num.corr(method=method)

    # --- 1. Heatmap full correlation matrix ---
    plt.figure(figsize=(12, 8))
    sns.heatmap(corr_matrix, cmap="coolwarm", center=0, annot=False)
    plt.title(f"Full Correlation Matrix ({method})")
    plt.show()

    # --- 2. Korelasi dengan target ---
    corr_target = corr_matrix[target].drop(target).sort_values(key=lambda x: x.abs(), ascending=False)

    # Barplot top_n
    plt.figure(figsize=(8, 6))
    sns.barplot(x=corr_target.head(top_n).values,
                y=corr_target.head(top_n).index,
                palette="coolwarm")
    plt.axvline(x=threshold, color='green', linestyle='--', label=f"Threshold {threshold}")
    plt.axvline(x=-threshold, color='green', linestyle='--')
    plt.title(f"Top {top_n} Correlations with {target}")
    plt.legend()
    plt.show()

    # --- 3. Strong correlations ---
    strong_corr = corr_target[abs(corr_target) >= threshold]
    if not strong_corr.empty:
        print("\n📌 Strong correlations with target:")
        display(strong_corr.to_frame(name="Correlation"))
    else:
        print(f"\n⚠️ No strong correlations with {target} (>{threshold}).")

    # --- 4. Multicollinearity ---
    corr_features = corr_matrix.drop(target, axis=0).drop(target, axis=1)
    redundant = []
    for col in corr_features.columns:
        for row in corr_features.index:
            if col < row and abs(corr_features.loc[row, col]) > 0.9:
                redundant.append((row, col, corr_features.loc[row, col]))
    redundant_df = pd.DataFrame(redundant, columns=["Feature 1", "Feature 2", "Correlation"])
    if not redundant_df.empty:
        print("\n⚠️ Potential duplicated/redundant features (high correlation > 0.9):")
        display(redundant_df.sort_values("Correlation", ascending=False))
    else:
        print("\n✅ No highly duplicated features found.")

    # --- 5. Save results if requested ---
    if save_to:
        with pd.ExcelWriter(save_to) as writer:
            corr_target.to_frame("Correlation").to_excel(writer, sheet_name="Target Correlation")
            if not redundant_df.empty:
                redundant_df.to_excel(writer, sheet_name="Redundant Features", index=False)
        print(f"\n📂 Results saved to {save_to}")

    return strong_corr

def mi_analysis(df, target, problem="regression", top_n=20, random_state=42):
    """
    Mutual Information (MI) feature selection.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe containing features + target
    target : str
        Target column name (must be numeric for regression, can be categorical for classification)
    problem : str
        'regression' or 'classification'
    top_n : int
        Show top N features by MI score
    random_state : int
        Random seed for reproducibility

    Returns
    -------
    mi_df : pd.DataFrame
        Sorted dataframe of features and their MI scores
    best_features : list
        List of top N features by MI score
    """

    # Pisahkan X dan y
    df_num = df.select_dtypes(include=[np.number]).dropna()
    if target not in df_num.columns:
        raise ValueError(f"Target '{target}' not found or not numeric.")
    
    X = df_num.drop(columns=[target])
    y = df_num[target]

    # Pilih fungsi MI sesuai problem
    if problem == "regression":
        mi = mutual_info_regression(X, y, random_state=random_state)
    elif problem == "classification":
        mi = mutual_info_classif(X, y, random_state=random_state)
    else:
        raise ValueError("Problem must be 'regression' or 'classification'.")

    # Buat DataFrame hasil
    mi_df = pd.DataFrame({
        "feature": X.columns,
        "mi_score": mi
    }).sort_values("mi_score", ascending=False).reset_index(drop=True)

    # --- Plot bar chart top_n ---
    plt.figure(figsize=(8, 6))
    sns.barplot(x="mi_score", y="feature", data=mi_df.head(top_n), palette="viridis")
    plt.title(f"Top {top_n} Features by Mutual Information ({problem})")
    plt.xlabel("MI Score")
    plt.ylabel("Feature")
    plt.show()

    # --- Print & display ---
    print("\n📌 Top features by MI Score:")
    display(mi_df.head(top_n))

    # Ambil list top features
    best_features = mi_df.head(top_n)["feature"].tolist()

    return mi_df, best_features

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
