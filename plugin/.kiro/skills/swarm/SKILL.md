---
name: swarm
description: "Espalha N workers em paralelo, drena os resultados e devolve um relatório só. Use para matriz de cobertura, corrida entre tentativas, bateria de ataques (gauntlet) ou partição de exploração, com worktrees locais e modelos da Policy models."
metadata:
  credits: "Baseada em PS swarm (pstack 0.15.25, MIT)"
---

# swarm

Abra uma lista de tarefas com uma entrada por fase antes de lançar qualquer coisa: Enquadrar, Espalhar, Agregar, Relatar, Limpar.

## Fase A: enquadrar

1. Escreva o predicado de pronto e o relatório que o swarm devolve.
2. Escolha a forma:
   - matriz de cobertura: cada célula (por exemplo critério de aceite × ponto de entrada) vira um worker, e toda célula exigida precisa de resultado;
   - partição de exploração: o espaço (pastas, módulos, hipóteses) é dividido sem sobreposição, um pedaço por worker;
   - corrida: N workers com o mesmo brief; declare antes de lançar se vale `primeiro que passa`, `ranquear todos` ou `melhor de N`;
   - gauntlet: o mesmo artefato, cada worker com uma lente de ataque diferente (entrada inválida, concorrência, permissão, regressão); o artefato só passa se passa em todas;
   - misturas das anteriores, com a regra de seleção declarada antes.
3. Escolha os modelos. Leia a Policy `models` do KB (`kb_get methodology/policies/models.md` no MCP `t0-kb`) e use o que ela aprova para worker de swarm. Papel sem linha: modelo da sessão. Sem o MCP, use `t0 kb get|find` ou leia os arquivos em `kb/` do workspace, e diga isso numa linha da resposta. Só sem nenhum dos três, pare e diga "KB indisponível". Numa corrida entre modelos, nomeie o modelo de cada braço antes. Se todos os workers são da mesma família, o relatório leva o rótulo `same-family`.
4. Escolha o tipo de subagente: `verifier` para quem verifica ou mede, `t0-agent` para quem escreve.
5. Isole quem escreve. Cada worker que escreve ganha a própria worktree local, presa ao SHA que o brief nomeia:

   ```bash
   git worktree add --detach "$TMPDIR/t0-swarm/<slug>/w<n>" <SHA>
   ```

   Worker só leitura pode ler o checkout principal. Ninguém faz push, abre PR ou escreve no KB.
6. Isole o app. Quando o worker dirige o app real, siga a seção Subir do `verify-<app>` do repo. Sem `verify-<app>`, os workers seguem os passos do "Como verificar" do slice e rodam em série. Se ela diz que duas instâncias não rodam lado a lado, os workers que dirigem o app rodam em série, e só a parte de leitura vai em paralelo.
7. Quando o worker verifica ou mede commits, o brief nomeia os SHAs exatos. Brief de medição nomeia também o método (quantas amostras, o que é uma amostra, a ordem). O worker grava os dois no resultado.

## Fase B: espalhar

Lance todos os workers numa mensagem só, em segundo plano.

Cada brief se sustenta sozinho: o objetivo, o escopo, a célula, o pedaço ou o braço exato, a worktree ou os SHAs, como verificar e o que relatar. O relatório usa `PASS`, `ISSUES` ou `BLOCKED`, sempre com evidência (comando e saída, `arquivo:linha`, caminho de screenshot). Um worker que prova um defeito relata `ISSUES` com todos os defeitos que consegue provar.

Se um worker desistir, siga com N-1 e anote.

## Fase C: agregar

Leia os resultados finais. Descarte o resultado que não grava os SHAs e o método que o brief pediu, e relance esse worker uma vez. No segundo erro, registre uma lacuna. Lacuna nunca conta como `PASS`.

Na cobertura, toda célula exigida precisa de resultado. Na corrida, aplique a regra declarada na Fase A. No gauntlet, um `ISSUES` em qualquer lente reprova o artefato. Nunca cole o despejo bruto dos workers.

## Fase D: relatar

Devolva um relatório consolidado em pt-BR. A primeira linha diz os modelos e o rótulo, por exemplo `Modelos: 6x <modelo> (same-family)`. Depois:

- a tabela (célula, pedaço ou braço → `PASS`/`ISSUES`/`BLOCKED` → evidência);
- uma linha por defeito;
- as lacunas e desistências;
- a regra de seleção, quando houve corrida.

## Fase E: limpar

Remova as worktrees que você criou (`git worktree remove "$TMPDIR/t0-swarm/<slug>/w<n>"`) e derrube as instâncias de app que os workers subiram, pela seção Limpeza do `verify-<app>`. A evidência fica: confira que os arquivos de evidência citados no relatório continuam no caminho nomeado depois da limpeza.
