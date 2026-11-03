import cv2
import face_recognition
import numpy as np
import threading
import time
import winsound
from datetime import datetime
from src.utilitarios import registrar_log, area_do_rosto

# Limites da validação de enquadramento frontal (calibráveis nos testes)
LIMITE_INCLINACAO = 0.3     # desnível máximo entre os olhos, relativo à distância entre eles
LIMITE_DESVIO_NARIZ = 0.2   # quanto o nariz pode se afastar do ponto médio entre os olhos

COR_NEUTRA = (160, 160, 160)


class ThreadedCamera:
    """Captura quadros da webcam continuamente em segundo plano para eliminar a latência."""
    def __init__(self, src=0):
        self.cap = cv2.VideoCapture(src, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.sucesso, self.frame = self.cap.read()
        self.rodando = True
        self.thread = threading.Thread(target=self._atualizar, daemon=True)
        self.thread.start()

    def _atualizar(self):
        while self.rodando:
            if self.cap.isOpened():
                sucesso, frame = self.cap.read()
                if sucesso:
                    self.sucesso = sucesso
                    self.frame = frame
            time.sleep(0.005)

    def ler(self):
        return self.sucesso, (self.frame.copy() if self.frame is not None else None)

    def liberar(self):
        self.rodando = False
        # Espera a thread de captura terminar antes de liberar a câmera
        self.thread.join(timeout=1.0)
        if self.cap.isOpened():
            self.cap.release()


class ReconhecedorAssincrono:
    """Gerencia a inferência biométrica com amortecimento temporal (histerese) e limiar calibrado."""
    def __init__(self, encodings_conhecidos, nomes_conhecidos, limiar=0.58):
        self.encodings_conhecidos = encodings_conhecidos
        self.nomes_conhecidos = nomes_conhecidos
        self.limiar = limiar
        self.processando = False

        # Estado confirmado exibido no HUD
        self.ultimo_reconhecido = "DESCONHECIDO"
        self.ultimo_status_autorizado = False
        self.ultima_confianca = 0.0

        # Mecanismo de histerese e consistência
        self.candidato_nome = "DESCONHECIDO"
        self.candidato_autorizado = False
        self.contagem_consistencia = 0
        self.LIMIAR_CONGRUENCIA = 2  # Exige pelo menos 2 leituras idênticas para comutar de estado

        self.ultimo_evento_disparado = None
        self.tempo_ultimo_evento = 0.0
        self.INTERVALO_COOLDOWN = 3.0  # Intervalo mínimo (segundos) entre dois eventos seguidos

    def solicitar_identificacao(self, rgb_frame, local_face):
        if self.processando:
            return

        self.processando = True

        def _inferir():
            try:
                # RECURSO 2: face_recognition.face_encodings (assinatura do rosto da câmera)
                encodings = face_recognition.face_encodings(rgb_frame, [local_face])
                if len(encodings) > 0:
                    encoding = encodings[0]

                    # RECURSO 7: face_recognition.face_distance
                    distancias = face_recognition.face_distance(self.encodings_conhecidos, encoding)

                    # RECURSO 8: face_recognition.compare_faces calibrado em 0.58
                    correspondencias = face_recognition.compare_faces(
                        self.encodings_conhecidos, encoding, tolerance=self.limiar
                    )

                    nome_instantaneo = "DESCONHECIDO"
                    autorizado_instantaneo = False
                    confianca_instantanea = 0.0

                    if len(distancias) > 0:
                        melhor_indice = distancias.argmin()
                        dist = distancias[melhor_indice]
                        confianca_instantanea = calcular_confianca(dist, limiar=self.limiar)

                        if correspondencias[melhor_indice]:
                            nome_instantaneo = self.nomes_conhecidos[melhor_indice]
                            autorizado_instantaneo = True

                    # Filtro de histerese para evitar oscilações passageiras de luz/ângulo
                    if nome_instantaneo == self.candidato_nome:
                        self.contagem_consistencia += 1
                    else:
                        self.candidato_nome = nome_instantaneo
                        self.candidato_autorizado = autorizado_instantaneo
                        self.contagem_consistencia = 1

                    # Comuta o estado apenas quando comprovada estabilidade temporal
                    if self.contagem_consistencia >= self.LIMIAR_CONGRUENCIA:
                        self.ultimo_reconhecido = self.candidato_nome
                        self.ultimo_status_autorizado = self.candidato_autorizado
                        self.ultima_confianca = confianca_instantanea

                        # Cada mudança de identidade gera um único evento (log + som).
                        # A mesma pessoa só gera outro evento depois de sair do quadro.
                        agora = time.time()
                        if (self.ultimo_reconhecido != self.ultimo_evento_disparado) and (
                            agora - self.tempo_ultimo_evento > self.INTERVALO_COOLDOWN
                        ):
                            status = "AUTORIZADO" if self.ultimo_status_autorizado else "NEGADO"
                            registrar_log(self.ultimo_reconhecido, status=status)
                            emitir_som(self.ultimo_status_autorizado)
                            print(f"[EVENTO] {status}: {self.ultimo_reconhecido} ({self.ultima_confianca:.1f}%)")
                            self.ultimo_evento_disparado = self.ultimo_reconhecido
                            self.tempo_ultimo_evento = agora
                    else:
                        # Mantém a leitura da confiança atualizada quando é o mesmo indivíduo
                        if nome_instantaneo == self.ultimo_reconhecido:
                            self.ultima_confianca = confianca_instantanea

            finally:
                self.processando = False

        threading.Thread(target=_inferir, daemon=True).start()

    def resetar_estado(self):
        """Reinicia os indicadores de estado quando a câmera fica sem nenhum rosto."""
        self.ultimo_reconhecido = "DESCONHECIDO"
        self.ultimo_status_autorizado = False
        self.ultima_confianca = 0.0
        self.candidato_nome = "DESCONHECIDO"
        self.candidato_autorizado = False
        self.contagem_consistencia = 0
        self.ultimo_evento_disparado = None


def emitir_som(autorizado: bool):
    """Emite alertas sonoros em segundo plano."""
    def _tocar():
        try:
            if autorizado:
                winsound.Beep(1200, 100)
                winsound.Beep(1600, 120)
            else:
                winsound.Beep(450, 300)
        except Exception:
            pass

    threading.Thread(target=_tocar, daemon=True).start()


def calcular_confianca(distancia, limiar=0.58):
    """Calibra a confiança percentual com base no limiar ótimo de 0.58."""
    if distancia <= limiar:
        fator = (limiar - distancia) / limiar
        confianca = 78.0 + (fator * 20.0)
    else:
        fator = min(1.0, (distancia - limiar) / (1.0 - limiar))
        confianca = 50.0 - (fator * 35.0)
    return round(max(10.0, min(99.0, confianca)), 1)


def verificar_enquadramento_frontal(rgb_pequeno, local_face):
    """
    RECURSO 5: face_recognition.face_landmarks com model='small'
    Usa os 5 marcos (cantos dos olhos e base do nariz) para recusar rostos
    inclinados ou de perfil antes da inferência pesada.
    """
    marcos_5 = face_recognition.face_landmarks(rgb_pequeno, [local_face], model="small")
    if not marcos_5:
        return False
    dados = marcos_5[0]

    # Centro de cada olho, ordenados da esquerda para a direita da imagem
    centro_a = np.mean(dados["left_eye"], axis=0)
    centro_b = np.mean(dados["right_eye"], axis=0)
    olho_esq, olho_dir = sorted([centro_a, centro_b], key=lambda centro: centro[0])
    nariz_x = dados["nose_tip"][0][0]

    distancia_olhos = olho_dir[0] - olho_esq[0]
    if distancia_olhos <= 0:
        return False

    # Cabeça inclinada para o lado: um olho fica bem mais alto que o outro
    inclinacao = abs(olho_dir[1] - olho_esq[1]) / distancia_olhos

    # Cabeça virada: o nariz sai do meio dos olhos (0.5 = centralizado)
    posicao_nariz = (nariz_x - olho_esq[0]) / distancia_olhos

    return inclinacao <= LIMITE_INCLINACAO and abs(posicao_nariz - 0.5) <= LIMITE_DESVIO_NARIZ


def extrair_malha_biometrica(rgb_pequeno, local_face):
    """
    RECURSO 6: face_recognition.face_landmarks com model='large'
    Extração dos 68 pontos anatômicos para desenhar a malha no HUD.
    """
    marcos_68 = face_recognition.face_landmarks(rgb_pequeno, [local_face], model="large")
    if marcos_68:
        return marcos_68[0]
    return {}


def desenhar_malha_hud(frame, marcos_dict, cor):
    """Desenha os pontos anatômicos, convertidos para a escala do quadro original."""
    for parte, pontos in marcos_dict.items():
        for (x, y) in pontos:
            cv2.circle(frame, (x * 4, y * 4), 1, cor, -1)


def desenhar_cantos_estilizados(imagem, x1, y1, x2, y2, cor, espessura=2, comprimento=20):
    """Desenha a moldura de segurança com cantos reforçados."""
    cv2.rectangle(imagem, (x1, y1), (x2, y2), cor, 1)

    # Cantos superiores
    cv2.line(imagem, (x1, y1), (x1 + comprimento, y1), cor, espessura)
    cv2.line(imagem, (x1, y1), (x1, y1 + comprimento), cor, espessura)
    cv2.line(imagem, (x2, y1), (x2 - comprimento, y1), cor, espessura)
    cv2.line(imagem, (x2, y1), (x2, y1 + comprimento), cor, espessura)

    # Cantos inferiores
    cv2.line(imagem, (x1, y2), (x1 + comprimento, y2), cor, espessura)
    cv2.line(imagem, (x1, y2), (x1, y2 - comprimento), cor, espessura)
    cv2.line(imagem, (x2, y2), (x2 - comprimento, y2), cor, espessura)
    cv2.line(imagem, (x2, y2), (x2, y2 - comprimento), cor, espessura)


def desenhar_rotulo_neutro(frame, x1, y1, x2, y2, texto):
    """Moldura cinza com um aviso, para rostos que não estão sendo verificados."""
    desenhar_cantos_estilizados(frame, x1, y1, x2, y2, COR_NEUTRA)
    pos_y = max(55, y1 - 10)
    cv2.putText(frame, texto, (x1, pos_y), cv2.FONT_HERSHEY_DUPLEX, 0.5, COR_NEUTRA, 1)


def desenhar_painel_superior(frame, total_cadastros):
    """Barra superior com cálculo dinâmico de layout."""
    altura, largura, _ = frame.shape
    overlay = frame.copy()

    cv2.rectangle(overlay, (0, 0), (largura, 40), (20, 20, 20), -1)
    cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)
    cv2.line(frame, (0, 40), (largura, 40), (70, 70, 70), 1)

    cv2.putText(frame, "VISIONGUARD | CONTROLE DE ACESSO", (15, 25),
                cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1)

    hora_atual = datetime.now().strftime("%H:%M:%S")
    texto_direita = f"BASE: {total_cadastros} | {hora_atual}"
    (largura_txt, _), _ = cv2.getTextSize(texto_direita, cv2.FONT_HERSHEY_DUPLEX, 0.45, 1)
    pos_x_direita = max(largura - largura_txt - 15, 330)

    cv2.putText(frame, texto_direita, (pos_x_direita, 25),
                cv2.FONT_HERSHEY_DUPLEX, 0.45, (180, 180, 180), 1)


def desenhar_badge_identificacao(frame, x1, y1, x2, y2, nome, autorizado, confianca):
    """Desenha a etiqueta translúcida sem deixar que ela saia da tela."""
    altura_frame, largura_frame, _ = frame.shape
    altura_badge = 48
    largura_badge = 200

    pos_y = y2 + 8
    if pos_y + altura_badge > altura_frame:
        pos_y = max(45, y1 - altura_badge - 8)

    pos_x = min(max(10, x1), largura_frame - largura_badge - 10)

    overlay = frame.copy()
    cor_fundo = (20, 90, 20) if autorizado else (25, 25, 130)
    cor_borda = (0, 255, 120) if autorizado else (0, 0, 255)

    cv2.rectangle(overlay, (pos_x, pos_y), (pos_x + largura_badge, pos_y + altura_badge), cor_fundo, -1)
    cv2.addWeighted(overlay, 0.85, frame, 0.15, 0, frame)
    cv2.rectangle(frame, (pos_x, pos_y), (pos_x + largura_badge, pos_y + altura_badge), cor_borda, 1)

    status_txt = "ACESSO LIBERADO" if autorizado else "ACESSO NEGADO"
    cv2.putText(frame, status_txt, (pos_x + 8, pos_y + 20),
                cv2.FONT_HERSHEY_DUPLEX, 0.48, cor_borda, 1)

    subtexto = f"{nome} ({confianca:.0f}%)" if autorizado else "DESCONHECIDO"
    cv2.putText(frame, subtexto, (pos_x + 8, pos_y + 38),
                cv2.FONT_HERSHEY_DUPLEX, 0.45, (255, 255, 255), 1)


def iniciar_reconhecimento(encodings_conhecidos, nomes_conhecidos):
    """Laço principal de monitoramento com pipeline assíncrono e estabilidade temporal."""
    nome_janela = "VisionGuard - Controle de Acesso Facial"

    camera = ThreadedCamera(0)
    if not camera.sucesso:
        print("[ERRO] Falha ao conectar a webcam via DirectShow.")
        camera.liberar()
        return

    cv2.namedWindow(nome_janela, cv2.WINDOW_NORMAL)

    print("\n[VISIONGUARD ATIVO] Monitoramento em tempo real iniciado.")
    print("Pressione 'q' na janela de monitoramento para encerrar.\n")

    reconhecedor = ReconhecedorAssincrono(encodings_conhecidos, nomes_conhecidos, limiar=0.58)

    contador_quadros = 0
    locais_faces = []
    local_principal = None
    frontal_ok = False
    marcos_faciais = {}
    tempo_ultimo_rosto = time.time()

    while True:
        sucesso, frame = camera.ler()
        if not sucesso or frame is None:
            time.sleep(0.01)
            continue

        contador_quadros += 1

        # Localiza os rostos a cada 2 quadros
        if contador_quadros % 2 == 0:
            frame_pequeno = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_pequeno = cv2.cvtColor(frame_pequeno, cv2.COLOR_BGR2RGB)

            # RECURSO 4: face_recognition.face_locations com model="hog"
            locais_faces = face_recognition.face_locations(rgb_pequeno, model="hog")

            if len(locais_faces) > 0:
                tempo_ultimo_rosto = time.time()
                # Só o rosto mais próximo da câmera (o maior) é verificado
                local_principal = max(locais_faces, key=area_do_rosto)

                # RECURSO 5: face_landmarks com model="small" recusa rostos inclinados ou de perfil
                frontal_ok = verificar_enquadramento_frontal(rgb_pequeno, local_principal)

                # RECURSO 6: face_landmarks com model="large" extrai os 68 marcos da malha do HUD
                marcos_faciais = extrair_malha_biometrica(rgb_pequeno, local_principal)

                if frontal_ok:
                    reconhecedor.solicitar_identificacao(rgb_pequeno, local_principal)
            else:
                local_principal = None
                marcos_faciais = {}
                if time.time() - tempo_ultimo_rosto > 2.0:
                    reconhecedor.resetar_estado()

        desenhar_painel_superior(frame, len(nomes_conhecidos))

        # Desenho dos elementos do HUD
        for local in locais_faces:
            topo, direita, baixo, esquerda = local
            x1, y1, x2, y2 = esquerda * 4, topo * 4, direita * 4, baixo * 4

            # Os demais rostos não foram verificados e nunca aparecem como liberados
            if local != local_principal:
                desenhar_rotulo_neutro(frame, x1, y1, x2, y2, "AGUARDE SUA VEZ")
                continue

            if not frontal_ok:
                desenhar_rotulo_neutro(frame, x1, y1, x2, y2, "OLHE PARA A CAMERA")
                continue

            autorizado = reconhecedor.ultimo_status_autorizado
            cor_tema = (0, 255, 120) if autorizado else (0, 0, 255)

            # Desenho da malha biométrica
            desenhar_malha_hud(frame, marcos_faciais, cor_tema)

            # Contornos estilizados e cartão de identificação
            desenhar_cantos_estilizados(frame, x1, y1, x2, y2, cor_tema)
            desenhar_badge_identificacao(
                frame, x1, y1, x2, y2,
                reconhecedor.ultimo_reconhecido,
                autorizado,
                reconhecedor.ultima_confianca
            )

        cv2.imshow(nome_janela, frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # Fechar a janela pelo X também encerra o sistema
        if cv2.getWindowProperty(nome_janela, cv2.WND_PROP_VISIBLE) < 1:
            break

    camera.liberar()
    cv2.destroyAllWindows()