import os
import re
import pandas as pd
import matplotlib.pyplot as plt
from packaging.version import Version
import seaborn as sns

# Diretório onde os arquivos CSV estão localizados
directory = "./ck_reports"

# Listar arquivos no diretório
files = os.listdir(directory)

# Lista para armazenar os dados
data = []

metric_names = {
    "wmc": "Weighted Methods per Class",
    "dit": "Depth of Inheritance Tree",
    "noc": "Number of Children",
    "cbo": "Coupling Between Object Classes",
    "lcom*": "Lack of Cohesion of Methods",
    "rfc": "Response For a Class",
    "loc": "Lines of Code"
}

# Processar cada arquivo CSV
for filename in files:
    if filename.endswith(".csvclass.csv"):
        print(f"Processando arquivo: {filename}")
        file_path = os.path.join(directory, filename)

        # Extrair a versão do nome do arquivo
        match = re.search(r'commons-lang-(.+?)_ck_metrics', filename)
        if match:
            version = match.group(1)
        else:
            version = filename

        # Carregar o CSV
        df_csv = pd.read_csv(file_path)

        # Selecionar as metricas
        metrics = ["wmc", "dit", "noc", "cbo", "lcom*", "rfc", "loc"]
        if all(metric in df_csv.columns for metric in metrics):
            df_csv['Release'] = version
            data.append(df_csv[metrics + ['Release']])

if data:
    df_metrics = pd.concat(data, ignore_index=True)

    df_metrics["Release"] = df_metrics["Release"].apply(Version)

    # Ordenar os dados por Release
    df_metrics = df_metrics.sort_values("Release").reset_index(drop=True)

    # Gerar gráficos para cada métrica
    metrics_to_plot = ["wmc", "dit", "noc", "cbo", "lcom*", "rfc", "loc"]
    plt.figure(figsize=(20, 14))

    for i, metric in enumerate(metrics_to_plot, 1):
        plt.subplot(4, 2, i)
        df_grouped = df_metrics.groupby("Release")[metric].mean().reset_index()
        plt.plot(df_grouped["Release"].astype(str), df_grouped[metric], marker='o', linestyle='-', label=metric)
        
        plt.xlabel("Release")
        plt.ylabel(f"{metric.upper()}")
        plt.title(f"Evolução da métrica {metric_names[metric]}")
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.tight_layout()
        plt.show()
    
else:
    print("Nenhum dado foi encontrado nos arquivos CSV.")
