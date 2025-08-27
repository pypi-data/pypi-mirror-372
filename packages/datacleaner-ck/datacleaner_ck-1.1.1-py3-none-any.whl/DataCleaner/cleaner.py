import pandas as pd
import numpy as np
from sklearn.impute import KNNImputer
from sklearn.ensemble import IsolationForest
from sklearn.feature_selection import VarianceThreshold
from sklearn.preprocessing import LabelEncoder, OneHotEncoder

class DataCleaner:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.report = []

    # ----------------------------
    # Missing Values Handling
    # ----------------------------
    def handle_missing(self, strategy="mean", columns=None, n_neighbors=3):
        if columns is None:
            columns = self.df.columns

        for col in columns:
            if self.df[col].isnull().sum() > 0:
                if strategy == "drop":
                    self.df = self.df.dropna(subset=[col])
                    self.report.append(f"Dropped rows with missing in {col}")
                elif strategy == "mean":
                    self.df[col].fillna(self.df[col].mean(), inplace=True)
                    self.report.append(f"Filled missing {col} with mean")
                elif strategy == "median":
                    self.df[col].fillna(self.df[col].median(), inplace=True)
                    self.report.append(f"Filled missing {col} with median")
                elif strategy == "mode":
                    self.df[col].fillna(self.df[col].mode()[0], inplace=True)
                    self.report.append(f"Filled missing {col} with mode")
                elif strategy == "knn":
                    imputer = KNNImputer(n_neighbors=n_neighbors)
                    self.df[columns] = imputer.fit_transform(self.df[columns])
                    self.report.append(f"Applied KNN imputation on {columns}")
        return self

    # ----------------------------
    # Remove Duplicates
    # ----------------------------
    def remove_duplicates(self):
        before = len(self.df)
        self.df = self.df.drop_duplicates()
        after = len(self.df)
        self.report.append(f"Removed {before - after} duplicate rows")
        return self

    # ----------------------------
    # Handle Outliers
    # ----------------------------
    def handle_outliers(self, method="iqr", columns=None):
        if columns is None:
            columns = self.df.select_dtypes(include=np.number).columns

        for col in columns:
            if method == "iqr":
                Q1 = self.df[col].quantile(0.25)
                Q3 = self.df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower, upper = Q1 - 1.5 * IQR, Q3 + 1.5 * IQR
                self.df = self.df[(self.df[col] >= lower) & (self.df[col] <= upper)]
                self.report.append(f"Removed outliers in {col} using IQR")
            elif method == "zscore":
                z = (self.df[col] - self.df[col].mean()) / self.df[col].std()
                self.df = self.df[(z < 3) & (z > -3)]
                self.report.append(f"Removed outliers in {col} using Z-score")
            elif method == "isolation_forest":
                iso = IsolationForest(contamination=0.05, random_state=42)
                preds = iso.fit_predict(self.df[columns])
                self.df = self.df[preds == 1]
                self.report.append(f"Removed outliers in {columns} using Isolation Forest")
        return self

    # ----------------------------
    # Feature Reduction
    # ----------------------------
    def remove_low_variance(self, threshold=0.01):
        selector = VarianceThreshold(threshold)
        selector.fit(self.df.select_dtypes(include=np.number))
        kept = self.df.select_dtypes(include=np.number).columns[selector.get_support()]
        dropped = set(self.df.select_dtypes(include=np.number).columns) - set(kept)
        self.df = self.df[kept]
        self.report.append(f"Dropped low-variance features: {dropped}")
        return self

    def remove_high_correlation(self, corr_threshold=0.9):
        corr_matrix = self.df.corr().abs()
        upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
        to_drop = [column for column in upper.columns if any(upper[column] > corr_threshold)]
        self.df = self.df.drop(columns=to_drop)
        self.report.append(f"Dropped highly correlated features: {to_drop}")
        return self

    # ----------------------------
    # Encoding Categorical Data
    # ----------------------------
    def encode(self, method="auto"):
        cat_cols = list(self.df.select_dtypes(include=["object", "category"]).columns)
        if method == "label":
            for col in cat_cols:
                self.df[col] = LabelEncoder().fit_transform(self.df[col].astype(str))
            self.report.append("Applied Label Encoding")
        elif method == "onehot":
            self.df = pd.get_dummies(self.df, columns=cat_cols)
            self.report.append("Applied One-Hot Encoding")
        elif method == "frequency":
            for col in cat_cols:
                freq = self.df[col].value_counts()
                self.df[col] = self.df[col].map(freq)
            self.report.append("Applied Frequency Encoding")
        elif method == "auto":
            for col in cat_cols:
                if self.df[col].nunique() <= 10:
                    self.df = pd.get_dummies(self.df, columns=[col])
                elif self.df[col].nunique() > 10 and self.df[col].dtype == "object":
                    freq = self.df[col].value_counts()
                    self.df[col] = self.df[col].map(freq)
            self.report.append("Applied Auto Encoding")
        return self

    # ----------------------------
    # Final Output
    # ----------------------------
    def get_data(self):
        return self.df

    def get_report(self):
        return pd.DataFrame({"Step": range(1, len(self.report)+1), "Action": self.report}) 