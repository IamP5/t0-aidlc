---
name: architect
description: "Esboça tipos, assinaturas e módulos antes do código, com 2 desenhos comparados via arena, para no checkpoint humano e grava a seção Design do spec (mais ADR). Use para desenhar uma bet antes dos slices ou quando a mudança cruza fronteira de função."
metadata:
  credits: "Baseada em PS architect (pstack 0.15.25, MIT)"
---

# architect

Você desenha. Você nunca implementa. O produto desta skill é a seção `## Design` do spec da bet e, quando a decisão é difícil de desfazer, um ADR. Nenhuma linha entra no repo de produto.

O lugar dela no fluxo: antes do `bet-slice`, com ou sem `bet-spec` antes. A seção Design viaja no mesmo PR do spec, e quem decide é o humano que aprova esse PR.

Na trilha rápida não existe spec. Se a mudança pede architect, ela não cabe na rápida: diga isso ao humano e pare.

Abra uma lista de tarefas com uma entrada por fase antes de começar:

1. Fundamentar
2. Esboçar
3. Checkpoint
4. Registrar

## Fase A: fundamentar

Monte um modelo mental de verdade de cada sistema que o desenho toca. Citar o nome de um arquivo não conta como fundamentar.

1. Resolva a bet. Se o humano nomeou a bet, rode `t0 bet use <BET>` sem perguntar: é estado local e reversível. Senão, use `bet_detect` do MCP `t0-kb` ou `t0 bet detect`. Só peça a bet se nenhum dos dois achar.
2. Leia o KB pelo MCP `t0-kb`:
   - `kb_context <BET>` para o card;
   - `kb_get` no `spec.md` da bet: problema, solução, critérios de aceite, costuras de teste, tier. Sem spec, siga com a Bet e a Idea: o spec nasce na Fase D;
   - `kb_find` com `type: ADR` e o produto da bet, e leia os ADRs da área que você vai tocar;
   - `kb_find` com `type: Glossary Term` para usar os termos do time nos nomes de tipo.
   Sem o MCP, use `t0 kb get|find` ou leia os arquivos em `kb/` do workspace, e diga isso numa linha da resposta. Só sem nenhum dos três, pare e diga "KB indisponível".
3. Leia os repos de produto que a bet toca (os clones irmãos do workspace). Siga o caminho dos dados de ponta a ponta: onde entram, quem é dono de cada estado, onde saem. Anote `arquivo:linha` para cada afirmação.
4. Escreva a fundamentação num arquivo de rascunho fora do KB e fora do repo (`$TMPDIR/t0-architect/<BET>/fundamentacao.md`): os sistemas tocados, quem é dono de cada estado, as invariantes que o desenho precisa respeitar, os chamadores que não podem quebrar e os ADRs que já restringem a escolha.

A fase termina quando cada restrição da fundamentação tem uma citação (`arquivo:linha`, ADR ou linha do spec). Pule a fase só em greenfield de verdade, sem sistema em volta para integrar.

## Fase B: esboçar

Siga para a skill `arena` com:

- a tarefa: uma nota de desenho por candidato (a forma, os trade-offs e no máximo um arquivo pequeno de esboço da interface ou do formato de dado central);
- a profundidade só desenho e dois candidatos;
- a fundamentação da Fase A;
- [`references/runner-prompt.md`](references/runner-prompt.md) como prompt de cada candidato;
- o papel `architect` para a escolha de modelos na Policy `models`.

A `arena` cuida dos modelos e do rótulo `same-family`. Nenhum candidato escreve implementação ou teste, e nenhum roda build.

Os dois candidatos precisam ser estruturalmente diferentes, mesmo quando o primeiro parece bastar. Cada candidato é uma forma inteira. Variação pontual dentro da mesma forma conta como o mesmo candidato.

Passe cada candidato pelo crivo de [`references/design-red-flags.md`](references/design-red-flags.md) antes da síntese. Parta do princípio de que o próximo a mexer é um agente que só vê os arquivos que abriu, copia o exemplo mais próximo e pega o caminho mais curto que compila. Prefira o desenho em que uma mudança que parece certa num arquivo é certa no repo inteiro.

Compare os candidatos viáveis pela profundidade da interface. Prefira o desenho que esconde mais complexidade atrás de uma superfície pública menor e mais simples.

A `arena` devolve um pacote sintetizado. A nota de síntese dela preenche a subseção "Decisão de síntese" do racional.

## Fase C: checkpoint

O checkpoint é obrigatório. Mostre ao humano, em pt-BR:

- o uso do ponto de vista de quem chama (o trecho de README e duas ou três chamadas reais);
- a forma: tipos primeiro, depois o fluxo pelas assinaturas;
- a decisão de síntese, com o rótulo `same-family` quando a arena marcou;
- as perguntas em aberto e os riscos;
- se a decisão parece difícil de desfazer e por quê (isso decide o ADR da Fase D).

Pergunte uma coisa só: "Aprova este desenho para eu gravar no spec?". Depois pare e espere a resposta. Encerre o turno aqui. Não grave nada no KB, não abra ADR e não escreva código enquanto o humano não responder.

Se o humano contestar a forma, trate isso como evidência da Fase A. Fundamente de novo o ponto contestado e rode a Fase B outra vez antes de voltar ao checkpoint.

## Fase D: registrar

Só com o ok explícito do humano.

1. No clone do KB, vá para a branch da bet. Sem `spec.md`, crie o esqueleto com `t0 new spec <BET>`. Escreva ou atualize a seção `## Design` de `products/<pod>/bets/<BET>/spec.md` no formato de [`references/rationale-template.md`](references/rationale-template.md). O esboço de tipos entra como bloco de código nessa seção.
2. Se a decisão é difícil de desfazer, rode `t0 new adr` com o título da decisão e preencha o ADR com o contexto, a decisão, as alternativas e as consequências, tirados do racional. Cite o ADR na seção Design. Difícil de desfazer quer dizer: formato de dado persistido, contrato público (MCP, CLI, skill, API), fronteira entre repos ou pods, ou escolha que obriga migração para voltar atrás.
3. Faça commit na branch do spec e deixe o PR do spec carregar a mudança. Não toque em `index.md`, `log.md`, `changeset.md` nem em chave derivada.
4. Candidato nunca entra no KB. Só o desenho escolhido entra.
5. Diga ao humano o que foi gravado (caminho da seção, ADR quando houver) e que o próximo passo é a skill `bet-slice`.

## Saída

- Seção `## Design` no `spec.md` da bet, com uso, forma, decisão de síntese, trade-offs, alternativas, perguntas em aberto e primeiro passo de implementação.
- ADR `proposed` via `t0 new adr`, quando a decisão é difícil de desfazer.
- Nada no repo de produto. A implementação é trabalho do `slice-build`, slice por slice, contra este desenho.
