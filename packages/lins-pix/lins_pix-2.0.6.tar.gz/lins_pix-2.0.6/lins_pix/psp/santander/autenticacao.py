# -*- coding: utf=8 -*-
import os
import logging

from time import sleep
from requests import request, HTTPError
from datetime import datetime, timedelta

from lins_pix.utils import (
    read_file,
    write_file,
    msg_exception,
    msg_erro
)
from lins_pix.settings import (
    CLIENT_SECRET,
    CLIENT_ID,
    VERIFY,
    CERT,
    URL
)

class Response:
    def __init__(self, text, status_code) -> None:
        self.text = text
        self.status_code = status_code


class Autenticacao:
    __instance = None
    instances = []

    def __init__(
            self,
            client_secret: str = CLIENT_SECRET,
            client_id: str = CLIENT_ID,
            verify: bool = VERIFY,
            cert: str = CERT,
            url: str = URL):
        self.client_secret = client_secret
        self.client_id = client_id
        self.verify = verify
        self.cert = cert
        self.url = url

        self.access_token = None
        self.data_hora_limite = None
        self.setup()

    def __new__(cls):
        if Autenticacao.__instance is None:
            Autenticacao.__instance = object.__new__(cls)

        return Autenticacao.__instance

    def setup(self):
        self.access_token = self.get_token()

    def set_token(self, token: str):
        data_hora = datetime.now()

        # Salva Token - Instância da Classe
        self.access_token = token
        self.data_hora_limite = data_hora + timedelta(minutes=45)
        data_hora_limite_str = self.data_hora_limite.strftime("%Y-%m-%d %H:%M:%S")

        try:
            # Salva Token - Variáveis de Ambiente
            os.environ['access_token'] = self.access_token 
            os.environ['data_hora_limite'] = data_hora_limite_str
        except Exception as e:
            logging.error(
                msg_exception(e, str(self.__class__.__name__)))

        try:
            # Salva Token - Arquivo .JSON
            write_file(
                content={
                    "access_token": self.access_token,
                    "data_hora_limite": data_hora_limite_str
                },
                path_file='api'
            )
        except Exception as e:
            logging.error(
                msg_exception(e, str(self.__class__.__name__)))

    def get_header(self):
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

    def get_token(self, force: bool = False):
        """Verifica se tem token e se ele está dentro do prazo estipulado
        """
        def make_auth():
            response = self.auth()
            if response.status_code != 500:
                data = response.json()
                self.set_token(token=data.get("access_token"))
                return self.access_token, None
            else:
                return False, response

        if force:
            return make_auth()
        else:
            data_hora = datetime.now()
            data_hora_formato = "%Y-%m-%d %H:%M:%S"

            try:
                # Tentativa para Buscar Token - Instância da Classe
                if self.data_hora_limite is not None and self.data_hora_limite > data_hora:
                    if self.access_token:
                        return self.access_token
            except:
                pass

            try:
                # Tentativa para Buscar Token - Variáveis de Ambiente
                data = os.environ
                data_hora_limite = datetime.strptime(
                    data.get('data_hora_limite'), data_hora_formato
                )
                if data_hora_limite is not None and data_hora_limite > data_hora:
                    return data.get('access_token')

            except Exception:
                pass

            try:
                # Tentativa para Buscar Token - Arquivo .JSON
                data = read_file(path_file='api')
                data_hora_limite = datetime.strptime(
                    data.get('data_hora_limite'), data_hora_formato
                )
                if data_hora_limite is not None and data_hora_limite > data_hora:
                    return data.get('access_token')

            except Exception:
                pass

            return make_auth()

    def auth(self, url: str = None, *args, **kwargs):
        """Autenticacao de homologacao
        """
        if not url:
            url = self.url + "/oauth/token"
        else:
            url += "/oauth/token"

        params = dict(
            grant_type="client_credentials"
        )
        payload = dict(
            client_id=self.client_id,
            client_secret=self.client_secret
        )
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = self.make_request(
            method="POST",
            url=url,
            params=params,
            headers=headers,
            payload=payload
        )
        return response

    def make_request(
            self,
            method: str,
            url: str = None,
            params: dict = dict(),
            headers: dict = dict(),
            payload: dict = dict(),
            retry: int = 0,
            max_retry: int = 5):
        """Função genérica para realizar operações HTTP.
        """
        if not headers:
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        kwargs = {
            'method': method,
            'params': params,
            'data': payload,
            'headers': headers,
            'cert': self.cert,
            'verify': self.verify,
            'url': url or self.url
        }

        try:
            with request(**kwargs) as response:
                response_http = response
                try:
                    response.raise_for_status()
                    return response
                except HTTPError:
                    logging.error(msg_erro(response))
                    if retry < max_retry:
                        retry += 1
                        sleep(3)

                        if response.status_code == 500:
                            headers['Cache-Control'] = "no-cache"
                            headers['Pragma'] = "no-cache"
                            sleep(10)

                        if response.status_code == 401 and response.reason == 'Unauthorized':
                            self.get_token(force=True)
                            headers = self.get_header()
                            sleep(5)

                        response_http = self.make_request(
                            method=method,
                            url=url,
                            params=params,
                            headers=headers,
                            payload=payload,
                            retry=retry
                        )

                return response_http

        except Exception as error:
            logging.error(
                msg_exception(error, str(self.__class__.__name__)))
            return Response(text=error, status_code=500)
