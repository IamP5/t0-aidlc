# Guia prático

Quatro passeios completos, com o que você digita. Os exemplos usam o produto fictício `exemplo` do KB, o bot que publica o status antes da daily do time, com o repo `status-bot` e o projeto Jira `EXE`.

Duas convenções:

- linha que começa com `$` vai no terminal;
- linha que começa com `>` vai no chat do agente. No Claude Code, com o plugin, a skill `bet-new` se chama `/t0:bet-new`; no Copilot e no Kiro, `/bet-new`. Aqui aparece o nome curto.

Antes de qualquer passeio, o básico precisa estar de pé: `t0` no PATH, plugin instalado e workspace montado em `~/ws/exemplo/`. Ver [Plugin e skills](07-plugin-e-skills.md) e [Workspace](06-workspace.md).

## 1. Uma correção pela trilha rápida, de ponta a ponta

Uma squad reclamou que o status saiu às 07:50 depois da mudança de offset do servidor. Cabe em um dia e não tem desenho a decidir.

### Registrar a ideia

```
> /idea-capture o status saiu 07:50 em vez de 08:50 depois da mudança de offset; quem reclamou foi a squad X, duas vezes essa semana
```

A skill procura duplicata, mostra o plano do `t0 new idea --dry-run` e, com o seu ok, cria a `IDEA-0003` num PR pequeno em draft.

### Reproduzir e abrir a aposta

```
> /t0 corrige o horário do status (IDEA-0003), é trilha rápida
```

A `/t0` escolhe o playbook `rapida`. Ela reproduz o bug pelo `verify-status-bot` e guarda a saída. Depois escreve com você:

- atual: o agendamento soma o offset do servidor, e o status sai às 07:50 quando o offset muda;
- esperado: o agendamento usa `America/Sao_Paulo`, e o status sai às 08:50 o ano todo;
- o que não muda: o conteúdo e a ordem das seções, o canal de destino;
- o teste que vai ficar vermelho: `test_horario_sobrevive_mudanca_de_offset`.

E roda `bet-new rapida IDEA-0003`, que por baixo chama:

```
$ t0 new bet --track rapida IDEA-0003 --dry-run
$ t0 new bet --track rapida IDEA-0003
$ t0 kb check --changed-from main
$ t0 gate aposta BET-001 --dry-run
```

Sai um PR em draft no KB com `bet.md` e o único slice, `slices/01-horario-em-brt.md`. A skill para aqui.

### Aprovar

Na daily, o Flow Steward (ou o Bet Owner) lê o PR e aprova. Aprovar é a decisão de aposta. Depois do merge, o CI roda `t0 jira sync`, cria `EXE-10` (Feature) e `EXE-11` (Story) e o slice fica `ready`.

### Construir

```
> /slice-build EXE-11
```

A skill roda:

```
$ t0 slice dor EXE-11
$ t0 slice start EXE-11
```

Ela cria a branch `EXE-11-horario-em-brt`, escreve o teste, vê vermelho, corrige, vê verde, roda a suíte e o lint, prova no app pelo `verify-status-bot` e abre o PR em draft com o rodapé `Jira: EXE-11`, `Tier: 1` e `Trilha: .audit/EXE-11.tsv`. Se você é júnior, ela pede o seu texto para "Em minhas palavras".

### Revisar

A `slice-build` chama a `slice-verify` no fim. Ela posta um comentário no PR com as raias de padrões e de spec, a evidência no app e os erros de agente. Você corrige o que ela achou com commit novo e pede outra rodada:

```
> /slice-verify EXE-11
```

### Fechar

Com o comentário limpo, você marca o PR como pronto (isso é seu, o agente não faz). Um humano revisa, porque é Tier 1. O merge é do time. O CI move o slice para `done`, roda `t0 bet ship` no último merge e a BET-001 vai para `shipped`.

## 2. Uma bet completa, da ideia ao ship

A ideia: o status da daily devia listar os PRs esperando review há mais de 24h.

### Ideia e protótipo

```
> /t0 ideia: mostrar review parado no status da daily
```

A `/t0` escolhe o playbook `ideia`. Ela roda `idea-capture` (sai a `IDEA-0001`), escreve a pergunta do protótipo em uma frase ("a busca do forge dá a idade do pedido de review?") e chama:

```
> /prototype IDEA-0001
```

O protótipo vive na branch `proto/IDEA-0001` do `status-bot`, nunca vai para o main. Na daily do pod, vocês abrem ao vivo. O pod confirma o veredito, e a skill grava:

```
$ t0 idea prototype IDEA-0001 --verdict segue --ref status-bot@proto/IDEA-0001:prototype_busca.py
```

### Aposta

Ainda na daily do pod:

```
> /bet-new bet IDEA-0001
```

A skill propõe apetite de 1 semana, hipótese ("com o review parado no status, a mediana até a primeira resposta cai para menos de 4h úteis"), métrica de sucesso, critério de kill e Tier 1. Roda `t0 new bet --track bet IDEA-0001` e abre o PR da aposta em draft. Um pod, Tier 1 e apetite de 1 semana: a Bet Owner aprova sozinha. Com o merge, a BET-002 vira `active`.

### Spec em mob

Na mesma daily do pod, ou numa mob mais longa:

```
> /grill BET-002
```

Rodadas de pergunta com resposta recomendada. "Review parado" vira verbete do glossário. A decisão de usar a API de busca do forge, sem webhook e sem estado, vira o ADR-0001 (`t0 new adr`).

```
> /bet-spec BET-002
```

A skill confirma os seams (`busca-do-forge` e `montagem-da-mensagem`) e escreve o `spec.md` com histórias, critérios de aceite em bullets, como verificar e tier:

- o status tem a seção Reviews parados, depois de Merges e antes de Travas;
- a seção lista só PRs fora de draft com review pedido há mais de 24h;
- cada linha traz o link do PR, a idade em horas e quem deve o review;
- sem PR parado, a seção diz que não há nenhum.

Se o desenho cruzasse fronteira de função, aqui entraria `/architect BET-002`, que compara candidatos com a `arena` e para no checkpoint esperando o seu ok.

### Slices e decisão de spec

```
> /bet-slice BET-002
```

A skill propõe o corte, você aprova:

```
1. Consulta de reviews parados
   Repo: status-bot · Tier: 1 · Bloqueado por: nenhum
2. Seção Reviews parados no status
   Repo: status-bot · Tier: 1 · Bloqueado por: 01
```

Ela grava os dois arquivos em `slices/`, roda `t0 gate spec BET-002 --dry-run` e abre o PR em draft com spec, slices e ADR. A Bet Owner aprova o PR: essa é a decisão de spec. No merge, o CI espelha `EXE-20`, `EXE-21` e `EXE-22` no Jira.

### Build, verify e ship

Cada slice segue o passeio 1 a partir de "Construir":

```
> /slice-build EXE-21
> /slice-build EXE-22
```

O slice 02 só começa quando o 01 mergear, porque depende dele. Lembre do WIP: no máximo 2 slices em construção por pessoa. No merge do último, o CI roda `t0 bet ship`: o spec da bet congela, o spec vivo em `products/exemplo/product.md` ganha a seção nova e a bet vai para `shipped`. Você escreve o aprendizado no corpo da Bet.

### Se a bet morrer no caminho

Só quando o Bet Owner disser que mata:

```
$ t0 log kill "a busca do forge não dá a idade do pedido de review" --bet BET-002
```

Bet morta conta como resultado.

## 3. Um dia com as duas dailies

### Antes da daily do time

O Flow Steward aprova o PR em lote dos registros de passo do dia anterior (`rec/batch/<data>`), com um clique.

### Daily do time, 10 minutos

O Flow Steward abre:

```
> /ritual daily-time open
```

Por baixo, `t0 ritual daily-time open` imprime o digest: merges desde ontem, reviews parados há mais de 24h e bloqueios. Ninguém conta o que fez ontem, porque está no digest. Para cada review parado, alguém assume:

```
$ t0 log decision "review de t0/status-bot#21 (dono: caio)"
```

Para cada bloqueio, alguém vira dono:

```
$ t0 log blocker "token do Jira de homologação expirou (dono: dani)"
```

E fecha:

```
$ t0 ritual daily-time close
```

### Daily do pod, 30 a 45 minutos

A Bet Owner abre com o agente na tela:

```
$ t0 ritual daily-pod open
```

A pauta vem do KB: ideias prototipadas sem decisão, bets ativas no pod, slices prontos. Daí o pod trabalha:

- uma ideia nova aparece: `/idea-capture`;
- alguém quer testar uma ideia: `/prototype IDEA-0002`, dez minutos ao vivo, veredito `mata`;
- a Bet Owner decide apostar: `/bet-new bet IDEA-0001` e ela aprova o PR;
- a bet ativa precisa de spec: `/bet-spec` e `/bet-slice` em mob;
- cada um escolhe os slices `ready` do dia, respeitando o WIP de 2.

Se a daily foi gravada, o fechamento leva o arquivo:

```
$ t0 ritual daily-pod close --transcript ~/.t0/inbox/2026-10-20-daily-pod.m4a --dry-run
```

A redação roda antes de qualquer modelo. Enquanto não houver aval de LGPD, fica em `--dry-run`: redige e não persiste. O que o agente extrair entra sem `verified`, e alguém confirma.

### O resto do dia

Cada Builder toca os próprios slices com `/slice-build`, orquestrando de 2 a 5 sessões de agente em paralelo. PR esperando review tem prioridade sobre slice novo. O hook de fim de sessão empurra os registros para o spool, e eles entram no lote de amanhã.

## 4. Um Harness Health

Quarta-feira, 20 minutos. Facilita o Harness Keeper.

### Durante a semana

A `slice-verify` achou, no PR #14 da BET-001, o agente escrevendo `datetime.now()` sem fuso. Foi uma vez só, então ficou no comentário. No PR #18 da BET-002, o mesmo padrão apareceu de novo, e a `slice-verify` abriu o item:

```
$ t0 new harness
```

Saiu o `HI-0001`, com `pattern: "datetime.now() ou datetime.utcnow() sem tz em código que agenda ou compara horário"` e as duas ocorrências.

### Abrir

```
> /ritual harness-health open
```

O `t0 ritual harness-health open` traz os Harness Items `open` com duas ocorrências ou mais, o orçamento de `harness/budget.md` (linhas de `AGENTS.md`, hooks contra o teto de 20), skills sem uso há 4 semanas e concepts vencidos no KB.

### Decidir e corrigir

O time aceita o `HI-0001`. Alguém roda:

```
> /harness-fix HI-0001
```

A skill sobe a escada e para no primeiro degrau que resolve. Aqui, o sensor: o ruff já tem as regras DTZ (flake8-datetimez), que pegam o padrão no CI com uma mensagem que o agente entende. Ela explica por que os degraus de cima (regra de área, skill, `AGENTS.md`) não precisam entrar, reaplica o diff do PR #14 numa worktree, mostra o lint falhando e depois passando com a correção, e abre o PR em draft `t0/status-bot#19`.

Se o item fosse o mapa do `verify-<app>` desatualizado, entraria `/verify-setup` no modo manter.

### Fechar

```
$ t0 ritual harness-health close
```

O close recusa enquanto algum item aceito estiver sem PR. Com o `#19` aberto, passa. Incidente da semana vira caso de eval (`t0 eval add` está previsto, ainda fora da CLI atual; até lá o caso entra direto em `evals/` no repo). Quando o PR mergeia, o item vira `fixed` com o `pr` gravado.
