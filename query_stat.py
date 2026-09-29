import sqlite3
import pandas as pd
conn = sqlite3.connect("db/ab.nn.db")
try:
    df = pd.read_sql_query("SELECT s.id, s.nn, s.duration, t.samples_per_second, t.gpu_type FROM stat s LEFT JOIN train_stat t ON s.id = t.stat_id LIMIT 5", conn)
    print(df.to_string())
except Exception as e:
    print(e)
