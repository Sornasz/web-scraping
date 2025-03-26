import os
import requests
from bs4 import BeautifulSoup
import zipfile
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin

url = "https://www.gov.br/ans/pt-br/acesso-a-informacao/participacao-da-sociedade/atualizacao-do-rol-de-procedimentos"

def baixar_pdf(link, pasta_destino):
    try:
        nome_arquivo = link.split('/')[-1]
        caminho_arquivo = os.path.join(pasta_destino, nome_arquivo)
        
        if os.path.exists(caminho_arquivo):
            print(f"Arquivo {nome_arquivo} já existe!")
            return caminho_arquivo
            
        print(f"Iniciando download: {nome_arquivo}")
        resposta_pdf = requests.get(link, timeout=30)
        resposta_pdf.raise_for_status()
        
        with open(caminho_arquivo, 'wb') as f:
            f.write(resposta_pdf.content)
            
        print(f"Concluído: {nome_arquivo}")
        return caminho_arquivo
        
    except Exception as e:
        print(f"Erro ao baixar {link}: {str(e)}...")
        return None

print("Acessando site")
resposta = requests.get(url)
resposta.raise_for_status()

print("Buscando anexos")
soup = BeautifulSoup(resposta.text, 'html.parser')
links_pdf = []

for link in soup.find_all('a'):
    texto_link = link.text.strip().lower()
    if 'anexo i' in texto_link or 'anexo ii' in texto_link:
        href = link.get('href')
        if href.endswith('.pdf'):
            link_completo = urljoin(url, href)
            links_pdf.append(link_completo)

print(f"Encontrados {len(links_pdf)} PDFs para download")

pasta_anexos = 'anexos'
os.makedirs(pasta_anexos, exist_ok=True)

print("\nIniciando downloads")
arquivos_baixados = []

with ThreadPoolExecutor(max_workers=5) as executor:  
    resultados = executor.map(lambda l: baixar_pdf(l, pasta_anexos), links_pdf)
    arquivos_baixados = [r for r in resultados if r is not None]

print("\nCompactando arquivos!")
with zipfile.ZipFile('anexos.zip', 'w') as zipf:
    for arquivo in arquivos_baixados:
        zipf.write(arquivo, os.path.basename(arquivo))
        print(f"Adicionado ao ZIP: {os.path.basename(arquivo)}")	

print(f"\nProcesso concluído! {len(arquivos_baixados)} arquivos compactados em 'anexos.zip'")