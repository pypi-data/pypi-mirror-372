import json


def write_file(content: str, path_file: str, type_file: str = '.json', mode: str = 'w') -> str:
    with open(path_file + type_file, mode) as outfile:
        outfile.write(json.dumps(content, indent=4))


def read_file(path_file: str, type_file: str = '.json') -> str:
    with open(path_file + type_file, 'r', encoding='utf8') as content:
        content = content.read()
    return json.loads(content)


def msg_erro(response):
    response.encoding = 'utf-8'
    try:
        response_data = response.json()
    except:
        response_data = response.text

    erro = {
        'aplicacao': 'lins-pix',
        'status_code': response.status_code,
        'url': response.url,
        'response': response_data
    }
    return erro


def msg_exception(erro, funcao):
    message = {
        'modo': 'CALLBACK',
        'aplicacao': 'lins-pix',
        'funcao': funcao,
        'erro': erro,
    }
    return message
