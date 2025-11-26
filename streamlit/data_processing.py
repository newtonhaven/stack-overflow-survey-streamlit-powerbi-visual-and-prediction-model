import pandas as pd
import numpy as np


def clean_years(value):
    if isinstance(value, str):
        if "Less than" in value:
            return 0
        if "+" in value:
            return float(value.replace("+", ""))
        try:
            return float(value)
        except:
            return np.nan
    return value
# separation
def split_multi(value):
    if isinstance(value, str):
        return [v.strip() for v in value.split(";") if v.strip()]
    return []

def parse_age(value):
    # "18-24 years old" -> 21, "25-34 years old" -> 29.5, "45-54 years old" -> 49.5, "65 years or older" -> 70, "Under 18 years old" -> 16
    if isinstance(value, str):
        if "Under 18" in value:
            return 16
        if "65 years or older" in value:
            return 70
        if "-" in value:
            parts = value.split("-")
            try:
                low = int(parts[0])
                high = int(parts[1].split()[0])
                return (low + high) / 2
            except:
                return np.nan
        if value.isdigit():
            return float(value)
    return np.nan

# -----------------------------
def clean_data(df: pd.DataFrame) -> pd.DataFrame:

    keep = [
        "Age",
        "YearsCode",
        "YearsCodePro",
        "DevType",
        "EdLevel",
        "RemoteWork",
        "Country",
        "LanguageHaveWorkedWith",
        "SurveyLength",
        "ConvertedCompYearly"
    ]

    df = df[[c for c in keep if c in df.columns]].copy()

    # Age: parse string ranges to numeric
    if "Age" in df.columns:
        df["Age"] = df["Age"].apply(parse_age)

    for col in ["YearsCode", "YearsCodePro", "SurveyLength", "ConvertedCompYearly", "CompTotal"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # multi columns
    if "LanguageHaveWorkedWith" in df.columns:
        df["LanguageHaveWorkedWith"] = df["LanguageHaveWorkedWith"].apply(split_multi)

    if "DevType" in df.columns:
        df["DevType"] = df["DevType"].apply(split_multi)

    # Fill missing safe fields
    df["EdLevel"] = df["EdLevel"].fillna("Unknown")
    df["RemoteWork"] = df["RemoteWork"].fillna("Unknown")
    df["Country"] = df["Country"].fillna("Unknown")


    df = df.dropna(subset=["Age"], how="any")

    return df

#data fetching and cleaning
def get_clean_data():
    
    df = pd.read_csv("survey_results_public.csv", low_memory=False)
    
    if "YearsCode" in df.columns:
        df["YearsCode_Numeric"] = df["YearsCode"].apply(clean_years)
        df["YearsCode_Numeric"] = pd.to_numeric(df["YearsCode_Numeric"], errors="coerce")
    return clean_data(df)
