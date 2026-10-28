---
name: grill
description: "Entrevista o usuário em rodadas sobre uma ideia, bet ou spec até fechar cada ramo das decisões, com uma resposta recomendada por pergunta. Grava termos no glossário do KB e propõe ADR via `t0 new adr`. Use para \"me grelha\", estressar um plano ou afiar um spec."
metadata:
  credits: "Baseada em MP grilling + domain-modeling (mattpocock-skills 1.3.1, MIT)"
---

# grill

Entreviste o usuário sem dó até vocês dois chegarem ao mesmo entendimento de uma ideia, bet ou spec. Ao mesmo tempo, afie a linguagem do domínio: termo resolvido vai para o glossário do KB na hora, e decisão que merece registro vira ADR.

## 1. Carregue o que já existe

Antes da primeira rodada, junte os fatos. Eles são trabalho seu e ficam com você: o usuário só responde decisões.

- O assunto: `t0 bet detect` e `t0 kb get <BET|IDEA>`, mais o `spec.md` da bet quando já existe.
- O glossário: `t0 kb find --type "Glossary Term"`.
- Os ADRs da área: `t0 kb find --type ADR --product <pod>` e os de `methodology/adr/`.
- O código, quando a conversa toca nele: leia nos repos do workspace.

## 2. Trabalhe a árvore em rodadas

Mapeie o assunto como uma árvore de decisões: cada decisão abre as decisões que dependem dela. A fronteira é o conjunto de decisões cujos pré-requisitos já estão fechados, ou seja, as perguntas que dá para fazer agora sem chutar respostas que você ainda não ouviu.

Pergunte a fronteira inteira numa rodada curta: no máximo 3 linhas de contexto, depois as perguntas numeradas, cada uma com sua resposta recomendada. Espere o usuário responder antes da próxima rodada. Formato:

```
**P1. <título da pergunta>**
<corpo da pergunta, com as opções quando houver>

Recomendação: <sua resposta>

---

**P2. <título da pergunta>**
<corpo>

Recomendação: <sua resposta>
```

Escreva cada pergunta de um jeito que "sim" aceite a recomendação.

Cada rodada respondida muda a árvore: decisões fechadas empurram a fronteira e destravam perguntas que dependiam delas. Recalcule a fronteira e faça a próxima rodada. Pergunta que depende de outra ainda aberta na mesma rodada fica para depois.

Quando uma pergunta precisa de um fato do ambiente (KB, código, CI, histórico do git), despache um subagente `t0-agent` para buscar. Só as perguntas que dependem daquele fato esperam a resposta dele; o resto da fronteira vai agora. Decisão é do usuário: ponha cada uma para ele e espere.

A sessão acaba quando a fronteira está vazia: todos os ramos visitados e nada assumido em silêncio. Só aja sobre o resultado depois que o usuário confirmar que vocês chegaram ao mesmo entendimento. Ramo que o usuário preferiu adiar fica registrado como `[PRECISA ESCLARECER: <pergunta>]`.

## 3. Afie a linguagem durante a sessão

- Confronte com o glossário. Quando o usuário usa um termo que briga com o glossário, aponte na hora: "O glossário define review parado como X, mas você parece querer dizer Y. Qual dos dois?"
- Afie termo vago. Quando um termo está sobrecarregado, proponha o canônico: "Você diz 'conta': é o Cliente ou o Usuário? São coisas diferentes."
- Teste com cenários concretos. Invente casos de borda que obriguem o usuário a dizer onde um conceito termina e o outro começa.
- Confira com o código. Quando o usuário diz como algo funciona, veja se o código concorda e mostre a contradição quando houver.

## 4. Grave termos no glossário

Quando um termo se resolve, grave ali mesmo, um por vez. O glossário do KB tem um arquivo por termo em `glossary/<slug>.md`, bilíngue (pt-BR e inglês). Leia `references/glossario.md` antes do primeiro termo da sessão: lá estão o formato e as regras.

Onde gravar:

- com bet ativa, no clone do KB, na branch da bet (`bet/<BET>/...`). Commite cada termo; ele chega ao `main` no PR da bet;
- sem bet (grill de uma ideia solta), guarde a lista e mostre no fechamento. A skill `bet-new` ou a `bet-spec` grava esses termos quando abrir a branch da bet.

Para mudar um termo que já existe, edite o arquivo dele. Os arquivos derivados do KB (`index.md`, `log.md`) ficam com o `kb-render`.

## 5. Proponha ADR com parcimônia

Ofereça um ADR só quando as três condições valem:

1. difícil de desfazer: mudar de ideia depois custa caro;
2. surpreendente sem contexto: quem ler depois vai perguntar "por que fizeram assim?";
3. fruto de um trade-off real: havia alternativas de verdade e vocês escolheram uma por motivos específicos.

Faltou uma, pule o ADR. Com o ok do usuário, rode `t0 new adr --dry-run`, mostre o plano e rode sem `--dry-run`. O `t0` numera o ADR e o grava como `proposed`, em `products/<pod>/adr/` quando a decisão é do produto e em `methodology/adr/` quando é da metodologia. O corpo segue `references/adr.md`. Quem aceita o ADR é o review do PR.

## 6. Feche

Responda em pt-BR com:

- as decisões fechadas, uma linha cada;
- os termos gravados (ou pendentes, sem bet) e os ADRs propostos, com link;
- os `[PRECISA ESCLARECER]` que ficaram;
- o próximo passo: a skill `bet-new` quando o assunto era uma ideia, a `bet-spec` quando era uma bet ativa.

Com bet ativa, registre cada decisão fechada com `t0 log decision "<decisão>" --bet <BET>`.
