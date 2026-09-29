from ab.nn.api import data
try:
    df = data(max_rows=10)
    print("Columns in nn-dataset API:", df.columns.tolist())
    print(df[['nn', 'duration']].head())
except Exception as e:
    print("Error:", e)
