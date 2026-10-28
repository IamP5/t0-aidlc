# Princípios

Os 19 princípios do t0, um parágrafo cada, escritos a partir dos princípios do pstack 0.15.25 (MIT). Leia o parágrafo inteiro antes de citar um princípio na resposta.

## Base

### laziness-protocol

Vale ao refatorar, ao dimensionar um diff ou quando dá vontade de criar abstração, camada ou repasse de sinal. Junte as decisões: a mesma escolha mora num lugar só, e o resultado passa adiante como um flag simples. Faça a menor mudança que resolve o problema. Menos linhas ganham de boilerplate "elegante".

### foundational-thinking

Vale antes de escrever lógica. Acerte o formato dos dados primeiro: defina os tipos centrais cedo, trace cada padrão de acesso e escolha a estrutura que serve os caminhos dominantes. Aplique DRY à estrutura e aceite linhas parecidas, porque três comandos parecidos ainda ganham de uma abstração prematura. Antes de dividir estado entre atores, pergunte o que acontece se outro ator mexer ao mesmo tempo; se a resposta for diferente de "nada", isole. Andaime vem primeiro: o que ajuda toda fase seguinte (CI, lint, infraestrutura de teste, tipos compartilhados) entra antes da feature. Cada incremento entrega uma abstração coerente ou aprofunda uma que já existe.

### subtract-before-you-add

Vale ao sequenciar um acréscimo, uma refatoração ou uma reescrita. Tire complexidade primeiro e construa depois. Remoção vem antes de construção, corte vem antes de polimento, e o desenho serve o uso observado em vez da borda especulativa. Validador, parser ou guarda só entram quando o spec pede. Referência sem conteúdo novo é apagada em vez de virar stub. Deixe o desenho um pouco mais simples e mais capaz, atrás da mesma superfície ou de uma menor.

### minimize-reader-load

Vale ao revisar ou moldar código difícil de seguir. Manutenção é o trabalho que o leitor faz para entender. Conte dois eixos independentes: camadas entre a pergunta e a resposta, e estado escondido ou mutável que o leitor precisa carregar na cabeça. Junte wrapper de um chamador só, adaptador sem segunda implementação e camada que só repassa. Prefira função pura, variável local a campo, campo a estado de módulo, e derive em vez de sincronizar. Nomeie o invariante na fronteira, uma vez. O teste: um leitor novo responde "de onde vem X?" e "o que muda X?" em menos de 30 segundos.

### build-the-lever

Vale em todo trabalho que não é trivial: edição, migração, análise, check. Construa a ferramenta que faz ou prova o trabalho (codemod, script, gerador, ou uma skill que os subagentes seguem) no lugar de fazer à mão. A ferramenta é o artefato que o revisor lê e roda de novo. Faça a primeira unidade à mão para aprender a receita, depois escreva a ferramenta e prove rodando-a nessa unidade. Uma alavanca determinística ganha de fan-out. Citou o princípio e não há codemod, script, gerador ou skill no diff: o princípio não foi aplicado. A barra é trivialidade, e repetição sozinha não decide.

## Arquitetura

### model-the-domain

Vale ao escrever lógica com estado, ou quando o código ramifica muito ou repete uma suposição de formato em vários arquivos. Codifique o domínio numa estrutura: máquina de estados no lugar de booleanos espalhados, modelo tipado no lugar de parâmetros soltos, tabela, registro ou união discriminada no lugar de ramos espalhados, reducer no lugar de mutação avulsa, módulo organizado por conhecimento de domínio em vez de por sequência (carregar, validar, transformar, salvar). Código chato fica quando o formato é claro, local e não vai crescer. O sinal de que você pulou este passo é uma feature nova que acrescenta mais um ramo num if/else, ou um segundo booleano que precisa ficar em sincronia com o primeiro.

### boundary-discipline

Vale ao ligar validação, tratamento de erro ou adaptador de framework. Validação, estreitamento de tipo e tratamento de erro ficam nas fronteiras do sistema: argumento de CLI, arquivo de config, API externa, rede. Por dentro, dados tipados, propagação de erro e confiança nos tipos, sem revalidar. Regra de negócio mora em função pura, sem dependência de framework, e a casca fica fina e mecânica. Pela fronteira passam conceitos de domínio, e os tipos de transporte e de armazenamento ficam do lado de dentro. Pergunte: este dado está cruzando uma fronteira agora? Se não está, a validação sobra.

### type-system-discipline

Vale ao desenhar tipos ou uma assinatura em linguagem tipada. Faça o compilador recusar estado impossível, primitivo trocado e variante sem tratamento. Dê tipo próprio a primitivo com significado: `UserId` e `OrderId` são strings por baixo e mesmo assim não se trocam. Valide uma vez na criação e confie no tipo depois. Dado externo (JSON, payload, argumento, variável de ambiente, linha de banco) fica sem tipo até passar por um parse na fronteira. Quando um schema é dono do formato (OpenAPI, protobuf, migration), derive o tipo dele.

### make-operations-idempotent

Vale ao desenhar comandos, passos de ciclo de vida ou loops que rodam no meio de crash, restart e retry. A operação converge para o mesmo estado final, não importa quantas vezes rode nem onde a anterior parou. Derive cada passo do estado que existe: leia, compare com a meta e aplique só a diferença. Tudo que uma execução deixa para trás (lock, arquivo temporário, registro pela metade, job reservado) precisa ser reconhecível como velho pela próxima, por uma evidência que vale em qualquer ponto onde a anterior possa ter parado. O teste: o que acontece se rodar duas vezes seguidas, e se a anterior caiu em cada ponto possível?

### separate-before-serializing-shared-state

Vale quando atores concorrentes podem escrever no mesmo arquivo, branch, chave ou objeto. Primeiro pergunte se eles precisam do mesmo objeto mutável. Por padrão, elimine o alvo compartilhado: cada ator escreve no seu arquivo, chave ou branch, e a junção acontece na leitura. A raia de registros do KB funciona assim, com um arquivo por passo. Só quando um escritor único é invariante real, serialize pela estrutura: lockfile, fases sequenciais, dono exclusivo ou compare-and-swap. Instrução e convenção não controlam concorrência.

## Verificação

### prove-it-works

Vale depois de uma tarefa, antes de dizer que acabou. Verifique contra a coisa real: o processo vivo, o valor lido de verdade, o app rodando. Proxy, autorrelato de subagente e "compila" ficam de fora como prova. Quando a verificação falha, suspeite primeiro do método de observação. A prova mais forte é um script determinístico que refaz a comparação; rode e guarde a saída como artefato que o revisor roda de novo. No t0, a superfície é o `verify-<app>` do repo, e a evidência vai no PR e na trilha `.audit/<KEY>.tsv`.

### fix-root-causes

Vale ao depurar. Corrija a falha onde ela nasce. O sintoma é só o lugar onde ela ficou visível. Reproduza primeiro. Pergunte "por quê" a cada passo até a resposta ser uma decisão errada no código. Travou, instrumente: leia o erro e o estado reais. Pergunte se o estado que disparou o sintoma é legítimo. Se é, o código que quebrou nele é a causa, e tratar o estado ali é o fix. Se o estado nunca deveria existir, ache quem o produziu; uma guarda no ponto da quebra só esconde o bug. Falha que só aparece depois de restart aponta para estado persistido. Procure o padrão além da instância. Se o dado decisivo deu trabalho para achar, proponha o sinal barato que o mostraria de cara.

### sequence-verifiable-units

Vale em trabalho de vários passos (varredura, migração, série de edições parecidas) e na ordem dos commits. Quebre o trabalho em unidades pequenas que terminam num estado checável e só avance com a atual verde: estado bom conhecido, uma mudança, o check, e então a próxima. Na entrega, empilhe os commits na ordem que prova o trabalho: teste vermelho antes do fix, subtração antes da remodelagem, baseline antes do tratamento, andaime antes da feature. No t0, organize os commits antes do primeiro push, porque reescrever histórico depois exige force push, e o hook bloqueia.

### test-behavior-not-implementation

Vale ao escrever, mudar ou manter um teste. O teste afirma o que o código faz para quem usa (quem chama, usuário final, outro serviço) pela interface que essa pessoa usa: retorno, erro, estado que ela lê de volta, efeito fora do código. Julgue cada teste com duas edições imaginárias. Quebre o comportamento: se o teste continua passando, ele não prova nada. Mude só o interior: se o teste quebra, ele está preso à implementação. Fique com o teste que pega a primeira e sobrevive à segunda. Tire o valor esperado do requisito, nunca de uma execução do próprio código.

## Desenho e mudança

### exhaust-the-design-space

Vale numa interação nova ou decisão de arquitetura sem precedente no código, e em decisão de produto em que a experiência depende de sensação mais que de lógica. Construa 2 ou 3 protótipos concorrentes e compare lado a lado antes de se comprometer. No t0, isso é o `prototype` com variantes atrás de um seletor, ou a `arena` para candidatos de desenho e de código.

### outcome-oriented-execution

Vale em reescrita e migração planejadas, com fronteiras de fase explícitas. Otimize para o estado final verificável, porque manter cada estado intermediário liso cria código de compatibilidade temporário que vira dívida longa. Quebra intermediária é aceitável quando é planejada, delimitada e reversível. Declare onde ela é aceitável, mantenha checks fortes nas áreas que você está mexendo e exija verificação estática e de execução completa no fim. No t0, a quebra vive dentro da branch do slice, e o PR que vai para review já está verde.

### redesign-from-first-principles

Vale ao integrar um requisito novo num desenho que já existe. Redesenhe como se o requisito estivesse lá desde o primeiro dia, em vez de pendurar a mudança por fora. Leia todos os arquivos afetados, pergunte o que você construiria do zero com esse requisito, propague a mudança por tipos, docs, exemplos e justificativas, e entregue o redesenho em incrementos.

### encode-lessons-in-structure

Vale quando você se pega escrevendo a mesma instrução pela segunda vez, ou vê uma correção que se repete. Codifique a regra como lint, flag de metadata, check em tempo de execução ou script no lugar de mais texto. Lição que precisa de julgamento e não dá para codificar ganha destaque e um exemplo do modo de falha. Quando o fix é estrutural, use só o fix estrutural: a instrução era o sintoma. No t0, este é o motor da escada do harness, com sensor primeiro e `AGENTS.md` por último (`harness-fix`).

## Delegação

### never-block-on-the-human

Vale quando dá vontade de perguntar "posso fazer X?". No t0, o princípio cobre só trabalho reversível dentro de um slice: código, teste, commit na branch do slice, rascunho na branch da bet, protótipo fora do main. Nesse escopo, faça, mostre o resultado e deixe o humano corrigir depois. Quando notar um problema, registre (`t0 log blocker` ou Harness Item) e corrija na rodada seguinte. Sempre param no humano: aposta, spec e degrau; merge e PR pronto; mudança de escopo do slice; mensagem para fora do time; apagar dado. A direção de produto vem do humano, e a execução dentro do slice segue.
