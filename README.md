# Atalaia

Deteção de alterações em listas oficiais de sanções, com alertas por email.

Monitoriza a lista consolidada do Conselho de Segurança da ONU, compara cada
versão publicada com a anterior ao nível da entidade, e envia um email
quando algo muda. Sem alterações, não envia nada.

## Como funciona

1. **Ingestão** — descarrega o XML da fonte oficial e arquiva-o com carimbo
   temporal. O ficheiro bruto nunca é alterado depois de gravado.
2. **Integridade** — calcula o SHA-256 sobre os bytes recebidos e regista
   carimbo, caminho, hash e tamanho.
3. **Deteção de alterações** — compara duas versões entidade a entidade,
   classificando em adições, remoções e modificações. As modificações
   descem ao nível do campo, com valor anterior e novo.
4. **Entrega** — formata o resultado e envia por email.

## Decisões de desenho

**A comparação é ao nível da entidade, não do ficheiro.** O XML da ONU traz
um atributo `dateGenerated` que muda a cada publicação, portanto o hash do
ficheiro difere mesmo quando nada mudou. Comparar texto produziria alertas
falsos todos os dias.

**A identidade é o `REFERENCE_NUMBER`.** Verificado empiricamente: 736
entradas, 736 valores distintos, nenhum em falta. Preferido ao `DATAID`,
igualmente único, por ser o identificador público citado em resoluções — a
sua alteração é custosa para a fonte, enquanto um número de série interno
pode mudar numa migração.

**Ausente, vazio e em branco são a mesma coisa.** A leitura de campos
normaliza os três casos, sem o que a troca de `<CAMPO></CAMPO>` por omissão
da etiqueta geraria uma alteração inexistente.

**Sem duas versões, não há comparação.** Na primeira execução o programa
arquiva e termina, em vez de reportar a lista inteira como adições.

## Configuração

```
URL_ONU=
BREVO_SERVIDOR=
BREVO_PORTA=
BREVO_UTILIZADOR=
BREVO_CHAVE=
REMETENTE=
DESTINATARIO=
```

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python script.py
```

## Estado

Fase 1 em curso: uma fonte de ponta a ponta. Ingestão, deteção e entrega
funcionais; falta containerizar, agendar e pôr a correr num servidor.

Fases seguintes: listas da UE e da OFAC; resumo por LLM restringido ao diff
estruturado, com conjunto de avaliação a correr em CI; painel e API.

As decisões de engenharia e os riscos conhecidos estão em `notas.md`.