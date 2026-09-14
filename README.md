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

Corre em container, agendado diariamente por um systemd timer. Os dados
persistem num volume; as credenciais são injetadas na execução e nunca
entram na imagem.

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

**Uma única dependência de execução**, por escolha deliberada:
`python-dotenv`. Tudo o resto usa a biblioteca padrão. As ferramentas de
teste estão separadas em `requirements-dev.txt` e não entram na imagem.

**Servidor em UTC, acesso só por chave SSH.** Login de root e autenticação
por palavra-passe desativados.

## Configuração

Criar um `.env` na raiz com:

```
URL_ONU=
BREVO_SERVIDOR=
BREVO_PORTA=
BREVO_UTILIZADOR=
BREVO_CHAVE=
REMETENTE=
DESTINATARIO=
```

## Execução

```
docker build -t atalaia .
docker run --rm --env-file .env -v ./dados:/app/dados atalaia
```

As unidades de systemd para o agendamento estão em `deploy/`.

## Testes

```
pip install -r requirements-dev.txt
pytest
```

Os fixtures em `testes/fixtures/` são XML mínimos com alterações conhecidas
— uma remoção, uma adição, uma modificação em vários campos, e uma entidade
inalterada para detetar falsos positivos. Testar contra dados fabricados
evita depender de a fonte real mudar.
