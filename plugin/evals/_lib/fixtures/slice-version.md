## O que entrega

A flag `--version` no CLI do springboot-plugin.

## Critérios de aceite

- `node scripts/cli.mjs --version` imprime `{"version": "<versão do package.json>"}` e sai com 0.
- `--help` lista a flag `--version`.

## Como verificar

- `node --test tests/*.test.mjs` com o teste novo.
