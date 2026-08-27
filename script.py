import xml.etree.ElementTree as ET


def texto(no_pai, etiqueta):
    no = no_pai.find(etiqueta)

    if no is None:
        return ""

    return (no.text or "").strip()

def carregar(caminho):
    arvore = ET.parse(caminho)
    raiz = arvore.getroot()

    individuos = raiz.findall("INDIVIDUALS/INDIVIDUAL")

    entidades = {}

    for individuo in individuos:
        ref = texto(individuo, "REFERENCE_NUMBER")
        pessoa = {
            "first_name": texto(individuo, "FIRST_NAME"),
            "second_name": texto(individuo, "SECOND_NAME"),
            "listed_date": texto(individuo, "LISTED_ON"),
            "gender": texto(individuo, "GENDER")
        }
        entidades[ref] = pessoa

    return entidades

def formatar(adicionados, removidos, modificados):
    resultado = ""

    if adicionados:
        resultado += "Adicionados:\n"
        for ref in adicionados:
            resultado += f"  {ref}\n"

    if removidos:
        resultado += "Removidos:\n"
        for ref in removidos:
            resultado += f"  {ref}\n"

    if modificados:
        resultado += "Modificados:\n"
        for ref, campos in modificados.items():
            resultado += f"  {ref}:\n"
            for campo, valores in campos.items():
                resultado += f"    {campo}: {valores['old']} -> {valores['new']}\n"

    return resultado

antiga = carregar("xml1.xml")
nova = carregar("xml2.xml")
comuns = antiga.keys() & nova.keys()
adicionados = nova.keys() - antiga.keys()
removidos = antiga.keys() - nova.keys()

modificados = {}
for ref in comuns:
    if antiga[ref] != nova[ref]:
        campos = {}
        for campo in nova[ref]:
            if antiga[ref][campo] != nova[ref][campo]:
                campos[campo] = {
                    "old": antiga[ref][campo],
                    "new": nova[ref][campo]
                }
        modificados[ref] = campos


print(formatar(adicionados, removidos, modificados))

