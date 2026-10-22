import sys
from src.utilitarios import carregar_rostos_conhecidos
from src.reconhecedor import iniciar_reconhecimento


def main():
    print("=" * 60)
    print("   SISTEMA DE SEGURANÇA E RECONHECIMENTO FACIAL - MVP")
    print("   Engenharia de Software - UniAnchieta")
    print("=" * 60)

    print("\n[INICIANDO] Carregando cadastros da base de dados...")
    encodings_conhecidos, nomes_conhecidos = carregar_rostos_conhecidos()

    if not encodings_conhecidos:
        print("\n[ALERTA] Nenhum rosto cadastrado em data/cadastros/.")
        print("Insira uma foto .jpg ou .png antes de iniciar.")
        sys.exit(1)

    print(
        f"[SUCESSO] {len(nomes_conhecidos)} face(s) autorizada(s) carregada(s)."
    )
    print("[INICIANDO] Abrindo captura da webcam...\n")

    iniciar_reconhecimento(encodings_conhecidos, nomes_conhecidos)


if __name__ == "__main__":
    main()