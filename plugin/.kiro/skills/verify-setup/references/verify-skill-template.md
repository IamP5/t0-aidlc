# Esqueleto do verify-<app>

Copie para `.t0/skills/verify-<app>/SKILL.md` e troque cada `<...>` pelo que a entrevista achou. Nenhum `<...>` pode sobrar. Sem o frontmatter, a skill nunca registra.

```markdown
---
name: verify-<app>
description: "Dirige o <app> real pela <superfície> e captura evidência. Use para provar um critério de aceite, reproduzir um bug ou verificar um slice neste repo."
---

# verify-<app>

<Uma frase: o que é o app e qual superfície esta skill dirige. As outras superfícies, se houver.>

Antes de dirigir, leia `features/README.md` e o arquivo da feature que você vai provar.

## Subir

<Comando exato a partir de um diretório de dados vazio, com migrações e seed.>

Pronto quando: <a linha de log, o prompt ou a resposta que prova que o app está usável; processo respondendo ainda não basta>.

Isolamento: <como rodar duas instâncias lado a lado (porta, diretório de dados, perfil), ou "não isola: dirija em série">.

## Diagnóstico

<Um comando só leitura que confere processo no ar, build ou versão certos, porta nossa e autenticação válida, e o que a saída mostra quando está tudo certo.>

Rode antes da primeira direção, em cada sessão nova e depois de qualquer direção que falhou.

## Dirigir

<A receita do harness com seletores e comandos reais deste repo. Alças estáveis: rótulos ARIA, atributos de dados, textos de prompt, rotas.>

## Evidência

Guarde em `<caminho fora do que a limpeza apaga>/<feature>/<run-id>/`.

Padrões de prova:

- exercite o caminho real do usuário, nunca setter interno nem endpoint só de teste;
- capture a ação e o estado resultante, além da tela final;
- confira os efeitos colaterais (arquivo gravado, linha inserida, mensagem enviada) junto com o que aparece;
- mock só onde uma fronteira de produção já isola o sistema externo;
- quando o caminho seguro é um dry-run ou modo de teste, observe o que ele pula de fato (arquivos, rede, refs de git), sem confiar no nome.

<O formato de cada artefato: screenshot e snapshot ARIA para UI; comando, stdout, stderr e código de saída para CLI; corpo e status para API.>

## Limpeza

<Como derrubar exatamente o que esta execução subiu, pelo PID ou pelo nome da sessão que você guardou. Nunca por nome de processo.>

A limpeza remove instâncias e estado de rascunho. A evidência fica no caminho da seção Evidência.

## Helpers

<Cada script em `scripts/`, executável, com a invocação exata. Ou "nenhum".>
```
