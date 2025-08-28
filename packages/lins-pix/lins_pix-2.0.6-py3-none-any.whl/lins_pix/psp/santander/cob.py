# python3 setup.py sdist upload -r testpypi
# pip install -i https://test.pypi.org/simple/ lins_pix==0.0.14
# requests~=2.25.1
# urllib3~=1.26.4
# PyJWT~=1.7.1
# websocket-client~=0.53.0

"""
Reúne endpoints destinados a lidar com gerenciamento de cobranças imediatas
"""

from lins_pix.psp.santander.autenticacao import Autenticacao


def checa_validade_dados(body):
    """Verifica validade dos dados e caso positivo
    retorna os dados em um dicionario
    """
    try:
        valor = body['valor']["original"]
        try:
            tipo_pessoa = "cnpj"
            doc_pessoa = body['devedor']["cnpj"]
        except:
            doc_pessoa = body['devedor']["cpf"]
            tipo_pessoa = "cpf"

        nome = body['devedor']["nome"]
        expiracao = body['calendario']['expiracao']
        info_adicionais = body['infoAdicionais']
        chave = body['chave']
        solicitacao_pagador = body['solicitacaoPagador']

        data = {
            "calendario": {
                "expiracao": expiracao
            },
            "devedor": {
                tipo_pessoa: doc_pessoa,
                "nome": nome
            },
            "valor": {
                "original": valor
            },
            "chave": chave,
            "solicitacaoPagador": solicitacao_pagador,
            "infoAdicionais": info_adicionais,
        }
        data = str(data).replace("'", '"')
        return data
    except:

        return False


class Cob:

    def __init__(self, verify: bool = True):
        self.api = Autenticacao()
        self.access_token = self.api.get_token()

    def criar_cobranca_put(
            self,
            txid: str,
            body: dict,
            url: str = None,
            cert: str = None,
            client_id: str = None,
            client_secret: str = None,
            verify: bool = True,
            *args,
            **kwargs):
        """
        TXID entre 27 e 35 caracteres
        Criar cobrança imediata.
        Endpoint para criar uma cobrança imediata.
        PUT - /cob/{txid}

        Status code tratados:
        201 (sucesso) - Cobrança imediata criada.
        400 (erro) - Requisição com formato inválido.
        403 (erro) - Requisição de participante autenticado que viola alguma regra de autorização.
        404 (erro) - Recurso solicitado não foi encontrado.
        503 (erro) - Serviço não está disponível no momento. Serviço solicitado pode estar em manutenção ou fora da janela de funcionamento.
        """
        data = checa_validade_dados(body)
        if not data or len(txid) < 27:
            result = {
                "title": "Cobrança inválida.",
                "status": 400,
                "detail": "A requisição que busca alterar ou criar uma cobrança para pagamento imediato não respeita o "
                          "schema ou está semanticamente errada."
            }
            return result, 400

        if not self.access_token:
            self.access_token, santander_response = self.api.get_token(force=True)

            if not self.access_token:
                try:
                    response_data = santander_response.json()
                except:
                    response_data = santander_response.text
                result = {
                    "title": "Erro ao autenticar",
                    "status": 400,
                    "detail:": "Erro na autenticação na api do Santader.",
                    "santander_response": response_data,
                    "santander_url": santander_response.url,
                    "santander_status_code": santander_response.status_code
                }
                return result, 400

        headers = {
            'Authorization': 'Bearer {}'.format(self.access_token),
            'Content-Type': 'application/json'
        }

        url = url if url else self.api.url
        url += "/api/v1/cob/{}".format(str(txid))

        result = self.api.make_request(
            method="PUT",
            url=url,
            headers=headers,
            payload=data
        )
        return result.text, result.status_code

    def consultar_cobranca_get(
            self,
            txid: str,
            url: str = None,
            cert: str = None,
            client_id: str = None,
            client_secret: str = None,
            verify: bool = True,
            *args,
            **kwargs):
        """
        Consultar cobrança imediata.
        Endpoint para consultar uma cobrança através de um determinado txid.
        GET - /cob/{txid}

        Status code tratados:
        200 (sucesso) - Dados da cobrança imediata.
        400 (erro) - Erro na autenticação na api do Santader
        403 (erro) - Requisição de participante autenticado que viola alguma regra de autorização.
        404 (erro) - Recurso solicitado não foi encontrado.
        503 (erro) - Serviço não está disponível no momento. Serviço solicitado pode estar em manutenção ou
         fora da janela de funcionamento.
        """
        if len(txid) < 27:
            result = {
                "title": "Cobrança inválida.",
                "status": 400,
                "detail": "Quantidade de caracteres do TXID inválido."
            }
            return result, 400

        if not self.access_token:
            self.access_token, santander_response = self.api.get_token(force=True)

            if not self.access_token:
                try:
                    response_data = santander_response.json()
                except:
                    response_data = santander_response.text
                result = {
                    "title": "Erro ao autenticar",
                    "status": 400,
                    "detail:": "Erro na autenticação na api do Santader.",
                    "santander_response": response_data,
                    "santander_url": santander_response.url,
                    "santander_status_code": santander_response.status_code
                }
                return result, 400

        url = url if url else self.api.url
        url += "/api/v1/cob/{}".format(str(txid))

        headers = {
            'Authorization': 'Bearer {}'.format(self.access_token),
            'Content-Type': 'application/json'
        }

        result = self.api.make_request(
            method="GET",
            url=url,
            headers=headers
        )
        return result.text, result.status_code

    def consultar_lista_cobranca_get(
            self,
            inicio,
            fim,
            body: dict,
            url: str = None,
            verify: bool = True,
            *args, 
            **kwargs):
        """Não definido pela área de negócio

        Todas as entradas são no formato de string e tem como campo obrigatório inicio e fim.
        O Body deve trazer um dicionario com as seguintes opções:
        cpf ou cnpj, locationPresent, status, paginaAtual, itensPorPagina

        Consultar lista de cobranças imediatas.
        Endpoint para consultar cobranças imediatas através de parâmetros como início, fim, cpf, cnpj e status.
        GET - /cob

        Status code tratados:
        200 (sucesso) - Lista de cobranças imediatas.
        403 (erro) - Requisição de participante autenticado que viola alguma regra de autorização.
        503 (erro) - Serviço não está disponível no momento. Serviço solicitado pode estar em manutenção ou fora da 
        janela de funcionamento.
        """
        if not self.access_token:
            self.access_token, santander_response = self.api.get_token(force=True)

            if not self.access_token:
                try:
                    response_data = santander_response.json()
                except:
                    response_data = santander_response.text
                result = {
                    "title": "Erro ao autenticar",
                    "status": 400,
                    "detail:": "Erro na autenticação na api do Santader.",
                    "santander_response": response_data,
                    "santander_url": santander_response.url,
                    "santander_status_code": santander_response.status_code
                }
                return result, 400

        headers = {
            'Authorization': 'Bearer {}'.format(self.access_token),
            'Content-Type': 'application/json'
        }

        url = url if url else self.api.url
        url += "/api/v1/pix/" + '?inicio=' + inicio + '&fim=' + fim

        if body:
            for item in body:
                url += '&{}={}'.format(item, body[item])

        result = self.api.make_request(
            method="GET",
            url=url, 
            headers=headers
        )
        return result.text, result.status_code
