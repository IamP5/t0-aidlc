# Criar nota

Criar nota deixa o usuário salvar uma nota com título pelo browser ou pela CLI, cancelar um rascunho e confirmar a nota salva por uma segunda visão do usuário.

## Subfeatures

- `create-open` abre um editor vazio por cada ponto de entrada do browser.
- `create-save` grava título e corpo.
- `create-cancel` descarta um rascunho não terminado no browser.
- `create-cli` cria a mesma nota pelo terminal.

## Como chegar (visão do usuário)

- Escolha o botão `Nova nota` na barra do browser.
- Aperte `n` no browser com o foco fora de campo editável.
- Rode `notes create --title <título> --body <corpo>` no terminal.

## Dirigindo com control-notes

Pré-condições:

- Notas saudável em `http://127.0.0.1:4173`.
- Nenhuma nota com o título `Checklist de release`.
- `control-notes doctor` mostra a URL esperada e o diretório de dados descartável.

- Abrir o editor. Escolha `Nova nota`. Rode `control-notes browser click --role button --name "Nova nota"`. Aparece um formulário `Editor de nota` com o foco na caixa `Título`.
- Preencher. Digite título e corpo. Rode `control-notes browser fill --role textbox --name "Título" --value "Checklist de release"` e `control-notes browser fill --role textbox --name "Corpo" --value "Tag e publicação"`. O botão `Salvar nota` fica habilitado.
- Salvar. Escolha `Salvar nota`. Rode `control-notes browser click --role button --name "Salvar nota"`. Aparece o status `Nota salva` e o título mostra `Checklist de release`.
- Confirmar persistência. Volte à lista e reabra a nota. Rode `control-notes browser click --role link --name "Todas as notas"` e `control-notes browser click --role link --name "Checklist de release"`. O editor mostra os dois valores salvos.
- Cancelar rascunho. Abra uma nota nova, digite `Descarte` e escolha `Cancelar`. Rode `control-notes browser click --role button --name "Nova nota"`, `control-notes browser fill --role textbox --name "Título" --value "Descarte"` e `control-notes browser click --role button --name "Cancelar"`. A lista volta e não tem o link `Descarte`.
- Entrada pela CLI. Crie uma segunda nota. Rode `control-notes cli -- notes create --title "Nota da CLI" --body "Criada no terminal" --format json`. Código de saída `0`, e o stdout traz o ID e o título da nota nova.
- Prova. Reabra as duas notas salvas a partir de `Todas as notas`. Rode `control-notes browser snapshot --aria --path artifacts/create-note/list.aria.txt` e `control-notes browser screenshot --path artifacts/create-note/list.png`. Os artefatos mostram `Checklist de release` e `Nota da CLI`.

## Armadilhas

- Apertar `n` com uma caixa de texto em foco digita a letra em vez de abrir um editor.
- O título é aparado ao salvar. Confira o título exibido, e deixe de lado o valor do rascunho.
- O status de salvo sozinho não prova nada. Reabra a nota pela lista.
- Remova `Checklist de release` e `Nota da CLI` na limpeza dos dados, e guarde os artefatos de prova.
