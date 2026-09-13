from script import carregar, comparar

def test_carregar_le_todas_as_entidades():
    entidades = carregar("testes/fixtures/v1.xml")
    assert len(entidades) == 3

def test_deteta_remocao():
    antiga = carregar("testes/fixtures/v1.xml")
    nova = carregar("testes/fixtures/v2.xml")
    adicionados, removidos, modificados = comparar(antiga, nova)
    assert removidos == {"TSi.001"}

def test_deteta_adicao():
    antiga = carregar("testes/fixtures/v1.xml")
    nova = carregar("testes/fixtures/v2.xml")
    adicionados, removidos, modificados = comparar(antiga, nova)
    assert adicionados == {"TSi.999"}

def test_deteta_modificacao():
    antiga = carregar("testes/fixtures/v1.xml")
    nova = carregar("testes/fixtures/v2.xml")
    adicionados, removidos, modificados = comparar(antiga, nova)
    assert modificados["TSi.003"]["gender"] == {"old": "Female", "new": "Male"}

def test_nao_deteta_modificacao():
    antiga = carregar("testes/fixtures/v1.xml")
    nova = carregar("testes/fixtures/v2.xml")
    adicionados, removidos, modificados = comparar(antiga, nova)
    assert "Tsi.002" not in modificados