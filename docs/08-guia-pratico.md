# Guia prático

Esta página traz quatro passeios completos, com o que você digita em cada passo. Os exemplos usam o produto fictício `exemplo` do KB: o bot que publica o status antes da daily do time. O repo é o `status-bot` e o projeto Jira é o `EXE`.

Duas convenções:

- linha que começa com `$` vai no terminal;
- linha que começa com `>` vai no chat do agente. No Claude Code, com o plugin, a skill `bet-new` se chama `/t0:bet-new`. No Copilot e no Kiro, ela se chama `/bet-new`. Esta página usa o nome curto.

Antes de começar qualquer passeio, confira o básico: o `t0` instalado (no PATH ou fixado em `.t0/bin/t0` no workspace), o plugin instalado e o workspace montado em `~/ws/exemplo/`. Veja [Plugin e skills](07-plugin-e-skills.md) e [Workspace](06-workspace.md).

## 1. Uma correção pela trilha rápida, de ponta a ponta

Uma squad reclamou que o status saiu às 07:50 depois da mudança de offset do servidor. A correção cabe em um dia e não tem desenho a decidir, então vai pela trilha rápida (a trilha para ajuste ou bugfix que cabe em 1 dia, sem spec, com um único slice).

### Registrar a ideia

```
> /idea-capture o status saiu 07:50 em vez de 08:50 depois da mudança de offset; quem reclamou foi a squad X, duas vezes essa semana
```

A skill procura duplicata e mostra o plano do `t0 new idea --dry-run`. Com o seu ok, ela cria a `IDEA-0003` num PR pequeno em draft.

### Reproduzir e abrir a aposta

```
> /t0 corrige o horário do status (IDEA-0003), é trilha rápida
```

A `/t0` escolhe o playbook `rapida`. Ela reproduz o bug pelo `verify-status-bot` (a skill local do repo que sobe, dirige e prova o app real) e guarda a saída. Depois, ela escreve com você:

- atual: o agendamento soma o offset do servidor, e o status sai às 07:50 quando o offset muda;
- esperado: o agendamento usa `America/Sao_Paulo`, e o status sai às 08:50 o ano todo;
- o que não muda: o conteúdo e a ordem das seções, o canal de destino;
- o teste que vai ficar vermelho: `test_horario_sobrevive_mudanca_de_offset`.

Em seguida, ela roda `bet-new rapida IDEA-0003`, que por baixo chama:

```
$ t0 new bet --track rapida IDEA-0003 --dry-run
$ t0 new bet --track rapida IDEA-0003
$ t0 kb check --changed-from main
$ t0 gate aposta BET-001 --dry-run
```

O resultado é um PR em draft no KB com o `bet.md` e o único slice (fatia vertical da bet: um repo, um PR), `slices/01-horario-em-brt.md`. A skill propõe sozinha a hipótese, o critério de kill e o tier. Ela não pergunta quem aprova, porque o gate (o check de CI que confere a decisão humana no PR) diz. A skill para aqui.

Atalho: se não houver Idea registrada, `/t0 corrige o horário do status, é trilha rápida` vai direto para `t0 new bet --track rapida "corrige o horário do status"`. Esse comando cria Idea, Bet e Slice no mesmo PR.

### Aprovar

Na daily, o Flow Steward (o rodízio que facilita a daily do time e cuida da fila de review) ou o Bet Owner (o sênior que decide o que vira bet e responde pelo resultado) lê o PR e aprova. Aprovar o PR é a decisão de aposta. Depois do merge, o CI roda `t0 jira sync` e cria `EXE-10` (Feature) e `EXE-11` (Story). O slice fica `ready`.

### Construir

```
> /slice-build EXE-11
```

A skill roda:

```
$ t0 slice dor EXE-11
$ t0 slice start EXE-11
```

Ela cria a branch `EXE-11-horario-em-brt` e escreve o teste. Vê o teste vermelho, corrige o código e vê o teste verde. Depois, roda a suíte e o lint, prova no app pelo `verify-status-bot` e abre o PR em draft com o rodapé `Jira: EXE-11`, `Tier: 1` e `Trilha: .audit/EXE-11.tsv` (o Tier é o nível de review do PR: 0, 1 ou 2). Se você é júnior, ela pede o seu texto para a seção "Em minhas palavras".

### Revisar

A `slice-build` termina no PR em draft e sugere a revisão. Você chama `slice-verify EXE-11`, ou o pod pede a revisão na daily. A `slice-verify` (o agente de review que roda antes do humano) posta um comentário no PR com as raias de padrões e de spec, a evidência no app e os erros de agente. Você corrige o que ela achou com um commit novo e pede outra rodada:

```
> /slice-verify EXE-11
```

### Fechar

Quando o comentário vier limpo, você marca o PR como pronto. Esse passo é seu, o agente não faz. Como o PR é Tier 1, um humano revisa. O merge é do time. Depois do merge, o CI move o slice para `done`. No último merge, o CI roda `t0 bet ship` e a BET-001 vai para `shipped`.

## 2. Uma bet completa, da ideia ao ship

A ideia é que o status da daily liste os PRs que esperam review há mais de 24h.

### Ideia e protótipo

```
> /t0 ideia: mostrar review parado no status da daily
```

A `/t0` escolhe o playbook `ideia` e roda `idea-capture`, que cria a `IDEA-0001`. Depois, ela escreve a pergunta do protótipo em uma frase ("a busca do forge dá a idade do pedido de review?") e chama:

```
> /prototype IDEA-0001
```

O protótipo vive na branch `proto/IDEA-0001` do `status-bot` e nunca vai para o main. Na daily do pod, vocês abrem o protótipo ao vivo. O pod confirma o veredito, e a skill grava:

```
$ t0 idea prototype IDEA-0001 --verdict segue --ref status-bot@proto/IDEA-0001:prototype_busca.py
```

### Aposta

Ainda na daily do pod:

```
> /bet-new bet IDEA-0001
```

A skill propõe apetite de 1 semana (o apetite é quanto tempo o time aceita gastar na bet), a hipótese ("com o review parado no status, a mediana até a primeira resposta cai para menos de 4h úteis"), a métrica de sucesso, o critério de kill e Tier 1. Ela roda `t0 new bet --track bet IDEA-0001` e abre o PR da aposta em draft. Como a bet tem um pod só, Tier 1 e apetite de 1 semana, a Bet Owner aprova sozinha. Com o merge, a BET-002 vira `active`.

### Spec em mob

Na mesma daily do pod, ou numa mob mais longa (trabalho em grupo com o agente ao vivo):

```
> /grill BET-002
```

O `/grill` faz rodadas de pergunta, cada uma com uma resposta recomendada. O termo "Review parado" vira verbete do glossário. A decisão de usar a API de busca do forge, sem webhook e sem estado, vira o ADR-0001 (`t0 new adr`).

```
> /bet-spec BET-002
```

A skill confirma os seams (as costuras, os pontos do código onde o comportamento é testado): `busca-do-forge` e `montagem-da-mensagem`. Depois, escreve o `spec.md` com histórias, critérios de aceite em bullets, como verificar e tier:

- o status tem a seção Reviews parados, depois de Merges e antes de Travas;
- a seção lista só PRs fora de draft com review pedido há mais de 24h;
- cada linha traz o link do PR, a idade em horas e quem deve o review;
- sem PR parado, a seção diz que não há nenhum.

Se o desenho cruzasse fronteira de função, este seria o momento de chamar `/architect BET-002`. Essa skill compara candidatos com a `arena` e para no checkpoint, esperando o seu ok.

### Slices e decisão de spec

```
> /bet-slice BET-002
```

A skill propõe o corte e você aprova:

```
1. Consulta de reviews parados
   Repo: status-bot · Tier: 1 · Bloqueado por: nenhum
2. Seção Reviews parados no status
   Repo: status-bot · Tier: 1 · Bloqueado por: 01
```

Ela grava os dois arquivos em `slices/`, roda `t0 gate spec BET-002 --dry-run` e abre o PR em draft com spec, slices e ADR. A Bet Owner aprova o PR, e essa aprovação é a decisão de spec. No merge, o CI espelha `EXE-20`, `EXE-21` e `EXE-22` no Jira.

### Build, verify e ship

Cada slice segue o passeio 1 a partir de "Construir":

```
> /slice-build EXE-21
> /slice-build EXE-22
```

O slice 02 depende do 01, então só começa quando o 01 mergear. Lembre do WIP: no máximo 2 slices em construção por pessoa. No merge do último slice, o CI roda `t0 bet ship`. O spec da bet congela, o spec vivo em `products/exemplo/product.md` ganha a seção nova e a bet vai para `shipped`. Por fim, você escreve o aprendizado no corpo da Bet.

### Se a bet morrer no caminho

Rode este comando só quando o Bet Owner decidir matar a bet:

```
$ t0 log kill "a busca do forge não dá a idade do pedido de review" --bet BET-002
```

Bet morta conta como resultado.

## 3. Um dia com as duas dailies

### Antes da daily do time

O Flow Steward aprova, com um clique, o PR em lote com os registros de passo do dia anterior (`rec/batch/<data>`).

### Daily do time, 10 minutos

O Flow Steward abre a daily:

```
> /ritual daily-time open
```

Por baixo, `t0 ritual daily-time open` imprime o digest: merges desde ontem, reviews parados há mais de 24h e bloqueios. Ninguém conta o que fez ontem, porque isso já está no digest. Para cada review parado, alguém assume o review:

```
$ t0 log decision "review de t0/status-bot#21 (dono: caio)"
```

Para cada bloqueio, alguém vira dono:

```
$ t0 log blocker "token do Jira de homologação expirou (dono: dani)"
```

Para fechar a daily:

```
$ t0 ritual daily-time close
```

### Daily do pod, 30 a 45 minutos

A Bet Owner abre a daily com o agente na tela:

```
$ t0 ritual daily-pod open
```

A pauta vem do KB: ideias prototipadas sem decisão, bets ativas no pod e slices prontos. A partir daí, o pod trabalha:

- uma ideia nova aparece: `/idea-capture`;
- alguém quer testar uma ideia: `/prototype IDEA-0002`, dez minutos ao vivo, veredito `mata`;
- a Bet Owner decide apostar: `/bet-new bet IDEA-0001` e ela aprova o PR;
- a bet ativa precisa de spec: `/bet-spec` e `/bet-slice` em mob;
- cada um escolhe os slices `ready` do dia, respeitando o WIP de 2.

Se a daily foi gravada, o fechamento leva o arquivo da gravação:

```
$ t0 ritual daily-pod close --transcript ~/.t0/inbox/2026-10-20-daily-pod.m4a --dry-run
```

A redação (a remoção de segredos e dados pessoais da transcrição) roda antes de qualquer modelo. Enquanto não houver aval de LGPD, o fechamento fica em `--dry-run`: o `t0` redige e não persiste nada. O que o agente extrair entra sem `verified`, e uma pessoa confirma.

### O resto do dia

Cada Builder toca os próprios slices com `/slice-build` e orquestra de 2 a 5 sessões de agente em paralelo. PR esperando review tem prioridade sobre slice novo. O hook de fim de sessão empurra os registros para o spool (a pasta local onde os registros esperam o push), e eles entram no lote de amanhã.

## 4. Um Harness Health

Quarta-feira, 20 minutos. O Harness Keeper (o rodízio que cuida do harness e do KB) facilita o ritual. Nele, erros repetidos do agente sobem a escada do harness (tudo o que cerca o agente para ele errar menos: `AGENTS.md`, regras, skills, linters, testes, hooks e CI).

### Durante a semana

No PR #14 da BET-001, a `slice-verify` achou o agente escrevendo `datetime.now()` sem fuso. Como foi uma vez só, o achado ficou no comentário. No PR #18 da BET-002, o mesmo padrão apareceu de novo, e a `slice-verify` abriu o item:

```
$ t0 new harness
```

Saiu o `HI-0001`, um Harness Item (o registro de uma classe de erro de agente), com `pattern: "datetime.now() ou datetime.utcnow() sem tz em código que agenda ou compara horário"` e as duas ocorrências.

### Abrir

```
> /ritual harness-health open
```

O `t0 ritual harness-health open` traz quatro coisas: os Harness Items `open` com duas ocorrências ou mais; o orçamento de `harness/budget.md` (linhas de `AGENTS.md`, hooks contra o teto de 20); as skills sem uso há 4 semanas; e os concepts vencidos no KB.

### Decidir e corrigir

O time aceita o `HI-0001`, e alguém roda:

```
> /harness-fix HI-0001
```

A skill sobe a escada e para no primeiro degrau (cada nível da escada, do sensor ao `AGENTS.md`) que resolve. Aqui, o degrau é o sensor (o degrau computacional, como lint, teste ou check de CI): o ruff já tem as regras DTZ (flake8-datetimez), que pegam o padrão no CI com uma mensagem que o agente entende. A skill explica por que os outros degraus (regra de área, skill, `AGENTS.md`) não precisam entrar. Depois, reaplica o diff do PR #14 numa worktree, mostra o lint falhando e depois passando com a correção, e abre o PR em draft `t0/status-bot#19`.

Se o item fosse o mapa do `verify-<app>` desatualizado, o caminho seria `/verify-setup` no modo manter.

### Fechar

```
$ t0 ritual harness-health close
```

O close recusa enquanto algum item aceito estiver sem PR. Com o `#19` aberto, o close passa. O incidente da semana vira caso de eval (uma tarefa da suíte de regressão que mede a ferramenta de agente). O comando `t0 eval add` está previsto, mas ainda fica fora da CLI atual. Até lá, o caso entra direto em `evals/` no repo. Quando o PR mergeia, o item vira `fixed` com o `pr` gravado.
