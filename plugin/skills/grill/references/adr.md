# Corpo do ADR

O `t0 new adr` cria o arquivo com número e frontmatter (`number`, `deciders[]`, `state: proposed`). Você escreve o corpo em pt-BR:

```markdown
# <Título curto da decisão>

<1 a 3 frases: o contexto, o que foi decidido e por quê.>
```

Um parágrafo basta. O valor está em registrar que a decisão existe e por quê.

Seções opcionais, só quando acrescentam algo:

- `## Opções consideradas`, quando vale lembrar as alternativas rejeitadas;
- `## Consequências`, quando há efeito que ninguém deduz sozinho.

## O que costuma merecer ADR

- Forma da arquitetura ("o modelo de escrita é event-sourced e a leitura é projetada no Postgres").
- Padrão de integração entre contextos ("PACO e Portal conversam por evento, sem HTTP síncrono").
- Tecnologia com lock-in: banco, fila, provedor de auth, alvo de deploy. Biblioteca comum fica de fora.
- Decisão de fronteira e escopo, incluindo os "nãos" explícitos.
- Desvio deliberado do caminho óbvio, para o próximo engenheiro não "consertar" o que foi de propósito.
- Restrição invisível no código: exigência do banco, contrato com parceiro, compliance.
- Alternativa rejeitada por motivo sutil, para ela não voltar em seis meses.
