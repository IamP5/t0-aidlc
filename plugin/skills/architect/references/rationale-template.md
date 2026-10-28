# Modelo da seção Design

É a seção `## Design` do `spec.md` da bet. Uma página. Títulos com só a primeira letra maiúscula, sem texto de enchimento. Troque cada nota em itálico pelo conteúdo real e apague a nota.

```markdown
## Design

### Problema

*Um parágrafo. O que queremos fazer e o que, no sistema atual ou nas restrições, deixa a forma pouco óbvia. Nomeie as restrições que a fundamentação achou (tipos existentes com que precisamos conversar, chamadores que não podem quebrar, invariantes que cruzam a nossa fronteira), com a citação de cada uma, para quem lê ver as mesmas restrições que você viu.*

### Uso (visão de quem chama)

*Escreva antes da forma. Mostre o README ou o quickstart que o consumidor lê, mais duas ou três chamadas reais no código dele: o que importa, o que chama, o que volta. A forma abaixo deriva deste uso, e os dois precisam bater. Quando divergirem, ajuste a forma ao uso.*

### Forma

*A arquitetura recomendada. Estruturas de dados primeiro, depois o caminho dos dados pelas assinaturas, num bloco de código com corpos `not implemented`. Nomeie as decisões que sustentam o desenho. Diga quais invariantes estão nos tipos, onde mora a validação e o que o sistema deliberadamente não faz. Julgue a profundidade da interface: que complexidade a superfície pública esconde, o que fica exposto a quem chama e por que a interface não é maior do que precisa. Cite o princípio por trás de cada decisão (por exemplo, "por boundary-discipline") sem reexplicar o princípio.*

### Decisão de síntese

*Vem da nota de síntese da `arena`. Qual candidato virou a base e por quê, o que foi enxertado de cada um dos outros, o que foi descartado e por quê. Inclua os modelos usados e o rótulo `same-family` quando a arena marcou.*

### Trade-offs aceitos

*Um bullet por trade-off, no formato "aceitamos X em troca de Y". Nomeie tudo que um leitor futuro poderia tomar por descuido, inclusive o que parece otimização ou simplificação prematura.*

### Alternativas consideradas

*Obrigatória. Pelo menos uma forma alternativa concreta, com uma linha sobre por que perdeu. Julgue cada alternativa pela profundidade da interface, além da simplicidade de implementar: que complexidade ela expõe a quem chama e qual ela esconde. Duas ou três quando o espaço de desenho tinha concorrentes de verdade. Uma basta quando as restrições forçaram a resposta, com a conclusão escrita como "era a única forma viável porque...". Evite listar sabores da mesma forma. Os outros candidatos da arena ficam na decisão de síntese; aqui entram as alternativas de desenho.*

### Perguntas em aberto e riscos

*O que você notou no esboço e o humano precisa pesar, e os riscos que valem aviso antes da implementação. Escreva como pergunta, para a resposta do humano ser a resolução.*

### ADR

*O ADR aberto com `t0 new adr`, quando a decisão é difícil de desfazer. Senão, "nenhum: a decisão é reversível porque ...".*

### Primeiro passo de implementação

*Uma frase. O primeiro slice ou a primeira costura que o `slice-build` vai atacar contra este desenho.*
```
