# Protótipo de UI

Gere algumas variações de UI bem diferentes numa rota só, trocadas por uma barra flutuante. O usuário alterna entre elas no navegador, escolhe uma (ou junta pedaços de várias) e o resto vai fora.

Se a pergunta é sobre lógica ou estado, o ramo certo é `logica.md`.

## Duas subformas: prefira a A

Variação de UI se julga melhor encostada no resto do app: header real, sidebar real, dados reais, densidade real. Uma rota isolada é um vácuo onde toda variação parece boa.

- Subforma A, ajuste numa página que existe (padrão). As variações aparecem na mesma rota, escolhidas pelo parâmetro `?variant=`. Busca de dados, parâmetros e auth continuam iguais; só a renderização muda. Algo novo que moraria dentro de uma página existente (uma seção nova, um card novo, um passo novo num fluxo) também é subforma A.
- Subforma B, página nova (último recurso). Só quando a coisa não tem página onde morar. Crie uma rota descartável seguindo a convenção do projeto, com `prototype` no caminho ou no nome, e o mesmo `?variant=`. Antes, confira se não existe mesmo uma página onde embutir.

## 1. Escreva a pergunta e escolha N

O padrão são 3 variações; o teto é 5. Escreva o plano em uma linha num comentário no topo:

> "Três variações da página de status do review, trocadas por `?variant=`, na rota `/reviews` que já existe."

## 2. Gere variações bem diferentes

Cada variação respeita o propósito da página e os dados que ela tem, usa a biblioteca de componentes do projeto e exporta um nome claro (`VariantA`, `VariantB`, `VariantC`).

As variações divergem em estrutura: layout, hierarquia de informação e ação principal diferentes. Três grades de cards com cores diferentes são papel de parede. Se duas saírem parecidas, refaça uma com a instrução explícita de largar o padrão da outra.

## 3. Ligue as variações

Um componente de troca na rota:

```tsx
// pseudocódigo, adapte ao framework do projeto
const variant = searchParams.get('variant') ?? 'A';
return (
  <>
    {variant === 'A' && <VariantA {...data} />}
    {variant === 'B' && <VariantB {...data} />}
    {variant === 'C' && <VariantC {...data} />}
    <PrototypeSwitcher variants={['A', 'B', 'C']} current={variant} />
  </>
);
```

Na subforma A, a busca de dados continua acima do switcher e só a subárvore renderizada muda.

## 4. A barra flutuante

Uma barra pequena, fixa no centro de baixo da tela, com seta para a variação anterior, o rótulo da atual (`B (layout com sidebar)`) e seta para a próxima, ambas dando a volta.

- A seta atualiza o parâmetro da URL pelo router do framework, para a variação ser compartilhável e sobreviver ao reload.
- As teclas `←` e `→` também trocam, exceto com foco em `<input>`, `<textarea>` ou `[contenteditable]`.
- Visual bem distinto da página (pílula de alto contraste, sombra leve), para ninguém confundir com o design avaliado.
- Escondida em build de produção, com `process.env.NODE_ENV !== 'production'` ou equivalente.

## 5. Entregue

Passe a URL e as chaves de `?variant=`. O retorno que mais vale costuma ser "quero o header da B com a sidebar da C": esse é o design que o usuário quer.

## 6. Depois da resposta

Grave qual variação venceu e por quê no veredito. Todas as variações e o switcher ficam na branch `proto/`, que é a fonte primária. A versão de verdade da vencedora é reescrita num slice, com teste e tratamento de erro, porque o código da variação foi feito sob regra de protótipo.

## Armadilhas

- Variações que mudam só cor ou texto.
- Código demais compartilhado entre variações: um `<Header>` comum tudo bem, um `<Layout>` comum mata a comparação.
- Variação ligada a mutação real: aponte para um stub. A pergunta é como a tela fica, e o backend fica para depois.
