# VISIONGUARD | Sistema de Controle de Acesso Biométrico

**Instituição:** Centro Universitário UniAnchieta  
**Disciplina:** Engenharia de Software (Entrega 3)  
**Professor:** Prof. Dr. Roger Antunes  

## Equipe de Desenvolvimento
* **Arthur** - RA: 2606317
* **Caua Olaia Ferrari** - RA: 2603820
* **Cesar Amarez Zotovicci** - RA: 2614117
* **Gabriel Rodrigues do Santos Angioleto** - RA: 2601619
* **Leonardo Gabriel de Lima Costa** - RA: 2527941

---

## Visão Geral do Projeto
O **VisionGuard** é um protótipo MVP (Produto Mínimo Viável) de controle de acesso físico baseado em biometria facial, desenvolvido em Python. O sistema monitora um fluxo de vídeo em tempo real, detecta rostos, mapeia traços anatômicos e valida a identidade contra uma base de dados local autorizada.

O projeto destaca-se pela sua **arquitetura assíncrona multithread**, que separa a captura de vídeo da inferência matemática pesada, garantindo um monitoramento fluido a 30 FPS sem latência.

---

## Arquitetura e Fluxo de Dados
O projeto utiliza um padrão modular limpo (`src/utilitarios.py` e `src/reconhecedor.py` invocados por um `main.py` central):

* **Thread de Captura:** O OpenCV lê o hardware da câmera continuamente em background para esvaziar o buffer do Windows (`ThreadedCamera`).
* **Auditoria Prévia:** Ao inicializar, o sistema audita o lote de fotos de cadastro para garantir a integridade da base (`batch_face_locations`).
* **Pipeline de Detecção:** Rastreamento dinâmico via HOG a cada 2 quadros, com projeção de malha biométrica (68 pontos anatômicos) estilo cyber-HUD.
* **Histerese e Logs:** Estabilizador temporal (*debounce*) calibrado a uma tolerância euclidiana de `0.58`. O sistema exige 2 leituras congruentes para alterar o estado de acesso, evitando falsos negativos por oscilação de luz e registrando os acessos no arquivo `data/logs/acessos.csv`.

---

## Integração da Biblioteca (Critério dos 8 Recursos)
Para satisfazer os requisitos técnicos da disciplina, implementamos 8 funcionalidades distintas da biblioteca principal `face_recognition`:

| Nº | Recurso / Método | Módulo | Função no Sistema |
| :---: | :--- | :--- | :--- |
| **1** | `load_image_file` | `src/utilitarios.py` | Decodificação das fotos de cadastro em matrizes NumPy RGB. |
| **2** | `face_encodings(num_jitters=5)` | `src/utilitarios.py` | Amostragem estocástica múltipla para gerar assinaturas vetoriais mais robustas no cadastro. |
| **3** | `batch_face_locations` | `src/utilitarios.py` | Auditoria em lote na inicialização para validar a integridade de toda a base de dados fotográfica. |
| **4** | `face_locations(model="hog")` | `src/reconhecedor.py` | Detecção das caixas delimitadoras (*bounding boxes*) em tempo real via HOG. |
| **5** | `face_landmarks(model="small")` | `src/reconhecedor.py` | Validação de enquadramento frontal (olhos e nariz nivelados) antes da inferência pesada. |
| **6** | `face_landmarks(model="large")` | `src/reconhecedor.py` | Mapeamento dos 68 pontos anatômicos projetados visualmente como malha no HUD da câmera. |
| **7** | `face_distance` | `src/reconhecedor.py` | Cálculo da distância euclidiana entre a pessoa na câmera e o vetor autorizado. |
| **8** | `compare_faces(tolerance=0.58)` | `src/reconhecedor.py` | Validação booleana calibrada para o equilíbrio ótimo de iluminação em webcams comerciais. |

---

## Guia de Instalação e Execução

### Pré-requisitos
* Python 3.12 instalado.
* Webcam compatível com DirectShow.
* Compilador C++ da Microsoft (Build Tools) e CMake configurados (exigidos pelo `dlib`).

### Passo a Passo

1. **Clonar o Repositório:**
   ```bash
   git clone https://github.com/leocosta-dev26/sistema-seguranca-facial
   cd faculdade-reconhecimento-facial

```

2. **Criar e Ativar o Ambiente Virtual:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1

```

3. **Instalar Dependências:**
```bash
pip install -r requirements.txt

```

4. **Preparar a Base e Executar:**
* Insira uma foto nítida (ex: `Leonardo.jpg`) na pasta `data/cadastros/`.
* Inicie a aplicação:
```bash
python main.py

```

## Casos de Teste e Resolução de Falhas Críticas

Durante a fase de testes práticos da Entrega 3, documentamos os seguintes cenários:

1. **Teste de Sucesso (Condições Normais):** Identificação estabilizada entre 76% e 85% de confiança, com emissão de alerta sonoro agudo e registro de status "AUTORIZADO" no CSV. Transição imediata para "DESCONHECIDO" com alerta grave ao captar uma face não cadastrada.
2. **Registro de Falha e Contingência (Latência de Vídeo):**
* **O Problema:** Na primeira iteração, a execução síncrona da inferência pesada (`face_encodings`) a cada quadro bloqueava a CPU, acumulando quadros na fila do driver e gerando um atraso de 1,5 a 2 segundos na imagem da câmera.
* **A Solução Aplicada:** Refatoramos a arquitetura para **Multithreading Assíncrono**. A câmera passou a ser consumida em tempo real por uma thread paralela dedicada (`ThreadedCamera`), enquanto a inferência pesada roda em segundo plano disparada apenas com enquadramento frontal validado. O atraso foi totalmente eliminado, sustentando 30 FPS contínuos.


3. **Limitações do Modelo:** O algoritmo HOG padrão atenua a detecção em rotações de perfil superiores a 45 graus ou a distâncias maiores que 2 metros (devido à redução de escala em 0.25x adotada para otimização do processador).

---

## Declaração de Uso de Ferramentas de IA

O uso de Inteligência Artificial generativa neste projeto ocorreu de forma pontual e focada. Utilizamos a ferramenta no início do desenvolvimento para auxiliar na ideação da estrutura modular inicial do projeto, consultamos esporadicamente no meio do processo para ultrapassar pequenos entraves sintáticos de integração com bibliotecas compiladas em C++, e, na fase final, utilizamos apenas para revisão textual e validação de documentação. Todo o planejamento arquitetural, calibração de histerese, isolamento de threads e resolução de gargalos de hardware foram executados e homologados integralmente pelos alunos.