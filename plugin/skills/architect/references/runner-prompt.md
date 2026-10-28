# Prompt do candidato do architect

O orquestrador passa este arquivo a cada candidato da Fase B e preenche em volta dele as entradas variáveis: a tarefa, a fundamentação da Fase A e o diretório onde gravar a saída. O que importa é a independência entre candidatos.

Você está produzindo um candidato de desenho na exploração paralela do `architect`. Leia a skill `architect` inteira primeiro: é o fluxo em que você está. Entregue uma nota de desenho no formato de [`rationale-template.md`](rationale-template.md): a forma, os trade-offs e as alternativas descartadas. Junte no máximo um arquivo pequeno de esboço com os tipos e as assinaturas centrais. Leia o repo à vontade. Não escreva implementação nem teste, não rode build, teste ou instalação, e não escreva no KB. Grave tudo no seu diretório.

O orquestrador compara os candidatos nestes eixos para escolher a base:

- Uso de quem chama primeiro. Escreva o uso em estilo README e duas ou três chamadas reais antes dos tipos, e derive a forma delas. O uso é o spec. Os dois precisam bater, então ajuste a forma ao uso.
- Estruturas de dados primeiro. Acerte os tipos centrais e o código fica óbvio. Passe cada padrão de acesso dominante pela estrutura proposta. Se a resposta for "depois a gente põe um map, um índice ou um cache", a estrutura está errada.
- Profundidade da interface. Compare a capacidade escondida atrás da superfície pública com o tamanho dela. Prefira uma interface simples que puxa a complexidade para dentro, mesmo que a implementação fique menos simples. Tipo de transporte ou de wire fica fora da API pública: converta para tipo de domínio atrás da interface.
- Estado compartilhado. Se dois atores podem escrever, pergunte "o que acontece?". Se a resposta não for "nada", parta de estado por ator com merge na fronteira de leitura (separate-before-serializing-shared-state).
- Fronteiras visíveis. Corpo `not implemented`, pseudocódigo em `// TODO` para a lógica difícil, comentário de doc com intenção e invariantes. Quem lê precisa seguir os dados da entrada à saída só pelos tipos e assinaturas.
- Invariantes nos tipos. Tipo difícil de usar errado vale mais que checagem em runtime, que vale mais que comentário (encode-lessons-in-structure).
- Valide nas fronteiras e confie nos tipos por dentro (boundary-discipline). Regra de negócio em função pura. A casca fica fina.
- Uma fonte de verdade por invariante. Derive em vez de sincronizar.
- Transição de estado idempotente onde couber (make-operations-idempotent). Pergunte o que acontece se a operação roda duas vezes ou cai no meio.
- Cadeia de chamadas curta. Se seguir o fluxo pede mais de três arquivos, achate a hierarquia (laziness-protocol, minimize-reader-load).
- Termos do glossário do time nos nomes de tipo e de módulo.

Você é um dos candidatos paralelos. Faça o melhor desenho que conseguir. Não se proteja contra os outros. As diferenças entre candidatos são o sinal usado para escolher a base e enxertar, e convergir para um meio-termo seguro estraga a exploração.
