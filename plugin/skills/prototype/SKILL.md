---
name: prototype
description: "Constrói um protótipo descartável, fora do main, para responder uma pergunta de uma Idea (lógica e estado, ou cara da UI) e grava o veredito com `t0 idea prototype`. Use para prototipar uma ideia, testar se um modelo de estado faz sentido ou ver opções de tela."
metadata:
  credits: "Baseada em MP prototype (mattpocock-skills 1.3.1, MIT)"
---

# prototype

Protótipo é código descartável que responde uma pergunta, e a pergunta decide o formato. No t0 ele responde a pergunta de uma Idea e termina num veredito: `segue`, `ajusta` ou `mata`. Não pede aprovação e leva de minutos a horas, sozinho ou ao vivo na daily do pod.

## 1. Ache a ideia e escreva a pergunta

O protótipo precisa de uma Idea. Sem `IDEA-NNNN`, siga primeiro para a skill `idea-capture`. Leia a ideia com `t0 kb get <IDEA>`.

Escreva a pergunta em uma frase ("o alerta dispara certo quando o PR volta para draft e sai de novo?"). Ela vai no topo do protótipo e no veredito.

## 2. Escolha o ramo

Descubra qual pergunta está sendo respondida, pelo pedido do usuário, pelo código em volta ou perguntando:

- "Essa lógica, esse modelo de estado, faz sentido?": leia `references/logica.md`. Você monta um HTML único com botões livres e roteiros guiados que empurram o modelo pelos casos difíceis de pensar no papel, e que alguém que não programa consegue usar.
- "Como isso deveria ficar?": leia `references/ui.md`. Você gera algumas variações de UI bem diferentes numa rota só, trocadas por um parâmetro de URL e uma barra flutuante.

Os dois ramos geram artefatos muito diferentes, então errar aqui joga o protótipo fora. Se a pergunta for ambígua e o usuário não estiver por perto, vá pelo código em volta (módulo de backend pede lógica, página ou componente pede UI) e escreva a suposição no topo do protótipo.

## 3. Trabalhe fora do main

O protótipo mora numa branch descartável do repo de produto: `proto/<IDEA>-<slug>`, criada a partir do `main` atualizado. Confira `git branch --show-current` antes da primeira edição. Se você estiver no `main` ou numa branch de slice, crie a branch do protótipo primeiro.

- Ponha o código perto de onde ele seria usado e com `prototype` no nome, para qualquer leitor ver que é protótipo.
- Commite na branch e deixe ela local. Nunca faça push dela, a menos que o usuário peça para compartilhar. A branch do protótipo fica sem PR e nunca vai para o `main`.
- Ideia sem repo de produto ainda: use o ramo de lógica, num HTML único, numa branch `proto/` do repo onde a solução mais provavelmente vai morar. Na dúvida, pergunte qual.

O protótipo em si fica fora do KB. No KB entram só o veredito e a referência.

## 4. Regras dos dois ramos

1. Descartável desde o primeiro minuto, e marcado assim. Na UI, siga a convenção de rotas do projeto.
2. Trivial de rodar: um comando do task runner do projeto (`pnpm <nome>`, `python <caminho>`) ou um HTML que abre com dois cliques.
3. Estado em memória. Persistência entra só quando é ela que a pergunta testa, e aí num banco ou arquivo de rascunho com nome "PROTOTYPE, pode apagar".
4. Sem polimento: sem testes, sem tratamento de erro além do que faz rodar, sem abstração. O objetivo é aprender rápido.
5. Estado à mostra: depois de cada ação (lógica) ou troca de variação (UI), mostre o estado relevante inteiro.
6. Só dados fictícios. Dado de cliente, segredo e credencial real ficam fora do protótipo, porque a branch pode ser compartilhada com o time.

## 5. Entregue

Passe o caminho, o comando ou a URL. Na daily do pod, abra ao vivo. Os momentos que valem são "peraí, isso não devia ser possível" e "achei que X seria diferente": são os bugs da ideia, e achar esses bugs é o objetivo. Se pedirem ação ou cenário novo, acrescente.

## 6. Grave o veredito

Proponha o veredito com o motivo em uma linha e confirme com o usuário (ou com o pod, na daily):

| Veredito | Quando |
|---|---|
| `segue` | a ideia se sustentou e pode virar bet |
| `ajusta` | tem algo ali, mas a pergunta ou a solução muda; diga o quê |
| `mata` | a ideia não se sustenta; o motivo fica registrado para ela voltar só com fato novo |

Faça o commit final na branch do protótipo com a pergunta e a resposta na mensagem, depois rode em dry-run, mostre o plano e rode de verdade:

```
t0 idea prototype <IDEA> --verdict segue|ajusta|mata --ref <repo>@proto/<IDEA>-<slug>:<caminho> --dry-run
```

A decisão validada fica no veredito e na branch do protótipo, e o `main` continua intocado. Quando a ideia virar bet, a `bet-spec` pode citar o trecho de lógica validado (reducer, máquina de estados, schema) avisando que veio do protótipo. O código de verdade nasce num slice, com teste.

## 7. Feche

Responda em pt-BR com a pergunta, a resposta, o veredito, a `--ref` gravada e o próximo passo:

- `segue`: levar para a daily do pod e, se o pod topar, a skill `bet-new` na trilha bet;
- `ajusta`: nova rodada de protótipo, ou a skill `grill` quando o que falta é decisão;
- `mata`: nada mais a fazer.
