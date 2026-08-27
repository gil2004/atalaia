# Atalaia — notas do projeto

Sistema de monitorização de alterações em fontes oficiais de sanções e
controlo de exportações.

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
- formatar() converte o diff em texto legível. Secções vazias não são
  impressas; sem alterações, devolve string vazia e não se envia email.

### Verificado
Os três tipos de alteração são detetados corretamente contra o conjunto de
teste, sem falsos positivos nas restantes entidades.

## 2026-08-27 — decisões de infraestrutura

### Higiene do repositório
Os ficheiros XML tinham entrado nos primeiros commits. O histórico foi
recriado do zero (remoção da pasta .git e novo git init) com .gitignore
em vigor desde o primeiro commit. O .gitignore cobre .env, *.xml e
__pycache__/.
Os ficheiros de dados não pertencem ao repositório de código: a versão de
trabalho vem sempre da fonte, e o histórico de versões terá o seu próprio
armazenamento com hash e timestamp.

### Envio de email: escolha do fornecedor
Escolhido o Brevo, por três razões:
- Dados alojados na UE, coerente com o RGPD e com o domínio do projeto.
- Plano gratuito de 300 emails/dia sem cartão de crédito; o sistema envia
  no máximo um por dia.
- Permite enviar sem domínio verificado, o que desbloqueia o
  desenvolvimento imediato.
Alternativa considerada: Resend (3.000/mês, API mais moderna), preterida
por ser norte-americana e por a integração forte ser com React.

### Envio por SMTP e não pelo SDK do fornecedor
Usado o smtplib da biblioteca padrão contra o relé SMTP do Brevo, em vez
do SDK. Evita uma dependência e mantém o código portável: trocar de
fornecedor implica mudar endereço e credenciais, não reescrever o envio.
Mesmo critério que levou a preferir xml.etree ao lxml.

### Gestão de segredos
Credenciais em variáveis de ambiente lidas de um .env fora do controlo de
versões, nunca no código. Motivo: um segredo que entra no histórico do git
não sai mais, mesmo que seja apagado depois.
Usada uma chave SMTP dedicada e revogável, não uma palavra-passe de conta
— princípio do menor privilégio.

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

## Dívida técnica assumida
- Envio sem domínio verificado. Prejudica a entregabilidade a prazo,
  sobretudo com o Gmail. Em produção exige domínio próprio autenticado
  com SPF, DKIM e DMARC.
- Chave SMTP sem restrição por IP. Não ativada porque o IP doméstico é
  dinâmico; ativar quando o sistema passar para servidor com IP fixo.

## Por fazer
- Envio de email por SMTP com credenciais em variáveis de ambiente.
- Ingestão agendada com armazenamento imutável, hash e timestamp.
- Estender o parser a ENTITIES (esquema parcialmente diferente do de
  INDIVIDUALS).
- Alargar de 4 para todos os campos relevantes, incluindo listas (alcunhas,
  moradas, documentos), que não têm identificador próprio e exigem
  comparação por conjunto de valores normalizados.