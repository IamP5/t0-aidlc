---
name: ritual
description: "Abre e fecha os rituais do time (daily-time, daily-pod, harness-health, demo, retro, pi) com `t0 ritual <slug> open|close` e grava o Ritual Record. Use para conduzir um ritual, registrar decisões e donos ou extrair ideias de uma gravação, sempre redigida antes."
---

# ritual

Você conduz um ritual junto com quem facilita. O `t0` monta a pauta e grava o registro. Você mostra a pauta, segura o foco do ritual, anota decisões com dono e fecha. Ninguém escreve ata à mão.

## Os seis rituais

| Slug | Quando | Duração | Facilita | Trava do close |
|---|---|---|---|---|
| `daily-time` | todo dia | 10 min | Flow Steward | nenhuma |
| `daily-pod` | todo dia, logo depois | 30 a 45 min | Bet Owner do pod | nenhuma |
| `harness-health` | toda semana | 20 min | Harness Keeper | recusa se um Harness Item aceito não tem PR |
| `demo` | a cada 2 semanas, com a iteração do ART | 30 min | Flow Steward | grava o rodízio |
| `retro` | uma vez por mês | 60 min | Flow Steward | ADR só se a metodologia muda |
| `pi` | quando o ART marcar | do ART | Lead/AIVA | nenhuma |

Antes do `open`, leia a seção do slug em [references/rituais.md](references/rituais.md). Ela traz o que acontece no ritual, o que você faz ao vivo e o que vai para o KB.

Status de trabalho quem dá é o bot, no digest da `daily-time`. Quando alguém começar a dar status em qualquer ritual, aponte para o digest e volte para a pauta.

## Passos

### 1. Abrir

1. Confirme o slug e, na `daily-pod`, o pod (`dev-tooling`, `paco` ou `portal-metricas`).
2. Rode `t0 ritual <slug> open`.
3. Mostre a pauta que o comando imprimiu, em pt-BR, sem reescrever os números. Se o comando recusar, mostre a recusa e pare. Recusa se resolve na causa, nunca contornando o comando.

O passo termina quando a pauta impressa pelo `t0` está na tela de quem facilita.

### 2. Conduzir

Siga a seção do slug em [references/rituais.md](references/rituais.md). Durante o ritual, registre pelo `t0`, na hora em que a coisa é dita:

- decisão: `t0 log decision "<texto> (dono: <pessoa>, prazo: <data>)"`, com `--bet` ou `--story` quando a decisão é de uma bet ou de um slice;
- bloqueio: `t0 log blocker "<texto> (dono: <pessoa>)"`. Bloqueio que ninguém pegou entra como `(dono: a definir)`, sem parar para perguntar: a próxima `daily-time` lista os bloqueios sem dono;
- ideia nova: siga para a skill `idea-capture`;
- kill de bet: `t0 log kill "<motivo>" --bet <BET>`, só quando o Bet Owner disse que mata.

Toda decisão tem dono. Se ninguém assumiu e a decisão cabe claramente num papel, ponha o papel como dono e diga isso numa linha: Harness Health é `role:harness-keeper`, fluxo é `role:flow-steward`, uma bet é o Bet Owner dela, a metodologia é `role:lead`. Pergunte só quando nenhum papel serve. Mudança de metodologia leva também um ADR por `t0 new adr`.

As decisões humanas (aposta, spec, degrau) acontecem na aprovação do PR. No ritual, você abre ou mostra o PR e quem decide aprova lá. Nunca registre uma aposta ou um spec como aprovado no ritual.

### 3. Fechar

1. Se houve gravação, faça a seção "Transcrição" abaixo antes de tudo.
2. Rode `t0 ritual <slug> close`, com `--transcript <arquivo>` quando houve gravação e `--dry-run` enquanto a Policy `transcript-retention` não registrar o aval de LGPD.
3. Mostre o `Plan` que o comando imprimiu: o Ritual Record, os PRs de decisão que ele abre e o que ficou bloqueado.
4. Se o close recusou, diga em pt-BR o que falta, quem resolve, e pare. As recusas de cada ritual estão em [references/rituais.md](references/rituais.md).

O passo termina quando o `close` passou e o `Plan` está na tela, ou quando a recusa e o dono de cada pendência estão ditos.

## Transcrição

As dailies podem ser gravadas, com aviso a todos. A gravação crua fica em `~/.t0/inbox/` e você nunca lê esse diretório: nada de `cat`, `ls`, `cp`, `grep` ou ferramenta de leitura ali. Você só passa o caminho para o `t0`.

1. Recuse gravação de 1:1. Uma conversa 1:1 nunca é gravada nem processada, mesmo que alguém mande o arquivo. Diga isso e siga sem transcrição.
2. Rode `t0 transcript redact <arquivo> --dry-run`. A redação é determinística e vem antes de qualquer modelo: scanner de segredo e regex de CPF, conta, e-mail e telefone. Trechos marcados "fora do registro" saem inteiros, e o Transcript guarda só a contagem em `off_record_spans`.
3. Leia só o texto redigido que o comando devolveu. Faça uma passada atrás de dado de cliente que a regex não pega (nome de cliente, número de contrato, valor de operação). Achou, pare e avise quem facilita: a correção vai no redator, por um Harness Item, e o arquivo não segue.
4. Sobre trecho fora do registro, fale só da contagem. Nunca tente reconstruir, resumir ou adivinhar o que foi dito ali. Se o texto redigido ainda tiver um trecho que alguém pediu para tirar, pare e trate como falha do redator, igual ao passo 3.
5. Extraia ideias e decisões do texto redigido. Ideia vai pela skill `idea-capture` com origem `transcript`. Decisão vai por `t0 log decision`. Decisão difícil de desfazer vira ADR por `t0 new adr`.
6. Tudo que você extraiu entra sem `verified`. Não peça confirmação antes do close: feche o ritual e, no fechamento, liste cada item extraído como não verificado, com quem precisa confirmar. Você só para e pergunta quando o redator falha (passos 3 e 4).

Enquanto a Policy `transcript-retention` não registrar o aval de LGPD, rode `redact` e `close` com `--dry-run`: o `t0` redige e não persiste. Diga isso no fechamento.

## Regras

- Escrita no KB só pelo `t0` (`t0 ritual`, `t0 log`, `t0 new`, `t0 transcript redact`). Nunca edite `index.md`, `log.md`, `changeset.md` nem chaves derivadas.
- Todo PR que sair do ritual é draft. Nunca marque como pronto e nunca faça merge.
- Jira só o CI mexe. Bloqueio e decisão vão para o KB, e o espelho no Jira vem depois do merge.
- Fale com o time em pt-BR.
