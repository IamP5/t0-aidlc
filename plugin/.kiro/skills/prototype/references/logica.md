# Protótipo de lógica

Um HTML único e autocontido, uma demo compartilhável, que deixa qualquer pessoa dirigir um modelo de estado clicando em botões. Use quando a pergunta é sobre regra de negócio, transição de estado ou forma de dado: o tipo de coisa que parece certa no papel e só soa errada quando passa por casos reais.

Por ser um arquivo só, sem nada para instalar, ele vai para quem não programa (designer, PM, Domain Expert de squad), que sente o modelo sozinho. Por isso ele fala a língua do domínio, e a do código fica escondida.

Se a pergunta é "como isso deveria ficar", o ramo certo é `ui.md`.

## 1. Escreva a pergunta no topo

Antes do código, escreva qual modelo de estado e qual pergunta o protótipo testa, num parágrafo visível no topo da página. Protótipo que responde a pergunta errada é desperdício, e a pergunta escrita deixa conferir depois, com o usuário olhando agora ou voltando mais tarde.

## 2. Isole a lógica num módulo portátil

Ponha a lógica que responde a pergunta num único bloco `<script>`, escrito como um módulo pequeno e puro que poderia ir para o código real depois. A página em volta é descartável; esse módulo é a parte que vale.

Escolha a forma pela pergunta:

- um reducer puro, `(estado, ação) => estado`, quando as ações são eventos discretos e o estado é um valor só;
- uma máquina de estados explícita, quando "quais ações valem agora" faz parte da pergunta;
- um conjunto de funções puras sobre um tipo de dado simples, quando não há estado corrente, só transformações;
- uma classe com superfície de métodos clara, quando a lógica realmente guarda estado interno.

Mantenha o módulo puro: nada de DOM, `document` ou handler de botão dentro dele. A página chama o módulo, e nada flui no sentido contrário.

## 3. Monte o HTML

Um arquivo, HTML, CSS e JS puros, tudo inline: sem framework, bundler ou servidor. Abre com dois cliques e sobrevive a ser mandado no chat do time.

Escreva para quem não programa. Todo rótulo está na língua do domínio, e cada botão e campo de estado lê como o negócio. De cima para baixo:

1. Título e uma linha explicando o que a demo deixa explorar (a pergunta do passo 1).
2. Estado atual: o estado relevante inteiro, num painel legível com campos rotulados (sem despejo de JSON), redesenhado a cada clique. Destaque o que acabou de mudar quando ajudar.
3. Botões livres: um por ação, sempre disponíveis, para mexer no modelo em qualquer ordem.
4. Roteiros guiados: um cenário por aba, com uma descrição curta da situação e do que observar, e embaixo os botões na ordem. Cada passo é um botão de verdade que executa a ação e avança. Começar um roteiro volta a um estado inicial conhecido, para o cenário rodar igual toda vez.

Escolha cenários que mostrem os casos chatos: o caminho feliz, um caso de borda difícil e uma tentativa de algo que deveria ser proibido.

Visual limpo e contido: tipografia clara, espaço generoso, uma cor de destaque, sem animação.

## 4. Depois da resposta

O HTML inteiro fica na branch `proto/` como fonte primária e roda de novo a qualquer hora. O módulo validado é o trecho que a `bet-spec` pode citar. Ele vai para o código real só por um slice, com teste.

## Armadilhas

- Teste no protótipo: protótipo que precisa de teste já virou outra coisa.
- Banco de verdade: use estado em memória, a menos que a pergunta seja sobre persistência.
- Generalizar para "e se um dia precisarmos de X": o protótipo responde uma pergunta.
- Misturar lógica e página: se o módulo toca o DOM, ele deixa de ser portátil.
- Framework, bundler ou servidor: um React ou um dev server acabam com o "abre com dois cliques".
