---
name: harness-fix
description: "Corrige um erro repetido de agente ou um Harness Item aceito no degrau mais alto da escada do harness, prova o sensor contra um erro real do passado e abre um PR em draft no repo certo. Use com `harness-fix <HI>`, no Harness Health ou quando o mesmo erro aparece pela segunda vez."
metadata:
  credits: "Baseada em PS correct (pstack 0.15.25, MIT) e MP retro (mattpocock-skills 1.3.1, MIT)"
---

# harness-fix

O time corrige agentes pelo mesmo erro mais de uma vez. Mude o repo para que o próximo agente não consiga repetir.

Pense em quem contribui como um agente que só vê os arquivos que abriu, copia o exemplo mais perto e pega o caminho mais curto que compila. Uma mudança que parece certa olhando um arquivo só tem que estar certa para o repo inteiro.

Um Harness Item trata uma classe de erro. Um PR em draft por item aceito.

## Passos

### 1. Achar o item

1. Com `harness-fix <HI>`, rode `t0 kb get <HI>` e leia `pattern` e `occurrences`.
2. Sem HI, procure se a classe já tem item com `t0 kb find "<padrão>"`. Achou, use esse. Não achou, rode `t0 new harness` com o padrão e a primeira ocorrência.
3. A classe conta a partir da segunda ocorrência. Com uma só, registre a ocorrência no item e pare. Item aceito no Harness Health segue mesmo assim.

O passo termina com um HI na mão, o padrão escrito em uma frase e pelo menos duas ocorrências com link.

### 2. Juntar a evidência

Leia as fontes primárias de cada ocorrência:
- commits, reverts e comentários de review dos PRs ligados;
- o `.audit/<KEY>.tsv` dos slices envolvidos;
- `AGENTS.md`, `agents/rules/` e comentários que explicam gambiarra;
- logs de sessão só deste workspace. No Claude Code é `~/.claude/projects/<caminho do workspace com / trocado por ->/`. Nas outras ferramentas, só o equivalente deste workspace.

Fora do escopo: logs de outro projeto da máquina, `~/.t0/inbox/` e transcrição crua. Precisa de algo de uma reunião, use o Transcript redigido do KB.

Antes de propor um sensor novo, leia o comando de check do repo (scripts de `lint`, `check` ou `test`, o workflow de CI). Um check que já existe e está desligado ou quebrado é o achado. Repo sem guardrail nenhum (sem hook de git e sem job de CI rodando lint, tipo e teste) também é achado.

Lentes para achar a causa, da MP `retro`: navegação (o agente demorou para achar o arquivo certo), check automático que pegaria o erro, padrão que o revisor deveria cobrar, instrução em `AGENTS.md` que não muda comportamento, chamada de ferramenta cara, informação que o agente não tinha.

O passo termina quando cada ocorrência tem a causa escrita em uma frase.

### 3. Escolher o repo certo

O PR vai no repo onde o erro nasce:
- código de produto: o repo de produto, pelo `repos[]` do Product no KB;
- skill, hook, lint do toolkit ou comando `t0`: o repo do toolkit;
- Template ou Policy: o repo do KB, pela raia de conhecimento.

Se a correção pede mudança em dois repos, são dois itens. Abra o segundo com `t0 new harness` e trate cada um no seu PR.

### 4. Subir a escada

Tente de cima para baixo e pare no primeiro degrau que resolve. O `ladder_step` do item é o degrau escolhido.

1. `sensor`, o degrau computacional. Dentro dele, nesta ordem:
   - arquitetura: cada estado com um dono, cada tarefa com um jeito suportado. Esconda internals para o import errado falhar. Troque lista sincronizada à mão por uma fonte de verdade. Apague o jeito antigo e o código morto que um agente copiaria;
   - tipos: o estado ruim não pode ser escrito;
   - lint ou check de CI cuja mensagem nomeia o arquivo, o tipo ou a função a usar, escrita para o agente ler. Se o padrão ruim já é comum, falhe só quando a mudança adiciona mais;
   - teste do comportamento. Conserte ou apague teste que passa com o comportamento quebrado ou que falha quando só o internal muda.
   Regra sem exceção mora em hook de git ou CI. Hook de agente fica como acelerador opcional, porque cada ferramenta tem semântica própria e no Copilot o timeout falha aberto.
2. `area-rule`: regra de área, de uma fonte só, em `agents/rules/<area>.md`. Use quando o erro é de julgamento e ninguém consegue escrever um check.
3. `skill`: procedimento longo vira skill no toolkit.
4. `agents-md`: por último, uma linha no `AGENTS.md`, que tem teto de 150 linhas. Nada falha quando o agente pula essa linha.

Para cada degrau acima do escolhido, escreva em uma frase por que ele não serviu.

Antes de adicionar um hook, confira o teto de 20 hooks e denies por repo em `harness/budget.md`. Estourou, o item precisa tirar um antes de pôr outro.

O passo termina com o degrau escolhido e uma frase por degrau de cima descartado.

### 5. Corrigir e provar

1. Crie a branch no repo certo e faça a correção. Uma correção por commit.
2. Prove que o sensor pega o erro de verdade. Pegue o diff de uma ocorrência real (o commit, o trecho do PR revisado) e reaplique numa worktree. Rode o check e veja falhar. Com a correção aplicada, rode de novo e veja passar. Guarde as duas saídas.
3. Rode o mesmo comando que o CI roda, localmente. O check local e o do CI têm que ser o mesmo comando.
4. Exceção vai na linha que ofende, com motivo, data de validade e o nome do humano que aprovou.

Em `area-rule`, `skill` ou `agents-md` não existe check para falhar. Mostre a ocorrência real e o texto que teria mudado a decisão do agente ali.

O passo termina quando a saída vermelha na ocorrência antiga e a verde depois da correção estão guardadas.

### 6. Abrir o PR em draft

Antes de qualquer push, confirme que existe forge: `gh` está instalado, `gh repo view` passa para o repo e `git remote get-url --push origin` não está desativado (`no_push`, `DISABLED` ou vazio). Se algum falhar, nunca faça push: o PR em draft é a branch local, com o corpo em `.t0/pr/<branch>.md`, e diga isso na resposta. Com forge, rode `gh pr create --draft` no repo certo, com este corpo.

```markdown
## Harness Item

HI-NNNN: <padrão em uma frase>

## Ocorrências

- <link da ocorrência 1>: <causa em uma frase>
- <link da ocorrência 2>: <causa em uma frase>

## Degrau

<sensor | area-rule | skill | agents-md>: <o que mudou>

Por que não o de cima:
- <degrau>: <motivo em uma frase>

## Prova

Comando: `<comando que o CI roda>`

Na ocorrência antiga:
<saída vermelha>

Com a correção:
<saída verde>

## Exceções

<linha, motivo, validade, quem aprovou; ou "nenhuma">
```

Um PR por item aceito. O PR fica em draft: nunca marque como pronto, nunca faça merge, nunca force push, nunca `reset --hard`.

### 7. Registrar

1. Rode `t0 log decision "HI-NNNN: degrau <ladder_step>, PR <url>"`.
2. Atualize `occurrences` e `ladder_step` do item pela raia de conhecimento do KB, num PR em draft. O `pr` e o `state: fixed` saem do `t0` a partir do link do PR. Nunca edite `pr`, `state` nem os derivados (`index.md`, `log.md`, `changeset.md`) à mão.
3. Se o item foi aceito no Harness Health, diga ao Harness Keeper que o PR existe, para o `t0 ritual harness-health close` passar.

O Harness Item termina `fixed` com `pr`. Item recusado pelo time termina `wontfix`, com o motivo no corpo.

## Resposta

Em pt-BR, por item: o padrão com a evidência, o degrau escolhido, por que um degrau mais alto não serviu, a prova (vermelho e verde) e o link do PR em draft.
