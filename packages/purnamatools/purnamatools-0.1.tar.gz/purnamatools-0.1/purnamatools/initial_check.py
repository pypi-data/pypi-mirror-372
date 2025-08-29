import pandas as pd
import numpy as np

def initial_data_overview(df, target=None, is_classification=True):
    """
    Function to provide a comprehensive initial check of a DataFrame.
    Checks structure, missing values, duplicates, outliers, validity, statistics,
    cardinality, correlation, and target distribution if provided.

    Parameters:
    df (pd.DataFrame): The dataframe to analyze
    target (str, optional): Target column name
    is_classification (bool): Whether the task is classification (True) or regression (False)
    """
    print("="*50)
    print("INITIAL DATA OVERVIEW")
    print("="*50)
    
    # 1. Structure
    print("\n[1] DATA STRUCTURE")
    print(f"Number of rows: {df.shape[0]}")
    print(f"Number of columns: {df.shape[1]}")
    print("Columns & Data Types:")
    for col, dtype in df.dtypes.items():
        print(f" - {col}: {dtype}")
    
    # 2. Missing values
    print("\n[2] MISSING VALUES")
    missing = df.isna().sum()
    missing_pct = df.isna().mean() * 100
    for col in df.columns:
        if missing[col] > 0:
            print(f" - {col}: {missing[col]} missing ({missing_pct[col]:.2f}%)")
    if missing.sum() == 0:
        print("No missing values detected.")
    
    # 3. Duplicates
    dup_count = df.duplicated().sum()
    print("\n[3] DUPLICATES")
    if dup_count > 0:
        print(f"Number of duplicate rows: {dup_count}")
    else:
        print("No duplicate rows detected.")
    
    # 4. Outliers (IQR method)
    print("\n[4] OUTLIERS (IQR METHOD)")
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    outlier_found = False
    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        outliers = df[(df[col] < Q1 - 1.5*IQR) | (df[col] > Q3 + 1.5*IQR)]
        if len(outliers) > 0:
            outlier_found = True
            print(f" - {col}: {len(outliers)} outliers")
    if not outlier_found:
        print("No outliers detected.")
    
    # 5. Validity check
    print("\n[5] VALIDITY CHECK")
    validity_issues = []
    for col in df.columns:
        if df[col].dtype in ['int64', 'float64']:
            if (df[col] < 0).any():
                validity_issues.append(f"Column '{col}' contains negative values")
        elif df[col].dtype == 'object':
            if df[col].str.strip().eq('').any():
                validity_issues.append(f"Column '{col}' contains empty strings")
    if validity_issues:
        for issue in validity_issues:
            print(f" - {issue}")
    else:
        print("No validity issues detected.")
    
    # 6. Basic statistics
    print("\n[6] BASIC STATISTICS")
    print("Numerical columns summary:")
    if len(numeric_cols) > 0:
        print(df[numeric_cols].describe().T)
    else:
        print("No numerical columns.")
    
    categorical_cols = df.select_dtypes(include=['object']).columns
    if len(categorical_cols) > 0:
        print("\nCategorical columns summary:")
        for col in categorical_cols:
            counts = df[col].value_counts()
            print(f" - {col}:")
            print(counts.head(5))
    else:
        print("No categorical columns.")
    
    # 7. Cardinality
    print("\n[7] CARDINALITY (Unique Values per Column)")
    for col in df.columns:
        unique_vals = df[col].nunique(dropna=True)
        print(f" - {col}: {unique_vals} unique values")
    
    # 8. Low variance
    print("\n[8] LOW VARIANCE / CONSTANT COLUMNS")
    low_var = [col for col in df.columns if df[col].nunique() <= 1]
    if low_var:
        print(f"Columns with constant value: {low_var}")
    else:
        print("No constant columns detected.")
    
    # 9. Target Analysis
    if target and target in df.columns:
        print("\n[10] TARGET ANALYSIS")
        if is_classification:
            print(f"Target '{target}' set as classification task")
            counts = df[target].value_counts(normalize=True) * 100
            print("Class distribution (%):")
            print(counts)
            if counts.min() < 10:
                print("⚠️ Warning: Imbalanced classes detected")
        else:
            print(f"Target '{target}' set as regression task")
            if target in numeric_cols:
                corrs = df[numeric_cols].corr()[target].drop(target).sort_values(ascending=False)
                print("Correlation of target with numeric features:")
                print(corrs)
            else:
                print("Target is not numeric, cannot compute correlation.")
    
    print("\n" + "="*50)
    print("INITIAL DATA CHECK COMPLETE")
    print("="*50)
