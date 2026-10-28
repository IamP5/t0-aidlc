---
name: slice-build
description: "Constrói um slice pronto: t0 slice dor e start, branch <KEY>-slug, TDD vermelho e verde nas costuras do spec, trilha .audit/<KEY>.tsv commitada e PR em draft com evidência antes e depois. Use quando alguém pede para implementar, construir ou pegar um slice ou uma chave Jira."
metadata:
  credits: "Baseada em MP implement + tdd + pr (mattpocock-skills 1.3.1, MIT; pr credita o show-me de Dex Horthy, Humanlayer) e PS show-me-your-work + in-your-own-words (pstack 0.15.25, MIT)"
---

# slice-build

Um slice vira um PR em draft, construído teste a teste nas costuras que o spec combinou, com uma trilha de decisões que qualquer revisor confere. Trabalho reversível dentro do slice segue sem pedir licença. O PR nasce draft e fica draft: marcar como pronto e fazer merge são do humano.

Abra uma lista de tarefas com estes passos antes de começar:

1. Entender o slice
2. Checar o DoR e começar
3. Abrir a trilha
4. Fixar as costuras e a evidência de antes
5. Vermelho e verde
6. Provar no app
7. Auditar a trilha
8. Abrir o PR em draft

## 1. Entender o slice

1. Pegue a chave Jira do pedido (`PAY-130`). Sem chave, use `bet_detect` do MCP `t0-kb` ou `t0 bet detect`. Sem chave nem bet resolvida, pare e peça a chave.
2. Leia `kb_context <KEY>` e `kb_get <KEY>` no MCP `t0-kb`. Na trilha bet, leia também o `spec.md` da bet, inclusive a seção Design quando existir. Sem o MCP, use `t0 kb get|find` ou leia os arquivos em `kb/` do workspace, e diga isso numa linha da resposta. Só sem nenhum dos três, pare e diga "KB indisponível".
3. Diga o título do slice e reescreva, com as suas palavras, em três ou quatro linhas, o que o slice precisa entregar e que problema resolve. Siga sem esperar resposta. Se o humano corrigir, ajuste e registre na trilha.
4. Anote o `repo` do slice e trabalhe no clone desse repo dentro do workspace.

## 2. Checar o DoR e começar

```bash
t0 slice dor <KEY>
t0 slice start <KEY>
```

- `t0 slice dor` recusa quando falta critério de aceite, "como verificar", tier, spec aprovado sem marcador aberto ou quando você já tem 2 slices em construção. Mostre a recusa ao humano em pt-BR e pare. Nunca contorne a recusa.
- Saída 3 em qualquer comando `t0`: KB indisponível, pare.
- `t0 slice start` recusa árvore suja. Resolva a sujeira com o humano antes.
- Confira a branch com `git branch --show-current`. O formato é `<KEY>-<slug>`, com o slug em kebab-case curto tirado do título (`PAY-130-limite-diario`). Se o comando não criou a branch, crie a partir da branch padrão atualizada: `git switch -c <KEY>-<slug>`.

## 3. Abrir a trilha

A trilha é `.audit/<KEY>.tsv` na raiz do repo, uma linha por decisão: `ts`, `phase`, `decision`, `why`, `evidence`, `result`. Grave sempre pelo helper, que carimba o horário, escreve o cabeçalho na primeira vez e neutraliza célula que viraria fórmula de planilha:

```bash
<dir desta skill>/scripts/log.sh .audit/<KEY>.tsv <phase> "<decisão>" "<por quê>" "<evidência>" "<resultado>"
```

- Escreva como contaria para um colega o que fez. Palavras simples, ações concretas.
- A evidência é um ponteiro: SHA de commit, `arquivo:linha`, nome do teste, caminho de screenshot ou de saída. Nunca um parágrafo.
- Registre decisões e marcos: a reescrita do passo 1, as costuras escolhidas, cada ciclo vermelho e verde, cada desvio ou reversão com o gatilho, cada bloqueio, a verificação no app, o PR.
- Só acrescente linhas. Uma decisão errada ganha uma linha nova que a substitui.
- Se a trilha já tem linhas de outra execução, leia as últimas e comece a sua com uma linha de phase `start` que cita o intervalo de `ts` que não é seu.

Bloqueio que você não resolve sozinho: grave na trilha, rode `t0 log blocker "<texto>" --story <KEY>` e pare.

## 4. Fixar as costuras e a evidência de antes

1. Liste as costuras de teste. Na trilha bet, elas vêm do spec (e da seção Design quando existir). Na trilha rápida, vêm do slice: "atual, esperado, o que não muda" e o teste que vai ficar vermelho. Grave a lista na trilha.
2. Teste só nessas costuras. Se achar que falta uma, siga com as combinadas e deixe a pergunta no PR.
3. Capture o antes. Rode o primeiro teste novo e guarde a saída vermelha. Se o slice muda comportamento visível no app, dirija a feature pelo `verify-<app>` do repo (seção 6) e guarde a evidência de antes também.

## 5. Vermelho e verde

Leia [`references/tdd.md`](references/tdd.md) antes do primeiro teste. Para cada critério de aceite, numa costura combinada:

1. Escreva um teste que falha pelo motivo certo. Rode e veja vermelho.
2. Escreva o mínimo de código para passar. Rode e veja verde.
3. Grave a linha na trilha com o nome do teste e o resultado.
4. Faça commit pequeno com a mensagem prefixada pela chave: `<KEY>: <o que mudou>`.

Rode o typecheck e o arquivo de teste da vez com frequência. No fim, rode a suíte inteira e o lint do repo, e guarde a saída. Refactor só depois do verde, com a suíte verde antes e depois.

Se a implementação briga com o desenho da seção Design, pare e registre o atrito. Parâmetro que o desenho não previu é sinal: ou o desenho errou, ou o requisito escapou, ou a implementação está indo longe demais. Leve isso ao humano no PR.

## 6. Provar no app

Verde nos testes ainda é proxy. Prove contra o app real:

1. Ache o `verify-<app>` do repo em `.t0/skills/verify-<app>/SKILL.md`.
2. Siga as seções dele: Subir, Diagnóstico, Dirigir (a feature do mapa que cobre o "Como verificar" do slice), Evidência e Limpeza.
3. Confira que a evidência continua no caminho nomeado depois da limpeza. Grave a linha na trilha.

Sem `verify-<app>` no repo, rode os passos do "Como verificar" do slice e o comando de teste do repo direto, e grave na trilha e no PR "sem verify-<app>; verificado pelos passos do slice". Sugira a skill `verify-setup` como próximo passo, sem esperar por ela.

## 7. Auditar a trilha

Antes de abrir o PR, confira que a trilha conta a verdade. Compare as suas linhas com o `git log` da branch, com as saídas de teste e de verificação desta sessão e com o diff. Leia só isso: nada de arquivo de transcrição, e nunca `~/.t0/inbox/`.

- Cada linha corresponde a uma decisão ou ação real.
- Cada evidência resolve e mostra o que a linha afirma.
- Desvio, mudança de rumo ou tentativa abandonada que moldou o trabalho e não está na trilha é lacuna: acrescente.

Corrija a trilha, nunca a história. A auditoria só acrescenta linhas que substituem as erradas.

Só em Tier 2, lance um subagente novo, só leitura, no modelo que a Policy `models` aprova para revisor (`kb_get methodology/policies/models.md`), de preferência de outra família que a sua. Ele lê a trilha, o diff e as saídas e aponta o que o humano precisa olhar: decisão com evidência fraca, verificação afirmada sem prova, escolha arriscada em retrospecto, lacuna que passaria numa leitura rápida. Se ele for da mesma família que você, anote `same-family`.

## 8. Abrir o PR em draft

1. Faça commit da trilha junto com o código: `git add .audit/<KEY>.tsv`. A trilha entra no PR.
2. Descubra se a seção "Em minhas palavras" é obrigatória: é em todo Tier 2 e em PR de autor júnior (veja o Person do autor no KB com `kb_find`; na dúvida, pergunte). Quando for, peça ao autor humano o texto dele, com as palavras dele: o que muda, por que, o que pode dar errado. Cole sem editar. Enquanto ele não mandar, deixe `[PRECISA DO AUTOR]`.
3. Escreva o corpo pelo modelo de [`references/pr-body.md`](references/pr-body.md) num arquivo temporário.
4. Antes de qualquer push, confirme que existe forge: `gh` está instalado, `gh repo view` passa para o repo e `git remote get-url --push origin` não está desativado (`no_push`, `DISABLED` ou vazio). Se algum falhar, nunca faça push: o PR em draft é a branch local, com o corpo em `.t0/pr/<branch>.md`, e diga isso na resposta.
5. Com forge, faça push da branch sem força e abra o PR em draft:

   ```bash
   git push -u origin <KEY>-<slug>
   gh pr create --draft --title "<KEY>: <título do slice>" --body-file <arquivo>
   ```

6. Grave a linha do PR na trilha e faça commit dela, com push só se houver forge. O estado do slice no KB muda pelo CI. Você não edita.

O build termina aqui, com a suíte verde e a trilha commitada. A revisão é passo à parte: sugira a skill `slice-verify` e não rode.

## Resposta ao humano

Em pt-BR: o link do PR, o que mudou para quem usa, a evidência de antes e depois, o tier, o que ficou em aberto e, em Tier 2, uma seção "Atenção". A seção começa numa linha própria com `revisado por <modelo>` (mais `(same-family)` quando for o caso) e lista cada ponto apontado pelo revisor da trilha, com a linha ou o momento. "Sem pontos" é um valor válido. O nome do modelo é obrigatório. Feche sugerindo `slice-verify <KEY>`.
