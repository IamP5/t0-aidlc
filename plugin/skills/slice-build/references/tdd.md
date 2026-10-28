# TDD nas costuras do spec

Leia antes do primeiro teste e volte aqui a cada ciclo.

## Teste bom

O teste verifica comportamento pela interface pública. O código pode mudar inteiro e o teste continua de pé. Um teste bom lê como especificação: "pedido parado há mais de 24h úteis entra no aviso" diz exatamente que capacidade existe.

Características:

- testa o comportamento que importa para quem chama;
- usa só a API pública;
- sobrevive a refactor interno;
- descreve o quê, e deixa o como para o código;
- uma asserção lógica por teste.

```typescript
// BOM: verifica pela interface
test("createUser deixa o usuário recuperável", async () => {
  const user = await createUser({ name: "Alice" });
  const retrieved = await getUser(user.id);
  expect(retrieved.name).toBe("Alice");
});
```

## Antipadrões

- Acoplado à implementação: mocka colaborador interno, testa método privado, conta chamadas ou verifica por canal lateral (consultar o banco em vez de usar a interface). O sinal: o teste quebra num refactor sem mudança de comportamento.
- Tautológico: a asserção recalcula o valor esperado do mesmo jeito que o código (`expect(soma(a, b)).toBe(a + b)`), então passa por construção e nunca discorda do código. O valor esperado vem de uma fonte independente: um literal conhecido, um exemplo trabalhado, uma linha do spec.
- Fatia horizontal: escrever todos os testes primeiro e depois toda a implementação. Teste em lote verifica comportamento imaginado. Trabalhe em fatia vertical: um teste, uma implementação, repete. Cada teste é uma tracer bullet que responde ao que o ciclo anterior ensinou.

```typescript
// RUIM: o esperado repete a implementação
test("calculateTotal soma os itens", () => {
  const items = [{ price: 10 }, { price: 5 }];
  const expected = items.reduce((s, i) => s + i.price, 0);
  expect(calculateTotal(items)).toBe(expected);
});

// BOM: literal independente
test("calculateTotal soma os itens", () => {
  expect(calculateTotal([{ price: 10 }, { price: 5 }])).toBe(15);
});
```

## Quando mockar

Mocke só nas fronteiras do sistema: API externa, banco (às vezes, prefira banco de teste), tempo e aleatoriedade, sistema de arquivos (às vezes). Seus próprios módulos e colaboradores internos rodam de verdade.

Para a fronteira ser fácil de trocar por um fake:

- injete a dependência em vez de criá-la por dentro (`processarPagamento(pedido, clientePagamento)`);
- prefira uma interface no estilo SDK, uma função por operação externa (`getUser`, `createOrder`), a um `fetch` genérico que obriga lógica condicional dentro do mock.

## Regras do ciclo

- Vermelho antes de verde. Escreva o teste que falha, rode, veja falhar pelo motivo certo e guarde a saída. Só então escreva o mínimo de código para passar.
- Uma fatia por vez: uma costura, um teste, uma implementação mínima por ciclo.
- Teste só nas costuras que o spec combinou. Costura nova que você acha que precisa vira pergunta no PR, à vista do revisor.
- Refactor fica fora do ciclo. Ele entra depois do verde, com a suíte toda verde antes e depois.
