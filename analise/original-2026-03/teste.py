import pandas as pd
df = pd.read_csv("resultados_robustez.csv")
sub = df[(df["n_pivos"] == 50) & (df["mapa"] == "brc000d")]
print(sub.groupby("semente")["exp_orig_mem"].mean())
