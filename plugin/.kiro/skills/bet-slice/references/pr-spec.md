# Corpo do PR de spec e slices

Preencha em pt-BR. Corte a linha do Lead quando a bet não é Tier 2.

```markdown
## Decisão de spec

Aprovar este PR é a decisão de spec da <BET-NNN> (<título>).

Aprova:
- o Bet Owner do <pod>
- o Lead, porque é Tier 2

## Spec

`products/<pod>/bets/<BET-NNN>/spec.md`: <n> histórias de usuário, <n> critérios de aceite, Tier <n>.

Seams de teste: <seams>.

Marcadores `[PRECISA ESCLARECER]` abertos: <0 | lista>.

## Slices

| # | Slice | Repo | Tier | Bloqueado por |
|---|---|---|---|---|
| 01 | <título> | <repo> | <n> | nenhum |
| 02 | <título> | <repo> | <n> | 01 |

Fronteira (começam logo depois do merge): <01, ...>.

## Depois do merge

O CI espelha a bet e os slices no Jira. Os slices da fronteira ficam prontos para a skill `slice-build`.
```
