---
name: verify-setup
description: "Cria ou mantém a skill verify-<app> de um repo de produto em .t0/skills/verify-<app>/ (subir, diagnosticar, dirigir, evidência, limpeza, mapa de features) e prova contra o app real. Use quando o repo não tem jeito roteirizado de provar comportamento, ou no Harness Health para auditar o mapa."
metadata:
  credits: "Baseada em PS create-verification-skill + maintain-verification-skill (pstack 0.15.25, MIT)"
---

# verify-setup

Todo repo de produto precisa de um jeito roteirizado de dirigir o app real e provar comportamento: subir, exercitar uma feature como o usuário faz e capturar evidência. Esta skill escreve esse jeito como uma skill local do repo, `verify-<app>`, que o `slice-build` e o `slice-verify` usam. Você escreve para o próximo agente: ele vai ler a skill a frio, no meio de uma tarefa, sem nunca ter visto o app.

A skill gerada mora em `.t0/skills/verify-<app>/` no repo de produto. Esse é o único lugar. O `t0 setup` liga esse diretório para cada ferramenta (Claude Code, Copilot, Kiro).

Escolha o modo e diga qual:

- criar: o repo não tem `.t0/skills/verify-<app>/`;
- manter: a skill existe, e o pedido é auditar, atualizar o mapa, ou é a pauta do Harness Health.

Nos dois modos, toda mudança vai num PR em draft só, numa branch `verify-<app>-<criar|manter>-<data>`, e você nunca edita código de produto.

## Modo criar

### 1. Entreviste o repo, e o humano só no que o repo não responde

- Superfície: o que o usuário toca de fato? UI web, CLI ou TUI, app desktop, API, app mobile, biblioteca? Com várias, escolha a principal e anote as outras.
- Subir: como o app sobe localmente? Prefira o comando documentado do repo (scripts de pacote, Makefile, quickstart do README). Anote portas, variáveis de ambiente, dados de seed, autenticação.
- Dirigir: como um agente interage com ele por programa? Primeiro os harnesses que já existem (specs Playwright ou Cypress, scripts expect, helpers de PTY, endpoints que o curl alcança, porta de debug). Só depois uma receita genérica: browser ou CDP para web e Electron, tmux ou PTY para CLI e TUI, HTTP para serviço.
- Observar: que evidência dá para capturar? Screenshot, transcrição de terminal, corpo de resposta, log, código de saída, estado do banco.
- Isolar: duas instâncias rodam lado a lado (portas, diretórios de dados, perfis)? Se não, a skill gerada diz isso, e o `swarm` dirige em série.

Se o checkout não builda ou não sobe como está, conserte isso primeiro ou relate com precisão. Skill escrita sobre base quebrada ensina passo errado. Quando um asset irrelevante que falta trava a subida (uma pasta estática que a API nem serve, uma config de exemplo), a skill gerada pode criá-lo, marcado como andaime de verificação, e removê-lo na limpeza.

### 2. Gere a skill

Escreva `.t0/skills/verify-<app>/SKILL.md` pelo esqueleto de [`references/verify-skill-template.md`](references/verify-skill-template.md). Cada seção sai do que a entrevista achou de verdade, sem nenhum `<...>` sobrando:

- Subir (Launch): o comando exato e como saber que está pronto. Pronto quer dizer usável, a partir de um diretório de dados vazio, com migrações e seed. Para CLI de vida curta não há servidor: subir é buildar uma vez, e cada direção roda numa sessão PTY ou tmux isolada.
- Diagnóstico (Doctor): uma checagem só leitura que responde "vale dirigir esta instância?": processo no ar, versão ou build certo, porta nossa, autenticação válida.
- Dirigir (Drive): a receita do harness com seletores e comandos reais deste repo. Prefira alças estáveis (rótulos ARIA, atributos de dados, textos de prompt, rotas) a coordenadas e ordem de tab.
- Evidência (Evidence): o que capturar e onde guardar, com os padrões de prova do esqueleto.
- Limpeza (Cleanup): como derrubar o que a execução criou. Mate o que você subiu, nunca por nome de processo. A limpeza remove instâncias e estado de rascunho, e a evidência fica, no caminho que a skill nomeia.
- Helpers: todo script que a skill traz é executável e tem a invocação mostrada no corpo.

### 3. Semeie o mapa de features

Crie `.t0/skills/verify-<app>/features/README.md` e um arquivo por feature visível ao usuário (comece pelas 3 a 5 principais, tiradas de rotas, comandos, menus ou docs). Siga o formato de [`references/feature-map-example/`](references/feature-map-example/): um README de índice e um arquivo por feature com as quatro seções `Subfeatures`, `Como chegar (visão do usuário)`, `Dirigindo com <harness>` e `Armadilhas`.

Se o seed não tem uma pré-condição que uma jornada precisa, a jornada relata falha e o motivo vai em `Armadilhas`. Nunca afrouxe a jornada para ela passar. O mapa é a fonte mantida de verificação do repo: uma prova que dirige só um ponto de entrada conveniente fica incompleta quando o mapa lista outros.

### 4. Prove a skill gerada

Rode as instruções dela de ponta a ponta uma vez contra o app real: subir, diagnóstico, dirigir UMA feature do mapa, capturar evidência, limpar. Depois da limpeza, confira que a evidência continua no caminho nomeado. Limpeza que come a prova reprova este passo.

Conserte o que falhar e rode a limpeza gerada depois de cada tentativa que falhou, para não deixar processo e porta pendurados. Skill gerada que nunca rodou é rascunho.

Se você provou num substituto do alvo real (um container no lugar de uma VM nova, uma stack local no lugar da remota), liste cada passo de preparo que o substituto fez e o alvo não vai fazer. Esses passos ficam não verificados até uma execução no alvo real.

### 5. Abra o PR em draft

1. Rode `t0 setup` para ligar a skill nova a cada ferramenta.
2. Faça commit de `.t0/skills/verify-<app>/` e do que o `t0 setup` gerou, e, antes de qualquer push, confirme que existe forge: `gh` está instalado, `gh repo view` passa para o repo e `git remote get-url --push origin` não está desativado (`no_push`, `DISABLED` ou vazio). Se algum falhar, nunca faça push: o PR em draft é a branch local, com o corpo em `.t0/pr/<branch>.md`, e diga isso na resposta. Com forge, faça push sem força e abra o PR: `gh pr create --draft --title "verify-<app>: skill de verificação" --body-file <arquivo>`. O corpo diz a superfície, a feature provada, o caminho da evidência e o que ficou não verificado.
3. Diga ao humano que o modo manter roda no Harness Health para manter o mapa honesto.

## Modo manter

O mapa apodrece no momento em que o app muda. A unidade de rigor é a feature: cubra cada arquivo de feature pelo código-fonte e exercite cada feature ao vivo. Este modo é insumo do Harness Health.

Escopo de edição: só o diretório da skill de verificação (o `SKILL.md`, `features/` e os scripts de harness dela). Comportamento que o mapa descreve e o app não faz mais é desvio de doc (conserte o mapa) ou regressão de produto (relate ao humano e deixe a doc dizendo o comportamento esperado).

Resultado, um destes três, e diga qual:

- limpo: toda feature teve cobertura de fonte e ao vivo, nada a mudar; sem branch, sem PR;
- mudou: um PR em draft com correções provadas;
- travado: a cobertura não terminou ou uma correção provada não dá para entregar com segurança; diga exatamente o que travou.

### 1. Ache o alvo

Procure `.t0/skills/verify-*/` no repo. Vários candidatos: pergunte qual. Nenhum: pare e siga o modo criar.

### 2. Higiene do índice

Leia o README do mapa e liste os arquivos irmãos. Conserte entrada faltando, sobrando, duplicada ou morta.

### 3. Onda de fonte

Lance um subagente `verifier` só leitura por arquivo de feature, todos de uma vez, no modelo que a Policy `models` aprova para worker (`kb_get methodology/policies/models.md`; mesma família em todos vira `same-family` no relatório). Cada um explica pelo código-fonte como a feature funciona, aponta desvio provável com citação e devolve uma receita de verificação ao vivo. Eles nunca dirigem o app e nunca editam arquivo. Formato da resposta: resumo da feature, pontos de entrada no código, desvio provável ou nenhum, uma receita.

### 4. Reconcilie

Cada arquivo de feature tem um resumo de volta. Junte receitas sobrepostas no menor número possível de estados do app. Confira por amostragem os desvios citados, sem reprovar o que veio limpo. Varra a mudança recente (`git log` desde a última manutenção) atrás de superfície visível ao usuário que falta no mapa, e só chame de faltante com um caminho de código concreto.

### 5. Passada ao vivo

Obrigatória mesmo com a fonte limpa. Você dirige tudo, seguindo o modelo de subida da própria skill: uma instância de vida longa dirigida em série para servidor e UI, ou uma sessão isolada nova por direção para CLI de vida curta. Exercite cada feature pelo menos uma vez e segure três invariantes a passada inteira, falhe o que falhar:

1. Nunca dirija instância sem diagnóstico desde a última surpresa: diagnóstico antes da primeira direção, em cada sessão nova, e de novo depois de qualquer direção que falhou. Onde o diagnóstico não enxerga a falha (UI travada com processo saudável), volte a um estado conhecido ou suba de novo.
2. A evidência capturada até ali sobrevive a toda limpeza, conferida no caminho nomeado.
3. Nada que uma direção subiu vive além da utilidade dela. Resíduo de tentativa que falhou é limpo com a sessão travada, encerrada ou compartilhada (na compartilhada, limpe o resíduo e deixe a instância).

Diagnóstico que falha por desvio da skill é desvio: conserte dentro do escopo e tente uma vez de novo, reiniciando só o que o conserto invalidou, antes de chamar de travado. Feature que não dá para alcançar é `verificada-inalcançável` só com a pré-condição concreta (autenticação, permissão, sistema operacional, estado externo) e a rota tentada. Se o mapa omite essa pré-condição, é desvio. Todo conserto de harness roda ao vivo de novo antes de entrar no PR. A derrubada final acontece depois da última direção, inclusive das reprovas, e a evidência fica.

### 6. Triagem

- Descrição errada ou faltando na visão do usuário: desvio de doc, conserte.
- Comportamento que funciona e o harness não dirige: lacuna de harness, conserte, com o script executável e a invocação no corpo da skill.
- Comportamento do app quebrado de fato: lacuna de produto. Relate ao humano e deixe fora do PR.

### 7. Entregue ou pare

No resultado mudou: releia cada arquivo alterado, faça commit e, antes de qualquer push, confirme que existe forge: `gh` está instalado, `gh repo view` passa para o repo e `git remote get-url --push origin` não está desativado (`no_push`, `DISABLED` ou vazio). Se algum falhar, nunca faça push: o PR em draft é a branch local, com o corpo em `.t0/pr/<branch>.md`, e diga isso na resposta. Com forge, faça push sem força e abra um PR em draft só (`gh pr create --draft`). Depois rode `t0 new harness` com "mapa do verify-<app> desatualizado", o link do PR e a lista de desvios, para o Harness Health fechar o item com o PR. No limpo ou no travado: sem PR, relate o resultado e a cobertura com honestidade.

Guarde notas curtas da execução (features cobertas, pré-condições inalcançáveis, desvios confirmados, resultado) num rascunho fora do repo. Nada disso vai para commit.
