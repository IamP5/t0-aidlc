---
name: slice-verify
description: "Revisa o PR de um slice em duas raias (padrões do repo e spec do KB), prova no app real pelo verify-<app>, roda o raio de impacto em Tier 2 e posta os achados como comentário no PR. Use para revisar um slice, um PR de slice ou uma chave Jira antes do review humano."
metadata:
  credits: "Baseada em MP code-review (mattpocock-skills 1.3.1, MIT) e PS blast-radius + swarm (pstack 0.15.25, MIT)"
---

# slice-verify

Você é o agente de review que roda antes do humano. O humano só lê depois que você e o CI passaram, então cada achado do seu comentário vem com prova. Você comenta. Você nunca aprova, nunca pede mudança como decisão, nunca marca pronto e nunca faz merge. Você também não faz commit na branch do autor.

Abra uma lista de tarefas com estes passos antes de começar:

1. Fixar o PR e a base
2. Achar o spec
3. Achar os padrões
4. Rodar as duas raias
5. Provar no app
6. Raio de impacto (só Tier 2)
7. Erros de agente
8. Postar o comentário

## 1. Fixar o PR e a base

1. Pegue o PR do pedido (número, branch ou chave). Leia com `gh pr view <PR> --json number,url,headRefName,baseRefName,isDraft,body`.
2. Calcule a base: `git merge-base origin/<baseRefName> HEAD`, com a branch do PR em checkout local.
3. Confira que a base resolve (`git rev-parse <base>`) e que `git diff <base>...HEAD` não está vazio. Ref ruim ou diff vazio falha aqui, antes de qualquer subagente.
4. Guarde o comando de diff e a lista de commits (`git log <base>..HEAD --oneline`).

## 2. Achar o spec

1. Tire a chave Jira (`[A-Z][A-Z0-9]+-[0-9]+`) do nome da branch. Sem chave na branch, procure nas mensagens de commit e depois na linha `Jira:` do corpo do PR.
2. Leia `kb_get <KEY>` no MCP `t0-kb`. Ele devolve o slice em `products/<pod>/bets/<BET>/slices/NN-slug.md`. O spec é `products/<pod>/bets/<BET>/spec.md`, lido com `kb_get`. Se o MCP não achar pela chave, procure no clone do KB por `jira: <KEY>` em `products/*/bets/*/slices/*.md`.
3. Na trilha rápida não há spec: a referência é o próprio slice, com "atual, esperado, o que não muda" e o teste.
4. Leia o tier no slice. Sem slice nem spec, não invente: pergunte ao humano onde está, e enquanto isso a raia de spec fica marcada "sem spec disponível".
5. Sem o MCP, use `t0 kb get|find` ou leia os arquivos em `kb/` do workspace, e diga isso numa linha da resposta. Só sem nenhum dos três, pare e diga "KB indisponível".

## 3. Achar os padrões

Liste todo arquivo do repo que documenta como o código deve ser escrito: `AGENTS.md`, `CONTRIBUTING.md`, `CODING_STANDARDS.md` quando existem (esses entram sempre), configs de lint e formatação, e os ADRs do produto (`kb_find` com `type: ADR` e o produto da bet).

## 4. Rodar as duas raias

Leia [`references/lanes.md`](references/lanes.md). Lance os dois subagentes numa mensagem só, novos e só leitura, no modelo que a Policy `models` aprova para revisor (`kb_get methodology/policies/models.md`):

- `standards-reviewer` com o brief da raia de padrões e a linha de base de cheiros;
- `spec-reviewer` com o brief da raia de spec, o slice, o spec e a seção Design.

Se o revisor é da mesma família de modelo que o agente que construiu o slice, o comentário leva o rótulo `same-family`.

Junte as duas respostas em seções separadas, `### Padrões` e `### Spec`, como vieram ou com limpeza leve. Nunca misture nem reordene achados entre raias. Uma mudança pode passar numa raia e falhar na outra, e separar impede que uma esconda a outra.

Confira também, por conta própria, o que o DoD pede no PR:

- o PR está em draft;
- o rodapé tem `Jira: <KEY>`, `Tier: <n>` e `Trilha: .audit/<KEY>.tsv`, e o tier bate com o do slice;
- `.audit/<KEY>.tsv` está no diff e cada evidência citada nas linhas resolve (SHA existe, `arquivo:linha` existe, teste existe);
- "Em minhas palavras" existe e foi escrita pelo autor em todo Tier 2 e em PR de júnior.

Cada falta vira achado.

## 5. Provar no app

1. Ache o `verify-<app>` do repo em `.t0/skills/verify-<app>/SKILL.md`. Sem ele, rode você mesmo os passos do "Como verificar" do slice e o comando de teste do repo, marque a evidência "sem verify-<app>; verificado pelos passos do slice" e sugira a skill `verify-setup` no comentário, sem esperar por ela. Pule os passos 2 e 3.
2. Monte a matriz de cobertura: uma linha por critério de aceite do slice, uma coluna por ponto de entrada que o mapa de features do `verify-<app>` lista para as features tocadas.
3. Com mais de uma célula e com a seção Subir dizendo que instâncias rodam lado a lado, siga para a skill `swarm` em forma de matriz de cobertura, com workers `verifier` e os SHAs exatos da cabeça do PR. Se as instâncias não isolam, dirija as células em série você mesmo.
4. Cada célula termina em `PASS`, `ISSUES` ou `BLOCKED`, com o caminho da evidência. Ponto de entrada pulado nunca conta como verificado por outro caminho.
5. Rode de novo o teste que o PR cita como "depois" e compare a saída com a do PR.
6. Depois da limpeza, confira que a evidência continua no caminho nomeado.

## 6. Raio de impacto (só Tier 2)

Em Tier 2, leia [`references/blast-radius.md`](references/blast-radius.md) e siga os passos. O fato de que a segurança depende chega pelo menos ao degrau 4 da escada de prova, ou o comentário diz "não provado" e em que degrau parou.

## 7. Erros de agente

Junte as linhas `ERRO-DE-AGENTE` das duas raias e as que você mesmo achou nos passos 4 a 6. Um erro é repetido quando o mesmo padrão aparece duas vezes ou mais neste PR, ou quando `kb_find` com `type: Harness Item` e o padrão como texto acha um item já aberto.

Para cada erro repetido, rode `t0 new harness` com o padrão em poucas palavras, a chave do slice e a evidência (link do PR, `arquivo:linha`). Se já existe um Harness Item para o padrão, cite o item e rode o comando mesmo assim para registrar a nova ocorrência. Cite cada Harness Item no comentário.

Erro que aparece uma vez só fica no comentário, marcado como erro de agente, sem Harness Item.

## 8. Postar o comentário

Escreva o comentário em pt-BR num arquivo temporário e poste um comentário só:

```bash
gh pr comment <PR> --body-file <arquivo>
```

Modelo:

```markdown
## Revisão do agente (slice-verify)

Modelos: <revisores> (<same-family quando for o caso>)
Base: <SHA da base> · Cabeça: <SHA da cabeça> · Tier: <n> · Spec: <caminho no KB>

### Padrões

<achados da raia de padrões>

### Spec

<achados da raia de spec>

### DoD do PR

<cada falta do passo 4, ou "completo">

### Evidência no app

| Critério | Ponto de entrada | Resultado | Evidência |
|---|---|---|---|

### Raio de impacto

<só Tier 2: fato de segurança, degrau, prova, riscos, descartados, antes do merge>

### Erros de agente

<cada erro, com o Harness Item quando repetido>

### Resumo

<total de achados por raia e o pior de cada raia, sem eleger um vencedor entre raias>
```

Se precisar apontar uma linha específica, acrescente comentários de linha pelo mesmo PR. Nunca use `gh pr review --approve`, `gh pr ready` nem `gh pr merge`.

## Resposta ao humano

Em pt-BR: o link do comentário, o total por raia, o pior achado de cada raia, o estado da matriz de evidência e os Harness Items abertos. Diga com clareza o que ficou `BLOCKED` ou "não provado".
