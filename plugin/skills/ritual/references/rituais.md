# Rituais: o que acontece em cada um

Leia só a seção do slug que você vai abrir.

## daily-time

Todo dia, 10 min, o time todo. Facilita o Flow Steward.

- O `open` imprime o digest: merges desde a última daily, reviews parados há mais de 24h e bloqueios abertos. Mostre o digest como veio.
- Na daily só se fala de duas coisas: bloqueios e pedidos de review. Para cada review parado, pergunte quem pega e registre com `t0 log decision "review de <PR> (dono: <pessoa>)"`. Para cada bloqueio, pergunte o dono e registre com `t0 log blocker`. Se ninguém pegar, registre com `(dono: a definir)` e siga. O `open` lista em "Bloqueios sem dono" os que ficaram assim.
- Status de trabalho já está no digest. Quem começar a contar o que fez ontem, aponte para o digest.
- Saída no KB: registro curto de bloqueios e donos.

## daily-pod

Todo dia, logo depois da `daily-time`, 30 a 45 min. Pode virar sessão de mob mais longa quando há spec para fechar. É o pod com você ao vivo. Facilita o Bet Owner. Domain Expert de squad entra quando precisar.

É trabalho, e você trabalha junto com o pod:
- ideia que aparece: siga para a skill `idea-capture`;
- ideia para validar: siga para a skill `prototype` e prototipe na hora, fora do main, até o veredito `segue`, `ajusta` ou `mata`;
- ideia ou spec que precisa de afiação: siga para a skill `grill`;
- o Bet Owner quer apostar: siga para a skill `bet-new`, que abre o PR da aposta. Quem decide é o Bet Owner aprovando o PR, e o Lead entra quando a bet cruza pods, é Tier 2 ou passa de 1 semana de apetite;
- bet ativa sem spec: siga para a skill `bet-spec`, escrevendo junto com o pod;
- spec pronto: siga para a skill `bet-slice`. Spec e slices vão no mesmo PR, que o Bet Owner aprova (mais o Lead em Tier 2);
- tarefas do dia: o pod escolhe slices `ready`, respeitando o WIP de 2 por pessoa.

Saída no KB: ideias, decisões, PRs de spec e o registro da sessão.

## harness-health

Toda semana, 20 min, o time. Facilita o Harness Keeper.

- O `open` traz os erros de agente que se repetiram na semana (Harness Items `open` com duas ocorrências ou mais), o orçamento de contexto (linhas de `AGENTS.md`, hooks contra o teto de 20 em `harness/budget.md`), skills sem uso para sunset e concepts vencidos no KB.
- Para cada erro repetido, o time aceita ou recusa o item. Item aceito segue para a skill `harness-fix`, que abre um PR em draft no repo certo. Erro novo sem item vira `t0 new harness`.
- Incidente da semana vira caso de eval.
- Se saiu versão nova do mattpocock-skills ou do pstack, o Harness Keeper lê o CHANGELOG e abre um Harness Item para o que vale portar.
- Trava do close: recusa enquanto algum item aceito não tem PR. Abra os PRs que faltam com a skill `harness-fix` e rode o close de novo. Nunca desaceite um item para o close passar.
- Saída no KB: Harness Items com PR e casos de eval.

## demo

A cada 2 semanas, junto com a iteração do ART, 30 min, o time. Facilita o Flow Steward.

- Demo ao vivo do que foi pro ar, mais o painel de fluxo e adoção.
- Bets encerradas: `shipped` vem do `t0 bet ship` no último merge. Bet que o time decide matar vai por `t0 log kill "<motivo>" --bet <BET>`.
- Rodízio: o Harness Keeper e o Flow Steward trocam a cada 2 semanas. Todo mundo passa pelos dois papéis, e júnior na primeira vez roda em par com um sênior. Pergunte ao time quem assume cada papel. Você propõe nomes a partir de `team/rotations/`, e o time escolhe.
- No close: o `t0 ritual demo close` grava o rodízio novo. Tenha os dois nomes combinados antes de fechar.
- Saída no KB: registro da Demo, Bets `shipped` ou `killed` e o rodízio novo.

## retro

Uma vez por mês, 60 min, o time. Facilita o Flow Steward.

- Como o time e a própria metodologia estão funcionando: o que atrapalha, que passo de processo cortar, o que mudar nas dailies e nos papéis.
- A régua: um passo só fica se protege algo concreto (risco técnico, exigência do banco, adoção pelas squads) ou gera aprendizado.
- O Harness Keeper reporta o teto de hooks de `harness/budget.md`.
- ADR só quando a metodologia muda: aí rode `t0 new adr` com a mudança e quem decidiu. Retro sem mudança de metodologia fecha sem ADR.
- Saída no KB: registro da Retro e, quando a metodologia muda, o ADR.

## pi

PI Planning ou Sense & Respond do ART, quando o ART marcar, com a duração do ART. Vai o Lead/AIVA.

- Pauta: bets candidatas e outcomes de adoção por produto.
- Gravação só entra se o ART permitir, e passa pelo mesmo fluxo de transcrição da skill.
- Saída no KB: registro com as decisões do ART, cada uma com dono do lado do time.
