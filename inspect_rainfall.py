import pandas as pd

file_path = "data/raw/precipitation_variables_indofloods.csv"

df = pd.read_csv(file_path)

print("Dataset shape:", df.shape)

print("\nColumn names:")
print(df.columns.tolist())

print("\nFirst 5 rows:")
print(df.head())

print("\nNumeric rainfall statistics:")
print(df.select_dtypes(include="number").describe().round(2))

print("\nMissing values:")
print(df.isnull().sum())