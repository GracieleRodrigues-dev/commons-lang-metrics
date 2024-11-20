import os
import re
import pandas as pd
import matplotlib.pyplot as plt
from packaging.version import Version

# Diretório onde os arquivos CSV estão localizados
directory = "./ck_reports"

# Listar arquivos no diretório
files = os.listdir(directory)

# Lista para armazenar os dados
data = []

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

        metrics = ["wmc", "dit", "noc", "cbo", "lcom*", "rfc", "loc"]
        if all(metric in df_csv.columns for metric in metrics):
            df_csv['Release'] = version
            data.append(df_csv[metrics + ['Release']])

# Combinar todos os dados em um único DataFrame
if data:
    df_metrics = pd.concat(data, ignore_index=True)

    # Converter a coluna Release para versão ordenável
    df_metrics["Release"] = df_metrics["Release"].apply(Version)

    # Ordenar os dados por Release
    df_metrics = df_metrics.sort_values("Release").reset_index(drop=True)

    # Inverter as métricas para que valores mais baixos indiquem melhoria
    df_metrics['wmc'] = 1 / (df_metrics['wmc'] + 1)  # Inverter WMC
    df_metrics['dit'] = 1 / (df_metrics['dit'] + 1)  # Inverter DIT
    df_metrics['cbo'] = 1 / (df_metrics['cbo'] + 1)  # Inverter CBO
    df_metrics['lcom*'] = 1 / (df_metrics['lcom*'] + 1)  # Inverter LCOM1

    # Calcular a média ponderada (ou simples) das métricas para cada release
    df_metrics['average_health'] = df_metrics[["wmc", "dit", "noc", "cbo", "lcom*", "rfc", "loc"]].mean(axis=1)

    # Calcular a média de saúde geral por release
    df_grouped = df_metrics.groupby("Release")["average_health"].mean().reset_index()

    # Plotar o gráfico de evolução da saúde do código
    plt.figure(figsize=(10, 6))
    plt.plot(df_grouped["Release"].astype(str), df_grouped["average_health"], marker='o', linestyle='-', color='b')
    plt.xlabel("Release")
    plt.ylabel("Saúde Geral do Código (Média das Métricas)")
    plt.title("Evolução da Saúde Geral do Código ao Longo das Releases")

    # Adicionar a descrição do Eixo Y e Eixo X fora do gráfico
    plt.figtext(0.5, 0.03, "Eixo Y (Saúde Geral do Código): Quanto maior o valor, pior a saúde geral do código. A inversão das métricas como WMC, DIT, CBO e LCOM1 faz com que valores mais baixos de cada uma dessas métricas representem melhorias. Já métricas como LOC, RFC e NOC são mais indicativas de problemas quando aumentam.", ha="center", fontsize=10, wrap=True)
    plt.figtext(0.5, 0.01, "Eixo X (Release): A evolução das releases do projeto.", ha="center", fontsize=10, wrap=True)

    # Adicionar grid e ajustar layout
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plt.show()

else:
    print("Nenhum dado relevante foi encontrado nos arquivos CSV.")
