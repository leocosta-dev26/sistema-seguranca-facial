# VisionGuard | Resultados dos Testes

**Responsável:** Gabriel Angioleto (Qualidade e documentação)
**Execução:** 05/11/2026 a 06/11/2026
**Repositório testado:** `github.com/leocosta-dev26/sistema-seguranca-facial`

Esta pasta reúne tudo o que foi produzido na etapa de testes: o documento completo, as evidências, os resultados dos testes automáticos e os scripts usados. **O documento principal é o [`testes.md`](testes.md).** Este arquivo é o índice.

---

## Resultado geral

**15 de 16 testes executados.** Falta só o T08 (pouca luz).

| Teste | Cenário | Resultado |
| :---: | :--- | :--- |
| T01 | Instalação seguindo o README | Falhou no PC 1 (processador sem AVX). Passou no PC 2 com adaptador de câmera |
| T02 | Cadastrado de frente | Passou (87% a 89%, dois bipes) |
| T03 | Pessoa desconhecida | Passou |
| T04 | Duas pessoas no quadro | Passou |
| T05 | Rosto de lado | **Falhou:** quase de perfil, o Gabriel foi reconhecido como Leonardo (P6) |
| T06 | Foto do cadastrado | Passou: a foto libera o acesso e confirma a falta de prova de vida |
| T07 | Sair e voltar (carência) | Passou, com a ressalva do P7 |
| T08 | Pouca luz | Pendente |
| T09 | Distância | Medido: reconhece até cerca de 1 m |
| T10 | Foto de cadastro sem rosto | Passou |
| T11 | Base vazia | Passou |
| T12 | Encerrar com `q` e pelo X | Passou |
| T13 | Dois cadastrados se alternando | Passou |
| T14 | Desconhecidos seguidos | Passou |
| T15 | Foto de cadastro com duas pessoas | Passou |
| T16 | Calibração da tolerância | Passou, com ressalvas (P6 e P7) |

### Correções confirmadas (F1–F8)

| Falha corrigida | Confirmada por |
| :--- | :--- |
| F2 Log e bipe repetidos com a pessoa parada | T07 |
| F4 Duas pessoas com o mesmo resultado | T04 |
| F5 Instalação falhava (compilação do `dlib`) | T01 |
| F6 Desconhecido fora do log | T03 |
| F7 Log só da última pessoa | T07, T13 e T14 |
| F8 Foto de cadastro com duas pessoas | T15 |

F1 (atraso da câmera) e F3 (rosto de lado negado) estão descritas no `testes.md`. O T05 mostrou que a checagem de rosto de frente ainda falha para um dos lados (P6).

### Problemas encontrados nos testes (P1–P8)

| ID | Gravidade | Resumo |
| :---: | :--- | :--- |
| P1 | Média | Com o Python errado, o programa fecha sem nenhuma mensagem |
| P2 | Baixa | O README só mostra a ativação do venv no PowerShell, e não no cmd |
| P3 | Alta | Não roda em processador sem AVX (`Illegal instruction` no `dlib`) |
| P4 | Baixa | Sem webcam, o programa encerra com código 0, como se tivesse dado certo |
| P5 | Alta | Só abre a câmera pelo DirectShow; câmeras como o DroidCam só funcionam pelo Media Foundation |
| P6 | **Grave** | Quase de perfil, a checagem de frente não barra, e o Gabriel foi registrado como Leonardo |
| P7 | Média | Entrando ou saindo do quadro, o cadastrado foi registrado como DESCONHECIDO (3 vezes em 6 min) |
| P8 | Baixa | O título "ACESSO NEGADO" fica quase invisível (vermelho sobre vermelho) |

Os detalhes, as evidências e as sugestões de correção de cada um estão no `testes.md`, seção 3.

---

## Como a pasta está organizada

```
resultados testes/
├── LEIA-ME.md                        este índice
├── testes.md                         documento completo: casos de teste, falhas e registro de cada execução
├── evidencias/                       prints e registros citados no testes.md (sem rostos)
├── testes-automaticos-ia/
│   ├── testes_ia.py                  roteiro automático dos testes T03, T04, T14, T15 e T16
│   ├── imagens/                      rostos gerados por IA (pessoas que não existem)
│   └── resultados/T03 … T16/         terminal.txt, acessos.csv e prints da tela de cada teste
├── scripts-de-apoio/                 scripts de preparação do ambiente (não publicados; ficam com o Gabriel)
└── evidencias-privadas-com-rosto/    prints com o rosto do Gabriel (publicados com a autorização dele)
```

### Os três jeitos de executar

1. **Manual, PC 1 (notebook):** só o T01, seguindo o README à risca.
2. **Manual, PC 2, com adaptador de câmera:** o testador diante da câmera (celular como webcam, pelo DroidCam). O `scripts-de-apoio/rodar_com_msmf.py` só troca o DirectShow pelo Media Foundation (P5).
3. **Automático, PC 2, com rostos gerados por IA:** o `testes-automaticos-ia/testes_ia.py` roda o `main.py` original trocando a câmera por imagens de pessoas que não existem. Assim não foi preciso usar o rosto de ninguém sem autorização.

**Em nenhum dos três o código do projeto foi alterado.**

---

## Scripts de apoio

Todos ficam **fora do repositório** e devem ser colocados na mesma pasta que contém `sistema-seguranca-facial/`.

| Arquivo | Para que serve |
| :--- | :--- |
| `PREPARAR-NO-OUTRO-PC.bat` | Cria o venv com o Python 3.12, instala as dependências, registra o ambiente e inicia o sistema |
| `DIAGNOSTICO-CAMERA.bat` + `diagnostico_camera.py` | Testa as câmeras 0 a 4 pelo DirectShow e pelo Media Foundation |
| `RODAR-VISIONGUARD-TESTE.bat` + `rodar_com_msmf.py` | Roda o sistema abrindo a câmera pelo Media Foundation, em 1280x720 |
| `RODAR-TESTES-IA.bat` | Roda os 5 testes automáticos (precisa da pasta `testes-automaticos-ia/` renomeada para `testes-ia/`) |

---

## Privacidade

- A pasta `evidencias-privadas-com-rosto/` foi publicada com autorização do Gabriel, que aparece nos prints.
- Nos prints de `evidencias/`, a janela da câmera foi tampada quando mostrava um rosto real.
- Os rostos de `testes-automaticos-ia/` foram gerados por IA e não são de pessoas reais.

## Para levar ao repositório

Vão para a pasta `docs/` do projeto: `testes.md`, `LEIA-ME.md`, `evidencias/`, `testes-automaticos-ia/` e `evidencias-privadas-com-rosto/`. A pasta `evidencias-privadas-com-rosto/` foi publicada com autorização do Gabriel, que aparece nos prints.
