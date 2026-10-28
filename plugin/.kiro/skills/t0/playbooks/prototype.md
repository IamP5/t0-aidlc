# Playbook prototype

Você responde pela decisão de desenho. O protótipo é um instrumento descartável, e a construção de verdade segue `playbooks/feature.md` dentro de um slice. Este playbook decide um fork que apareceu no meio do trabalho (layout, interação, comportamento, tempo) observando no lugar de perguntar. Para testar uma Idea do KB e gravar o veredito, use `playbooks/ideia.md` com a skill `prototype`.

Aqui a menor mudança e a barra de verificação se invertem. Velocidade vale mais que acabamento, qualidade de código não conta e não há planejamento. O rigor está em escolher o desenho certo gastando pouco. Proponha variações que ninguém pediu, jogue fora uma abordagem e tente outra.

1. Delimite a decisão que o protótipo existe para tomar: qual layout, qual interação, qual densidade, ou, num fork empírico, qual comportamento, tempo ou abordagem. Sem decisão, sem protótipo: volte para `playbooks/feature.md`.
2. Com o espaço de desenho aberto, junte referências (arte prévia no repo, specs e ADRs no KB) e, quando a escolha for de preferência, deixe a pessoa escolher direções antes de construir. Direção já definida fica com `pular: direção definida`.
3. Construa descartável num diretório de rascunho fora do repo, ou numa worktree que nunca recebe push. Decisão visual: HTML, CSS e JS puros, ou a stack mais leve que renderiza a ideia. Decisão de comportamento ou tempo: o menor script que exercita a pergunta. Sem framework de produção, sem teste e sem abstração.
4. Comparando alternativas, ponha todas atrás de um seletor (botões ou tecla), cada variante com rótulo (`exhaust-the-design-space`).
5. Verifique na superfície certa. Decisão visual: screenshot de cada variante e a interação dirigida. Decisão de comportamento ou tempo: log do tempo, saída impressa ou render observado. Aqui a observação faz o papel do teste.
6. Apresente alternativas, tradeoffs e uma recomendação. A saída é a decisão mais o artefato descartável. Leve a direção escolhida para `playbooks/feature.md` ou para o `architect`. Decisão difícil de desfazer vira ADR por `t0 new adr`.

Na resposta: as variantes, a evidência (screenshots ou a saída observada), os tradeoffs, a recomendação e o caminho do rascunho. Diga com todas as letras que o protótipo é descartável.
