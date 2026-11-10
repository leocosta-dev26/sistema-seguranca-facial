# Casos de Teste e Registro de Falhas | VisionGuard

**Responsável:** Gabriel Angioleto (Qualidade e documentação)
**Período de execução:** a partir de 05/11/2026

## Ambiente de teste

| Item | PC 1: notebook do Gabriel | PC 2: desktop (DESKTOP-T39HOPS) |
| :--- | :--- | :--- |
| Sistema | Windows 11 | Windows 11 Home |
| Processador | Intel Celeron N4000 @ 1.10 GHz, **sem AVX** ([print](evidencias/T01-processador.png)) | Intel com AVX ([registro](evidencias/T01-ambiente-pc2.txt)) |
| Python | 3.12 em `venv` | 3.12.10 em `venv` (na 1ª tentativa, 3.14.7 global; ver o registro do T01) |
| Terminal | Prompt de Comando (cmd) | Prompt de Comando (cmd), pelo `PREPARAR-NO-OUTRO-PC.bat` |
| Webcam | Integrada | Celular como webcam, pelo DroidCam Client (na 1ª tentativa, nenhuma) |

## Como ler este documento

- **Status:** `Passou`, `Falhou` ou `Pendente` (ainda não executado).
- **Evidência:** link para o print em `docs/evidencias/`, a gravação de tela ou o trecho do `data/logs/acessos.csv`. Prints com o rosto do Gabriel estão em `evidencias-privadas-com-rosto/`, publicados com a autorização dele.
- Os detalhes de cada execução ficam na seção "Registro das execuções", no fim do documento.

## Como os testes foram executados

| Forma | Testes | Como |
| :--- | :--- | :--- |
| Manual, PC 1 | T01 | Seguindo o README à risca no notebook do Gabriel |
| Manual, PC 2, com adaptador de câmera | T01, T02, T05, T06, T07, T09, T10, T11, T12, T13 | O Gabriel diante da câmera (celular pelo DroidCam). O adaptador `rodar_com_msmf.py` só troca o DirectShow pelo Media Foundation (P5) |
| Automática, PC 2, com rostos gerados por IA | T03, T04, T14, T15, T16 | O `testes_ia.py` roda o `main.py` original e troca a câmera por uma sequência de imagens de **pessoas que não existem**, geradas por IA. Assim não foi preciso usar o rosto de pessoas reais sem autorização. Cada teste usa uma pasta de cadastros e um log próprios, sem misturar com o log real |

Em todas as formas, **nenhum arquivo do projeto foi alterado**. Os scripts de apoio ficam em `scripts-de-apoio/` e `testes-automaticos-ia/`.

---

## 1. Casos de teste

| ID | Cenário | Resultado esperado | Obtido | Status | Evidência |
| :---: | :--- | :--- | :--- | :---: | :--- |
| T01 | Instalação em máquina limpa, seguindo só o README | Instala sem erro e abre a janela da câmera | **PC 1:** as dependências instalaram, mas o `python main.py` fecha sem mensagem: `Illegal instruction` no `dlib`, porque o processador não tem AVX (P1, P2, P3). **PC 2:** instalou sem erro, carregou os 2 cadastros e parou em `[ERRO] Falha ao conectar a webcam via DirectShow`, porque não havia webcam (P4). Com o DroidCam: `int divide by zero` no driver ao abrir a câmera 0 (P5). **Com o adaptador de teste (Media Foundation, 1280x720): a janela da câmera abriu com imagem e reconheceu o Gabriel** | Passou no PC 2 (com adaptador); falhou no PC 1 | PC 1: [pip](evidencias/T01-pip-ok.png), [erro](evidencias/T01-illegal-instruction.png), [CPU](evidencias/T01-processador.png) · PC 2: [início](evidencias/T01-pc2-1-sem-python312.png), [pip](evidencias/T01-pc2-2-pip-no-python314.png), [sem webcam](evidencias/T01-pc2-3-sem-webcam.png), [DroidCam](evidencias/T01-pc2-4-droidcam-divide-by-zero.png), [aprovado](evidencias/T01-pc2-7-terminal-autorizado.png) |
| T02 | Pessoa cadastrada de frente, a 50 cm–1 m | "ACESSO LIBERADO", nome e %, dois bipes agudos, uma linha AUTORIZADO. Anotar o % | PC 2, com adaptador: moldura verde com "ACESSO LIBERADO" e "Gabriel (89%)", malha de pontos no rosto, dois bipes agudos (confirmados pelo testador) e uma linha no log (`05/11/2026,23:56:36,Gabriel,AUTORIZADO`). Terminal: `AUTORIZADO: Gabriel (89.1%, distância 0.257)`. Na 1ª leitura, às 23:53: 87,2% | Passou | [terminal](evidencias/T02-terminal-autorizado.png), [tela](evidencias-privadas-com-rosto/T02-acesso-liberado-COM-ROSTO.png) |
| T03 | Pessoa desconhecida (foto no celular ou pessoa real que concordou) | "ACESSO NEGADO", um bipe grave, uma linha DESCONHECIDO, NEGADO | Automático, rosto gerado por IA: cartão vermelho "ACESSO NEGADO / DESCONHECIDO", terminal `NEGADO: DESCONHECIDO (34.9%, distância 0.761)`, uma linha `DESCONHECIDO,NEGADO` no log. Som não verificado (execução automática) | Passou | [terminal](testes-automaticos-ia/resultados/T03/terminal.txt), [log](testes-automaticos-ia/resultados/T03/acessos.csv), [tela](testes-automaticos-ia/resultados/T03/tela_006s.jpg) |
| T04 | Duas pessoas, uma mais perto que a outra | O mais perto é verificado; o outro fica cinza com "AGUARDE SUA VEZ" | Automático, com a foto de cadastro do Gabriel e um rosto gerado por IA. **Gabriel perto:** `AUTORIZADO: Gabriel (94.2%)` e o rosto de trás cinza, "AGUARDE SUA VEZ". **Rosto IA perto:** `NEGADO: DESCONHECIDO (35.0%)` e o Gabriel, atrás, cinza, "AGUARDE SUA VEZ", **sem ser liberado** | Passou | [terminal](testes-automaticos-ia/resultados/T04/terminal.txt), [log](testes-automaticos-ia/resultados/T04/acessos.csv), [Gabriel perto](evidencias-privadas-com-rosto/T04-gabriel-perto-ia-longe-COM-ROSTO.jpg), [rosto IA perto](evidencias-privadas-com-rosto/T04-ia-perto-gabriel-longe-COM-ROSTO.jpg) |
| T05 | Rosto de lado (virar a cabeça devagar para os dois lados) | "OLHE PARA A CAMERA" antes de qualquer "ACESSO NEGADO"; muito de lado, a moldura some | PC 2, com adaptador. **Um lado:** funcionou como esperado (moldura cinza "OLHE PARA A CAMERA" e, mais de lado, a moldura some). **Outro lado:** quase de perfil, a checagem de frente **não barrou**: moldura verde "ACESSO LIBERADO" e, em seguida, **o Gabriel foi reconhecido como Leonardo** (`AUTORIZADO: Leonardo (79.7%, distância 0.530)`) e o log registrou `23:59:21,Leonardo,AUTORIZADO` (P6). **Reteste em 10/11, depois da correção, com duas pessoas cadastradas (Arthur e Leonardo):** os dois lados mostraram "OLHE PARA A CAMERA", e o sistema nunca trocou o nome | Falhou em 05/11; **passou no reteste de 10/11** | [terminal](evidencias/T05-terminal-leonardo-autorizado.png), [olhe para a câmera](evidencias-privadas-com-rosto/T05-1-olhe-para-a-camera-COM-ROSTO.png), [de lado](evidencias-privadas-com-rosto/T05-2-de-lado-sem-moldura-COM-ROSTO.png), [perfil liberado](evidencias-privadas-com-rosto/T05-3-perfil-liberado-gabriel-COM-ROSTO.png), [liberado como Leonardo](evidencias-privadas-com-rosto/T05-4-perfil-liberado-como-leonardo-COM-ROSTO.png) · Reteste: [lado 1](evidencias-privadas-com-rosto/T05-reteste-1-lado-1-olhe-para-a-camera-COM-ROSTO.png), [lado 2](evidencias-privadas-com-rosto/T05-reteste-2-lado-2-olhe-para-a-camera-COM-ROSTO.png), [liberado](evidencias-privadas-com-rosto/T05-reteste-3-de-frente-liberado-COM-ROSTO.png) |
| T06 | Foto do cadastrado no celular | Provavelmente libera (confirma a falta de prova de vida) | PC 2, com adaptador: a foto `Gabriel.jpeg`, aberta no segundo monitor e filmada pelo celular, **liberou o acesso**. Tela: "ACESSO LIBERADO", "Gabriel (93%)". Terminal: `AUTORIZADO: Gabriel (93.2%, distância 0.139)`. Log: `06/11/2026,00:14:48,Gabriel,AUTORIZADO`. A confiança foi **maior** que com o rosto real (85% a 89%) | Passou (confirma a limitação) | [terminal](evidencias/T06-terminal-foto-liberada.png), [tela](evidencias-privadas-com-rosto/T06-foto-no-monitor-liberada-COM-ROSTO.png) |
| T07 | Sair e voltar (carência) | Volta rápida: som e `[CARÊNCIA]`, sem linha nova. Após 5 min: linha nova. Parado: nenhuma linha nova | PC 2, com adaptador. Registro às 00:25:47. **Parado e voltas rápidas:** só `[CARÊNCIA] Gabriel já registrado há 47 s ... 295 s`, sem linha nova. **Depois de 5 min:** linha nova às 00:31:18 (`AUTORIZADO: Gabriel (88.8%)`). Na mesma execução, 3 leituras do Gabriel entrando ou saindo do quadro viraram `DESCONHECIDO, NEGADO` (P7) | Passou (com a ressalva do P7) | [terminal](evidencias/T07-terminal-completo.png) |
| T08 | Pouca luz / contra a luz | Anotar se reconhece, nega ou nem detecta | | Pendente | |
| T09 | Distância: 0,5 m, 1 m, 2 m e 3 m | Anotar até onde detecta e até onde reconhece | PC 2, com adaptador (celular pelo DroidCam, 1280x720). **Até cerca de 1 m:** detecta e reconhece (moldura verde, Gabriel). **A partir de cerca de 1 m:** não reconhece, e nas capturas mais distantes nem desenha moldura (o rosto não é detectado). Distâncias estimadas pelo testador | Executado (medição) | 3 prints com rosto guardados fora do repositório |
| T10 | Foto de cadastro sem rosto (ex.: `paisagem.jpg`) | `[AUDITORIA] O detector CNN não achou rosto...` e `[AVISO] Nenhum rosto identificado`; as outras fotos carregam | PC 2, com adaptador: `[AUDITORIA] 2 de 3 foto(s) com rosto detectado`, `[AUDITORIA] O detector CNN não achou rosto em paisagem.jpg`, `[AVISO] Nenhum rosto identificado na foto: paisagem.jpg`; Gabriel e Leonardo carregados (`2 face(s) autorizada(s)`, "BASE: 2" na tela), e o sistema seguiu funcionando (`AUTORIZADO: Gabriel (85.3%)`) | Passou | [print](evidencias/T10-foto-sem-rosto.png) |
| T11 | Base vazia (sem fotos em `data/cadastros/`) | `[ALERTA] Nenhum rosto cadastrado` e o programa encerra | PC 2: `[ALERTA] Nenhum rosto cadastrado em data/cadastros/.` e `Insira uma foto .jpg, .jpeg ou .png antes de iniciar.`; o programa encerrou sozinho, antes de abrir a câmera, com **código de saída 1** | Passou | [print](evidencias/T11-base-vazia.png) |
| T12 | Encerrar com `q` e depois pelo X | O programa encerra nos dois casos | PC 2, com adaptador. **`q`** (05/11, 23:49): encerrou, código de saída 0. **X da janela** (06/11, 00:08): encerrou, código de saída 0, sem travar nem deixar a câmera presa | Passou | [q](evidencias/T12-fechar-com-q.png), [X](evidencias/T12-fechar-pelo-x.png) |
| T13 | Duas pessoas cadastradas se alternando (A, B, A, B) em menos de 5 min | Só duas linhas no log, uma de cada pessoa | PC 2, com adaptador: Gabriel (pessoa real) e Leonardo (foto `Leonardo.jpeg` no segundo monitor) se alternaram 3 vezes cada. Log: **só duas linhas**, `00:18:53,Gabriel` e `00:19:03,Leonardo`. Nas voltas, o terminal mostrou `[CARÊNCIA] Gabriel já registrado há 20 s / 33 s` e `[CARÊNCIA] Leonardo já registrado há 17 s / 29 s` | Passou | [terminal](evidencias/T13-alternancia-terminal.png) |
| T14 | Dois desconhecidos seguidos (menos e mais de 30 s) | Menos de 30 s: `[CARÊNCIA]`, sem linha nova. Mais de 30 s: nova linha NEGADO | Automático, 3 rostos gerados por IA. 1º desconhecido: linha NEGADO. 2º, 10 s depois: `[CARÊNCIA] DESCONHECIDO já registrado há 10 s`, sem linha. 3º, 48 s depois: nova linha NEGADO. Log com **2 linhas** | Passou | [terminal](testes-automaticos-ia/resultados/T14/terminal.txt), [log](testes-automaticos-ia/resultados/T14/acessos.csv), [telas](testes-automaticos-ia/resultados/T14/) |
| T15 | Foto de cadastro com duas pessoas (que concordaram) | `[AUDITORIA] 2 rostos em ... Usando o maior.` | Automático, foto `Dupla.jpg` gerada por IA (rosto maior: homem; menor: mulher). Terminal: `[AUDITORIA] 2 rostos em Dupla.jpg. Usando o maior.` Na câmera, o homem foi `AUTORIZADO: Dupla (92.2%)` e a mulher `NEGADO: DESCONHECIDO (35.6%)`: só o maior rosto foi cadastrado | Passou | [terminal](testes-automaticos-ia/resultados/T15/terminal.txt), [log](testes-automaticos-ia/resultados/T15/acessos.csv), [telas](testes-automaticos-ia/resultados/T15/) |
| T16 | Calibração: `python main.py --calibrar` | Cadastrado abaixo de 0,58 e desconhecidos acima. Anotar as distâncias | Automático, 5 rostos gerados por IA: distâncias de **0.708 a 0.922**, todas fora da tolerância. Gabriel (câmera real, testes anteriores): **0.257 a 0.370** de frente. Exceções: 0.530 quase de perfil, confundido com o Leonardo (P6), e 0.67–0.71 entrando no quadro (P7) | Passou (com ressalvas P6 e P7) | [terminal](testes-automaticos-ia/resultados/T16/terminal.txt) |

**Resumo:** 15 de 16 executados · 1 pendente (T08, pouca luz)

---

## 2. Falhas encontradas e corrigidas (F1–F8)

A coluna "Antes" aponta o commit da correção no GitHub, que mostra o código antes e depois. A coluna "Depois" é o teste que confirma que a correção funciona.

| ID | O que falhava | Correção | Antes (commit) | Depois (teste) |
| :---: | :--- | :--- | :--- | :--- |
| F1 | Imagem da câmera com 1,5 a 2 s de atraso | Captura e reconhecimento em threads separadas | [63be90a](https://github.com/leocosta-dev26/sistema-seguranca-facial/commit/63be90a) | T02 (gravação de tela) |
| F2 | Pessoa autorizada parada gerava log e bipe a cada 3 s | Um evento por chegada | [ddf48f7](https://github.com/leocosta-dev26/sistema-seguranca-facial/commit/ddf48f7) | T07: confirmado (parado diante da câmera, nenhuma linha nova por mais de 5 min) |
| F3 | Rosto levemente de lado era negado ("DESCONHECIDO") | `LIMITE_DESVIO_NARIZ` calibrado de 0,3 para 0,2 | [ddf48f7](https://github.com/leocosta-dev26/sistema-seguranca-facial/commit/ddf48f7) | T05 |
| F4 | Com duas pessoas, todos recebiam o resultado do primeiro (desconhecido aparecia como LIBERADO) | Só o maior rosto é verificado; os outros ficam cinza | [ddf48f7](https://github.com/leocosta-dev26/sistema-seguranca-facial/commit/ddf48f7) | T04: confirmado (o rosto de trás fica cinza, e o Gabriel atrás de um desconhecido não foi liberado) |
| F5 | Instalação falhava em máquina limpa (o pip tentava compilar o `dlib`) | Instalação com `--no-deps` e versões fixas | [87abb42](https://github.com/leocosta-dev26/sistema-seguranca-facial/commit/87abb42) | T01: confirmado nos dois PCs, o `pip` instalou sem compilar nada |
| F6 | Desconhecido não entrava no log (apontado pelo professor na Entrega 2) | Desconhecido registrado como NEGADO | [ddf48f7](https://github.com/leocosta-dev26/sistema-seguranca-facial/commit/ddf48f7) | T03: confirmado (linha `DESCONHECIDO,NEGADO` no log) |
| F7 | O log guardava só a última pessoa; com duas se alternando, enchia de novo (apontado pelo professor) | Horário do último registro de cada pessoa e carência de 5 min (30 s para desconhecido) | [a8b851a](https://github.com/leocosta-dev26/sistema-seguranca-facial/commit/a8b851a) | T13, T07 e T14: confirmados (alternância, carência de 5 min e carência de 30 s do desconhecido) |
| F8 | Foto de cadastro com duas pessoas autorizava a errada sem aviso (apontado pelo professor) | A auditoria avisa e usa o maior rosto | [ee6c6dd](https://github.com/leocosta-dev26/sistema-seguranca-facial/commit/ee6c6dd) | T15: confirmado (aviso exibido; só o maior rosto autoriza) |

---

## 3. Problemas encontrados nestes testes (em aberto)

| ID | Problema | Onde apareceu | Impacto | Sugestão |
| :---: | :--- | :--- | :--- | :--- |
| P1 | Com o Python errado (ex.: 3.15), o programa fecha **sem nenhuma mensagem** | T01 ([print](evidencias/T01-python315-fecha-sem-erro.png)) | Quem instala não sabe o que deu errado | No README, pedir para conferir `python --version` (tem que ser 3.12) antes de instalar |
| P2 | O README só mostra a ativação do venv no PowerShell (`.\venv\Scripts\Activate.ps1`) | T01 | No Prompt de Comando (cmd) o comando é outro | Acrescentar: no cmd, usar `venv\Scripts\activate` |
| P3 | Mesmo com o Python 3.12, o programa fecha sem mensagem. Com `python -X faulthandler main.py`, aparece `Fatal Python error: Illegal instruction` em `dlib\__init__.py`, linha 40 | T01 ([print](evidencias/T01-illegal-instruction.png)) | O sistema não roda em processadores sem AVX (este é um Celeron N4000) | Causa: o `dlib-bin` vem compilado com instruções AVX, que o Celeron N4000 não tem. Registrar como limitação no README ("requer processador com suporte a AVX"). Os testes seguem no PC 2, que tem AVX: lá o `dlib` carregou normalmente |
| P4 | Sem webcam, o sistema mostra `[ERRO] Falha ao conectar a webcam via DirectShow` e encerra com código de saída 0 (como se tivesse dado certo) | T01, PC 2 ([print](evidencias/T01-pc2-3-sem-webcam.png)) | A mensagem é clara; só o código de saída engana scripts | Avisar o Leonardo: encerrar com código diferente de 0 quando a câmera falhar. Para continuar os testes, conectar uma webcam no PC 2 |
| P5 | Com o celular como webcam (DroidCam), abrir a câmera 0 pelo DirectShow derruba o driver (`Windows fatal exception: int divide by zero` em `reconhecedor.py`, linha 20) e o sistema mostra `[ERRO] Falha ao conectar a webcam` | T01, PC 2 ([print](evidencias/T01-pc2-4-droidcam-divide-by-zero.png)) | Câmeras virtuais podem não funcionar. O sistema sempre usa a câmera 0 e o DirectShow, sem opção de escolher outra | **Causa confirmada pelo diagnóstico:** nenhuma câmera abre pelo DirectShow; o DroidCam abre como câmera 0 só pelo Media Foundation (640x480) ([print](evidencias/T01-pc2-5-diagnostico-camera.png)). Sugestão ao Leonardo: se o DirectShow falhar, tentar `cv2.CAP_MSMF`. Enquanto isso, os testes no PC 2 usam um adaptador de teste fora do repositório (ver o registro do T01) |
| P6 | **Grave.** Com o rosto quase de perfil para um dos lados, a checagem de rosto de frente não barra. O sistema verifica o rosto e **confunde o Gabriel com o Leonardo** (distância 0.530, abaixo da tolerância de 0.58), registrando `Leonardo, AUTORIZADO` no log | T05, PC 2 ([print](evidencias/T05-terminal-leonardo-autorizado.png)) | Uma pessoa cadastrada pode ser registrada como outra. É um falso positivo de identidade e deixa o log errado | Avisar o Leonardo com prioridade. Pontos a investigar: a checagem de frente (`LIMITE_DESVIO_NARIZ` e `LIMITE_INCLINACAO`) funciona para um lado e não para o outro, e mesmo a tolerância de 0,55 não teria barrado essa leitura (0.530). Repetir o T05 depois da correção. **Corrigido** no commit [d86ed25](https://github.com/leocosta-dev26/sistema-seguranca-facial/commit/d86ed25) (recusa do rosto achado por um filtro de perfil do detector HOG); **reteste em 10/11 passou** (ver o registro do T05) |
| P7 | Quando a pessoa **cadastrada** entra ou sai do quadro, uma leitura com o rosto parcial ou em movimento foi classificada como estranha: `NEGADO: DESCONHECIDO (39.4%, distância 0.707)`, com linha `DESCONHECIDO,NEGADO` no log. Só o Gabriel estava diante da câmera. **Aconteceu 3 vezes em 6 minutos** (00:26:45, 00:27:53 e 00:28:40), com distâncias de 0.67 a 0.71 | T07, PC 2 ([print](evidencias/T07-parte1-terminal.png)) | Bipe de negação e registro falso de "desconhecido" no log. A regra das 2 leituras iguais seguidas não impediu | Avisar o Leonardo. Pontos a investigar: exigir mais leituras para mudar para NEGADO, ou não verificar enquanto o rosto se mexe ou está cortado na borda do quadro |
| P8 | No cartão de acesso negado, o título **"ACESSO NEGADO" fica quase invisível**: texto vermelho sobre fundo vermelho-escuro. Só o "DESCONHECIDO", em branco, é legível | T03, T04, T14, T15 ([tela](testes-automaticos-ia/resultados/T03/tela_006s.jpg)) | Baixo contraste: quem olha a tela de longe pode não perceber que o acesso foi negado | Avisar o Leonardo: usar branco no título, ou um fundo vermelho mais claro. A cor está em `desenhar_badge_identificacao`, `reconhecedor.py` |

---

## 4. Registro das execuções

### T01 | Instalação em máquina limpa | 05/11/2026

**Passos executados**

1. `git clone` do repositório e `cd sistema-seguranca-facial`.
2. Primeira tentativa: `python main.py` sem venv. O `python` do sistema era o 3.15, e o programa fechou sem mensagem (P1). Os arquivos `src\__pycache__\*.cpython-315.pyc` confirmam a versão usada.
3. Criação do venv com o 3.12: `py -3.12 -m venv venv`.
4. Ativação no cmd: `venv\Scripts\activate` (o comando do README é para PowerShell; P2).
5. `pip install --no-deps -r requirements.txt`: **concluiu sem erro** (pacotes `cp312` instalados: numpy 2.5.3, opencv-python 5.0.0.93, dlib-bin 20.0.1.post1, face-recognition 1.3.0, face_recognition_models 0.3.0, pillow 12.3.0, click 8.5.0, setuptools 69.5.1).
6. `python main.py`: fechou de novo **sem nenhuma mensagem**, nem o título do sistema (P3).

**Diagnóstico**

| Comando | Resultado |
| :--- | :--- |
| `python -X faulthandler main.py` | `Fatal Python error: Illegal instruction`, no carregamento de `venv\Lib\site-packages\dlib\__init__.py`, linha 40 (cadeia: `main.py` linha 2 → `src\utilitarios.py` linha 6 → `face_recognition` → `dlib`) |
| `echo %errorlevel%` | `3` |
| `python -c "import numpy"` | OK |
| `python -c "import cv2"` | OK |
| `python -c "import dlib"` | Fecha sem mensagem (falha) |
| `(Get-CimInstance Win32_Processor).Name` | `Intel(R) Celeron(R) N4000 CPU @ 1.10GHz` |

**Conclusão:** o numpy e o OpenCV funcionam, e a falha está no `dlib-bin`. "Illegal instruction" significa que a biblioteca usa uma instrução que o processador não executa. O Celeron N4000 não tem AVX, e o `dlib-bin` vem compilado com AVX.

**Evidências:** [instalação do pip](evidencias/T01-pip-ok.png) · [Python 3.15 fechando sem erro](evidencias/T01-python315-fecha-sem-erro.png) · [Illegal instruction no dlib](evidencias/T01-illegal-instruction.png) · [processador](evidencias/T01-processador.png)

**Status:** Falhou · **Próximo passo:** repetir o T01 num computador com AVX (PC 2).

### T01 | Repetição no PC 2 (DESKTOP-T39HOPS) | 05/11/2026, 23:29

Executado com o `PREPARAR-NO-OUTRO-PC.bat`, um script de apoio que cria o venv, instala as dependências, registra o ambiente e inicia o sistema.

1. **Criação do venv:** `py -3.12 -m venv venv` falhou com `[ERROR] No runtime installed that matches 3.12`, porque o PC 2 só tem o Python 3.14. O script não parou nesse ponto (falha do script de apoio, não do sistema; já corrigida) e seguiu com o Python 3.14 global ([print](evidencias/T01-pc2-1-sem-python312.png)).
2. **Instalação:** `pip install --no-deps -r requirements.txt` instalou todos os pacotes sem compilar nada. Para o 3.14 existem pacotes prontos (`cp314`) ([print](evidencias/T01-pc2-2-pip-no-python314.png)).
3. **Ambiente registrado:** Windows 11 Home, Python 3.14.7 ([registro](evidencias/T01-ambiente-pc2.txt)).
4. **Execução:** o `dlib` carregou normalmente (o processador tem AVX). A auditoria encontrou rosto nas 2 fotos (`[AUDITORIA] 2 de 2 foto(s) com rosto detectado`) e registrou Gabriel e Leonardo. O `data/logs/acessos.csv` foi criado com o cabeçalho. Ao abrir a câmera: `[ERRO] Falha ao conectar a webcam via DirectShow`, porque não há webcam conectada ([print](evidencias/T01-pc2-3-sem-webcam.png)).

**Conclusão:** com AVX, a instalação e o carregamento funcionam, e isso confirma o P3 como causa no PC 1. O sistema também rodou com o Python 3.14, mas o grupo validou o 3.12, que é o que o README exige. Falta só a câmera.

**Status:** Falhou (sem webcam) · **Próximo passo:** conectar uma webcam no PC 2 e repetir.

### T01 | 2ª repetição no PC 2, com o DroidCam | 05/11/2026, 23:42

1. Python 3.12 instalado. O `.bat` corrigido criou o venv com o **Python 3.12.10**, e a instalação passou sem erro.
2. Cadastros carregados normalmente (2 de 2 fotos com rosto).
3. Ao abrir a câmera: `Windows fatal exception: int divide by zero` dentro de `cv2.VideoCapture(0, cv2.CAP_DSHOW)` (`reconhecedor.py`, linha 20), seguido de `[ERRO] Falha ao conectar a webcam via DirectShow` ([print](evidencias/T01-pc2-4-droidcam-divide-by-zero.png)).
4. O DroidCam Client estava conectado e mostrando a imagem do celular, então o celular não era o problema. O erro acontece quando o OpenCV abre a câmera virtual pelo DirectShow.

**Status:** Falhou (P5)

### Diagnóstico de câmera no PC 2 | 05/11/2026, 23:46

Script de apoio (`diagnostico_camera.py`, fora do repositório) que abre as câmeras 0 a 4 por dois métodos do Windows, cada teste num processo separado ([print](evidencias/T01-pc2-5-diagnostico-camera.png), [registro](evidencias/T01-pc2-diagnostico-camera.txt)):

| Câmera | DirectShow (`CAP_DSHOW`, usado pelo sistema) | Media Foundation (`CAP_MSMF`) |
| :---: | :--- | :--- |
| 0 | não abriu | **OK, imagem 640x480** |
| 1 a 4 | não abriu | não abriu |

**Conclusão:** o DroidCam funciona como webcam pelo Media Foundation, mas não pelo DirectShow. O VisionGuard só usa o DirectShow (`reconhecedor.py`, linha 20), por isso não consegue abrir essa câmera (P5).

**Como os testes continuam no PC 2:** o código do projeto não foi alterado (a regra do grupo é que `src/` é do Leonardo). Os testes seguintes rodam pelo `RODAR-VISIONGUARD-TESTE.bat`. Ele usa um adaptador fora do repositório (`rodar_com_msmf.py`) que troca o DirectShow pelo Media Foundation só durante a execução e roda o `main.py` sem nenhuma alteração. **Todo teste executado com o adaptador traz essa observação.**

### T01 | 3ª repetição no PC 2, com o adaptador | 05/11/2026, 23:48

1. O adaptador abriu a câmera pelo Media Foundation, e o sistema chegou a `[VISIONGUARD ATIVO] Monitoramento em tempo real iniciado`.
2. A janela "VisionGuard - Controle de Acesso Facial" abriu, com o cabeçalho, a base (2) e o relógio atualizando. Mas **a imagem da câmera ficou toda verde** por cerca de 1 minuto ([print](evidencias/T01-pc2-6-msmf-imagem-verde.png)).
3. Pressionar `q` encerrou o programa normalmente (código de saída 0). Esse resultado entrou no T12.

**Causa provável:** a conversão de cor por hardware do Media Foundation com o DroidCam. **Ajuste:** o adaptador passou a desligar essa conversão (`OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS=0`). O diagnóstico de câmera também passou a conferir se o quadro tem imagem de verdade ou só uma cor.

**Status:** Falhou (imagem verde) · **Próximo passo:** repetir com o adaptador ajustado.

### T01 | 4ª repetição no PC 2 | 05/11/2026, 23:50

Com a conversão por hardware desligada, **a imagem continuou verde**. Investigação no DroidCam Client:
- A fonte "Dispositivo" (o celular) estava transmitindo imagem normalmente.
- Em **Configurações → Vídeo**, a saída do DroidCam é **1280x720 a 30 fps**.
- O diagnóstico anterior mostrou que o OpenCV abre a câmera em **640x480**.

**Causa provável:** a câmera virtual só entrega quadros na resolução configurada (1280x720). Quando o OpenCV pede 640x480, recebe quadros vazios, que aparecem verdes. **Ajuste:** o adaptador passou a pedir 1280x720 ao abrir a câmera e mostra no terminal a resolução recebida (`[TESTE] Resolucao pedida...`). Nenhuma configuração do DroidCam foi alterada.

**Observação para os testes seguintes:** o sistema reduz cada quadro para 1/4 antes de detectar rostos. Em 1280x720 isso dá 320x180; numa webcam comum de 640x480, dá 160x120. Os resultados de distância (T09) no PC 2 podem ser melhores que numa webcam comum.

**Status:** Falhou (imagem verde) · **Próximo passo:** repetir com a resolução 1280x720.

### T01 | 5ª repetição no PC 2: aprovado | 05/11/2026, 23:53

1. O adaptador pediu 1280x720 e recebeu `1280x720`.
2. A janela "VisionGuard - Controle de Acesso Facial" abriu **com a imagem da câmera**.
3. O sistema reconheceu o Gabriel: `[EVENTO] AUTORIZADO: Gabriel (87.2%, distância 0.313)`.
4. O log registrou uma linha: `05/11/2026,23:53:54,Gabriel,AUTORIZADO`.

Evidências: [terminal](evidencias/T01-pc2-7-terminal-autorizado.png), com a janela da câmera ocultada porque mostra rosto. Print da janela da câmera: [janela com o Gabriel](evidencias-privadas-com-rosto/T01-pc2-8-janela-camera-COM-ROSTO.png).

**Status:** **Passou** no PC 2, com o adaptador de teste. Seguindo o README à risca, sem adaptador, o T01 falhou nos dois PCs (P3 e P5).

### T02 | Pessoa cadastrada de frente | 05/11/2026, 23:56 | PC 2, com adaptador

1. O sistema foi reiniciado para zerar a carência (ela fica na memória do programa).
2. Gabriel de frente para a câmera (celular pelo DroidCam, 1280x720).
3. **Tela:** moldura verde, "ACESSO LIBERADO" e "Gabriel (89%)", com a malha de pontos sobre o rosto.
4. **Som:** dois bipes agudos, confirmados pelo testador.
5. **Terminal:** `[EVENTO] AUTORIZADO: Gabriel (89.1%, distância 0.257)` ([print](evidencias/T02-terminal-autorizado.png), [tela](evidencias-privadas-com-rosto/T02-acesso-liberado-COM-ROSTO.png)).
6. **Log:** uma linha nova, `05/11/2026,23:56:36,Gabriel,AUTORIZADO`.

**Percentuais medidos:** 87,2% (23:53) e 89,1% (23:56). Os dois ficam **acima** da faixa "76% a 85%" que o README afirma hoje (ver a seção 5 do guia: correções do README).

**Status:** Passou

### T05 | Rosto de lado | 05/11/2026, 23:58–23:59 | PC 2, com adaptador

Gabriel diante da câmera, virando a cabeça devagar para um lado e depois para o outro. Prints a cada 2 s.

| Momento | Tela | Terminal / log |
| :--- | :--- | :--- |
| 1º lado, levemente virado | Moldura cinza, "OLHE PARA A CAMERA" | Nada (como esperado) |
| 1º lado, bem de lado | Moldura some | Nada (como esperado) |
| De frente (23:59:06) | Moldura verde, Gabriel | `AUTORIZADO: Gabriel (85.2%, distância 0.370)`; linha no log |
| 2º lado, quase de perfil | **Moldura verde "ACESSO LIBERADO"**, Gabriel | `[CARÊNCIA] Gabriel já registrado há 9 s` |
| 2º lado, quase de perfil (23:59:21) | **Moldura verde "ACESSO LIBERADO", nome Leonardo** | **`AUTORIZADO: Leonardo (79.7%, distância 0.530)`; linha `Leonardo, AUTORIZADO` no log** |
| Voltando | Moldura verde, Gabriel | `[CARÊNCIA] Gabriel já registrado há 16 s` e `há 24 s` |

**Log no fim do teste:**
```
05/11/2026,23:59:06,Gabriel,AUTORIZADO
05/11/2026,23:59:21,Leonardo,AUTORIZADO
```

**Conclusão:** para um lado, o comportamento é o esperado. Para o outro, a checagem de frente deixa passar um rosto quase de perfil, e o reconhecimento erra a pessoa (P6). A carência funcionou: as leituras repetidas do Gabriel não geraram linhas novas. Isso é um indício para o T07.

**Evidências:** [terminal](evidencias/T05-terminal-leonardo-autorizado.png). Prints da janela: [olhe para a câmera](evidencias-privadas-com-rosto/T05-1-olhe-para-a-camera-COM-ROSTO.png), [de lado, sem moldura](evidencias-privadas-com-rosto/T05-2-de-lado-sem-moldura-COM-ROSTO.png), [perfil liberado](evidencias-privadas-com-rosto/T05-3-perfil-liberado-gabriel-COM-ROSTO.png) e [liberado como Leonardo](evidencias-privadas-com-rosto/T05-4-perfil-liberado-como-leonardo-COM-ROSTO.png).

**Status:** Falhou (P6)

### T05 | Reteste com duas pessoas cadastradas | 10/11/2026, cerca de 01:00–01:03 | Notebook do Leonardo

**Executado pelo Leonardo**, depois da correção do P6 (commit [d86ed25](https://github.com/leocosta-dev26/sistema-seguranca-facial/commit/d86ed25): o sistema recusa o rosto que o detector HOG encontrou com um filtro de perfil). Webcam integrada, aberta pelo DirectShow, com `python main.py --calibrar`.

**Por que duas pessoas:** o P6 foi um erro de identidade (o Gabriel liberado como Leonardo). Com uma pessoa só na base, o teste não teria com quem confundir. A base tinha **Arthur e Leonardo** (`2 face(s) autorizada(s)`, "BASE: 2" na tela). O Arthur autorizou o uso da foto dele no teste.

**Foto de cadastro:** a do Leonardo foi trocada antes deste teste por uma tirada pela própria webcam do notebook.

| Momento | Tela | Terminal |
| :--- | :--- | :--- |
| De frente | "ACESSO LIBERADO", "Leonardo (85%)", malha verde | `[EVENTO] AUTORIZADO: Leonardo (83.6%, distância 0.416)` |
| 1º lado, quase de perfil | Moldura cinza, "OLHE PARA A CAMERA" | Blocos de `[ROSTO] filtro 2 (perfil ou não encontrado)` e `filtro None`; nenhuma `[CALIBRAÇÃO]` |
| 2º lado, quase de perfil | Moldura cinza, "OLHE PARA A CAMERA" | Blocos de `[ROSTO] filtro 1 (perfil ou não encontrado)` e `filtro None`; nenhuma `[CALIBRAÇÃO]` |
| Levemente virado ou inclinado (filtro 0) | Moldura cinza | `nariz para o lado` de 0,21 a 0,24 (limite 0,2) ou `inclinação` de 0,32 a 0,38 (limite 0,3): recusado antes do reconhecimento |
| Voltando de frente | Verde, Leonardo | `[CARÊNCIA] Leonardo já registrado há 71 s / 86 s / 94 s / 119 s`, sem linha nova |

**Resultado:**
- **Nenhuma troca de identidade:** um único evento (`AUTORIZADO: Leonardo`); todas as leituras `[CALIBRAÇÃO]` apontaram o Leonardo; o nome do Arthur não apareceu nenhuma vez.
- **Os dois lados barrados:** filtro de perfil 1 para um lado e 2 para o outro, além dos rostos não encontrados (`None`) e dos recusados pelos limites de inclinação e de nariz.
- **Distâncias do Leonardo de frente:** de **0.308 a 0.528**, a maioria entre 0,33 e 0,43, todas abaixo da tolerância de 0,58.

**Tentativa anterior, no mesmo dia, sem prints e com a foto de cadastro antiga:** o mesmo resultado quanto à identidade (um evento só, sempre Leonardo, perfil barrado), mas as distâncias de frente foram de 0.392 a 0.603. A leitura de 0.603 ficou fora da tolerância e **não** virou "ACESSO NEGADO", porque o sistema só nega depois de 2 s seguidos de desconhecido. A troca da foto de cadastro por uma tirada pela webcam baixou as distâncias.

**Evidências:** [lado 1](evidencias-privadas-com-rosto/T05-reteste-1-lado-1-olhe-para-a-camera-COM-ROSTO.png), [lado 2](evidencias-privadas-com-rosto/T05-reteste-2-lado-2-olhe-para-a-camera-COM-ROSTO.png), [de frente, liberado](evidencias-privadas-com-rosto/T05-reteste-3-de-frente-liberado-COM-ROSTO.png) (rosto do Leonardo, publicado com a autorização dele) e a saída do terminal resumida acima.

**Status:** Passou (P6 corrigido)

### T10 | Foto de cadastro sem rosto | 06/11/2026, 00:03 | PC 2, com adaptador

1. Uma imagem de paisagem sem nenhum rosto (`paisagem.jpg`, 800x600, desenhada para o teste) foi colocada em `data/cadastros/`, junto com `Gabriel.jpeg` e `Leonardo.jpeg`.
2. O sistema foi iniciado pelo `RODAR-VISIONGUARD-TESTE.bat`.
3. Terminal:
   ```
   [AUDITORIA] 2 de 3 foto(s) com rosto detectado.
   [CADASTRO] Assinatura biométrica registrada: Gabriel
   [CADASTRO] Assinatura biométrica registrada: Leonardo
   [AUDITORIA] O detector CNN não achou rosto em paisagem.jpg...
   [AVISO] Nenhum rosto identificado na foto: paisagem.jpg
   [SUCESSO] 2 face(s) autorizada(s) carregada(s).
   ```
4. A câmera abriu normalmente, a tela mostrou "BASE: 2", e o Gabriel foi reconhecido em seguida (`AUTORIZADO: Gabriel (85.3%, distância 0.369)`).

Evidência: [print](evidencias/T10-foto-sem-rosto.png). Depois do teste, a `paisagem.jpg` deve ser retirada de `data/cadastros/`.

**Status:** Passou

### T11 | Base vazia | 06/11/2026, 00:05 | PC 2

1. As fotos `Gabriel.jpeg`, `Leonardo.jpeg` e `paisagem.jpg` foram movidas de `data/cadastros/` para uma pasta fora do projeto (`fotos guardadas`).
2. O sistema foi iniciado pelo `RODAR-VISIONGUARD-TESTE.bat`.
3. Terminal:
   ```
   [INICIANDO] Carregando cadastros da base de dados...
   [ALERTA] Nenhum rosto cadastrado em data/cadastros/.
   Insira uma foto .jpg, .jpeg ou .png antes de iniciar.
   Codigo de saida: 1
   ```
4. O programa encerrou sozinho, sem abrir a câmera. O código de saída 1 indica erro, como deveria. Compare com o P4: quando a câmera falha, o código é 0.
5. Depois do teste, `Gabriel.jpeg` e `Leonardo.jpeg` voltaram para `data/cadastros/`. A `paisagem.jpg` ficou fora.

Evidência: [print](evidencias/T11-base-vazia.png).

**Status:** Passou

### T12 | Encerrar | 05/11/2026, 23:49 e 06/11/2026, 00:08 | PC 2, com adaptador

| Como | Resultado | Evidência |
| :--- | :--- | :--- |
| Tecla `q` na janela da câmera | O programa encerrou, a janela fechou e o código de saída foi 0 | [print](evidencias/T12-fechar-com-q.png) |
| X da janela da câmera | O programa encerrou logo depois do `AUTORIZADO: Gabriel (88.2%, distância 0.284)`, com código de saída 0. Não travou, e a câmera pôde ser aberta de novo em seguida | [print](evidencias/T12-fechar-pelo-x.png) |

**Status:** Passou

### T06 | Foto do cadastrado | 06/11/2026, 00:14 | PC 2, com adaptador

1. A foto de cadastro `Gabriel.jpeg` foi aberta em tela cheia no segundo monitor (SAMSUNG).
2. A câmera (o celular, pelo DroidCam) foi apontada para o monitor, a cerca de 50 cm.
3. Com a foto girada no quadro, o sistema não desenhou moldura. Com a foto em pé, de frente:
   - **Tela:** moldura verde, "ACESSO LIBERADO", "Gabriel (93%)"
   - **Terminal:** `[EVENTO] AUTORIZADO: Gabriel (93.2%, distância 0.139)`
   - **Log:** `06/11/2026,00:14:48,Gabriel,AUTORIZADO`

**Conclusão:** o resultado foi o esperado, e **confirma a limitação**: o sistema não tem prova de vida, e uma foto da pessoa cadastrada libera o acesso. A foto deu confiança **maior** (93,2%, distância 0.139) que o rosto real (85% a 89%, distância 0.26 a 0.37), porque é a mesma imagem usada no cadastro. Isso entra na seção "Limitações conhecidas" do README.

Evidência: [terminal](evidencias/T06-terminal-foto-liberada.png). Print da tela: [foto no monitor liberada](evidencias-privadas-com-rosto/T06-foto-no-monitor-liberada-COM-ROSTO.png).

**Status:** Passou (resultado esperado: confirma a falta de prova de vida)

### T13 | Duas pessoas se alternando | 06/11/2026, 00:18–00:19 | PC 2, com adaptador

1. O sistema foi reiniciado para zerar a carência.
2. A câmera alternou entre o Gabriel (pessoa real) e o Leonardo (foto de cadastro `Leonardo.jpeg`, aberta em tela cheia no segundo monitor), saindo do quadro entre as trocas.
3. Terminal ([print](evidencias/T13-alternancia-terminal.png)):
   ```
   [EVENTO] AUTORIZADO: Gabriel (87.9%, distância 0.292)
   [EVENTO] AUTORIZADO: Leonardo (91.8%, distância 0.179)
   [CARÊNCIA] Gabriel já registrado há 20 s; sem novo registro no log.
   [CARÊNCIA] Leonardo já registrado há 17 s; sem novo registro no log.
   [CARÊNCIA] Gabriel já registrado há 33 s; sem novo registro no log.
   [CARÊNCIA] Leonardo já registrado há 29 s; sem novo registro no log.
   ```
4. Log, só duas linhas novas:
   ```
   06/11/2026,00:18:53,Gabriel,AUTORIZADO
   06/11/2026,00:19:03,Leonardo,AUTORIZADO
   ```

**Conclusão:** cada pessoa tem a própria carência. A alternância não encheu o log, e isso **confirma a correção F7**, apontada pelo professor. Observação: o Leonardo foi representado pela foto de cadastro, que dá distância menor que um rosto real (ver o T06). Isso não muda o que este teste verifica, que é a regra do log.

**Status:** Passou

### T09 | Distância | 06/11/2026, 00:21–00:22 | PC 2, com adaptador

1. O Gabriel se afastou aos poucos da câmera (o celular pelo DroidCam, em 1280x720). Capturas a cada 6 s.
2. Resultado, com distâncias estimadas pelo testador:

| Distância | Detecta o rosto? | Reconhece? |
| :--- | :--- | :--- |
| Menos de 1 m | Sim | Sim: moldura verde, "ACESSO LIBERADO", Gabriel |
| A partir de cerca de 1 m | Não, nas capturas mais distantes (nenhuma moldura) | Não |

**Conclusão:** neste equipamento, o alcance prático é de **cerca de 1 metro**. Isso é **menos** do que o README afirma hoje ("distâncias maiores que 2 metros", na seção "Limitações do Modelo"), e deve ser corrigido com o valor medido. A causa provável é a redução do quadro para 1/4 antes da detecção (README: "redução de escala em 0.25x"): longe, o rosto fica pequeno demais para o detector HOG. Com uma webcam de 640x480, o alcance tende a ser **ainda menor**, porque o quadro reduzido tem a metade da largura.

**Limite desta medição:** as distâncias foram estimadas, não medidas com trena. Para a apresentação, vale repetir marcando 0,5 m, 1 m, 2 m e 3 m no chão.

Evidência: 3 prints da janela da câmera (perto, com reconhecimento, e longe, sem moldura), com rosto, guardados fora do repositório (`evidencias-privadas/`).

**Status:** Executado (medição)

### T07 | Sair e voltar (carência) | 06/11/2026, 00:25–00:31 (relógio do PC 2) | PC 2, com adaptador

1. O programa foi reiniciado, o que zera a carência. Primeiro registro: `00:25:47, Gabriel, AUTORIZADO`.
2. O Gabriel ficou parado de frente e, várias vezes, saiu do quadro por alguns segundos e voltou.
3. Terminal ([print](evidencias/T07-terminal-completo.png)):
   ```
   [EVENTO] AUTORIZADO: Gabriel (88.2%, distância 0.283)
   [CARÊNCIA] Gabriel já registrado há 47 s; sem novo registro no log.
   [EVENTO] NEGADO: DESCONHECIDO (39.4%, distância 0.707)
   [CARÊNCIA] Gabriel já registrado há 63 s ... 68 s ...
   [EVENTO] NEGADO: DESCONHECIDO (41.6%, distância 0.681)
   [CARÊNCIA] Gabriel já registrado há 170 s ...
   [EVENTO] NEGADO: DESCONHECIDO (42.1%, distância 0.674)
   [CARÊNCIA] Gabriel já registrado há 176 s, 206 s, 232 s, 238 s, 283 s, 295 s ...
   [EVENTO] AUTORIZADO: Gabriel (88.8%, distância 0.267)
   ```
4. Log:
   ```
   06/11/2026,00:25:47,Gabriel,AUTORIZADO
   06/11/2026,00:26:45,DESCONHECIDO,NEGADO
   06/11/2026,00:27:53,DESCONHECIDO,NEGADO
   06/11/2026,00:28:40,DESCONHECIDO,NEGADO
   06/11/2026,00:31:18,Gabriel,AUTORIZADO
   ```

| Parte | Esperado | Obtido |
| :--- | :--- | :--- |
| Parado diante da câmera | Nenhuma linha nova | Nenhuma linha nova do Gabriel por mais de 5 min ✅ |
| Volta rápida (menos de 5 min) | Som e `[CARÊNCIA]`, sem linha nova | `[CARÊNCIA]` de 47 s a 295 s, sem linha nova ✅ |
| Volta depois de 5 min | Linha nova | Linha nova às 00:31:18, 5 min e 31 s após o registro ✅ |

**Conclusão:** a carência de 5 minutos funciona como descrito, e isso confirma as correções F2 e F7. **Ressalva:** na mesma execução, 3 leituras do Gabriel entrando ou saindo do quadro foram registradas como `DESCONHECIDO, NEGADO` (P7).

**Observação:** o relógio do PC 2 está cerca de 1,5 min adiantado em relação ao horário oficial. Os horários deste registro são os do PC 2, os mesmos do log.

**Status:** Passou (com a ressalva do P7)

---

## Testes automáticos com rostos gerados por IA (T03, T04, T14, T15, T16)

**Data:** 06/11/2026, 19:03–19:08 · **Ambiente:** PC 2, Python 3.12.10, `main.py` original

**Como funciona** (`testes-automaticos-ia/testes_ia.py`):
1. Para cada teste, o script roda o `main.py` do projeto **sem nenhuma alteração**, num processo separado. Assim a carência começa zerada em cada teste.
2. A webcam é substituída por uma "câmera de teste" que mostra um roteiro de imagens, por exemplo: 3 s sem ninguém, 8 s com um rosto, 3 s sem ninguém.
3. Os rostos são de **pessoas que não existem**, gerados por IA (`testes-automaticos-ia/imagens/`). Nos testes com pessoa cadastrada (T04), foi usada a foto de cadastro do Gabriel.
4. A pasta de cadastros e o log são próprios de cada teste (`resultados/<teste>/`), para não misturar com o log real do projeto.
5. Ficam guardados o terminal completo (`terminal.txt`), o log (`acessos.csv`) e um print da tela do sistema a cada 2 s (`tela_XXs.jpg`).
6. No fim do roteiro, o script simula a tecla `q`, e o sistema encerra sozinho (código de saída 0 nos 5 testes).

**Limite:** nesta forma de execução não há ninguém ouvindo, então o **som não foi verificado**. Os bipes foram confirmados pelo testador no T02.

### T03 | Pessoa desconhecida

| Cena | Tela | Terminal / log |
| :--- | :--- | :--- |
| 0–3 s: ninguém | Sem moldura | Nada |
| 3–11 s: `pessoa_ia_1` de frente | Moldura e cartão vermelhos, "DESCONHECIDO" ([tela](testes-automaticos-ia/resultados/T03/tela_006s.jpg)) | `[EVENTO] NEGADO: DESCONHECIDO (34.9%, distância 0.761)` |

Log: `06/11/2026,19:04:09,DESCONHECIDO,NEGADO`. **Confirma a correção F6:** o desconhecido entra no log. **Status:** Passou

### T04 | Duas pessoas no quadro

| Cena | Tela | Terminal / log |
| :--- | :--- | :--- |
| Gabriel perto + `pessoa_ia_1` longe | Gabriel: moldura verde, "ACESSO LIBERADO, Gabriel (94%)". Rosto de trás: cinza, "AGUARDE SUA VEZ" | `AUTORIZADO: Gabriel (94.2%, distância 0.109)` |
| `pessoa_ia_1` perto + Gabriel longe | Rosto da frente: cartão vermelho, "DESCONHECIDO". Gabriel, atrás: cinza, "AGUARDE SUA VEZ" | `NEGADO: DESCONHECIDO (35.0%, distância 0.760)` |

Log: `19:04:41,Gabriel,AUTORIZADO` e `19:04:53,DESCONHECIDO,NEGADO`. **Confirma a correção F4:** um desconhecido na frente não é liberado por causa de um cadastrado atrás, e o de trás nunca aparece como liberado. Telas: [Gabriel perto](evidencias-privadas-com-rosto/T04-gabriel-perto-ia-longe-COM-ROSTO.jpg) e [rosto IA perto](evidencias-privadas-com-rosto/T04-ia-perto-gabriel-longe-COM-ROSTO.jpg). **Status:** Passou

### T14 | Dois desconhecidos seguidos

| Cena | Terminal | Linha no log? |
| :--- | :--- | :--- |
| 3 s: `pessoa_ia_1` | `NEGADO: DESCONHECIDO (34.9%, distância 0.761)` | Sim, 19:05:25 |
| 13 s: `pessoa_ia_2` (10 s depois) | `[CARÊNCIA] DESCONHECIDO já registrado há 10 s; sem novo registro no log.` | Não |
| 51 s: `pessoa_ia_3` (48 s depois) | `NEGADO: DESCONHECIDO (36.3%, distância 0.744)` | Sim, 19:06:13 |

**Confirma a carência de 30 s do desconhecido (F7).** Observação: como todos os estranhos têm o mesmo nome, "DESCONHECIDO", **um segundo estranho que chega em menos de 30 s não é registrado**. É o comportamento planejado, mas é uma limitação do log. **Status:** Passou

### T15 | Foto de cadastro com duas pessoas

Cadastros do teste: `Gabriel.jpeg`, `Leonardo.jpeg` e `Dupla.jpg` (gerada por IA: o homem à esquerda com o rosto maior, a mulher à direita com o rosto menor).

```
[AUDITORIA] 3 de 3 foto(s) com rosto detectado.
[AUDITORIA] 2 rostos em Dupla.jpg. Usando o maior.
[CADASTRO] Assinatura biométrica registrada: Dupla
[SUCESSO] 3 face(s) autorizada(s) carregada(s).
```

| Cena | Tela | Terminal |
| :--- | :--- | :--- |
| Homem da Dupla (rosto maior) | "ACESSO LIBERADO, Dupla (92%)" ([tela](testes-automaticos-ia/resultados/T15/tela_006s.jpg)) | `AUTORIZADO: Dupla (92.2%, distância 0.169)` |
| Mulher da Dupla (rosto menor) | Cartão vermelho, "DESCONHECIDO" ([tela](testes-automaticos-ia/resultados/T15/tela_016s.jpg)) | `NEGADO: DESCONHECIDO (35.6%, distância 0.753)` |

**Confirma a correção F8:** o sistema avisa e cadastra **só o maior rosto**. A outra pessoa da foto não ganha acesso. **Status:** Passou

### T16 | Calibração da tolerância (0,58)

Executado com `--calibrar`. Cada desconhecido ficou cerca de 6 s diante da "câmera", com cerca de 14 leituras cada:

| Rosto (gerado por IA) | Distância medida | Mais parecido com | Resultado |
| :--- | :---: | :--- | :--- |
| `pessoa_ia_1` | 0.761 | Leonardo | Fora da tolerância (negado) |
| `pessoa_ia_2` | 0.708 | Gabriel | Fora da tolerância (negado) |
| `pessoa_ia_3` | 0.744 | Gabriel | Fora da tolerância (negado) |
| Homem da Dupla | 0.825 | Leonardo | Fora da tolerância (negado) |
| Mulher da Dupla | 0.922 | Leonardo | Fora da tolerância (negado) |

**Comparando com as leituras reais do Gabriel** (câmera do PC 2, testes T02, T05, T07, T10, T12 e T13):

| Situação | Distâncias |
| :--- | :--- |
| Gabriel de frente | 0.257 a 0.370 |
| Gabriel quase de perfil, confundido com o Leonardo (P6) | **0.530** |
| Gabriel entrando ou saindo do quadro, lido como desconhecido (P7) | 0.674 a 0.707 |
| Desconhecidos (este teste) | 0.708 a 0.922 |
| **Tolerância atual** | **0,58** |

**Conclusão para o professor (por que 0,58):** nesta amostra, os rostos reais de frente ficam bem abaixo de 0,58 e todos os desconhecidos ficam bem acima. Há uma margem de cerca de 0,2 dos dois lados. **Mas** a leitura de perfil que confundiu o Gabriel com o Leonardo (0.530) **também passaria com 0,55**. Uma tolerância **perto de 0,45** ainda aceitaria todas as leituras de frente medidas (até 0.370) e teria barrado a confusão do P6. A amostra é pequena (1 cadastrado real e 5 rostos gerados por IA), então a sugestão é repetir com mais pessoas antes de mudar o valor. O problema principal do P6 continua sendo a checagem de frente.

**Status:** Passou (com as ressalvas do P6 e do P7)

