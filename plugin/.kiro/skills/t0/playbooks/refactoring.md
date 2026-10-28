# Playbook refactoring

Você é dono do contrato. A estrutura muda e o comportamento fica. Comportamento novo vai para `playbooks/feature.md` e correção para `playbooks/bug-fix.md`. Este playbook roda dentro do passo de build do `playbooks/slice.md`.

Se a limpeza revelar uma feature faltando ou um bug real, separe: registre com `idea-capture` e entregue primeiro a mudança estrutural contra o contrato fixado. Redesenho é permitido, desde que você o nomeie e mande para `playbooks/feature.md`.

1. Fixe o contrato de comportamento primeiro. Leia o subsistema e escreva um teste de caracterização, snapshot ou harness de equivalência que capture o comportamento atual antes de mexer na estrutura. Área sem cobertura ganha o pino antes de tudo. Type check e lint ficam de fora do pino.
2. Nomeie a estrutura que falta no código (`model-the-domain`). Código chato fica quando o formato já é claro e local. A remodelagem precisa apagar ramos ou estados inválidos.
3. Nomeie o formato alvo: layout de módulos, tipos e grafo de chamadas como seriam se escritos hoje (`foundational-thinking`, `redesign-from-first-principles`). Alvo que cruza fronteira de função passa antes pelo `architect`.
4. Subtraia antes de somar (`subtract-before-you-add`). Apague código morto, junte wrapper de um chamador só, tire validador redundante e referência órfã antes de introduzir o formato novo. Entra a menor mudança que chega ao alvo (`laziness-protocol`). Limpeza especulativa é revertida.
5. Mova em passos pequenos que preservam o comportamento, com o pino verde em cada um. Em mudança de API, migre todos os chamadores e apague a API velha na mesma onda, sem shim de compatibilidade e sem caminho velho e novo em paralelo. Confira cada rename nos arquivos, porque rename escapa em string, prosa e referência reversa. Com muitas edições iguais, escreva o codemod (`build-the-lever`). Delegue as edições mecânicas a um `t0-agent`, com o modelo do papel na Policy `models` e escopo fechado (caminhos, nomes movidos, comportamento a manter).
6. Prove no artefato real que o comportamento não mudou (`prove-it-works`). Em remodelagem grande, rode um check de equivalência: script que compara a saída velha com a nova, baseline gravado e reproduzido, ou smoke pelo `verify-<app>`.
7. Confirme que vale a pena. A medida é a carga de leitura (`minimize-reader-load`). Se o diff não reduz a carga de leitura em lugar nenhum, reverta.
8. Organize os commits antes do primeiro push: subtração, remodelagem e a limpeza seguinte (`sequence-verifiable-units`), cada um verde. Volte ao `slice-build` para abrir o PR em draft.

Na resposta: a estrutura que mudou, o pino, a prova de equivalência, a diferença de carga de leitura, o que entrou e o que foi revertido. Nenhum comportamento novo.
