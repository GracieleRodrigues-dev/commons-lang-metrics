import os
import re
import pandas as pd
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
from packaging.version import Version

directory = "./spotbugs_reports"

files = os.listdir(directory)

data = []

for filename in files:
    if filename.endswith(".xml"):
        print(f"Processando arquivo: {filename}")
        file_path = os.path.join(directory, filename)

        # Extrair a versão do nome do arquivo
        match = re.search(r'commons-lang-(.+?)_spotbugs', filename)
        if match:
            version = match.group(1)
        else:
            version = filename

        # Parse do XML
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Contar bugs por categoria
        for bug in root.findall(".//BugInstance"):
            category = bug.get('category')  # Captura a categoria do bug
            data.append({
                "Release": version,
                "Category": category,
                "BugCount": 1  # Contabiliza 1 bug por instância
            })

# Criar DataFrame
df = pd.DataFrame(data)

# Criar DataFrame para o gráfico total
df_total = df.groupby(['Release']).count().reset_index()

# Criar DataFrame para o gráfico por categoria
df_grouped = df.groupby(['Release', 'Category']).sum().reset_index()

# Ordenar o DataFrame pelas versões das releases
df_total["Release"] = df_total["Release"].apply(Version)
df_grouped["Release"] = df_grouped["Release"].apply(Version)
df_total = df_total.sort_values("Release").reset_index(drop=True)
df_grouped = df_grouped.sort_values("Release").reset_index(drop=True)

# Plotar o gráfico total de bugs
plt.figure(figsize=(14, 6))

# Gráfico total de bugs
plt.subplot(1, 2, 1)
plt.plot(df_total["Release"].astype(str), df_total["BugCount"], marker='o', color='b', linestyle='-')
plt.xlabel("Release")
plt.ylabel("Número de Bugs")
plt.title("Evolução Total dos Bugs nas Releases")
plt.xticks(rotation=45)
plt.grid(True)

# Gráfico por categoria
plt.subplot(1, 2, 2)
categories = df_grouped['Category'].unique()  # Obter categorias únicas para o gráfico
for category in categories:
    subset = df_grouped[df_grouped['Category'] == category]
    plt.plot(subset["Release"].astype(str), subset["BugCount"], marker='o', label=category)

plt.xlabel("Release")
plt.ylabel("Número de Bugs")
plt.title("Evolução dos Bugs nas Releases por Categoria")
plt.xticks(rotation=45)
plt.legend(title='Categoria')
plt.grid(True)

plt.tight_layout()
plt.show()
