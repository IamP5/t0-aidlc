import pytest

from t0.redact import RULESET_VERSION, Redacted, RuleKind, redact, scan

# (input, expected output, expected counts) — expected strings written from the rules, not from a run.
CORPUS = [
    ("cpf 529.982.247-25 do cliente", "cpf [CPF] do cliente", {RuleKind.CPF: 1}),
    ("cpf sem pontuação 52998224725.", "cpf sem pontuação [CPF].", {RuleKind.CPF: 1}),
    ("cnpj 11.222.333/0001-81 fornecedor", "cnpj [CNPJ] fornecedor", {RuleKind.CNPJ: 1}),
    ("cnpj 11222333000181", "cnpj [CNPJ]", {RuleKind.CNPJ: 1}),
    ("cartão 4111 1111 1111 1111 recusado", "cartão [CARTAO] recusado", {RuleKind.CARD: 1}),
    ("agência 1234-5 conta 98765-4", "agência [CONTA] conta [CONTA]", {RuleKind.ACCOUNT: 2}),
    ("ag: 0001, c/c 123456", "ag: [CONTA], c/c [CONTA]", {RuleKind.ACCOUNT: 2}),
    ("mande para ana.silva@banco.com.br hoje", "mande para [EMAIL] hoje", {RuleKind.EMAIL: 1}),
    ("ligue (11) 98765-4321 ou +55 21 3456-7890", "ligue [TELEFONE] ou [TELEFONE]", {RuleKind.PHONE: 2}),
    ("token ghp_" + "a" * 36 + " vazou", "token [SEGREDO] vazou", {RuleKind.SECRET: 1}),
    ("chave AKIAABCDEFGHIJKLMNOP", "chave [SEGREDO]", {RuleKind.SECRET: 1}),
    ("senha: hunter22 ok", "senha: [SEGREDO] ok", {RuleKind.SECRET: 1}),
    ('api_key="abcd1234efgh"', 'api_key="[SEGREDO]"', {RuleKind.SECRET: 1}),
    ("Authorization: Bearer abcdefghijklmnopqrstuvwxyz012345", "Authorization: Bearer [SEGREDO]", {RuleKind.SECRET: 1}),
    ("postgres://app:s3cr3tpw@db.interno:5432/x", "postgres://app:[SEGREDO]@db.interno:5432/x", {RuleKind.SECRET: 1}),
    ("jwt eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U fim",
     "jwt [SEGREDO] fim", {RuleKind.SECRET: 1}),
    ("-----BEGIN RSA PRIVATE KEY-----\nMIIEow\nabc\n-----END RSA PRIVATE KEY-----\nresto", "[SEGREDO]\nresto",
     {RuleKind.SECRET: 1}),
]

FALSE_POSITIVES = [
    "cpf inválido 529.982.247-26 não deve sair",
    "cpf repetido 111.111.111-11",
    "cnpj inválido 11.222.333/0001-82",
    "data 2026-10-27T10:00:00-03:00 e hora 10:30",
    "versão 1.2.3 e build 20261027",
    "valor R$ 1.234.567,89 no extrato",
    "Jira PAY-1234 e BET-042",
    "repo git@github.example.bank:t0/payments-api.git",
    "o campo password é obrigatório",
    "password: ${DB_PASSWORD}",
    "token: [SEGREDO]",
    "conta 2026 do ano",
    "pedido 12345678 confirmado",
    "número 4111 1111 1111 1112 não passa no Luhn",
    "uid bet-042 owner human:ana",
]


@pytest.mark.parametrize("raw,expected,counts", CORPUS)
def test_redacts_corpus(raw, expected, counts):
    out, report = redact(raw)
    assert out == expected
    assert report.counts == counts
    assert report.version == RULESET_VERSION


@pytest.mark.parametrize("raw", FALSE_POSITIVES)
def test_false_positives_untouched(raw):
    out, report = redact(raw)
    assert out == raw
    assert report.total == 0
    assert scan(raw) == ()


@pytest.mark.parametrize("raw", [c[0] for c in CORPUS] + FALSE_POSITIVES)
def test_idempotent(raw):
    once, _ = redact(raw)
    twice, report = redact(once)
    assert twice == once
    assert report.total == 0


def test_off_record_spans_removed_and_counted():
    raw = ("início [fora do registro]cpf 529.982.247-25 e fofoca[/fora do registro] meio\n"
           "[FORA DO REGISTRO]\nlinha secreta\n[/Fora do Registro] fim")
    out, report = redact(raw)
    assert "fofoca" not in out and "linha secreta" not in out
    assert out == ("início [trecho fora do registro removido] meio\n"
                   "[trecho fora do registro removido] fim")
    assert report.off_record_spans == 2
    assert report.total == 0


OFF_RECORD_UTTERANCES = [
    ("[09:34] Ana: fora do registro: o fornecedor atrasou de novo.",
     "[09:34] Ana: [trecho fora do registro removido]", 1),
    ("[09:35] Bruno: Fora do registro, cpf 529.982.247-25 do gerente\n[09:36] Ana: voltando à pauta",
     "[09:35] Bruno: [trecho fora do registro removido]\n[09:36] Ana: voltando à pauta", 1),
    ("Carla: FORA DO REGISTRO : isso não sai\nfora do registro, sem orador também some",
     "Carla: [trecho fora do registro removido]\n[trecho fora do registro removido]", 2),
    ("[10:00] Ana: fora do registro: um\n[10:01] Ana: dito [fora do registro]dois[/fora do registro] fim",
     "[10:00] Ana: [trecho fora do registro removido]\n[10:01] Ana: dito [trecho fora do registro removido] fim", 2),
]

OFF_RECORD_MENTIONS = [
    "[09:40] Ana: isso fica fora do registro: combinado?",
    "[09:41] Bruno: a reunião fora do registro foi ontem",
    "Ana: fora do registro foi pedido duas vezes",
]


@pytest.mark.parametrize("raw,expected,spans", OFF_RECORD_UTTERANCES)
def test_off_record_utterance_removed_keeping_speaker(raw, expected, spans):
    out, report = redact(raw)
    assert out == expected
    assert report.off_record_spans == spans
    assert report.total == 0
    again, report2 = redact(out)
    assert again == out and report2.off_record_spans == 0


@pytest.mark.parametrize("raw", OFF_RECORD_MENTIONS)
def test_off_record_mentioned_mid_utterance_is_kept(raw):
    out, report = redact(raw)
    assert out == raw and report.off_record_spans == 0


def test_unclosed_off_record_removes_to_end():
    out, report = redact("antes [fora do registro] tudo isso some")
    assert out == "antes [trecho fora do registro removido]"
    assert report.off_record_spans == 1


def test_scan_reports_position_without_text():
    findings = scan("linha um\nemail: x.y@z.com.br")
    assert [(f.kind, f.line, f.col) for f in findings] == [(RuleKind.EMAIL, 2, 8)]
    assert not hasattr(findings[0], "text")


def test_redacted_cannot_be_constructed_directly():
    with pytest.raises(TypeError):
        Redacted("texto qualquer")
    out, _ = redact("ok")
    assert isinstance(out, Redacted)
