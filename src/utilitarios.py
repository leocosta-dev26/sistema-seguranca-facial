import os
import csv
import cv2
import numpy as np
from datetime import datetime
import face_recognition

# Caminhos base do sistema, calculados a partir da pasta do projeto
# (funciona mesmo que o main.py seja executado de outra pasta)
RAIZ_PROJETO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIRETORIO_CADASTROS = os.path.join(RAIZ_PROJETO, "data", "cadastros")
DIRETORIO_LOGS = os.path.join(RAIZ_PROJETO, "data", "logs")
ARQUIVO_LOG = os.path.join(DIRETORIO_LOGS, "acessos.csv")

# O detector CNN processa o lote de uma vez e exige que todas as fotos tenham o mesmo tamanho
LADO_AUDITORIA = 600


def inicializar_estrutura():
    """Garante que as pastas e o arquivo de log existam com cabeçalho antes da execução."""
    os.makedirs(DIRETORIO_CADASTROS, exist_ok=True)
    os.makedirs(DIRETORIO_LOGS, exist_ok=True)

    # Escreve o cabeçalho caso o arquivo não exista ou esteja zerado (0 bytes)
    if not os.path.exists(ARQUIVO_LOG) or os.path.getsize(ARQUIVO_LOG) == 0:
        with open(ARQUIVO_LOG, mode="w", newline="", encoding="utf-8") as f:
            escritor = csv.writer(f)
            escritor.writerow(["Data", "Hora", "Nome", "Status"])


def area_do_rosto(local_face):
    """Área da caixa (topo, direita, baixo, esquerda) de um rosto. Serve para achar o maior."""
    topo, direita, baixo, esquerda = local_face
    return (baixo - topo) * (direita - esquerda)


def preparar_para_lote(imagem):
    """
    Reduz a foto para caber num quadrado de LADO_AUDITORIA pixels e completa o resto com preto.
    Retorna a imagem preparada e a escala usada, para converter as coordenadas de volta.
    """
    altura, largura = imagem.shape[:2]
    escala = min(LADO_AUDITORIA / largura, LADO_AUDITORIA / altura, 1.0)
    reduzida = cv2.resize(imagem, (int(largura * escala), int(altura * escala)))

    quadro = np.zeros((LADO_AUDITORIA, LADO_AUDITORIA, 3), dtype=np.uint8)
    quadro[:reduzida.shape[0], :reduzida.shape[1]] = reduzida
    return quadro, escala


def auditar_integridade_base(imagens):
    """
    RECURSO 3: face_recognition.batch_face_locations
    Procura, em lote e com o detector CNN, os rostos de todas as fotos de cadastro.
    Retorna, para cada foto, a lista de rostos encontrados nas coordenadas da foto original.
    """
    preparadas = []
    escalas = []
    for imagem in imagens:
        quadro, escala = preparar_para_lote(imagem)
        preparadas.append(quadro)
        escalas.append(escala)

    resultados_lote = face_recognition.batch_face_locations(
        preparadas, number_of_times_to_upsample=0, batch_size=4
    )

    rostos_por_foto = []
    for imagem, escala, locais in zip(imagens, escalas, resultados_lote):
        altura, largura = imagem.shape[:2]
        rostos = []
        for local in locais:
            topo, direita, baixo, esquerda = (int(coord / escala) for coord in local)
            rostos.append((max(topo, 0), min(direita, largura), min(baixo, altura), max(esquerda, 0)))
        rostos_por_foto.append(rostos)

    return rostos_por_foto


def carregar_rostos_conhecidos():
    """
    Varre data/cadastros, audita as fotos em lote, extrai as assinaturas biométricas
    com superamostragem e retorna as listas de vetores de 128 dimensões e de nomes conhecidos.
    """
    inicializar_estrutura()
    encodings_conhecidos = []
    nomes_conhecidos = []

    extensoes_validas = (".jpg", ".jpeg", ".png")
    arquivos_validos = [
        f for f in os.listdir(DIRETORIO_CADASTROS) if f.lower().endswith(extensoes_validas)
    ]
    if not arquivos_validos:
        return encodings_conhecidos, nomes_conhecidos

    # RECURSO 1: face_recognition.load_image_file
    imagens = [
        face_recognition.load_image_file(os.path.join(DIRETORIO_CADASTROS, f))
        for f in arquivos_validos
    ]

    # Auditoria em lote: descobre quais fotos têm rosto antes do processamento pesado
    try:
        rostos_por_foto = auditar_integridade_base(imagens)
        com_rosto = sum(1 for rostos in rostos_por_foto if rostos)
        print(f"[AUDITORIA] {com_rosto} de {len(imagens)} foto(s) com rosto detectado.")
    except Exception as erro:
        print(f"[AUDITORIA] Não foi possível executar a auditoria em lote: {erro}")
        print("[AUDITORIA] Seguindo com a detecção padrão (HOG) em cada foto.")
        rostos_por_foto = [None] * len(imagens)

    for arquivo, imagem, rostos in zip(arquivos_validos, imagens, rostos_por_foto):
        if rostos is not None:
            if not rostos:
                print(f"[AUDITORIA] O detector CNN não achou rosto em {arquivo}. Tentando com o HOG.")
                rostos = None
            else:
                if len(rostos) > 1:
                    print(f"[AUDITORIA] {len(rostos)} rostos em {arquivo}. Usando o maior.")
                rostos = [max(rostos, key=area_do_rosto)]

        # RECURSO 2: face_recognition.face_encodings com num_jitters=5
        # num_jitters reamostra o rosto 5 vezes com leves distorções para maior robustez.
        # Quando a auditoria funcionou, usa o rosto que ela encontrou (rostos=None faz a busca via HOG).
        codificacoes = face_recognition.face_encodings(
            imagem, known_face_locations=rostos, num_jitters=5
        )

        if len(codificacoes) > 0:
            encodings_conhecidos.append(codificacoes[0])
            nome = os.path.splitext(arquivo)[0].replace("_", " ").title()
            nomes_conhecidos.append(nome)
            print(f"[CADASTRO] Assinatura biométrica registrada: {nome}")
        else:
            print(f"[AVISO] Nenhum rosto identificado na foto: {arquivo}")

    return encodings_conhecidos, nomes_conhecidos


def registrar_log(nome, status="AUTORIZADO"):
    """Registra uma ocorrência de acesso com data e hora no CSV."""
    agora = datetime.now()
    data = agora.strftime("%d/%m/%Y")
    hora = agora.strftime("%H:%M:%S")

    with open(ARQUIVO_LOG, mode="a", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f)
        escritor.writerow([data, hora, nome, status])
