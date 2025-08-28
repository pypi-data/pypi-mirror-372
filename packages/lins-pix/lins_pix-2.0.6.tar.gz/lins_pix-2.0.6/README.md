# Pacote PIX

Principais dependências:

![](https://img.shields.io/badge/Python-v3.0+-blue)

Pacote pela integração do meio de pagamento PIX do banco Santader.

## Projetos relacionados

- Sem dependência de outro projeto.

## Variáveis de Ambiente Necessárias

- Não se aplica.

## Como configurar o Pacote em Serviço

### Instalação

Comando:

```sh
pip install lins-pix
```

### Importação

- **Cob**: Para instanciar as cobranças

INSTALLED_APPS:


    'lins_pix',


Código:

```python
from lins_pix.psp.santander.cob import Cob
```

## Utilização

### 1) Gerar Cobrança

#### Exemplo:

Código:

```python
from lins_pix.psp.santander.cob import Cob

'''
exemplo de body válido
body = {
            'calendario': {
                'expiracao': '300' #Tempo de 6 minutos
            },
            'devedor': {
                'cnpj': '11258313000160', #cnpj do pagador
                'nome': 'Devedor teste'  #nome do devedor
            },
            'valor': {
                'original': "0.10" #valor da cobrança
            },
            'chave': '40401210000188', #chave pix da empresa
            'solicitacaoPagador': 'Pagamento teste',
            'infoAdicionais': [{"nome": "Pagamento", "valor": "Parcela 1"}]
}
'''
cobranca = Cob()
cobranca.criar_cobranca_put(txid, body, url, cert, client_id, client_secret)



```

#### Parâmetros Obrigatórios:

- txid, string, única entre 27 e 35 caracteres de controle interno do utilizador
- body
- url, url https fornecida pelo banco Santader
- cert, tupla com o endereço do certificado.pem e do certificadokey.pem
- client_id, definido pelo Santander
- client_secret, definido pelo Santader.
#### 2) Consultar Cobrança 

- Consulta de uma cobrança expecífica.

Exemplo:

```python
from lins_pix.psp.santander.cob import Cob
cobranca = Cob()
cobranca.consultar_cobranca_get(txid, url, cert, client_id, client_secret)
```

#### Parâmetros Obrigatórios:

- txid, string utilizada na criação de uma consulta
- url, url https fornecida pelo banco Santader
- cert, tupla com o endereço do certificado.pem e do certificadokey.pem
- client_id, definido pelo Santander
- client_secret, definido pelo Santader.

#### 3) Consultar  lista Cobrança 

- Consulta de cobranças realizadas realizadas em um determinado período.

Exemplo:

```python
from lins_pix.psp.santander.cob import Cob
cobranca = Cob()
cobranca.consultar_lista_cobranca_get(inicio, fim, body, url, cert, client_id, client_secret)
```

#### Parâmetros Obrigatórios:

- inicio, data em formato de string. Exemplo: '2020-12-09T08:00:00Z'
- fim, data, maior que a data de início em formato de string. Exemplo: '2021-12-09T23:00:00Z'
- body, dicionário de dados podento conter: cpf ou cnpj, status, paginaAtual(inteiro, default=0), 
    itensPorPagina(inteiro, default=100)
- url, url https fornecida pelo banco Santader
- cert, tupla com o endereço do certificado.pem e do certificadokey.pem
- client_id, definido pelo Santander
- client_secret, definido pelo Santader.
