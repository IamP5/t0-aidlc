# Buscar notas

A busca deixa o usuário achar notas pelo título ou pelo corpo, abrir um resultado e distinguir "nenhum resultado" de "busca indisponível".

## Subfeatures

- `search-open` abre a busca por cada ponto de entrada do browser.
- `search-match` devolve resultados por título e por corpo sem mudar os dados.
- `search-open-result` abre um resultado no editor.
- `search-empty` mostra o estado vazio completo para uma busca sem resultado.
- `search-clear` limpa a busca e volta à visão de notas recentes.
- `search-cli` devolve as mesmas notas pelo terminal.

## Como chegar (visão do usuário)

- Escolha o botão `Buscar` na barra do browser.
- Aperte `/` no browser com o foco fora de campo editável.
- Rode `notes search <termo>` no terminal.

## Dirigindo com control-notes

Pré-condições:

- Notas saudável em `http://127.0.0.1:4173`.
- O diretório de dados descartável tem `Plano trimestral` com o corpo `Rascunho do orçamento`.
- `control-notes doctor` mostra a URL e o diretório de dados esperados.

- Entrada pela barra. Escolha o botão `Buscar`. Rode `control-notes browser click --role button --name "Buscar"`. Aparece o diálogo `Buscar notas` com o foco na caixa de busca.
- Entrada pelo teclado. Feche o diálogo, foque a página e aperte `/`. Rode `control-notes browser press --key "/"`. O mesmo diálogo aparece e a página não insere uma barra.
- Resultado por título. Digite `trimestral`. Rode `control-notes browser fill --role searchbox --name "Buscar notas" --value "trimestral"`. A lista `Resultados` tem `Plano trimestral` e não tem `Lista de compras`.
- Resultado por corpo. Troque a busca por `orçamento`. Rode `control-notes browser fill --role searchbox --name "Buscar notas" --value "orçamento"`. `Plano trimestral` continua visível com um trecho do corpo.
- Abrir resultado. Escolha `Plano trimestral`. Rode `control-notes browser click --role link --name "Plano trimestral"`. O diálogo fecha e o título do editor mostra `Plano trimestral`.
- Estado vazio. Reabra a busca e digite `vulcão`. Rode `control-notes browser fill --role searchbox --name "Buscar notas" --value "vulcão"`. Aparece o status `Nenhuma nota encontrada` quando a busca termina.
- Limpar. Escolha `Limpar busca`. Rode `control-notes browser click --role button --name "Limpar busca"`. A caixa fica vazia e a região `Notas recentes` substitui a lista de resultados.
- Resultado pela CLI. Busque pelo terminal. Rode `control-notes cli -- notes search "trimestral" --format json`. Código de saída `0`, e o stdout traz um objeto com o título `Plano trimestral`.
- Sem resultado pela CLI. Busque um valor ausente. Rode `control-notes cli -- notes search "vulcão" --format json`. Código de saída `0`, e o stdout é `[]`.
- Prova. Capture o estado com resultados. Rode `control-notes browser snapshot --aria --path artifacts/search/results.aria.txt` e `control-notes browser screenshot --path artifacts/search/results.png`. Os dois artefatos identificam o Notas, a busca e `Plano trimestral`.

## Armadilhas

- Apertar `/` com o editor ou a caixa de busca em foco insere texto em vez de abrir a busca.
- Os resultados atualizam depois de um debounce curto. Espere a lista ou o status vazio, em vez de um sleep fixo.
- Notas arquivadas ficam de fora, salvo quando o usuário liga `Incluir arquivadas`.
- A CLI usa saída legível por padrão. Use `--format json` para asserções estáveis.
- Abrir um resultado muda o estado do browser. Reabra a busca antes de provar outra consulta.
