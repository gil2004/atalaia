# Atalaia — notas do projeto

Monitorização de alterações em fontes oficiais de sanções e controlo de
exportações. Fonte inicial: lista consolidada do Conselho de Segurança da
ONU (XML).

## Decisões

**Chave de identidade: REFERENCE_NUMBER.**
DATAID e REFERENCE_NUMBER são ambos únicos e completos (736/736), logo os
dados não desempatam. O REFERENCE_NUMBER é citado em resoluções e documentos
oficiais externos, o que torna a sua alteração custosa para a fonte; o
DATAID é um número de série interno, exposto a mudar numa migração.

**Armazenamento: dados/ONU_2026-09-02T030000.xml.**
Carimbo ISO sem dois pontos ordena por nome pela mesma ordem que por data,
logo a versão anterior descobre-se listando a pasta. Alternativa preterida:
subpasta por fonte — custo é filtrar por prefixo com três fontes juntas.

**Hash SHA-256** sobre os bytes recebidos, antes de gravar, guardado num
registo à parte com data, nome, hash e tamanho. Não deteta alterações
(dateGenerated muda sempre); prova integridade do arquivo, compara
conteúdos e rastreia entre que versões um alerta foi gerado.

**Email via Brevo, por SMTP e não pelo SDK.**
Brevo por alojar na UE, 300 emails/dia grátis e permitir enviar sem domínio
verificado. SMTP com smtplib evita uma dependência e mantém o código
portável entre fornecedores. Alternativa: Resend, preterida por ser
norte-americana e centrada em React.

**Segredos e configuração em .env**, fora do git, lidos por variáveis de
ambiente. Um segredo que entra no histórico não sai mais. Chave SMTP
dedicada e revogável, não palavra-passe de conta.

**Uma leitura por fonte, resto partilhado.**
As três listas têm conteúdos distintos e esquemas diferentes mesmo sendo
todas XML. Cada leitor normaliza para a mesma estrutura interna;
comparação, formatação e envio são comuns. Sem deduplicação entre fontes.

## Medições (2026-08-25, versão da lista da ONU dessa data)
736 indivíduos. DATAID e REFERENCE_NUMBER: 736 distintos, nenhum em falta.
FIRST_NAME: 550 distintos — nomes não servem como identidade.

## Conjunto de teste
xml2.xml derivado de xml1.xml com três alterações conhecidas:
removido CDi.001, adicionado CDi.999, modificado CDi.003 (GENDER
Male → Female). 735 chaves comuns, 734 sem alterações.
Os três tipos são detetados corretamente, sem falsos positivos.
Guardar cópia fora da pasta de trabalho — é o primeiro caso do conjunto de
avaliação e não se recupera.

## Riscos
- texto() devolve "" tanto para campo ausente como para etiqueta mal
  escrita: erros de nome de campo são silenciosos. Teste: falhar se um
  campo esperado vier vazio em 100% das entradas.
- Nº de chaves tem de igualar o nº de nós INDIVIDUAL; divergência significa
  chave duplicada com sobreposição silenciosa.
- Renumeração da fonte produz remoções e adições em massa: é preciso um
  limite que recuse processar.
- O ciclo de campos percorre as chaves da versão nova: campos removidos
  passam despercebidos, campos novos dão KeyError. Usar a união.
- Distinguir "não houve alterações" de "não consegui verificar". Uma falha
  de ingestão não pode produzir o mesmo silêncio que um dia sem novidades.
- Chave SMTP expira a 2027-08-27. Um sistema de alertas que deixa de
  alertar falha em silêncio.

## Dívida técnica
- Envio sem domínio verificado; produção exige SPF, DKIM e DMARC.
- Chave SMTP sem restrição por IP; ativar quando houver IP fixo.
- os.getenv devolve None em silêncio; configuração obrigatória devia falhar
  cedo.

## Por fazer
- Descarregamento automático com hash e gravação.
- Agrupar adicionados/removidos/modificados numa estrutura única.
- Container, agendamento, máquina que não seja o portátil.
- Testes com pytest e fixtures XML mínimos, versionados no repositório.
- Publicar no GitHub com README.
- Estender a ENTITIES e a todos os campos, incluindo listas sem
  identificador próprio (alcunhas, moradas).