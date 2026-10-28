# Corpo do PR do slice

Use este modelo para o corpo do PR em draft. Sem preâmbulo, prosa curta, termos do glossário do time. Troque cada `<...>` pelo conteúdo real.

```markdown
## Resumo

<diagrama, esboço de diff ou árvore: a menor visão que deixa claro o ponto>

## Evidência

- Antes: <teste vermelho, saída ou screenshot de antes>
  Depois: <o mesmo teste verde, a mesma saída ou screenshot de depois>
- Verificação no app: <feature do mapa do verify-<app>, comando e caminho da evidência>

## Risco de merge

Porta: <uma via ou duas vias>

<opcional: por quê>

Raio de impacto: <uma palavra>

<opcional: o que pode quebrar fora do diff>

## Em minhas palavras

<só em PR de júnior e em todo Tier 2: o texto do autor humano, colado sem edição>

Jira: <KEY>
Tier: <0, 1 ou 2>
Trilha: .audit/<KEY>.tsv
```

## Resumo

Escolha a menor visão que deixa o ponto claro. Coloque cada visual ao lado do texto curto que ele sustenta e mostre só as chamadas, arquivos, props, estados e fronteiras que importam para o ponto. Use uma visão, às vezes várias, quase nunca todas.

- Lógica ou algoritmo vira pseudocódigo:

  ```text
  on(salvar)
    se o conteúdo não mudou
      devolve o resultado em cache
    grava o conteúdo novo
    devolve o resultado novo
  ```

- Fluxo de execução vira árvore de chamadas:

  ```text
  enviarFormulario
    criarSessao
      gravarPrompt
      iniciarAgente
    navegarParaSessao
  ```

- Estrutura de UI vira árvore de componentes, com o estado e as fronteiras de módulo que importam.
- Responsabilidade de arquivo ou refactor amplo vira uma árvore de arquivos rasa.
- Interação entre componentes ou fluxo de dados vira Mermaid (`sequenceDiagram`).
- Quando o ponto é o que muda e a forma em volta já existe, use `diff` no formato do assunto (árvore de componentes, de arquivos, de chamadas ou de estado):

  ```diff
   enviarFormulario
     criarSessao
       gravarPrompt
  +    expandirSkill
       iniciarAgente
  ```

- Mostre o bloco inteiro quando quase tudo é novo, quando cortar contexto esconderia dono ou ordem, ou quando quem revisa precisa de uma forma alvo para copiar.

## Evidência

Prova concreta de que a mudança funciona, sempre com antes e depois. Screenshot é a melhor evidência quando a mudança é visual e o ambiente permite. Evidência de execução vem logo atrás: o teste exato que falhava e agora passa (em pseudocódigo ou com o nome do teste), a saída do console, a saída do `verify-<app>`. Cole a saída real. Nunca escreva "testes passando" sem a saída.

## Risco de merge

Diga se é porta de uma via ou de duas vias. Porta de duas vias dá para voltar atrás: um PR barato de reverter tem risco menor. Mudança com ação destrutiva, migração de dado persistido ou decisão difícil de reverter é porta de uma via.

O raio de impacto é o alcance possível da mudança. Pense em tudo: deslocamento de layout, quebra para consumidores, contrato público, dados de cliente, permissões de agente, outros repos da bet.

## Em minhas palavras

Obrigatória em PR de autor júnior e em todo Tier 2. Quem escreve é o autor humano, com as próprias palavras: o que muda, por que, e o que pode dar errado. O agente nunca escreve esta seção. Peça o texto ao autor e cole sem editar. Enquanto o autor não mandar, deixe `[PRECISA DO AUTOR]` no lugar. Fora desses casos, apague a seção.

## Rodapé

As três linhas finais são lidas pelo CI e pelo `t0 ci <KEY>`. Mantenha o formato exato: `Jira: <KEY>`, `Tier: <n>`, `Trilha: .audit/<KEY>.tsv`, uma por linha.

O menu de visuais do Resumo vem do skill `show-me` de Dex Horthy (Humanlayer), por meio do MP `pr`.
