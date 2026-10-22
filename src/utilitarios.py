import os
import csv
from datetime import datetime
import face_recognition

# Caminhos base do projeto
DIRETORIO_CADASTROS = os.path.join("data", "cadastros")
DIRETORIO_LOGS = os.path.join("data", "logs")
ARQUIVO_LOG = os.path.join(DIRETORIO_LOGS, "acessos.csv")


def inicializar_estrutura():
    """Garante que as pastas e o arquivo de log existam antes da execução."""
    os.makedirs(DIRETORIO_CADASTROS, exist_ok=True)
    os.makedirs(DIRETORIO_LOGS, exist_ok=True)

    if not os.path.exists(ARQUIVO_LOG):
        with open(ARQUIVO_LOG, mode="w", newline="", encoding="utf-8") as f:
            escritor = csv.writer(f)
            escritor.writerow(["Data", "Hora", "Nome", "Status"])


def carregar_rostos_conhecidos():
    """
    Varre a pasta data/cadastros, extrai as assinaturas faciais (encodings)
    e retorna as listas de vetores biométricos e nomes cadastrados.
    """
    inicializar_estrutura()
    encodings_conhecidos = []
    nomes_conhecidos = []

    extensoes_validas = (".jpg", ".jpeg", ".png")

    for arquivo in os.listdir(DIRETORIO_CADASTROS):
        if arquivo.lower().endswith(extensoes_validas):
            caminho_foto = os.path.join(DIRETORIO_CADASTROS, arquivo)
            
            # Recurso da biblioteca: carrega o arquivo de imagem em array numpy
            imagem = face_recognition.load_image_file(caminho_foto)
            
            # Recurso da biblioteca: extrai os vetores matemáticos de 128 dimensões
            codificacoes = face_recognition.face_encodings(imagem)

            if len(codificacoes) > 0:
                encodings_conhecidos.append(codificacoes[0])
                # Usa o nome do arquivo sem a extensão (ex: 'leonardo.jpg' vira 'leonardo')
                nome = os.path.splitext(arquivo)[0].replace("_", " ").title()
                nomes_conhecidos.append(nome)
                print(f"[CADASTRO] Rosto mapeado com sucesso: {nome}")
            else:
                print(f"[AVISO] Nenhum rosto detectado na foto: {arquivo}")

    return encodings_conhecidos, nomes_conhecidos


def registrar_log(nome, status="AUTORIZADO"):
    """Registra uma ocorrência de acesso com carimbo de data e hora em CSV."""
    agora = datetime.now()
    data = agora.strftime("%d/%m/%Y")
    hora = agora.strftime("%H:%M:%S")

    with open(ARQUIVO_LOG, mode="a", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f)
        escritor.writerow([data, hora, nome, status])