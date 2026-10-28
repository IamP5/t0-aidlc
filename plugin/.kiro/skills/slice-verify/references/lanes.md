# Briefs das duas raias

Cole o brief inteiro no prompt de cada subagente. Eles não têm outro acesso a este arquivo.

## Raia de padrões (subagente `standards-reviewer`)

Entradas que você passa:

- o comando de diff (`git diff <base>...HEAD`) e a lista de commits;
- a lista de arquivos de padrão do repo (passo 3 da skill);
- a linha de base de cheiros abaixo, inteira.

Brief:

> Revise o diff contra os padrões documentados do repo e contra a linha de base de cheiros. Relate, por arquivo e trecho: (a) cada ponto em que o diff viola um padrão documentado, citando o arquivo do padrão e a regra; (b) cada cheiro da linha de base que você encontrar, com o nome do cheiro e o trecho citado. Separe violação dura de julgamento: violação de padrão documentado pode ser dura, cheiro da linha de base é sempre julgamento, e padrão documentado do repo vence a linha de base. Pule o que o tooling já garante. Relate também cada erro de agente que você reconhecer (seção "Erros de agente"). Responda em pt-BR, em até 400 palavras.

### Linha de base de cheiros

Vale mesmo quando o repo não documenta nada. Duas regras: o padrão do repo vence (onde o repo endossa algo que a linha de base marcaria, suprima o cheiro), e cada cheiro é sempre um julgamento rotulado ("possível Feature Envy"), nunca uma violação dura. Cada item diz o que é e como corrigir.

- Nome misterioso: função, variável ou tipo cujo nome não diz o que faz ou guarda. Renomeie. Se não vem um nome honesto, o desenho está turvo.
- Código duplicado: a mesma forma de lógica em mais de um trecho ou arquivo da mudança. Extraia a forma comum e chame dos dois lados.
- Feature Envy: método que mexe mais nos dados de outro objeto que nos seus. Leve o método para junto dos dados.
- Data Clumps: os mesmos campos ou parâmetros sempre viajando juntos. Junte num tipo e passe o tipo.
- Obsessão por primitivo: primitivo ou string no lugar de um conceito de domínio que merece tipo próprio. Dê ao conceito um tipo pequeno.
- Switch repetido: o mesmo `switch` ou cascata de `if` sobre o mesmo tipo em vários lugares da mudança. Troque por polimorfismo ou por um mapa que os dois lugares compartilham.
- Cirurgia com espingarda: uma mudança lógica obriga edições espalhadas por muitos arquivos. Junte num módulo o que muda junto.
- Mudança divergente: um arquivo ou módulo editado por vários motivos sem relação. Separe para cada módulo mudar por um motivo.
- Generalidade especulativa: abstração, parâmetro ou gancho para necessidade que o spec não tem. Apague e volte ao simples até a necessidade aparecer.
- Cadeia de mensagens: navegação longa `a.b().c().d()` de que quem chama não deveria depender. Esconda o caminho atrás de um método no primeiro objeto.
- Intermediário: classe ou função que quase só repassa. Corte e chame o alvo direto.
- Herança recusada: subclasse ou implementação que ignora ou sobrescreve quase tudo que herda. Troque herança por composição.

## Raia de spec (subagente `spec-reviewer`)

Entradas que você passa:

- o comando de diff e a lista de commits;
- o caminho no KB e o conteúdo do slice e do spec (na trilha rápida, só o slice com "atual, esperado, o que não muda");
- a seção Design do spec, quando existir.

Brief:

> Revise o diff contra o slice e o spec. Relate: (a) critérios de aceite pedidos que faltam ou estão parciais; (b) comportamento no diff que ninguém pediu (escopo a mais), incluindo o que o spec põe em "Fora de escopo" ou o slice põe em "o que não muda"; (c) requisitos que parecem implementados mas cuja implementação parece errada; (d) desvios da seção Design sem justificativa no PR; (e) testes fora das costuras combinadas, ou costura combinada sem teste. Cite a linha do spec ou do slice em cada achado. Relate também cada erro de agente que você reconhecer (seção "Erros de agente"). Responda em pt-BR, em até 400 palavras.

## Erros de agente

Um erro de agente é um achado cuja causa é o comportamento do agente que construiu: ele tinha a regra ou o fato à mão e errou mesmo assim. Os dois subagentes marcam cada um com uma linha `ERRO-DE-AGENTE: <padrão em poucas palavras>`. Exemplos de padrão:

- inventou API, flag ou chamador que não existe;
- teste tautológico ou acoplado à implementação;
- verificação afirmada sem saída que prove;
- ignorou um padrão documentado do repo;
- mexeu em arquivo fora do escopo do slice;
- linha da trilha sem evidência que resolva.
