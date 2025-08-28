# src/shash/dataprep.py
import pandas as pd

def datacheck(df: pd.DataFrame) -> pd.DataFrame:
    """
    Check a DataFrame for missing values, nulls, and duplicates,
    and return a summary report including number of duplicates as a special row.
    
    Returns:
    - summary_df (pd.DataFrame): column summary with duplicates row
    """
    # Column-wise summary
    summary_df = pd.DataFrame({
        "dtype": df.dtypes,
        "missing_count": df.isnull().sum(),
        "missing_percent": 100 * df.isnull().mean(),
        "unique_values": df.nunique()
    }).sort_values(by="missing_percent", ascending=False)

    # Separator row
    summary_df.loc["----------------"] = ["----------------"] * 4
    
    # Add duplicates as a special row
    duplicates = df.duplicated().sum()
    if duplicates > 0:
         summary_df.loc["Number of"] = ["duplicate", "rows", "present:", duplicates]
    else:
         summary_df.loc["No duplicate"] = ["rows", "found", "in the", "dataset"]
    
    return summary_df
    


def dataeda(df: pd.DataFrame):
    """
    Perform basic exploratory data analysis (EDA) on a DataFrame.
    
    Displays:
    - First 5 rows
    - Shape of the DataFrame
    - Info about columns
    - Numerical summary statistics
    - Categorical summary statistics
    """
    print("\n--- Exploratory Data Analysis (EDA) Report ---")
    print("\nFirst 5 rows:\n", df.head())
    print("\n" + "-"*50)
    print(f"\nShape of DataFrame: {df.shape}")
    print("\n" + "-"*50)
    print("\nDataFrame Info:")
    df.info()
    print("\n" + "-"*50)
    print("\nStatistical Summary (Numerical):\n", df.describe())
    print("\n" + "-"*50)
    print("\nStatistical Summary (Categorical):\n", df.describe(include=[object]))
    print("\n" + "-"*50)
