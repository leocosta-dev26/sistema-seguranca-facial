import cv2
import face_recognition
from src.utilitarios import registrar_log


def iniciar_reconhecimento(encodings_conhecidos, nomes_conhecidos):
    """Inicializa a webcam e realiza a detecção e reconhecimento facial em tempo real."""
    # 0 seleciona a câmera padrão do computador
    captura_video = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not captura_video.isOpened():
        print("[ERRO] Não foi possível acessar a webcam.")
        return

    print("\n[SISTEMA ATIVO] Pressione 'q' na janela da câmera para encerrar.\n")

    # Controle para não registrar log a cada milissegundo da mesma pessoa
    ultimo_acesso_registrado = None

    while True:
        sucesso, frame = captura_video.read()
        if not sucesso:
            print("[ERRO] Falha na captura do quadro de vídeo.")
            break

        # Reduz o tamanho do frame para 1/4 (0.25) para aumentar o FPS e não travar a CPU
        frame_pequeno = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # O OpenCV lê em formato BGR, mas o face_recognition exige RGB
        rgb_frame_pequeno = cv2.cvtColor(frame_pequeno, cv2.COLOR_BGR2RGB)

        # Recurso da biblioteca: Localiza as coordenadas das faces no quadro
        locais_faces = face_recognition.face_locations(rgb_frame_pequeno)

        # Recurso da biblioteca: Extrai os vetores matemáticos das faces encontradas
        encodings_faces = face_recognition.face_encodings(
            rgb_frame_pequeno, locais_faces
        )

        for (topo, direita, baixo, esquerda), encoding_face in zip(
            locais_faces, encodings_faces
        ):
            # Recurso da biblioteca: Calcula a distância euclidiana para medir a similaridade
            distancias = face_recognition.face_distance(
                encodings_conhecidos, encoding_face
            )
            # Recurso da biblioteca: Compara tolerâncias (padrão 0.6)
            correspondencias = face_recognition.compare_faces(
                encodings_conhecidos, encoding_face, tolerance=0.55
            )

            nome = "DESCONHECIDO"
            cor = (0, 0, 255)  # Vermelho em BGR (Acesso Negado)

            if len(distancias) > 0:
                melhor_indice = distancias.argmin()
                if correspondencias[melhor_indice]:
                    nome = nomes_conhecidos[melhor_indice]
                    cor = (0, 255, 0)  # Verde em BGR (Acesso Autorizado)

                    if ultimo_acesso_registrado != nome:
                        registrar_log(nome, status="AUTORIZADO")
                        ultimo_acesso_registrado = nome
                        print(f"[EVENTO] Acesso liberado para: {nome}")

            # Reajusta as coordenadas para o tamanho original da tela (multiplica por 4)
            topo *= 4
            direita *= 4
            baixo *= 4
            esquerda *= 4

            # Desenha o retângulo ao redor do rosto
            cv2.rectangle(frame, (esquerda, topo), (direita, baixo), cor, 2)

            # Desenha a barra para o nome
            cv2.rectangle(
                frame,
                (esquerda, baixo - 35),
                (direita, baixo),
                cor,
                cv2.FILLED,
            )
            cv2.putText(
                frame,
                nome,
                (esquerda + 6, baixo - 6),
                cv2.FONT_HERSHEY_DUPLEX,
                0.8,
                (255, 255, 255),
                1,
            )

        # Exibe a janela de segurança em tempo real
        cv2.imshow("Sistema de Seguranca Facial - UniAnchieta", frame)

        # Tecla 'q' encerra a execução
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # Libera os recursos de hardware da câmera e fecha janelas
    captura_video.release()
    cv2.destroyAllWindows()