# import json
# import qrcode
# import base64
#
#
# class Qrcode:
#
#     def __init__(self, data):
#         self.data = data
#
#     def to_base64(self):
#         # b64 = base64.b64encode(urlopen(self.data).read()).decode('utf-8')
#         b64 = base64.b64encode(bytes(self.data, 'utf-8'))
#
#         return b64
#
#     def to_imagem(self, path='', name='qrcode.png'):
#         qr = qrcode.QRCode(
#             version=2,
#             error_correction=qrcode.constants.ERROR_CORRECT_L,
#             box_size=10,
#             border=4,
#         )
#         qr.add_data(self.data)
#         qr.make(fit=True)
#
#         img = qr.make_image(fill_color="black", back_color="white")
#         img.save(path + name)
#
#         return img
