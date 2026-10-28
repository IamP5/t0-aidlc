---
type: Ritual
title: "PI Planning e Sense & Respond"
description: "Eventos do ART em que o Lead/AIVA leva bets candidatas e outcomes de adoção, e traz as decisões do ART de volta como ADR ou Idea."
uid: ritual-pi
owner: role:lead
tags: [ritual]
generated: { by: claude-code/opus-5.5, at: 2026-10-28T10:00:00-03:00 }
cadence: "external:art"
duration: P2D
facilitator: role:lead
participants: [role:lead]
command: "t0 ritual pi open|close"
recorded: true
transcribable: false
inputs:
  - { id: adocao, source: "kb:Adoption Report since=last-ritual", desc: "degraus e números de adoção por produto" }
  - { id: bets-candidatas, source: "kb:Idea state=prototyped", desc: "ideias com veredito segue que podem virar bet" }
  - { id: demos, source: "kb:Ritual Record ritual=ritual-demo since=last-ritual", desc: "registros das Demos do PI" }
outputs:
  - /rituals/pi/
  - /ideas/
state: active
status: stable
stale_after: 2027-04-28T00:00:00-03:00
---

# PI Planning e Sense & Respond

Quando o ART marcar, com a duração que o ART definir. A `duration` de 2 dias é só um padrão (não verificado). Vai o Lead/AIVA.

## O que acontece

O Lead leva as bets candidatas e os outcomes de adoção. Os degraus de adoção já são outcomes, então a interface com o SAFe fica fina.

## Saída no KB

Um registro com as decisões do ART, feito a partir da pauta ou da gravação, se o ART permitir. As decisões voltam como ADR ou Idea.
