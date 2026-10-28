# Playbook bet

Bet: ideia com veredito `segue` e apetite de até 2 semanas. Passa por aposta, spec, desenho quando precisa, e slices. Spec e slices vão no mesmo PR. Duas das três decisões humanas moram aqui: aposta e spec.

1. Confirme na Idea o veredito `segue` com `prototype_ref`. Sem protótipo, volte para `playbooks/ideia.md`.
2. Rode `bet-new bet <IDEA>`. Ela roda `t0 new bet --track bet` e abre o PR da aposta em draft. O `t0 gate aposta --ci` exige o Lead quando a bet cruza pods, é Tier 2 ou passa de 1 semana de apetite.
3. Pare até a aposta ser aprovada. Entregue o link e diga quem decide: o Bet Owner, e o Lead nos três casos do passo 2.
4. Com a bet `active`, rode `grill` com o pod sobre o problema e os termos. Termo vai para `glossary/`. Decisão difícil de desfazer vira ADR por `t0 new adr`.
5. Rode `bet-spec <BET>`. O spec sai do Template, com Critérios de aceite em bullets, Como verificar, Tier e as costuras de teste.
6. Se o desenho cruza fronteira de função ou não tem precedente no repo, rode `architect`, que usa `arena` para comparar candidatos. Ela para no desenho e espera o ok. A saída vai para a seção Design do spec e para um ADR. Desenho óbvio fica com `pular: <por quê>`.
7. Rode `bet-slice <BET>`. Um arquivo por slice, na branch do spec, no mesmo PR.
8. Rode `t0 gate spec <BET> --dry-run` e mostre o resultado. Marcador `[PRECISA ESCLARECER]` aberto volta para o passo 4 ou 5.
9. Pare. O spec é decisão humana: o Bet Owner aprova o PR, e o Lead também em Tier 2.
10. Depois do merge, o CI roda `t0 jira sync` e os slices ficam `ready`. Cada slice segue por `playbooks/slice.md`.

Kill só quando a pessoa pedir: `t0 log kill "<motivo>" --bet <BET>`.

Na resposta: o link do PR da aposta ou do spec, quem decide, os marcadores abertos, os slices com o tier de cada um, os ADRs propostos e o rótulo `same-family` quando a `arena` rodou numa família só.
