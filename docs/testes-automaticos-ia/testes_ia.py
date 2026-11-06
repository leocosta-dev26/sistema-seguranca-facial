"""Testes automaticos do VisionGuard com rostos gerados por IA (fica fora do repositorio).

O que este script faz:
  - Roda o main.py ORIGINAL do projeto uma vez para cada teste (T03, T04, T14, T15, T16).
  - Troca a webcam por uma "camera de teste" que mostra, em sequencia, imagens de
    pessoas que NAO EXISTEM (geradas por IA). Nenhuma pessoa real e necessaria.
  - Usa uma pasta de cadastros e um arquivo de log so do teste, para nao misturar
    com o log real do projeto.
  - Guarda o terminal, o log e alguns quadros da tela de cada teste em resultados/.

Nenhum arquivo do projeto e alterado.

Uso: venv\\Scripts\\python.exe testes_ia.py            (roda todos)
     venv\\Scripts\\python.exe testes_ia.py T03 T14    (roda so alguns)
"""
import os
import shutil
import subprocess
import sys
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
PROJETO = os.path.join(os.path.dirname(AQUI), "sistema-seguranca-facial")
IMAGENS = os.path.join(AQUI, "imagens")
RESULTADOS = os.path.join(AQUI, "resultados")
CADASTROS_PROJETO = os.path.join(PROJETO, "data", "cadastros")

GABRIEL = os.path.join(CADASTROS_PROJETO, "Gabriel.jpeg")
IA1 = os.path.join(IMAGENS, "pessoa_ia_1.jpg")
IA2 = os.path.join(IMAGENS, "pessoa_ia_2.jpg")
IA3 = os.path.join(IMAGENS, "pessoa_ia_3.jpg")
HOMEM = os.path.join(IMAGENS, "dupla_homem.jpg")
MULHER = os.path.join(IMAGENS, "dupla_mulher.jpg")
DUPLA = os.path.join(IMAGENS, "Dupla.jpg")

# Cada cena: (lista de imagens [(arquivo, altura_em_px, centro_x)], segundos). Lista vazia = ninguem.
VAZIO = []
CENARIOS = {
    "T03": {
        "descricao": "Pessoa desconhecida (rosto gerado por IA)",
        "cadastros_extras": [],
        "argumentos": [],
        "roteiro": [
            (VAZIO, 3, "ninguem"),
            ([(IA1, 700, 640)], 8, "pessoa_ia_1 de frente"),
            (VAZIO, 3, "ninguem"),
        ],
    },
    "T04": {
        "descricao": "Duas pessoas no quadro, uma mais perto",
        "cadastros_extras": [],
        "argumentos": [],
        "roteiro": [
            (VAZIO, 3, "ninguem"),
            ([(GABRIEL, 700, 420), (IA1, 420, 1000)], 8, "Gabriel perto + pessoa_ia_1 longe"),
            (VAZIO, 4, "ninguem"),
            ([(IA1, 700, 420), (GABRIEL, 420, 1000)], 8, "pessoa_ia_1 perto + Gabriel longe"),
            (VAZIO, 2, "ninguem"),
        ],
    },
    "T14": {
        "descricao": "Desconhecidos seguidos (menos e mais de 30 s)",
        "cadastros_extras": [],
        "argumentos": [],
        "roteiro": [
            (VAZIO, 3, "ninguem"),
            ([(IA1, 700, 640)], 6, "pessoa_ia_1"),
            (VAZIO, 4, "ninguem"),
            ([(IA2, 700, 640)], 6, "pessoa_ia_2 (menos de 30 s depois)"),
            (VAZIO, 32, "ninguem (esperando passar 30 s)"),
            ([(IA3, 700, 640)], 6, "pessoa_ia_3 (mais de 30 s depois)"),
            (VAZIO, 2, "ninguem"),
        ],
    },
    "T15": {
        "descricao": "Foto de cadastro com duas pessoas (Dupla.jpg, gerada por IA)",
        "cadastros_extras": [DUPLA],
        "argumentos": [],
        "roteiro": [
            (VAZIO, 2, "ninguem"),
            ([(HOMEM, 700, 640)], 7, "homem da Dupla (rosto maior na foto)"),
            (VAZIO, 4, "ninguem"),
            ([(MULHER, 700, 640)], 7, "mulher da Dupla (rosto menor na foto)"),
            (VAZIO, 2, "ninguem"),
        ],
    },
    "T16": {
        "descricao": "Calibracao: distancias de 5 desconhecidos (rostos gerados por IA)",
        "cadastros_extras": [],
        "argumentos": ["--calibrar"],
        "roteiro": [
            (VAZIO, 2, "ninguem"),
            ([(IA1, 700, 640)], 6, "pessoa_ia_1"),
            (VAZIO, 3, "ninguem"),
            ([(IA2, 700, 640)], 6, "pessoa_ia_2"),
            (VAZIO, 3, "ninguem"),
            ([(IA3, 700, 640)], 6, "pessoa_ia_3"),
            (VAZIO, 3, "ninguem"),
            ([(HOMEM, 700, 640)], 6, "homem da Dupla"),
            (VAZIO, 3, "ninguem"),
            ([(MULHER, 700, 640)], 6, "mulher da Dupla"),
            (VAZIO, 2, "ninguem"),
        ],
    },
}


# --------------------------------------------------------------------------- execucao de um teste
def executar_teste(nome):
    """Roda dentro do processo filho: prepara a camera de teste e chama o main.py original."""
    import numpy as np
    import cv2

    cenario = CENARIOS[nome]
    pasta = os.path.join(RESULTADOS, nome)
    largura, altura = 1280, 720
    fundo = np.full((altura, largura, 3), (200, 205, 205), dtype=np.uint8)

    def montar_quadro(itens):
        quadro = fundo.copy()
        for arquivo, alt, centro_x in itens:
            img = cv2.imread(arquivo)
            esc = alt / img.shape[0]
            img = cv2.resize(img, (int(img.shape[1] * esc), alt))
            h, w = img.shape[:2]
            x = max(0, min(largura - w, centro_x - w // 2))
            y = altura - h
            quadro[y:y + h, x:x + w] = img
        return quadro

    cenas = [(montar_quadro(itens), seg, rotulo) for itens, seg, rotulo in cenario["roteiro"]]
    total = sum(seg for _, seg, _ in cenas)
    estado = {"inicio": None, "fim": False, "ultima_cena": -1, "ultimo_print": -1}

    def cena_atual():
        if estado["inicio"] is None:
            estado["inicio"] = time.time()
        t = time.time() - estado["inicio"]
        acumulado = 0
        for i, (quadro, seg, rotulo) in enumerate(cenas):
            acumulado += seg
            if t < acumulado:
                if i != estado["ultima_cena"]:
                    estado["ultima_cena"] = i
                    print(f"[ROTEIRO] t={t:5.1f}s  cena {i + 1}: {rotulo}", flush=True)
                return quadro, t
        estado["fim"] = True
        return cenas[-1][0], t

    class CameraDeTeste:
        def __init__(self, *args, **kwargs):
            pass

        def isOpened(self):
            return True

        def read(self):
            quadro, _ = cena_atual()
            return True, quadro.copy()

        def set(self, *args):
            return True

        def get(self, *args):
            return 0

        def release(self):
            pass

    cv2.VideoCapture = CameraDeTeste

    # Guarda um quadro da tela (com o HUD desenhado) a cada 2 segundos
    imshow_original = cv2.imshow

    def imshow_com_registro(janela, frame):
        if estado["inicio"] is not None:
            segundo = int(time.time() - estado["inicio"])
            if segundo % 2 == 0 and segundo != estado["ultimo_print"]:
                estado["ultimo_print"] = segundo
                cv2.imwrite(os.path.join(pasta, f"tela_{segundo:03d}s.jpg"), frame,
                            [cv2.IMWRITE_JPEG_QUALITY, 80])
        imshow_original(janela, frame)

    cv2.imshow = imshow_com_registro

    # Quando o roteiro acaba, simula a tecla q para encerrar o sistema
    waitkey_original = cv2.waitKey

    def waitkey_de_teste(atraso=1):
        tecla = waitkey_original(atraso)
        return ord("q") if estado["fim"] else tecla

    cv2.waitKey = waitkey_de_teste

    # Pasta de cadastros e log so deste teste
    os.chdir(PROJETO)
    sys.path.insert(0, PROJETO)
    import src.utilitarios as utilitarios

    utilitarios.DIRETORIO_CADASTROS = os.path.join(pasta, "cadastros")
    utilitarios.DIRETORIO_LOGS = pasta
    utilitarios.ARQUIVO_LOG = os.path.join(pasta, "acessos.csv")

    print(f"[TESTE IA] {nome}: {cenario['descricao']}")
    print(f"[TESTE IA] Camera substituida por imagens ({total} s de roteiro). "
          f"Cadastros e log do teste em {pasta}. O codigo do projeto nao foi alterado.", flush=True)

    import runpy
    sys.argv = [os.path.join(PROJETO, "main.py")] + cenario["argumentos"]
    runpy.run_path(os.path.join(PROJETO, "main.py"), run_name="__main__")


# --------------------------------------------------------------------------- orquestrador
def preparar_pasta(nome):
    pasta = os.path.join(RESULTADOS, nome)
    if os.path.isdir(pasta):
        antiga = pasta + "_anterior_" + time.strftime("%H%M%S")
        os.rename(pasta, antiga)
    os.makedirs(os.path.join(pasta, "cadastros"))
    for arquivo in ("Gabriel.jpeg", "Leonardo.jpeg"):
        shutil.copy(os.path.join(CADASTROS_PROJETO, arquivo), os.path.join(pasta, "cadastros"))
    for extra in CENARIOS[nome]["cadastros_extras"]:
        shutil.copy(extra, os.path.join(pasta, "cadastros"))
    return pasta


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    if len(sys.argv) >= 3 and sys.argv[1] == "--executar":
        executar_teste(sys.argv[2])
        return

    pedidos = [a.upper() for a in sys.argv[1:]] or list(CENARIOS)
    os.makedirs(RESULTADOS, exist_ok=True)
    resumo = []

    for nome in pedidos:
        if nome not in CENARIOS:
            print(f"Teste desconhecido: {nome}")
            continue
        pasta = preparar_pasta(nome)
        print("\n" + "=" * 70)
        print(f" {nome} - {CENARIOS[nome]['descricao']}")
        print("=" * 70, flush=True)

        ambiente = dict(os.environ, PYTHONIOENCODING="utf-8")
        inicio = time.time()
        with open(os.path.join(pasta, "terminal.txt"), "w", encoding="utf-8") as saida:
            proc = subprocess.Popen(
                [sys.executable, "-u", "-X", "faulthandler", os.path.abspath(__file__), "--executar", nome],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=ambiente,
                text=True, encoding="utf-8", errors="replace",
            )
            for linha in proc.stdout:
                print(linha, end="", flush=True)
                saida.write(linha)
            proc.wait(timeout=300)
        duracao = time.time() - inicio

        log = os.path.join(pasta, "acessos.csv")
        linhas_log = []
        if os.path.exists(log):
            with open(log, encoding="utf-8") as f:
                linhas_log = [l.strip() for l in f.readlines()[1:] if l.strip()]
        print(f"\n[LOG DO TESTE] {len(linhas_log)} linha(s):")
        for l in linhas_log:
            print("   " + l)
        print(f"[FIM] {nome} terminou em {duracao:.0f} s, codigo de saida {proc.returncode}.", flush=True)
        resumo.append((nome, proc.returncode, len(linhas_log)))

    print("\n" + "=" * 70)
    print(" RESUMO")
    for nome, codigo, n in resumo:
        print(f"   {nome}: codigo de saida {codigo}, {n} linha(s) no log do teste")
    print(f" Resultados em: {RESULTADOS}")
    print("=" * 70)


if __name__ == "__main__":
    main()
