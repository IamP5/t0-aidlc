# Rituais

São seis rituais: cinco internos e o do ART. Cada um abre e fecha por comando, e o registro sai sozinho no KB. Status de trabalho quem dá é o bot, e ritual nenhum serve para isso.

## A tabela

| Ritual | Slug | Quando | Duração | Quem | Facilita | Saída no KB |
|---|---|---|---|---|---|---|
| Daily do time | `daily-time` | todo dia | 10 min | todos | Flow Steward | registro curto de bloqueios e donos |
| Daily do pod | `daily-pod` | todo dia, logo depois | 30 a 45 min, ou mob mais longa quando há spec para fechar | o pod, com o agente ao vivo; Domain Expert quando precisar | Bet Owner | ideias, decisões, PRs de spec, registro da sessão |
| Harness Health | `harness-health` | toda semana | 20 min | o time | Harness Keeper | Harness Items com PR, casos de eval |
| Demo | `demo` | a cada 2 semanas, com a iteração do ART | 30 min | o time | Flow Steward | registro da Demo, Bets `shipped` ou `killed`, rodízio novo |
| Retro | `retro` | uma vez por mês | 60 min | o time | Flow Steward | registro da Retro; ADR quando a metodologia muda |
| PI Planning / Sense & Respond | `pi` | quando o ART marcar | a do ART | Lead/AIVA | Lead/AIVA | registro com as decisões do ART |

## Como todo ritual roda

```
t0 ritual <slug> open
t0 ritual <slug> close [--transcript <arquivo>] [--dry-run]
```

- O `open` monta a pauta a partir do KB. Cada ritual tem uma definição em `rituals/<slug>/ritual.md`, com os `inputs` que o comando lê.
- Durante o ritual, decisão vira `t0 log decision "<texto> (dono: <pessoa>, prazo: <data>)"`, bloqueio vira `t0 log blocker`, ideia vai pela skill `idea-capture`. Toda decisão tem dono.
- O `close` grava o Ritual Record em `rituals/<slug>/AAAA-MM-DD.md`, com decisões e donos, roda a transcrição se houve gravação e abre os PRs de decisão que saíram dali.
- Aposta e spec nunca são aprovadas "no ritual". No ritual, alguém abre ou mostra o PR, e quem decide aprova lá.

A skill `ritual` conduz isso junto com quem facilita. Ela mostra a pauta como o comando imprimiu, segura o foco e aponta para o digest quando alguém começa a dar status.

## Daily do time

Todo dia, 10 minutos, o time todo. Facilita o Flow Steward.

O `t0 ritual daily-time open` imprime o digest: merges desde a última daily, reviews parados há mais de 24h e bloqueios abertos. Na daily só se fala de duas coisas: bloqueios e pedidos de review. Para cada review parado, alguém assume, e a skill registra `t0 log decision "review de <PR> (dono: <pessoa>)"`. Para cada bloqueio, alguém vira dono.

Antes da daily, o Flow Steward aprova o PR em lote dos registros de passo do dia anterior.

## Daily do pod

Todo dia, logo depois da daily do time, 30 a 45 minutos. Pode virar uma sessão de mob mais longa quando há spec para fechar. Facilita o Bet Owner. O agente está ao vivo na tela.

A daily do pod conta como trabalho. É ali que o pod:

- valida ideias prototipando na hora (`prototype`), até o veredito;
- decide o que vira bet (`bet-new`, e o Bet Owner aprova o PR);
- afia ideia ou spec (`grill`);
- escreve o spec junto (`bet-spec`) e corta os slices (`bet-slice`);
- escolhe os slices `ready` do dia, respeitando o WIP de 2 por pessoa;
- destrava quem está travado.

Shaping, decisão de aposta e refinamento acontecem aqui, em grupo e com o agente.

Trecho real do Ritual Record de uma daily do pod, no exemplo do KB (`rituals/daily-pod/2026-10-20.md`):

```yaml
type: Ritual Record
ritual: ritual-daily-pod
date: 2026-10-20T09:15:00-03:00
facilitator: human:ana-exemplo
decisions:
  - { text: "IDEA-0001 segue e vira a BET-002, trilha bet, apetite de 1 semana", owner: human:ana-exemplo, due: 2026-10-21T18:00:00-03:00 }
  - { text: "IDEA-0002 morre: o áudio leva mais tempo que a leitura", owner: human:caio-exemplo, due: 2026-10-20T12:00:00-03:00 }
transcript: /transcripts/2026-10-20-daily-pod.md
```

## Harness Health

Toda semana, 20 minutos, o time. Facilita o Harness Keeper.

O `open` traz:

- os erros de agente que se repetiram na semana (Harness Items `open` com duas ocorrências ou mais);
- o orçamento de contexto: linhas de `AGENTS.md` e hooks contra o teto de 20 em `harness/budget.md`;
- skills sem uso há 4 semanas, candidatas a sunset;
- concepts do KB com `stale_after` vencido.

Para cada erro repetido, o time aceita ou recusa o item. Item aceito vai para a skill `harness-fix`, que abre um PR em draft no repo certo. Incidente da semana vira caso de eval. Se saiu versão nova do mattpocock-skills ou do pstack, o Harness Keeper lê o CHANGELOG e abre um Harness Item para o que vale portar.

A trava: o `t0 ritual harness-health close` recusa enquanto algum item aceito estiver sem PR. A saída é abrir os PRs que faltam. Desaceitar um item para o close passar está fora de cogitação.

## Demo

A cada 2 semanas, junto com a iteração do ART, 30 minutos, o time. Facilita o Flow Steward.

- Demo ao vivo do que foi pro ar, mais o painel de fluxo e adoção.
- Bets encerradas: `shipped` vem do `t0 bet ship` no último merge; bet que o time decide matar vai por `t0 log kill "<motivo>" --bet <BET>`.
- Rodízio: o time combina quem assume Harness Keeper e Flow Steward nas próximas 2 semanas. O `t0 ritual demo close` grava a troca.

## Retro

Uma vez por mês, 60 minutos, o time. Facilita o Flow Steward.

A pauta é como o time e a própria metodologia estão funcionando: o que atrapalha, que passo de processo cortar, o que mudar nas dailies e nos papéis. A régua é a de sempre: um passo só fica se protege algo concreto ou gera aprendizado. O Harness Keeper mostra o teto de hooks de `harness/budget.md`.

Retro que muda a metodologia abre ADR por `t0 new adr`, com a mudança e quem decidiu. Retro sem mudança fecha sem ADR.

## PI Planning e Sense & Respond do ART

Quando o ART marcar, com a duração do ART. Vai o Lead/AIVA. A pauta do time são as bets candidatas e os outcomes de adoção por produto. O registro sai com as decisões do ART, cada uma com dono do lado do time. Gravação só entra se o ART permitir, e passa pelo mesmo fluxo de transcrição.

## Interface com o ART

SAFe por fora, builder pods por dentro. O AI-Native SAFe pede outcomes no PI em vez de features comprometidas, e os degraus de adoção já são outcomes, então a interface fica fina.

| SAFe (AI-Native) | No t0 |
|---|---|
| AI-Native Team (3 a 7 pessoas) | 3 pods + Lead; o segundo revisor de Tier 2 pode vir de outro pod |
| Epic / tema | Idea promovida e outcome de PI |
| Feature / Story | Bet / Slice, espelhadas pelo `t0 jira sync` no CI |
| Iteração (2 semanas) | fluxo contínuo por dentro; Demo no fim de cada iteração do ART |
| PI Planning / PI Outcome Planning | compromisso com degraus de adoção, pisos de eval, SLO de review e DORA por produto; bets candidatas com apetite e risco entram como meio |
| Sense & Respond | registro da Demo e snapshot da quinzena como insumo; decisões do ART voltam como ADR ou Idea |
| Capacidades Product, Builder, Domain Expert, AI | Bet Owner; todo mundo; dev de squad chamado para a daily do pod; agentes com as skills do plugin |
| AI Value Architect | o Lead acumula |
| Capacidade / pontos | throughput de slices e cycle time; 1 ponto fixo por slice se exigirem |

Se o ART rodar SAFe clássico, a Demo alimenta a System Demo, as Retros e o Harness Health alimentam o I&A, e o PI Planning recebe bets candidatas além dos outcomes. A interface volta à mesa se houver mais de 3 pods no mesmo produto, se a BU exigir pontos por PI, se o ART pedir a cadência dele por dentro ou se a agenda do Lead estourar.

## Conta de tempo

A cerimônia pura, a cada 2 semanas, por pessoa:

| Ritual | Conta | Tempo |
|---|---|---|
| Daily do time | 10 min × 10 dias | 1h40 |
| Harness Health | 2 × 20 min | 40 min |
| Demo | 1 × 30 min | 30 min |
| Retro | metade de 60 min mensais | 30 min |
| Total | | cerca de 3h20 |

O Lead soma o PI Planning e o Sense & Respond, no ritmo do ART. A daily do pod fica fora da conta porque é trabalho: o pod prototipa, especifica e planeja ali.

## Transcrições

As dailies podem ser gravadas, com aviso a todos, para o agente extrair ideias e decisões. As regras estão na Policy `transcript-retention` do KB:

- A gravação crua mora só em `~/.t0/inbox/`, na máquina de quem gravou. O hook bloqueia qualquer agente de ler ali.
- A redação é determinística e vem antes de qualquer modelo. O `ritual <slug> close --transcript <arquivo>` chama `t0 transcript redact`, que roda o scanner de segredo e as regex de CPF, conta, e-mail e telefone. Depois o agente faz uma passada atrás de dado de cliente que a regex não pega. Achou, o arquivo para e a correção vai no redator, por um Harness Item.
- Qualquer pessoa pode pedir "fora do registro" para um trecho. O trecho sai inteiro, e o Transcript guarda só a contagem em `off_record_spans`. Ninguém tenta reconstruir ou resumir o que foi dito ali.
- Conversa 1:1 nunca é gravada nem processada.
- Até o aval de LGPD, tudo roda em dry-run: o `t0` redige e mostra, sem persistir nada no KB. Quando o jurídico der o aval, um PR na Policy preenche `lgpd_signoff` e troca `persist` para `on`.
- Tudo que o agente extrai da transcrição entra sem `verified` até alguém confirmar.
- Retenção: Transcript com `stale_after` de 180 dias (PROPOSTA, pendente de validação com jurídico e LGPD). Vencido o prazo, a transcrição é apagada e o Ritual Record fica.

Trecho real de uma transcrição redigida do exemplo:

```
caio: Vi. Pegou três PRs com mais de dois dias. Um era do [REDIGIDO:EMAIL].

ana: Então segue? Cabe numa semana, um pod só, Tier 1.

[FORA DO REGISTRO: 1 trecho]
```
