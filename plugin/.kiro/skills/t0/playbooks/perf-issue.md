# Playbook perf-issue

Você é dono da história da medição. Toda correção se amarra a uma medida, e ler código fica como fonte de hipótese, nunca de prova. Este playbook roda dentro do passo de build do `playbooks/slice.md`.

1. Capture um baseline na superfície certa: `verify-<app>`, trace ou benchmark. Antes de confiar no número, confira mesma máquina e mesma carga, aquecimento separado da medida, várias execuções com a variação, e que o número mede o trabalho que você acha que mede. Faça a mesma conferência em todo número seguinte. O passo acaba com o baseline com unidade, variação e caminho do artefato.
2. Leia o subsistema para levantar hipóteses. Teto de performance só se afirma depois de rodar. Tente os mantras na ordem, do mais barato:
   1. Não faça. Pare o trabalho cujo resultado ninguém usa.
   2. Faça, mas não faça de novo.
   3. Faça menos.
   4. Faça depois.
   5. Faça quando ninguém está olhando.
   6. Faça em paralelo.
   7. Faça mais barato.

   Quando um mantra anterior bate a meta, pare.
3. Planeje o fix pelo trace. Se ele cruza fronteira de função, rode `architect` antes. Delegue a implementação a um `t0-agent`, com o modelo do papel na Policy `models`. Revise o diff e capture o trace depois do fix. Verifique cada tentativa antes da próxima (`sequence-verifiable-units`).
4. Compare os artefatos com ferramenta (JSON para sqlite, diff). "Inconclusivo" ou superfície errada conta como falha de verificação, e você sinaliza.
5. Ponha a medida no corpo do PR: o número principal com unidade, `antes → depois`, e o caminho do artefato.
6. Volte ao `slice-build` para provar no app e abrir o PR em draft.

Na resposta: o número do baseline, o número depois do fix, o delta e o caminho do artefato.
