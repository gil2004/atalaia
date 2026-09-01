import xml.etree.ElementTree as ET
import os 
from dotenv import load_dotenv
import smtplib
from email.message import EmailMessage


load_dotenv()

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

def enviar(corpo):
    mensagem = EmailMessage()
    mensagem["From"] = os.getenv("REMETENTE")
    mensagem["To"] = os.getenv("DESTINATARIO")
    mensagem["Subject"] = "Alterações na lista da ONU"
    mensagem.set_content(corpo)

    with smtplib.SMTP(os.getenv("BREVO_SERVIDOR"), int(os.getenv("BREVO_PORTA"))) as smtp:
        smtp.starttls()
        smtp.login(os.getenv("BREVO_UTILIZADOR"), os.getenv("BREVO_CHAVE"))
        smtp.send_message(mensagem)

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

corpo_email = formatar(adicionados, removidos, modificados)


if corpo_email:
    enviar(corpo_email)



