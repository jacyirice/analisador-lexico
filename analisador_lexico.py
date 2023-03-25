import re
import json


class AnalisadorLexico:
    caracteristicas = [
        {'keys': ['while', 'do'], 'type': 'Palavra reservada'},
        {'keys': ['<', '=', '+'], 'type': 'Operador'},
        {'keys': ['i', 'j'], 'type': 'Identificador'},
        {'pattern': '\d\d+', 'type': 'Constante'},
        {'pattern': '\d', 'type': 'Número'},
        {'keys': [';'], 'type': 'Terminador'},
    ]
    terminadores = caracteristicas[-1]['keys']

    def __init__(self):
        self.tokens_info = []
        self.simbolos = []
        self.simbolos_tipo = ['Identificador', 'Constante']

    def verifica_e_adiciona_simbolo(self, simbolo: str, tipo: str) -> None:
        if tipo in self.simbolos_tipo and simbolo not in self.simbolos:
            self.simbolos.append(simbolo)

    def adiciona_token_info(self, token: str, caracteristica: dict, posicao: list) -> None:
        token_info = (token, caracteristica['type'], len(
            token), posicao.copy())
        self.tokens_info.append(token_info)
        self.verifica_e_adiciona_simbolo(*token_info[:2])

    def separar_tokens_com_terminador(self, token, terminador) -> list:
        new_tokens = re.split(f'([{"".join(terminador)}])', token)
        tokens = [new_tokens[0]]

        for new_token in new_tokens[1:]:
            if new_token:
                tokens.append(new_token)

        return tokens

    def analisar_linha(self, linha: list, posicao_linha: int) -> None:
        posicao = [posicao_linha, 0]
        tokens = re.split('([/ ])', linha)
        terminadores = self.terminadores
        cont = 0
        print(tokens)
        while cont < len(tokens):
            token = tokens[cont]

            if not token.strip():
                posicao[1] += len(token)
                cont += 1
                continue

            if len(token) > 1 and any(terminador in token for terminador in terminadores):
                tokens = tokens[:cont] + self.separar_tokens_com_terminador(
                    token, terminadores) + tokens[cont+1:]
                token = tokens[cont]

            for caracteristica in self.caracteristicas:
                if any(('keys' in caracteristica and token in caracteristica['keys'],
                        'pattern' in caracteristica and re.match(caracteristica['pattern'], token))):
                    self.adiciona_token_info(token, caracteristica, posicao)
                    break

            posicao[1] += len(token)
            cont += 1

    def analisar(self, linhas: list) -> None:
        for i, linha in enumerate(linhas):
            self.analisar_linha(linha, i)

    def analisar_from_file(self, filename: str) -> None:
        with open(filename, 'r') as f:
            self.analisar(f.read().splitlines())

    def salvar_tokens_in_json(self, filename: str) -> None:
        
        tokens = []
        for token, tipo, tamanho, posicao in self.tokens_info:

            if tipo in self.simbolos_tipo:
                tipo = [tipo, self.simbolos.index(token)+1]

            tokens.append({'token': token, 'identificação': tipo,
                           'tamanho': tamanho, 'posição (lin, col)': posicao})

        simbolos = [{'índice': i+1, 'símbolo': simbolo}
                    for i, simbolo in enumerate(self.simbolos)]

        tokens_json = {'tokens': tokens, 'simbolos': simbolos}

        with open(filename, 'w') as f:
            f.write(json.dumps(tokens_json, indent=4))


if __name__ == '__main__':
    analisador = AnalisadorLexico()
    analisador.analisar_from_file('teste.txt')
    analisador.salvar_tokens_in_json('teste.json')
    
    analise = json.load(open('teste.json','r'))
    tokens = analise['tokens']
    simbolos = analise['simbolos']
    
    import pandas as pd
    print(pd.DataFrame(tokens))
    print(pd.DataFrame(simbolos))
    