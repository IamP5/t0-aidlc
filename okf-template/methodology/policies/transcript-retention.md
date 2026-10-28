---
type: Policy
title: "Retenção de transcrições"
description: "Por quanto tempo uma transcrição redigida fica no KB, e o dry-run que vale até o aval de LGPD."
uid: policy-transcript-retention
owner: role:lead
tags: [policy, transcricao, lgpd, retencao]
state: proposed
status: draft
stale_after: 2027-01-28T00:00:00-03:00
generated: { by: claude-code/opus-5.5, at: 2026-10-28T10:00:00-03:00 }
persist: dry-run
lgpd_signoff: null
thresholds:
  retention: P180D
---

# Retenção de transcrições

Enquanto `lgpd_signoff` estiver vazio, `persist` fica em `dry-run`: o `t0 transcript redact` e o `t0 ritual <slug> close --transcript` redigem e mostram o resultado, mas não gravam nada no KB. Quando o jurídico der o aval, o PR desta Policy preenche `lgpd_signoff` com quem assinou e a data, e troca `persist` para `on`. Fonte: [metodologia §4.3](/methodology/methodology.md).

## Regras

- A transcrição bruta mora só em `~/.t0/inbox/` na máquina de quem gravou. O hook bloqueia agente de ler ali.
- A redação é determinística e vem antes de qualquer modelo: scanner de segredo e regex de CPF, conta, e-mail e telefone. Depois o agente faz uma passada para dado de cliente.
- Qualquer pessoa pode pedir "fora do registro" para um trecho. O trecho sai inteiro e o Transcript guarda só a contagem em `off_record_spans`.
- 1:1 nunca é gravado.
- Toda Transcript tem `stale_after` de 180 dias depois do ritual (PROPOSTA, pendente de validação com jurídico e LGPD). Vencido o prazo, a transcrição é apagada e o Ritual Record fica.
- Tudo que o agente extrai de uma transcrição entra sem `verified` até alguém confirmar.
