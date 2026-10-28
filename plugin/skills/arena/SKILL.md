---
name: arena
description: "Roda 2 ou mais candidatos em paralelo na mesma tarefa, um juiz pontua contra uma rubrica, e você escolhe a base e enxerta o melhor dos outros. Use para comparar desenhos ou código quando uma tentativa só travaria a forma errada."
metadata:
  credits: "Baseada em PS arena (pstack 0.15.25, MIT)"
---

# arena

Abra uma lista de tarefas com uma entrada por fase antes de lançar qualquer coisa: Enquadrar, Espalhar, Julgar, Escolher, Enxertar, Verificar, Limpar.

Quem chama (por exemplo o `architect`) pode passar a tarefa, a profundidade do candidato, N, a fundamentação, o prompt dos candidatos e o papel na Policy `models`. O que não vier, você define na Fase A.

## Fase A: enquadrar

Todo candidato recebe o mesmo prompt, então o prompt é o contrato.

1. Diga qual artefato cada candidato produz e com que profundidade. O padrão é só desenho: uma nota com a forma e os trade-offs, mais no máximo um arquivo pequeno de esboço da interface ou do formato de dado central. Sem implementação e sem suíte de testes. Código completo só quando quem chama pede.
2. Escreva a rubrica: de 3 a 6 critérios concretos e pontuáveis para o que é sucesso nesta tarefa. A rubrica é ferramenta do juiz e sua na Fase D. Os candidatos só veem a tarefa.
3. Escolha os modelos. Leia a Policy `models` do KB (`kb_get methodology/policies/models.md` no MCP `t0-kb`) e use o que ela aprova para o papel (o papel que quem chamou passou, senão `arena`) e para o juiz. Papel sem linha na Policy: use o modelo da sessão. Sem o MCP, use `t0 kb get|find` ou leia os arquivos em `kb/` do workspace, e diga isso numa linha da resposta. Só sem nenhum dos três, pare e diga "KB indisponível". Nunca use modelo que a Policy não aprova.
4. Decida o rótulo. Se todos os candidatos e o juiz são da mesma família de modelo, a saída inteira leva o rótulo `same-family`. Isso vale também quando a Policy aprova uma família só e você roda N candidatos no mesmo modelo.
5. Decida N. Dois por padrão. Mais só quando quem chama pede.
6. Só desenho: cada candidato grava num diretório próprio, `$TMPDIR/t0-arena/<slug>/c<n>/`, e lê o repo sem rodar build, teste ou instalação. Código: dê a cada candidato a própria worktree, criada a partir do mesmo commit:

   ```bash
   git worktree add "$TMPDIR/t0-arena/<slug>/c<n>" -b arena/<slug>/c<n> <SHA>
   ```

   As branches `arena/*` são locais. Nunca faça push delas, nunca abra PR a partir delas.

## Fase B: espalhar

Lance os N subagentes `t0-agent` numa mensagem só, em segundo plano. Cada um recebe:

- a tarefa e o prompt dos candidatos;
- o caminho da fundamentação compartilhada;
- o caminho do próprio diretório ou worktree, que é o único lugar onde ele escreve;
- o pedido de entregar o artefato mais um racional curto com as alternativas que considerou e o que descartou;
- a profundidade e a regra de que ele nunca faz push, PR ou escrita no KB.

Se um candidato não entregar nada, siga com N-1 e anote a desistência.

## Fase C: julgar

Depois que todos os candidatos terminaram, lance um subagente juiz só leitura, no modelo da Policy para juiz, de preferência de outra família que a dos candidatos. Ele recebe a rubrica e os candidatos por rótulo de caminho (`c1`, `c2`, ...), sem saber qual modelo fez qual. Ele pontua cada critério por candidato e recomenda uma base com justificativa. Ele roda em paralelo com a sua leitura da Fase D. Nunca lance o juiz com candidato ainda escrevendo.

## Fase D: escolher a base

Leia cada candidato de ponta a ponta antes de escolher. Pontue cada um contra a rubrica, critério por critério, e compare com o juiz. Concordância sobre a base confirma a escolha. Discordância quer dizer que um dos dois está enviesado ou que a rubrica ficou ambígua: leia as duas justificativas antes de decidir.

Escolha a base que um mantenedor futuro consegue estender com mais facilidade sem quebrar invariantes. No empate, fique com a fronteira mais limpa ou a API menor.

## Fase E: enxertar

Passe mais uma vez por cada candidato perdedor procurando o que vale trazer para a base, em geral uma ou duas coisas por candidato. Incorpore cada enxerto à mão, para o resultado continuar coerente sob um modelo mental só. Nada de colar mecanicamente.

Candidatos que convergem para a mesma forma são concordância forte: anote e entregue a forma de consenso, sem enxerto. Candidatos que divergem demais mostram que a Fase A ficou mal especificada: reenquadre e rode de novo, em vez de tirar a média da divergência.

## Fase F: verificar

Verifique o artefato sintetizado como qualquer outra saída, contra o artefato real. Código: rode os testes e a verificação do repo. Desenho: confira cada restrição da fundamentação contra a forma final e passe o resultado pelo crivo de sinais de alerta de quem chamou.

Se a verificação acha um problema que a arena deixou passar, ou a Fase A estava errada (reenquadre e rode de novo) ou um candidato tinha pegado e você perdeu o enxerto (volte à Fase E). Nunca esconda o problema.

## Fase G: limpar

Grave o artefato sintetizado onde quem chamou pediu (para o `architect`, de volta para ele, que grava no spec). Depois remova os diretórios, as worktrees e as branches locais que você criou:

```bash
git worktree remove "$TMPDIR/t0-arena/<slug>/c<n>"
git branch -D arena/<slug>/c<n>
```

Apague só as branches `arena/<slug>/*` desta rodada. Candidato nunca entra no KB.

## Saída

Um artefato sintetizado e, ao lado dele, uma nota de síntese em pt-BR. A primeira linha da nota diz os modelos usados e o rótulo, por exemplo `Modelos: candidatos 3x <modelo>, juiz <modelo> (same-family)`. Depois:

- a base escolhida e por quê;
- o veredito do juiz e se concordou com você;
- cada enxerto com o candidato de origem;
- o que foi descartado e por quê;
- convergência ou desistências;
- o resultado da verificação.
