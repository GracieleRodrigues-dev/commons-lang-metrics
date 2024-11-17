import os
import subprocess
import requests
import csv
import xml.etree.ElementTree as ET

# URLs e configurações
GITHUB_API_URL_REPO  = "https://github.com/apache/commons-lang.git"
GITHUB_API_URL = "https://api.github.com/repos/apache/commons-lang/tags"
REPO_DIR = "apache_commons_repo"  # Nome do diretório onde o repositório será clonado
POM_PATH = os.path.join(REPO_DIR, "pom.xml") # Caminho do pom no repositório
MAVEN_PATH = "C:/apache-maven-3.9.9/bin/mvn.cmd"  # Caminho do Maven
OUTPUT_REPORTS_DIR = "jacoco_reports"
CSV_OUTPUT_PATH = os.path.join(OUTPUT_REPORTS_DIR, "jacoco_metrics.csv")
JACOCO_REPORT_PATH = os.path.join(REPO_DIR, "target", "site", "jacoco", "jacoco.xml")
RELEASES_NUMBER = 20

# Função para clonar o repositório
def clone_repository():
    if not os.path.exists(REPO_DIR):
        subprocess.run(["git", "clone", GITHUB_API_URL_REPO, REPO_DIR], check=True)

# Teste
def teste_busca_releases():
    """Busca as últimas releases no GitHub."""
    response = requests.get(GITHUB_API_URL)
    response.raise_for_status()
    releases = response.json()
    release_count = 0
    for release in releases:
        release_count = release_count + 1
        print(f"Release {release_count}: ", release["name"])

def fetch_releases_1():
    """Busca as últimas releases no GitHub."""
    response = requests.get(GITHUB_API_URL)
    response.raise_for_status()
    releases = response.json()[:RELEASES_NUMBER]
    return [(release["name"], release["commit"]["sha"]) for release in releases]

def fetch_releases():
    """Busca as últimas releases no GitHub."""
    response = requests.get(GITHUB_API_URL)
    response.raise_for_status()
    releases = response.json()
    return [(release["name"], release["commit"]["sha"]) for release in releases]

# Função para mudar para uma release específica
def checkout_release(tag):
    os.chdir(REPO_DIR)
    subprocess.run(["git", "checkout", tag], check=True)
    os.chdir("..")

# Função para compilar o código com o plugin JaCoCo
def compile_with_jacoco():
    os.chdir(REPO_DIR)
    # Adiciona o plugin do JaCoCo e compila o projeto com o Maven
    result = subprocess.run([MAVEN_PATH, "clean", "compile", "-Dmaven.test.failure.ignore=true", "jacoco:prepare-agent", "test", "jacoco:report"],
                            capture_output=True, text=True)
    os.chdir("..")
    return result.returncode == 0

# Função para extrair métricas do relatório do JaCoCo
def extract_jacoco_metrics(name):
    if not os.path.exists(JACOCO_REPORT_PATH):
        print(f"Relatório do JaCoCo não encontrado para a branch {name}.")
        return {}

    tree = ET.parse(JACOCO_REPORT_PATH)
    root = tree.getroot()

    metrics = {}
    for counter in root.findall(".//counter"):
        type_ = counter.get("type")
        covered = int(counter.get("covered"))
        missed = int(counter.get("missed"))
        total = covered + missed
        metrics[type_] = {
            "covered": covered,
            "missed": missed,
            "total": total,
            "coverage": (covered / total) * 100 if total > 0 else 0
        }

    save_metrics_to_csv(name, metrics)

    return metrics

def save_metrics_to_csv(release_name, metrics):
    """Salva as métricas extraídas no CSV."""
    file_exists = os.path.isfile(CSV_OUTPUT_PATH)
    with open(CSV_OUTPUT_PATH, mode="a", newline="") as csv_file:
        writer = csv.writer(csv_file)
        if not file_exists:
            # Escreve o cabeçalho do arquivo se não existir
            writer.writerow(["Release", "Metric", "Coverage", "Covered", "Total", "Missed"])
        for metric, values in metrics.items():
            writer.writerow([release_name, metric, values["coverage"], values["covered"], values["total"], values["missed"]])

# Função principal para iterar sobre as releases e extrair métricas
def process_releases(releases_number=20):
    clone_repository()
    releases = fetch_releases()

    if not os.path.exists(OUTPUT_REPORTS_DIR):
        os.makedirs(OUTPUT_REPORTS_DIR)

    for name, commit_sha in releases:
        print(f"\nProcessando release {name} - Commit: {commit_sha}")
            
        # Faz o checkout da release específica
        checkout_release(commit_sha)

        if update_jacoco_skip(skip_value=False):
            print("Propriedade <jacoco.skip> ajustada com sucesso.")
        else:
            print("Ajuste de <jacoco.skip> falhou ou a propriedade não foi encontrada.")
            
        # Compila o código
        if compile_with_jacoco():
            print("Compilação e execução de testes concluídas.")
            metrics = extract_jacoco_metrics(name)
            if not metrics:
                print(f"Sem métricas de cobertura para {name}:")
            else :
                print(f"Métricas de cobertura para {name}:")
                for metric, values in metrics.items():
                    print(f"{metric}: {values['coverage']:.2f}% ({values['covered']}/{values['total']})")
                    
                print(f"Análise Jacoco concluída para a tag {name}.\n")
                releases_number = releases_number - 1
        else:
            print(f"Erro na compilação da tag {name}. Pulando para a próxima.\n")

        if releases_number < 0:
            break

        reset_release(name)

def reset_release(name):
    try:
        os.chdir(REPO_DIR)
        subprocess.run(["git", "reset", "--hard"], check=True)
        os.chdir("..")
        print("Reset release efetuado com sucesso. Passando para próxima versão.")
    
    except Exception as e:
        print(f"Ocorreu um erro durante o reset da release {name}. Erro: {e}. Passando para a próxima versão.")


# Altera a propriedade <jacoco.skip> do POM.xml
def update_jacoco_skip(skip_value=False):
    """
    Atualiza o valor da propriedade <jacoco.skip> no arquivo pom.xml, fazendo apenas o replace de true para false,
    sem alterar a estrutura do arquivo XML.
    
    Args:
        skip_value (bool): Valor desejado para jacoco.skip (True ou False).
        
    Returns:
        bool: True se a propriedade foi encontrada e atualizada, False caso contrário.
    """
    try:
        # Define o caminho do arquivo
        with open(POM_PATH, 'r', encoding='utf-8') as file:
            # Lê o conteúdo do arquivo como texto
            content = file.read()

        # Define o valor que deve ser substituído
        new_value = "true" if skip_value else "false"
        old_value = "true"

        # Substitui o valor de jacoco.skip
        if f"<jacoco.skip>{old_value}</jacoco.skip>" in content:
            # Realiza o replace do valor dentro da tag <jacoco.skip>
            content = content.replace(f"<jacoco.skip>{old_value}</jacoco.skip>", f"<jacoco.skip>{new_value}</jacoco.skip>")
            
            # Escreve o conteúdo de volta no arquivo
            with open(POM_PATH, 'w', encoding='utf-8') as file:
                file.write(content)
            
            print(f"Propriedade <jacoco.skip> alterada para {new_value} no arquivo {POM_PATH}.")
            return True
        else:
            print(f"A tag <jacoco.skip> com o valor {old_value} não foi encontrada no arquivo {POM_PATH}.")
            return False

    except Exception as e:
        print(f"Erro ao atualizar o arquivo {POM_PATH}: {e}")
        return False

# Executa o script
if __name__ == "__main__":
    process_releases()
    """if update_jacoco_skip(skip_value=False):
        print("Propriedade <jacoco.skip> ajustada com sucesso.")
    else:
        print("Ajuste de <jacoco.skip> falhou ou a propriedade não foi encontrada.")"""
    #teste_busca_releases()