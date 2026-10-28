# Sinais de alerta de desenho

Passe cada candidato por esta lista antes da síntese. Um sinal de alerta é motivo para revisar ou descartar a forma.

## Módulo raso

Um módulo raso expõe uma interface grande e esconde pouca complexidade. Meça a profundidade pela capacidade e pela política escondidas atrás da superfície pública, em relação ao tamanho dessa superfície. Prefira uma interface simples com bastante comportamento por trás.

Módulo profundo e cadeia de chamadas profunda são coisas diferentes. A cadeia profunda espalha o entendimento por várias camadas. O módulo profundo concentra capacidade atrás de uma interface.

Sinais:

- quem chama coordena vários métodos para fazer uma operação só;
- as opções públicas expõem etapas internas ou escolhas de implementação;
- aprender a interface não poupa quem chama de aprender a implementação.

## Vazamento de informação

Vários módulos dependem da mesma decisão interna. Uma representação, uma política ou um detalhe de protocolo aparece em mais de um lugar, e mudar exige edição coordenada.

Reexportar tipo de transporte ou de wire na API pública é vazamento. Converta dado externo em tipo de domínio atrás da interface. Mantenha privados o schema de armazenamento, os objetos de framework e os detalhes de protocolo.

## Decomposição temporal

Os módulos seguem a ordem de execução em vez do conhecimento que cada um guarda. Etapas separadas de carregar, validar, transformar e salvar costumam repetir a mesma representação e as mesmas invariantes em várias fronteiras.

Agrupe o código em torno do conhecimento de domínio e de quem é dono dele. Métodos que rodam em momentos diferentes podem morar no mesmo módulo quando protegem as mesmas decisões.

## Método de repasse

O método só repassa os mesmos argumentos para outro método com a mesma forma. Ele acrescenta uma camada sem esconder complexidade.

Remova, ou leve a responsabilidade para o módulo que consegue completar a operação. Mantenha a fronteira de repasse só quando ela acrescenta política, adaptação ou uma abstração distinta.

## Dono dividido

Mais de um módulo escreve o mesmo estado ou guarda sua própria cópia dele. Um agente que edita um dos escritores não enxerga os outros, e as regras divergem.

Dê um dono a cada pedaço de estado. Os outros módulos leem ou pedem ao dono para mudar.

## Dois jeitos de fazer a mesma tarefa

O desenho aceita mais de um jeito de fazer a mesma coisa. O agente copia o primeiro que encontra, e cada jeito continua ganhando chamadores.

Fique com um jeito. Migre os chamadores dos outros e apague os outros na mesma mudança.

## Internals importáveis

Quem chama consegue importar os internals de um módulo. O agente pega o caminho mais curto que compila, importa direto, e os internals viram parte da interface.

Torne os internals inalcançáveis de fora do módulo, de modo que um import de fora quebre o build.

## Lista sincronizada à mão

Dois ou mais lugares listam os mesmos itens, e acrescentar um item exige editar todas as listas. O agente que vê uma lista só atualiza só aquela.

Mantenha uma lista e derive as outras dela. Se não der para derivar, faça o build falhar quando as listas divergirem.
