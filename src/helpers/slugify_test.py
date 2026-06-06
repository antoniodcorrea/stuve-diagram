from src.helpers.slugify import slugify


def test_lowercases_and_hyphenates():
    assert slugify("Hello World") == "hello-world"


def test_strips_accents_to_ascii():
    assert slugify("Aeródromo de Fuentemilanos") == "aerodromo-de-fuentemilanos"


def test_collapses_runs_of_non_alphanumerics():
    assert slugify("a  --  b") == "a-b"


def test_trims_leading_and_trailing_hyphens():
    assert slugify("  !hi!  ") == "hi"


def test_drops_symbols():
    assert slugify("São Paulo (BR)!") == "sao-paulo-br"


def test_empty_string():
    assert slugify("") == ""
