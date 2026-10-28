# Corpo do PR da aposta

Preencha em pt-BR. "Quem aprova" vem do `t0 gate aposta <BET> --dry-run`.

```markdown
## Aposta

<BET-NNN>: <título>. Nasce da <IDEA-NNNN>.

Aprovar este PR é a decisão de aposta.

## Quem aprova

- <aprovadores que o gate listou>
- <quando Tier 2: "Tier 2 porque toca <superfície pública>, por isso o Lead também aprova">

Os campos abaixo são propostos. Ajuste aqui no PR o que discordar.

## A bet

- Trilha: <rapida | bet>
- Apetite: <P1D | P1W | P2W>
- Tier: <0 | 1 | 2>
- Pods: <pods>
- Hipótese: <se fizermos X, Y acontece para Z>
- Métrica de sucesso: <como saber que deu certo>
- Critério de kill: <o que faz parar>
- Protótipo: <veredito e ref | não houve>

## Fora de escopo

- <item>

## Depois do merge

<Na rápida: o slice `01-<slug>` fica `ready` para a skill `slice-build`. Na bet: a skill `bet-spec` escreve o spec.>
```
