# import unittest
# import secrets
# import string
#
# #testes python -m unittest
# from psp.santander.cob import Cob


# cert = None
#
# class ApiSantanderTest(unittest.TestCase):
#
#     def setUp(self):
#         self.txid_valido = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for i in range(27))
#         self.txid_valido1 = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for i in range(27))
#         self.txid_inexistente = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for i in range(27))
#         self.body = {
#                     'calendario': {
#                         'expiracao': '300'
#                     },
#                     'devedor': {
#                         'cnpj': '11258313000160',
#                         'nome': 'Devedor teste'
#                     },
#                     'valor': {
#                         'original': "0.10"
#                     },
#                     'chave': '22501210000155',
#                     'solicitacaoPagador': 'solicitacao_pagador',
#                     'infoAdicionais': [{"nome": "nome1", "valor": "valor1"}]
#         }
#         self.invalid_body = {
#                 'valor': {
#                     'original': "0.10"
#                 },
#                 'chave': '225001210000155no',
#                 'solicitacaoPagador': 'solicitacao_pagador',
#                 'infoAdicionais': [{"nome": "nome1", "valor": "valor1"}]
#         }
#         cobranca = Cob()
#         cobranca.criar_cobranca_put(self.txid_valido, self.body, url, cert, client_id, client_secret)
#
#     def test_api_criar_nova_cobranca_com_novo_txid_valido(self):
#
#         cobranca = Cob()
#         result = cobranca.criar_cobranca_put(self.txid_valido1, self.body, url, cert, client_id, client_secret)
#         self.assertEqual(result[1], 201)
#
#     def test_api_criar_nova_cobranca_com_novo_txid_valido_dados_invalidos(self):
#         cobranca = Cob()
#         result = cobranca.criar_cobranca_put(self.txid_valido, self.invalid_body, url, cert, client_id, client_secret)
#         self.assertEqual(result[1], 400)
#
#     def test_api_criar_nova_cobranca_com_txid_existente(self):
#         cobranca = Cob()
#         result = cobranca.criar_cobranca_put(self.txid_valido, self.body, url, cert, client_id, client_secret)
#         self.assertEqual(result[1], 400)
#
#     def test_api_criar_nova_cobranca_com_txid_invalido_menor_27_caracteres(self):
#         cobranca = Cob()
#         result = cobranca.criar_cobranca_put("HRAT14SSHFD", self.body, url, cert, client_id, client_secret)
#         self.assertEqual(result[1], 400)
#
#     def test_api_consultar_cobranca_com_txid_inexistente(self):
#         cobranca = Cob()
#         result = cobranca.consultar_cobranca_get(self.txid_inexistente, url, cert, client_id, client_secret)
#         self.assertEqual(result[1], 404)
#
#     def test_api_criar_nova_cobranca_com_txid_invalido_menor_27_caracteres(self):
#         cobranca = Cob()
#         result = cobranca.consultar_cobranca_get('HRAT14SSHFD', url, cert, client_id, client_secret)
#         self.assertEqual(result[1], 400)
#
#     def test_api_consultar_cobranca_com_txid_existente(self):
#         cobranca = Cob()
#         result = cobranca.consultar_cobranca_get(self.txid_valido, url, cert, client_id, client_secret)
#         self.assertEqual(result[1], 200)
#
#
#     def test_api_consultar_cobrancas_lista(self):
#         inicio = '2020-12-09T08:00:00Z'
#         fim = '2021-12-09T23:00:00Z'
#         cobranca = Cob()
#         body=None
#         r = cobranca.consultar_lista_cobranca_get(inicio, fim, body, url, cert, client_id, client_secret)
#         result = False
#         if r[1] in [200, 404]:
#             result = True
#         self.assertTrue(result)
#
#
# if __name__ == '__main__':
#     unittest.main()
