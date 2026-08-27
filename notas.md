# Atalaia — notas do projeto

## Fonte
Lista consolidada do Conselho de Segurança da ONU, formato XML.
Ficheiro de trabalho: consolidatedLegacyByPRN.xml

## 2026-08-25 — exploração da fonte

### Medições
- 736 indivíduos (INDIVIDUALS/INDIVIDUAL).
- DATAID: 736 distintos, nenhum em falta.
- REFERENCE_NUMBER: 736 distintos, nenhum em falta.
- FIRST_NAME: 550 distintos — nomes repetem-se, não servem como identidade.

### Decisão de arquitetura: chave de identidade
Escolhido o REFERENCE_NUMBER. Ambos os candidatos são únicos e completos,
logo os dados não desempatam. O REFERENCE_NUMBER é o identificador público
citado em resoluções e documentos oficiais externos, o que torna a sua
alteração custosa para a fonte. O DATAID é um número de série interno, sem
dependências externas, e portanto mais exposto a mudar numa migração.

## 2026-08-27 — deteção de alterações

### Conjunto de teste fabricado
xml2.xml foi criado a partir de xml1.xml com três alterações deliberadas:
- Removido: CDi.001
- Adicionado: CDi.999 (bloco duplicado com REFERENCE_NUMBER e DATAID novos)
- Modificado: CDi.003, campo GENDER (Male -> Female)
- Chaves comuns às duas versões: 735; sem alterações: 734
- Total em ambos os ficheiros: 736

### Implementação
- carregar(caminho) devolve um dicionário indexado por REFERENCE_NUMBER,
  em que cada valor é um dicionário com os campos da entidade.
- Adições e remoções por diferença de conjuntos sobre as chaves.
- Modificações: para as chaves comuns, comparação dos registos e, quando
  diferem, comparação campo a campo.
- Saída: {referência: {campo: {"old": valor, "new": valor}}}
  Contém apenas os campos que mudaram — é a entrada da camada de LLM e o
  que garante que o resumo é rastreável a um campo alterado.

### Verificado
Os três tipos de alteração são detetados corretamente contra o conjunto de
teste, sem falsos positivos nas restantes entidades.

## Riscos e verificações pendentes
- A raiz do XML tem um atributo dateGenerated que muda a cada publicação.
  O hash do ficheiro bruto serve para integridade e versionamento, não para
  decidir se houve alterações — isso compete à comparação por entidade.
- A função texto() devolve "" tanto para campo ausente como para etiqueta
  mal escrita, portanto erros de nome de campo são silenciosos.
  Mitigação: teste que falha se um campo esperado vier vazio em 100% das
  entradas.
- O número de chaves no dicionário tem de igualar o número de nós
  INDIVIDUAL. Divergência significa chave duplicada com sobreposição
  silenciosa de uma entidade.
- Se a fonte renumerar os identificadores, o diff reporta remoções e adições
  em massa. É preciso um limite que recuse processar nesse caso.
- O ciclo de campos percorre as chaves da versão nova. Campos removidos do
  esquema passam despercebidos; campos novos provocam KeyError.
  Solução: percorrer a união das chaves das duas versões.

## Por fazer
- Estender o parser a ENTITIES (esquema parcialmente diferente do de
  INDIVIDUALS).
- Alargar de 4 para todos os campos relevantes, incluindo listas (alcunhas,
  moradas, documentos), que não têm identificador próprio e exigem
  comparação por conjunto de valores normalizados.
- Ingestão agendada com armazenamento imutável, hash e timestamp.
- Envio de email.