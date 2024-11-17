import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

OUTPUT_REPORTS_DIR = "jacoco_reports"
CSV_OUTPUT_PATH = os.path.join(OUTPUT_REPORTS_DIR, "jacoco_metrics.csv")

def generate_graphs():
    """Gera gráficos para cada métrica a partir de um arquivo CSV."""

    if not os.path.exists(CSV_OUTPUT_PATH):
        print("Arquivo de métricas não encontrado.")
    else:
        # Lê o CSV
        df = pd.read_csv(CSV_OUTPUT_PATH)

        # Itera sobre as métricas disponíveis
        metrics = df["Metric"].unique()
        for metric in metrics:
            metric_data = df[df["Metric"] == metric]

            # Remove o prefixo 'rel/' para ordenação
            metric_data["Release"] = metric_data["Release"].str.replace("rel/", "", regex=False)

            metric_data = metric_data.sort_values(by="Release", key=lambda x: x.str.lower())

            plt.figure(figsize=(10, 6))
            plt.plot(metric_data["Release"], metric_data["Coverage"], marker="o", label="Coverage (%)")
            plt.title(f"Métrica: {metric}")
            plt.xlabel("Release")
            plt.ylabel("Cobertura (%)")
            plt.xticks(rotation=45, ha="right")
            plt.grid(True, linestyle="--", alpha=0.6)

            # Define o limite máximo do eixo Y para 100%
            #plt.ylim(0, 100)

            # Formata os valores do eixo Y para mostrar até 2 casas decimais
            #plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{x:.3f}'))            

            plt.tight_layout()

            # Salva o gráfico
            output_path = os.path.join(OUTPUT_REPORTS_DIR, f"{metric}_coverage.png")
            plt.savefig(output_path)
            plt.close()
            print(f"Gráfico gerado: {output_path}")

# Executa o script
if __name__ == "__main__":
    generate_graphs()