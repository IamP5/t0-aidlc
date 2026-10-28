# Rituais

O time tem seis rituais: cinco internos e o do ART (o trem do SAFe de que o time faz parte). Cada ritual abre e fecha por comando, e o comando grava o registro no KB (o repositório do time, `t0-kb`). Nenhum ritual serve para dar status de trabalho. Quem dá status é o bot.

## A tabela

| Ritual | Slug | Quando | Duração | Quem | Facilita | Saída no KB |
|---|---|---|---|---|---|---|
| Daily do time | `daily-time` | todo dia | 10 min | todos | Flow Steward | registro curto de bloqueios e donos |
| Daily do pod | `daily-pod` | todo dia, logo depois | 30 a 45 min, ou mob mais longa quando há spec para fechar | o pod, com o agente ao vivo; Domain Expert quando precisar | Bet Owner | ideias, decisões, PRs de spec, registro da sessão |
| Harness Health | `harness-health` | toda semana | 20 min | o time | Harness Keeper | Harness Items com PR, casos de eval |
| Demo | `demo` | a cada 2 semanas, com a iteração do ART | 30 min | o time | Flow Steward | registro da Demo, Bets `shipped` ou `killed`, rodízio novo |
| Retro | `retro` | uma vez por mês | 60 min | o time | Flow Steward | registro da Retro; ADR quando a metodologia muda |
| PI Planning / Sense & Respond | `pi` | quando o ART marcar | a do ART | Lead/AIVA | Lead/AIVA | registro com as decisões do ART |

Flow Steward e Harness Keeper são papéis de rodízio de 2 semanas. O Bet Owner é o sênior que decide o que vira bet (uma aposta de até 2 semanas). O Lead/AIVA é o Chapter Lead, que faz a interface com o ART.

## Como todo ritual roda

```
t0 ritual <slug> open
t0 ritual <slug> close [--transcript <arquivo>] [--dry-run]
```

- O `open` monta a pauta a partir do KB. Cada ritual tem uma definição em `rituals/<slug>/ritual.md`, e os `inputs` dessa definição dizem o que o comando lê.
- Durante o ritual, cada decisão vira `t0 log decision "<texto> (dono: <pessoa>, prazo: <data>)"`, cada bloqueio vira `t0 log blocker` e cada ideia entra pela skill `idea-capture`. Toda decisão tem dono. Quando a decisão é claramente de um papel, o dono é quem ocupa o papel. Um bloqueio que ninguém pegou entra como `(dono: a definir)` e não trava o close.
- O `close` grava o Ritual Record (o registro da sessão, com decisões e donos) em `rituals/<slug>/AAAA-MM-DD.md`. Se houve gravação, ele roda a transcrição. Ele também abre os PRs das decisões tomadas no ritual.
- Aposta e spec (o contrato da bet) nunca são aprovadas "no ritual". No ritual, alguém abre ou mostra o PR, e quem decide aprova no PR.

A skill `ritual` conduz o ritual junto com quem facilita. Ela mostra a pauta como o comando imprimiu, mantém o foco e aponta para o digest quando alguém começa a dar status.

## Daily do time

Todo dia, 10 minutos, com o time todo. O Flow Steward facilita.

O `t0 ritual daily-time open` imprime o digest, o status que o bot monta: merges desde a última daily, reviews parados há mais de 24h, bloqueios abertos e bloqueios sem dono. A daily trata só de dois assuntos: bloqueios e pedidos de review. Cada review parado ganha alguém que assume, e a skill registra `t0 log decision "review de <PR> (dono: <pessoa>)"`. Cada bloqueio ganha um dono.

Antes da daily, o Flow Steward aprova o PR em lote com os registros de passo do dia anterior.

## Daily do pod

Todo dia, logo depois da daily do time, por 30 a 45 minutos. Quando há spec para fechar, a daily pode virar uma sessão de mob (trabalho em grupo com o agente ao vivo) mais longa. O Bet Owner facilita, e o agente fica ao vivo na tela.

A daily do pod conta como trabalho. Nela, o pod (o grupo do time dono de um produto):

- valida ideias com um protótipo feito na hora (`prototype`), até chegar ao veredito;
- decide o que vira bet (`bet-new`), e o Bet Owner aprova o PR;
- afia uma ideia ou um spec (`grill`);
- escreve o spec em grupo (`bet-spec`) e corta os slices (`bet-slice`), as fatias verticais da bet, com um repo e um PR cada;
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

Toda semana, 20 minutos, com o time. O Harness Keeper facilita.

O `open` traz:

- os erros de agente que se repetiram na semana, ou seja, os Harness Items `open` com duas ocorrências ou mais (cada Harness Item registra uma classe de erro de agente);
- o orçamento de contexto: as linhas de `AGENTS.md` e os hooks, contra o teto de 20 em `harness/budget.md`;
- as skills sem uso há 4 semanas, candidatas a sunset (desligamento);
- os concepts do KB (os arquivos do KB, um por item) com `stale_after` vencido.

O time aceita ou recusa cada erro repetido. Um item aceito vai para a skill `harness-fix`, que abre um PR em draft no repo certo. Cada incidente da semana vira caso de eval. Se saiu versão nova do mattpocock-skills ou do pstack, o Harness Keeper lê o CHANGELOG e abre um Harness Item para o que vale portar.

A trava: o `t0 ritual harness-health close` recusa fechar enquanto algum item aceito estiver sem PR. Para destravar, o time abre os PRs que faltam. Desaceitar um item só para o close passar não é uma opção.

## Demo

A cada 2 semanas, junto com a iteração do ART, por 30 minutos, com o time. O Flow Steward facilita.

- Demo ao vivo do que foi para o ar, mais o painel de fluxo e de adoção.
- Bets encerradas: o estado `shipped` vem do `t0 bet ship` no último merge. Quando o time decide matar uma bet, usa `t0 log kill "<motivo>" --bet <BET>`. O kill fica numa branch do KB até o Bet Owner aprovar.
- Rodízio: o time combina quem assume Harness Keeper e Flow Steward nas próximas 2 semanas, e o `t0 ritual demo close` grava a troca.

## Retro

Uma vez por mês, 60 minutos, com o time. O Flow Steward facilita.

A pauta é como o time e a própria metodologia estão funcionando: o que atrapalha, que passo de processo cortar, o que mudar nas dailies e nos papéis. O critério é o de sempre: um passo só fica se protege algo concreto ou gera aprendizado. O Harness Keeper mostra o teto de hooks de `harness/budget.md`.

Quando a Retro muda a metodologia, ela abre um ADR (registro de decisão) por `t0 new adr`, com a mudança e quem decidiu. Quando não muda nada, a Retro fecha sem ADR.

## PI Planning e Sense & Respond do ART

Acontece quando o ART marcar e dura o que o ART definir. Do time, vai o Lead/AIVA. A pauta do time são as bets candidatas e os outcomes de adoção por produto. O registro traz as decisões do ART, cada uma com um dono do lado do time. A gravação só entra se o ART permitir e, nesse caso, passa pelo mesmo fluxo de transcrição.

## Interface com o ART

Por fora, o time segue o SAFe do ART. Por dentro, trabalha em builder pods. O AI-Native SAFe pede outcomes no PI em vez de features comprometidas. Os degraus de adoção (os passos de adoção de um produto: o time, depois squads piloto, depois o ART) já são outcomes, por isso a interface entre os dois lados fica fina.

| SAFe (AI-Native) | No t0 |
|---|---|
| AI-Native Team (3 a 7 pessoas) | 3 pods + Lead; o segundo revisor de Tier 2 (Tier é o nível de review do PR, de 0 a 2) pode vir de outro pod |
| Epic / tema | Idea promovida e outcome de PI |
| Feature / Story | Bet / Slice, espelhadas pelo `t0 jira sync` no CI |
| Iteração (2 semanas) | fluxo contínuo por dentro; Demo no fim de cada iteração do ART |
| PI Planning / PI Outcome Planning | compromisso com degraus de adoção, pisos de eval, SLO de review e DORA por produto; bets candidatas com apetite e risco entram como meio |
| Sense & Respond | registro da Demo e snapshot da quinzena como insumo; decisões do ART voltam como ADR ou Idea |
| Capacidades Product, Builder, Domain Expert, AI | Bet Owner; todo mundo; dev de squad chamado para a daily do pod; agentes com as skills do plugin |
| AI Value Architect | o Lead acumula |
| Capacidade / pontos | throughput de slices e cycle time; 1 ponto fixo por slice se exigirem |

Se o ART rodar SAFe clássico, a Demo alimenta a System Demo, as Retros e o Harness Health alimentam o I&A, e o PI Planning recebe bets candidatas além dos outcomes. A interface volta à mesa em quatro casos: mais de 3 pods no mesmo produto, a BU exigir pontos por PI, o ART pedir a cadência dele por dentro ou a agenda do Lead estourar.

## Conta de tempo

Tempo de cerimônia pura por pessoa, a cada 2 semanas:

| Ritual | Conta | Tempo |
|---|---|---|
| Daily do time | 10 min × 10 dias | 1h40 |
| Harness Health | 2 × 20 min | 40 min |
| Demo | 1 × 30 min | 30 min |
| Retro | metade de 60 min mensais | 30 min |
| Total | | cerca de 3h20 |

O Lead soma o PI Planning e o Sense & Respond, no ritmo do ART. A daily do pod fica fora da conta porque é trabalho: nela o pod prototipa, especifica e planeja.

## Transcrições

As dailies podem ser gravadas, com aviso a todos, para o agente extrair ideias e decisões. A Policy `transcript-retention` do KB define as regras:

- A gravação crua fica só em `~/.t0/inbox/`, na máquina de quem gravou. O hook impede que qualquer agente leia essa pasta.
- A redação (a remoção de dados sensíveis) é determinística e acontece antes de qualquer modelo. O `ritual <slug> close --transcript <arquivo>` chama `t0 transcript redact`, que roda o scanner de segredo e as regex de CPF, conta, e-mail e telefone. Depois, o agente faz uma passada para achar dado de cliente que a regex não pega. Se ele achar, o arquivo para ali, e a correção vai para o redator por um Harness Item.
- Qualquer pessoa pode pedir "fora do registro" para um trecho. O trecho sai inteiro, e o Transcript guarda só a contagem em `off_record_spans`. Ninguém tenta reconstruir ou resumir o que foi dito ali.
- Conversa 1:1 nunca é gravada nem processada.
- Até sair o aval de LGPD, tudo roda em dry-run: o `t0` redige e mostra o resultado, mas não persiste nada no KB. Quando o jurídico der o aval, um PR na Policy preenche `lgpd_signoff` e troca `persist` para `on`.
- Tudo o que o agente extrai da transcrição entra sem `verified` até alguém confirmar. O close não para para perguntar: ele lista cada item como não verificado e indica quem confirma.
- Retenção: o Transcript tem `stale_after` de 180 dias (PROPOSTA, pendente de validação com jurídico e LGPD). Quando o prazo vence, a transcrição é apagada e o Ritual Record continua no KB.

Trecho real de uma transcrição redigida do exemplo:

```
caio: Vi. Pegou três PRs com mais de dois dias. Um era do [REDIGIDO:EMAIL].

ana: Então segue? Cabe numa semana, um pod só, Tier 1.

[FORA DO REGISTRO: 1 trecho]
```
