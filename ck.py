import os
import subprocess
import requests

GITHUB_API_URL="https://api.github.com/repos/apache/commons-lang/tags" # Repositório a ser analisado
REPO_DIR="apache_commons_repo"  # Diretório onde será clonado o repositório de análise
MAVEN_PATH="C:/apache-maven-3.9.9/bin/mvn.cmd"  # Diretório do Maven
OUTPUT_DIR="C:/Users/Bruno/Documents/commons-lang-metrics/ck_reports"  # Diretório onde será salvo o resultado do CK
CK_REPO_JAR_DIR="C:/Users/Bruno/Documents/commons-lang-metrics/ck/target/ck-0.7.1-SNAPSHOT-jar-with-dependencies.jar" # Diretório do JAR do CK 
N_RELEASES=20 # Número de Releases que serão analisadas

def fetch_releases(limit=N_RELEASES):
    """Busca as últimas releases no GitHub."""
    response = requests.get(GITHUB_API_URL)
    response.raise_for_status()
    releases = response.json()[:limit]
    return [(release["name"], release["commit"]["sha"]) for release in releases]

def clone_repository():
    """Clona o repositório se ele ainda não estiver clonado."""
    if not os.path.exists(REPO_DIR):
        print("Clonando o repositório...")
        subprocess.run(["git", "clone", "https://github.com/apache/commons-lang.git", REPO_DIR], check=True)

def checkout_release(commit_sha):
    """Faz o checkout de um commit específico no repositório"""
    os.chdir(REPO_DIR)
    subprocess.run(["git", "checkout", commit_sha], check=True)
    os.chdir("..")

def compile_code():
    """Compila o código Java da release usando Maven."""
    os.chdir(REPO_DIR)
    print("Compilando o código...")
    
    result = subprocess.run([MAVEN_PATH, "clean", "compile"], capture_output=True, text=True)
    os.chdir("..")
    
    if result.returncode == 0:
        print("Compilação concluída com sucesso.")
        if os.path.exists(os.path.join(REPO_DIR, "src/main")):
            return True
        else:
            print("Erro: O diretório src/main não foi gerado após a compilação.")
            return False
    else:
        print("Erro na compilação:")
        print(result.stdout)
        print(result.stderr)
        return False
     
def run_ck_metrics(tag):
    """Executa a ferramenta CK para extrair as métricas e gera os relatórios JSON e CSV para uma tag/release específica."""
    safe_tag = tag.replace("/", "_")
    csv_report_path = os.path.normpath(os.path.join(OUTPUT_DIR, f"{safe_tag}_ck_metrics.csv"))

    # Cria o diretório OUTPUT_DIR se ainda não existir
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Verifica se o JAR existe
    if not os.path.exists(CK_REPO_JAR_DIR):
        print(f"Erro: O JAR CK não foi encontrado no caminho {CK_REPO_JAR_DIR}. Certifique-se de ter compilado o repositório CK corretamente.")
        return 

    # Executa a ferramenta CK para gerar métricas
    result_csv = subprocess.run(
        [
            "java", "-jar", CK_REPO_JAR_DIR,
            REPO_DIR,  # Diretório do código compilado
            "true",  # Usar JARs
            "0",  # Máximo de arquivos por partição (automático)
            "true",  # Coletar métricas de variáveis e campos
            csv_report_path,  # Diretório de saída
        ],
        capture_output=True, text=True
    )

def process_releases():
    """Clona, processa as releases e executa o SpotBugs para cada uma."""
    # Clona o repositório se necessário
    clone_repository()
    
    # Busca as últimas releases
    releases = fetch_releases()
    
    for name, commit_sha in releases:
        print(f"\nProcessando release {name} - Commit: {commit_sha}")
        
        # Faz o checkout da release específica
        checkout_release(commit_sha)
        
        # Compila o código
        if compile_code():
            run_ck_metrics(name)
            print(f"Análise CK concluída para a tag {name}.\n")
        else:
            print(f"Erro na compilação da tag {name}. Pulando para a próxima.\n")

if __name__ == "__main__":
    process_releases()
