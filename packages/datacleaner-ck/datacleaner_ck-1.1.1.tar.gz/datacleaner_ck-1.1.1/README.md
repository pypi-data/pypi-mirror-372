# 🧹 DataCleaner

A simple and flexible Python utility for **data cleaning and preprocessing**.  
It helps you handle missing values, remove duplicates, treat outliers, reduce features, and encode categorical data — all in one place.  

---

## ✨ Features
- **Missing Values Handling**  
  - Drop, Mean, Median, Mode, KNN Imputation  
- **Remove Duplicates**  
- **Outlier Detection & Removal**  
  - IQR, Z-score, Isolation Forest  
- **Feature Reduction**  
  - Low variance feature removal  
  - High correlation feature removal  
- **Encoding Categorical Data**  
  - Label Encoding  
  - One-Hot Encoding  
  - Frequency Encoding  
  - Auto Encoding (chooses based on cardinality)  
- **Report Generation** – keeps track of all cleaning steps applied  

---

## 📦 Installation

Clone the repo:

```bash
git clone https://github.com/ck-ahmad/datacleaner.git
```
## Install dependencies:

```bash
pip install -r requirements.txt
```

## 🚀 Usage Example

``` python
import pandas as pd
from cleaner import DataCleaner

# Sample dataset
df = pd.DataFrame({
    "Name": ["Ali", "Sara", "John", "Ali", None],
    "Age": [25, None, 30, 25, 22],
    "Salary": [50000, 60000, None, 50000, 45000],
    "City": ["Lahore", "Karachi", "Karachi", "Lahore", "Islamabad"]
})

# Initialize cleaner
cleaner = DataCleaner(df)

# Apply cleaning steps
cleaned_df = (
    cleaner
    .handle_missing(strategy="mean")   # fill missing values
    .remove_duplicates()               # remove duplicate rows
    .handle_outliers(method="iqr")     # handle outliers
    .remove_low_variance(threshold=0.01)
    .remove_high_correlation(corr_threshold=0.9)
    .encode(method="auto")             # encode categorical columns
    .get_data()
)

# Get report of cleaning steps
report = cleaner.get_report()

print("✅ Cleaned Data:")
print(cleaned_df)

print("\n📝 Cleaning Report:")
print(report)
```
## 📋 Example Output
# Cleaned Data

``` bash
Copy code
   Age   Salary  City_Karachi  City_Lahore  City_Islamabad
0   25  50000.0             0            1               0
1   25  50000.0             1            0               0
2   22  45000.0             0            0               1
```
# Cleaning Report

``` sql
 Step  Action
 1     Filled missing Age with mean
 2     Filled missing Salary with mean
 3     Dropped rows with missing in Name
 4     Removed 1 duplicate rows
 5     Removed outliers in Age using IQR
 6     Applied Auto Encoding
```
## 🛠️ Requirements
pandas
numpy
scikit-learn

```bash
Copy code
pip install pandas numpy scikit-learn
```
## 📖 License
This project is licensed under the MIT License – feel free to use and Open To Collabrate For Contibutions in it.

## 👨‍💻 Author
Ahmad Abdullah
🌐 LinkedIn: linkedin.com/in/ahmad0763
💻 GitHub: github.com/ck-ahmad