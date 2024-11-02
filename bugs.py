import os
import subprocess
import requests

# URLs e configurações
GITHUB_API_URL = "https://api.github.com/repos/apache/commons-lang/tags"
REPO_DIR = "apache_commons_repo"  # Nome do diretório onde o repositório será clonado
MAVEN_PATH = "C:/apache-maven-3.9.9/bin/mvn.cmd"  # Caminho do Maven
SPOTBUGS_PATH = "C:/Users/graci/Documents/spotbugs-4.8.6/bin/spotbugs.bat"  # Diretório do spotBugs
OUTPUT_DIR = "C:/Users/graci/Documents/commons-lang-metrics/spotbugs_reports"  # Diretório onde será salvo o resultado do spotBugs

def fetch_releases(limit=20): #20 releases
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
    os.chdir(REPO_DIR)  # Muda para o diretório do repositório
    print("Compilando o código...")
    
    # Executa o Maven
    result = subprocess.run([MAVEN_PATH, "clean", "compile"], capture_output=True, text=True)
    os.chdir("..")
    
    if result.returncode == 0:
        print("Compilação concluída com sucesso.")
        if os.path.exists(os.path.join(REPO_DIR, "target/classes")):
            return True
        else:
            print("Erro: O diretório target/classes não foi gerado após a compilação.")
            return False
    else:
        print("Erro na compilação:")
        print(result.stdout)
        print(result.stderr)
        return False
     
def run_spotbugs(tag):
    """Executa o SpotBugs e gera os relatórios XML e HTML para uma tag/release específica."""
    # Verifica se o arquivo está formatado e que o diretório OUTPUT_DIR existe
    safe_tag = tag.replace("/", "_")
    report_dir = os.path.join(REPO_DIR, OUTPUT_DIR)
    xml_report_path = os.path.abspath(os.path.join(report_dir, f"{safe_tag}_spotbugs.xml"))
    html_report_path = os.path.abspath(os.path.join(report_dir, f"{safe_tag}_spotbugs.html"))
    
    print(f"Executando SpotBugs para a tag {tag}...")

    # Cria o diretório OUTPUT_DIR se ainda não existir
    os.makedirs(report_dir, exist_ok=True)
    
    os.chdir(REPO_DIR)
    
    #Gera o relatório XML
    result_xml = subprocess.run(
        [SPOTBUGS_PATH, "-textui", "-xml", "-output", xml_report_path, "target/classes"],
        capture_output=True, text=True
    )
    
    # Verifica se o relatório XML foi gerado com sucesso
    if result_xml.returncode != 0 or not os.path.exists(xml_report_path):
        print("Erro ao executar o SpotBugs ou ao gerar o relatório XML:")
        print(result_xml.stderr)
        if not os.path.exists(xml_report_path):
            print(f"Erro: O relatório SpotBugs {xml_report_path} não foi criado.")
        os.chdir("..")
        return  # Encerra a função se houve erro no XML

    #Gera o relatório HTML 
    result_html = subprocess.run(
        [SPOTBUGS_PATH, "-textui", "-html", "-output", html_report_path, "target/classes"],
        capture_output=True, text=True
    )
    
    os.chdir("..")
    
    # Verifica se o relatório HTML foi gerado com sucesso
    if result_html.returncode == 0 and os.path.exists(html_report_path):
        print(f"Relatório SpotBugs gerado: {xml_report_path}")
        print(f"Relatório SpotBugs em HTML gerado: {html_report_path}")
    else:
        print("Erro ao executar o SpotBugs ou ao gerar o relatório HTML:")
        print(result_html.stderr)
        if not os.path.exists(html_report_path):
            print(f"Erro: O relatório SpotBugs {html_report_path} não foi criado.")

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
            run_spotbugs(name)
            print(f"Análise SpotBugs concluída para a tag {name}.\n")
        else:
            print(f"Erro na compilação da tag {name}. Pulando para a próxima.\n")

if __name__ == "__main__":
    process_releases()
