from script import carregar

def test_carregar_le_todas_as_entidades():
    entidades = carregar("testes/fixtures/v1.xml")
    assert len(entidades) == 3