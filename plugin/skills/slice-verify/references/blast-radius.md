# Raio de impacto (Tier 2)

Ache o que a mudança quebra em outro lugar, fora do diff, antes do merge. O trabalho é a quebra que o grep não mostra. A lista de chamadores o grep dá em um segundo.

## Desconfie do próprio texto

Um texto de raio de impacto que soa certo não vale nada: ele convence sendo verdade ou não. Ache o fato, ou os dois fatos, de que a segurança da mudança depende, e prove rodando código.

### Escada de prova

Para cada fato de que a segurança depende, desça na escada até onde for barato e diga onde parou.

1. Você disse. Sozinho, não vale nada.
2. Você apontou a linha. Um `arquivo:linha` real, ou o código-fonte da própria biblioteca.
3. Você mostrou que o caso ruim não acontece. Seguiu a falha passo a passo e ela não chega.
4. Você rodou. Um script ou teste que chama o código real e falha alto se você estiver errado.
5. Você reproduziu no app rodando, pelo `verify-<app>`.

O degrau 4 costuma ser um script pequeno que importa a mesma biblioteca que o app usa e chama a função exata que preocupa.

## Passos

1. Leia a mudança: o diff, os símbolos que ela cria, muda e apaga, e o que ela passa a fazer de diferente, inclusive o que o diff não deixa explícito. Puxe o contexto com `gh pr view <PR> --json title,body,commits`, `git log <base>..HEAD` e `git log -L` ou `git blame` nos trechos tocados.
2. Ache o fato de que ela depende para ser segura. Quase toda mudança que parece arriscada é segura por causa de um fato só, como "esta chamada só descarta entradas de cache já mortas e nada mais". Ache esse fato. Se ele vale, a maior parte dos casos arriscados cai junto. Gaste o tempo aqui, no fato, em vez de numa lista longa de talvezes.
3. Olhe onde o grep para. Leia o código-fonte da biblioteca chamada, confira a versão fixada e qualquer patch local. Entenda quando as coisas rodam: microtasks, desmontagem, ordem de inicialização, retry. Siga o que a busca por símbolo perde: o JSON que uma API devolve, uma coluna de banco, um formato de wire, outra linguagem lendo os mesmos bytes, uma feature flag, código três saltos adiante, os outros repos da bet.
4. Seja honesto com cada risco. Dê uma chance real de acontecer e um custo real se acontecer. Fique com os riscos confirmados. Liste à parte os que você conferiu e descartou. Cite `arquivo:linha` real. Uma busca que não acha nada também é resposta. Nunca invente chamador nem API.
5. Prove o fato. Escreva um script ou teste que roda o código real, rode e cole o que aconteceu. Guarde o script fora do diff do PR (no rascunho da sessão) e cole o conteúdo no comentário.

## O que entra no comentário

- O que a mudança faz, inclusive a parte que não é óbvia.
- O fato de que a segurança depende: o fato, o degrau em que você chegou e a prova. Sem prova, escreva "não provado".
- Riscos: como quebra, `arquivo:linha`, chance e custo, como conferir. Cole a prova dos que importam.
- Descartados: o que você conferiu e por que está ok.
- Antes do merge: o teste ou a reprodução mais barata que pega o bug real, com o script que você escreveu.

Tire do texto qualquer dado privado antes de postar.
