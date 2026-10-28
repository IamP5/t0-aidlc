# Mapa de verificação do Notas

Este diretório é a fonte mantida para verificar o comportamento visível do Notas. Leia o índice antes de dirigir o app e use o arquivo da feature como receita.

## Pré-condições de base

- Suba o Notas em `http://127.0.0.1:4173` com um diretório de dados descartável.
- Defina `NOTES_DATA_DIR=/tmp/notes-verify-$RUN_ID` para execuções paralelas não dividirem estado.
- Semeie as notas `Plano trimestral` e `Lista de compras`.
- Ponha `control-notes` e a CLI `notes` no `PATH`.
- Rode `control-notes doctor` e exija a URL, o diretório de dados e a revisão de build esperados.
- Nunca dirija uma instância que esta execução não subiu.

## Convenções de direção

- Comece toda receita do estado de base, salvo quando as pré-condições dela dizem outra coisa.
- Prefira papéis e nomes ARIA a seletores CSS ou posição no DOM.
- Trate cada comando como literal. Nomes entre aspas e flags ficam como estão.
- Rode ações de browser por `control-notes browser`.
- Rode ações de terminal por `control-notes cli -- <comando>`.
- Restaure os dados semeados depois de uma mutação. A limpeza nunca remove artefato de prova.

## Prova e relato de pulo

- Capture a ação do usuário e o estado resultante, além da tela final.
- Prova de UI inclui snapshot ARIA e screenshot com a identidade do app visível.
- Prova de CLI inclui o comando, stdout, stderr e o código de saída.
- Prova de mutação inclui uma segunda visão só leitura do valor gravado.
- Registre o ID da feature e o ponto de entrada usado junto com cada artefato.
- Relate caminho inalcançável com o comando tentado e a pré-condição que faltou.
- Ponto de entrada pulado nunca é relatado como verificado por outro caminho.

## Contrato de cada feature

Cada arquivo de feature começa com um título H1 e um parágrafo que descreve o comportamento visível. Depois vêm exatamente quatro seções H2, nesta ordem:

1. `Subfeatures` lista IDs curtos, uma linha por comportamento.
2. `Como chegar (visão do usuário)` lista cada ponto de entrada do usuário.
3. `Dirigindo com <harness>` começa com `Pré-condições:` e usa bullets que juntam cada ação do usuário com o comando exato e o resultado observável.
4. `Armadilhas` lista as ciladas que podem desperdiçar ou invalidar uma verificação.

Detalhe de implementação fica fora do mapa. Nomeie só caminhos do usuário, alças estáveis, estado exigido, comandos e prova observável.

## Features

- [Criar nota](./create-note.md) cobre criação pelo browser e pela CLI, cancelamento, persistência e limpeza.
- [Buscar notas](./search.md) cobre busca pela barra, pelo teclado e pela CLI, com estados de resultado, vazio e limpo.
