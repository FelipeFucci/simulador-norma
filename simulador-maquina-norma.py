import re

def inc(registrador, pc_atual, memoria_registradores):
    memoria_registradores[registrador] += 1
    pc_atual += 1
    return pc_atual

def dec(registrador, pc_atual, memoria_registradores):
    if memoria_registradores[registrador] == 0:
        pc_atual += 1
        return pc_atual
    else:
        memoria_registradores[registrador] -= 1
        pc_atual += 1
        return pc_atual

def tst(registrador, salto_zero, salto_nao_zero, memoria_registradores):
    if memoria_registradores[registrador] == 0:
        pc_atual = salto_zero
        return pc_atual
    else:
        pc_atual = salto_nao_zero
        return pc_atual

def registrador_existe(registrador, memoria_registradores):
    return registrador in memoria_registradores

def criar_registrador(registrador, memoria_registradores, valor = 0):
    if valor < 0:
        return False
    memoria_registradores[registrador] = valor
    return True

def carregar_programa(nome):
    memoria_codigo = []
    with open(nome, "r", encoding="utf-8") as arquivo:
        for linha in arquivo:
            memoria_codigo.append(" ".join(linha.split()))
    return memoria_codigo

def obter_lista_padroes_sintaxe():
    padroes = [
        r"INC [A-Z]",
        r"DEC [A-Z]",
        r"TST ([A-Z]) VÁ_PARA ([A-Z0-9]+) SENÃO ([A-Z0-9]+)",

        r"ZER [A-Z]",

        r"[A-Z] := \d+",

        r"([A-Z]) := \1 \+ ([A-Z]) com ([A-Z])",
        r"([A-Z]) := ([A-Z]) \+ ([A-Z]) com ([A-Z]), ([A-Z])",

        r"([A-Z]) := \1 - ([A-Z]) com ([A-Z])",
        r"([A-Z]) := ([A-Z]) - ([A-Z]) com ([A-Z]), ([A-Z])",

        r"([A-Z]) := \1 \* ([A-Z]) com ([A-Z]), ([A-Z]), ([A-Z])",
        r"([A-Z]) := ([A-Z]) \* ([A-Z]) com ([A-Z]), ([A-Z])",

        r"([A-Z]) := ([A-Z]) div ([A-Z]), ([A-Z]) := \2 mod \3 com ([A-Z]), ([A-Z]), ([A-Z])",

        r"[A-Z0-9]+:"
    ]
    return padroes

def validar_sintaxe(memoria_codigo):
    lista_padroes = obter_lista_padroes_sintaxe()
    memoria_rotulos = {}

    for conteudo_linha in memoria_codigo:
        condiz = re.fullmatch(lista_padroes[12], conteudo_linha)
        if condiz:
            memoria_rotulos[conteudo_linha.removesuffix(":")] = memoria_codigo.index(conteudo_linha)

    rotulos_vistos = set()
    memoria_erros_sintaxe = []

    for numero_linha, conteudo_linha in enumerate(memoria_codigo, start=1):
        if not conteudo_linha:
            continue

        if not any(re.fullmatch(padrao, conteudo_linha) for padrao in lista_padroes):
            memoria_erros_sintaxe.append(
                f"Linha {numero_linha}, ID {numero_linha - 1}: sintaxe inválida: {conteudo_linha}"
            )
            continue

        if re.fullmatch(lista_padroes[12], conteudo_linha):
            rotulo = conteudo_linha.removesuffix(":")
            if rotulo in rotulos_vistos:
                memoria_erros_sintaxe.append(
                    f"Linha {numero_linha}, ID {numero_linha - 1}: rótulo já existe: {conteudo_linha}"
                )
            rotulos_vistos.add(rotulo)
            continue

        condiz = re.fullmatch(lista_padroes[2], conteudo_linha)
        if condiz:
            _, salto_zero, salto_nao_zero = condiz.groups()
            if not salto_zero.isdigit() and salto_zero not in memoria_rotulos:
                memoria_erros_sintaxe.append(f"Linha {numero_linha}: rótulo inexistente: {salto_zero}: {conteudo_linha}")
            if not salto_nao_zero.isdigit() and salto_nao_zero not in memoria_rotulos:
                memoria_erros_sintaxe.append(f"Linha {numero_linha}: rótulo inexistente: {salto_nao_zero}: {conteudo_linha}")

    return memoria_erros_sintaxe

def traduzir_zerar(registrador, memoria_codigo_traduzido):
    macro_traduzida = [
    f"DEC {registrador}",
    f"TST {registrador} VÁ_PARA {len(memoria_codigo_traduzido) + 2} SENÃO {(len(memoria_codigo_traduzido) + 1) - 1}"
        ]
    memoria_codigo_traduzido.extend(macro_traduzida)

def traduzir_atribuicao(registrador, valor, memoria_codigo_traduzido):
    if valor < 0:
        return False
    traduzir_zerar(registrador, memoria_codigo_traduzido)
    for i in range(valor):
        instrucao = f"INC {registrador}"
        memoria_codigo_traduzido.append(instrucao)
    return True

def traduzir_soma_com_3_registradores(registrador1, registrador2, registrador3, auxiliar1, auxiliar2, memoria_codigo_traduzido):
    traduzir_zerar(registrador3, memoria_codigo_traduzido)
    traduzir_zerar(auxiliar1, memoria_codigo_traduzido)
    traduzir_zerar(auxiliar2, memoria_codigo_traduzido)
    macro_traduzida = [
    f"TST {registrador1} VÁ_PARA {len(memoria_codigo_traduzido) + 8} SENÃO {len(memoria_codigo_traduzido) + 1}",
    f"DEC {registrador1}",
    f"INC {registrador3}",
    f"INC {auxiliar1}",
    f"TST {registrador1} VÁ_PARA {len(memoria_codigo_traduzido) + 5} SENÃO {(len(memoria_codigo_traduzido) + 4) - 3}",
    f"DEC {auxiliar1}",
    f"INC {registrador1}",
    f"TST {auxiliar1} VÁ_PARA {len(memoria_codigo_traduzido) + 8} SENÃO {(len(memoria_codigo_traduzido) + 7) - 2}",
    f"TST {registrador2} VÁ_PARA {len(memoria_codigo_traduzido) + 16} SENÃO {(len(memoria_codigo_traduzido) + 8) + 1}",
    f"DEC {registrador2}",
    f"INC {registrador3}",
    f"INC {auxiliar2}",
    f"TST {registrador2} VÁ_PARA {len(memoria_codigo_traduzido) + 13} SENÃO {(len(memoria_codigo_traduzido) + 12) - 3}",
    f"DEC {auxiliar2}",
    f"INC {registrador2}",
    f"TST {auxiliar2} VÁ_PARA {len(memoria_codigo_traduzido) + 16} SENÃO {(len(memoria_codigo_traduzido) + 15) - 2}"
        ]
    memoria_codigo_traduzido.extend(macro_traduzida)

def traduzir_soma_com_2_registradores(registrador1, registrador2, auxiliar, memoria_codigo_traduzido):
    traduzir_zerar(auxiliar, memoria_codigo_traduzido)
    macro_traduzida = [
    f"TST {registrador2} VÁ_PARA {len(memoria_codigo_traduzido) + 8} SENÃO {len(memoria_codigo_traduzido) + 1}",
    f"DEC {registrador2}",
    f"INC {registrador1}",
    f"INC {auxiliar}",
    f"TST {registrador2} VÁ_PARA {len(memoria_codigo_traduzido) + 5} SENÃO {(len(memoria_codigo_traduzido) + 4) - 3}",
    f"DEC {auxiliar}",
    f"INC {registrador2}",
    f"TST {auxiliar} VÁ_PARA {len(memoria_codigo_traduzido) + 8} SENÃO {(len(memoria_codigo_traduzido) + 7) - 2}"
        ]
    memoria_codigo_traduzido.extend(macro_traduzida)

def traduzir_subtracao_com_3_registradores(registrador1, registrador2, registrador3, auxiliar1, auxiliar2, memoria_codigo_traduzido):
    traduzir_zerar(registrador3, memoria_codigo_traduzido)
    traduzir_zerar(auxiliar1, memoria_codigo_traduzido)
    traduzir_zerar(auxiliar2, memoria_codigo_traduzido)
    macro_traduzida = [
    f"TST {registrador1} VÁ_PARA {len(memoria_codigo_traduzido) + 17} SENÃO {len(memoria_codigo_traduzido) + 1}",
    f"TST {registrador2} VÁ_PARA {len(memoria_codigo_traduzido) + 10} SENÃO {(len(memoria_codigo_traduzido) + 1) + 1}",
    f"DEC {registrador2}",
    f"DEC {registrador1}",
    f"INC {auxiliar1}",
    f"INC {auxiliar2}",
    f"TST {registrador2} VÁ_PARA {len(memoria_codigo_traduzido) + 7} SENÃO {(len(memoria_codigo_traduzido) + 6) - 4}",
    f"DEC {auxiliar2}",
    f"INC {registrador2}",
    f"TST {auxiliar2} VÁ_PARA {len(memoria_codigo_traduzido) + 10} SENÃO {(len(memoria_codigo_traduzido) + 9) - 2}",
    f"DEC {registrador1}",
    f"INC {registrador3}",
    f"INC {auxiliar1}",
    f"TST {registrador1} VÁ_PARA {len(memoria_codigo_traduzido) + 14} SENÃO {(len(memoria_codigo_traduzido) + 13) - 3}",
    f"DEC {auxiliar1}",
    f"INC {registrador1}",
    f"TST {auxiliar1} VÁ_PARA {len(memoria_codigo_traduzido) + 17} SENÃO {(len(memoria_codigo_traduzido) + 16) - 2}"
        ]
    memoria_codigo_traduzido.extend(macro_traduzida)

def traduzir_subtracao_com_2_registradores(registrador1, registrador2, auxiliar, memoria_codigo_traduzido):
    traduzir_zerar(auxiliar, memoria_codigo_traduzido)
    macro_traduzida = [
    f"TST {registrador1} VÁ_PARA {len(memoria_codigo_traduzido) + 9} SENÃO {len(memoria_codigo_traduzido) + 1}",
    f"TST {registrador2} VÁ_PARA {len(memoria_codigo_traduzido) + 9} SENÃO {(len(memoria_codigo_traduzido) + 1) + 1}",
    f"DEC {registrador2}",
    f"DEC {registrador1}",
    f"INC {auxiliar}",
    f"TST {registrador2} VÁ_PARA {len(memoria_codigo_traduzido) + 6} SENÃO {(len(memoria_codigo_traduzido) + 5) - 3}",
    f"DEC {auxiliar}",
    f"INC {registrador2}",
    f"TST {auxiliar} VÁ_PARA {len(memoria_codigo_traduzido) + 9} SENÃO {(len(memoria_codigo_traduzido) + 8) - 2}"
        ]
    memoria_codigo_traduzido.extend(macro_traduzida)

def traduzir_multiplicacao_com_3_registradores(registrador1, registrador2, registrador3, auxiliar1, auxiliar2, memoria_codigo_traduzido):
    traduzir_zerar(registrador3, memoria_codigo_traduzido)
    traduzir_zerar(auxiliar1, memoria_codigo_traduzido)
    traduzir_zerar(auxiliar2, memoria_codigo_traduzido)
    macro_traduzida = [
        f"TST {registrador2} VÁ_PARA {len(memoria_codigo_traduzido) + 15} SENÃO {len(memoria_codigo_traduzido) + 2}",
        f"TST {registrador1} VÁ_PARA {len(memoria_codigo_traduzido) + 15} SENÃO {(len(memoria_codigo_traduzido) + 1) + 1}",
        f"DEC {registrador2}",
        f"DEC {registrador1}",
        f"INC {registrador3}",
        f"INC {auxiliar1}",
        f"TST {registrador1} VÁ_PARA {len(memoria_codigo_traduzido) + 7} SENÃO {(len(memoria_codigo_traduzido) + 6) - 3}",
        f"DEC {auxiliar1}",
        f"INC {registrador1}",
        f"TST {auxiliar1} VÁ_PARA {len(memoria_codigo_traduzido) + 10} SENÃO {(len(memoria_codigo_traduzido) + 9) - 2}",
        f"INC {auxiliar2}",
        f"TST {registrador2} VÁ_PARA {len(memoria_codigo_traduzido) + 12} SENÃO {(len(memoria_codigo_traduzido) + 11) - 9}",
        f"DEC {auxiliar2}",
        f"INC {registrador2}",
        f"TST {auxiliar2} VÁ_PARA {len(memoria_codigo_traduzido) + 15} SENÃO {(len(memoria_codigo_traduzido) + 14) - 2}"
    ]
    memoria_codigo_traduzido.extend(macro_traduzida)

def traduzir_multiplicacao_com_2_registradores(registrador1, registrador2, auxiliar1, auxiliar2, auxiliar3, memoria_codigo_traduzido):
    traduzir_zerar(auxiliar1, memoria_codigo_traduzido)
    traduzir_zerar(auxiliar2, memoria_codigo_traduzido)
    traduzir_zerar(auxiliar3, memoria_codigo_traduzido)
    macro_traduzida = [
        f"TST {registrador2} VÁ_PARA {len(memoria_codigo_traduzido) + 16} SENÃO {len(memoria_codigo_traduzido) + 1}",
        f"TST {registrador1} VÁ_PARA {len(memoria_codigo_traduzido) + 21} SENÃO {(len(memoria_codigo_traduzido) + 1) + 1}",
        f"DEC {registrador2}",
        f"DEC {registrador1}",
        f"INC {auxiliar1}",
        f"INC {auxiliar2}",
        f"TST {registrador1} VÁ_PARA {len(memoria_codigo_traduzido) + 7} SENÃO {(len(memoria_codigo_traduzido) + 6) - 3}",
        f"DEC {auxiliar2}",
        f"INC {registrador1}",
        f"TST {auxiliar2} VÁ_PARA {len(memoria_codigo_traduzido) + 10} SENÃO {(len(memoria_codigo_traduzido) + 9) - 2}",
        f"INC {auxiliar3}",
        f"TST {registrador2} VÁ_PARA {len(memoria_codigo_traduzido) + 12} SENÃO {(len(memoria_codigo_traduzido) + 11) - 9}",
        f"DEC {auxiliar3}",
        f"INC {registrador2}",
        f"TST {auxiliar3} VÁ_PARA {len(memoria_codigo_traduzido) + 15} SENÃO {(len(memoria_codigo_traduzido) + 14) - 2}",
        f"DEC {registrador1}",
        f"TST {registrador1} VÁ_PARA {len(memoria_codigo_traduzido) + 17} SENÃO {(len(memoria_codigo_traduzido) + 16) - 1}",
        f"TST {registrador2} VÁ_PARA {len(memoria_codigo_traduzido) + 21} SENÃO {(len(memoria_codigo_traduzido) + 17) + 1}",
        f"DEC {auxiliar1}",
        f"INC {registrador1}",
        f"TST {auxiliar1} VÁ_PARA {len(memoria_codigo_traduzido) + 21} SENÃO {(len(memoria_codigo_traduzido) + 20) - 2}"
    ]
    memoria_codigo_traduzido.extend(macro_traduzida)

def traduzir_divisao(quociente, registrador1, registrador2, resto, auxiliar1, auxiliar2, auxiliar3, memoria_codigo_traduzido):
    traduzir_zerar(quociente, memoria_codigo_traduzido)
    traduzir_zerar(resto, memoria_codigo_traduzido)
    traduzir_zerar(auxiliar1, memoria_codigo_traduzido)
    traduzir_zerar(auxiliar2, memoria_codigo_traduzido)
    traduzir_zerar(auxiliar3, memoria_codigo_traduzido)
    macro_traduzida = [
        f"TST {registrador1} VÁ_PARA {len(memoria_codigo_traduzido) + 27} SENÃO {len(memoria_codigo_traduzido) + 1}",
        f"TST {registrador2} VÁ_PARA {len(memoria_codigo_traduzido) + 27} SENÃO {(len(memoria_codigo_traduzido) + 1) + 1}",
        f"DEC {registrador1}",
        f"INC {resto}",
        f"INC {auxiliar1}",
        f"DEC {resto}",
        f"DEC {registrador2}",
        f"INC {auxiliar2}",
        f"INC {auxiliar3}",
        f"TST {resto} VÁ_PARA {len(memoria_codigo_traduzido) + 12} SENÃO {(len(memoria_codigo_traduzido) + 9) + 1}",
        f"TST {registrador2} VÁ_PARA {len(memoria_codigo_traduzido) + 11} SENÃO {(len(memoria_codigo_traduzido) + 10) - 5}",
        f"TST {resto} VÁ_PARA {len(memoria_codigo_traduzido) + 16} SENÃO {(len(memoria_codigo_traduzido) + 11) + 2}",
        f"TST {registrador2} VÁ_PARA {len(memoria_codigo_traduzido) + 16} SENÃO {(len(memoria_codigo_traduzido) + 12) + 1}",
        f"DEC {auxiliar2}",
        f"INC {resto}",
        f"TST {auxiliar2} VÁ_PARA {len(memoria_codigo_traduzido) + 16} SENÃO {(len(memoria_codigo_traduzido) + 15) - 2}",
        f"DEC {auxiliar3}",
        f"INC {registrador2}",
        f"TST {auxiliar3} VÁ_PARA {len(memoria_codigo_traduzido) + 19} SENÃO {(len(memoria_codigo_traduzido) + 18) - 2}",
        f"DEC {auxiliar2}",
        f"TST {auxiliar2} VÁ_PARA {len(memoria_codigo_traduzido) + 21} SENÃO {(len(memoria_codigo_traduzido) + 20) - 1}",
        f"TST {resto} VÁ_PARA {len(memoria_codigo_traduzido) + 22} SENÃO {(len(memoria_codigo_traduzido) + 21) + 2}",
        f"INC {quociente}",
        f"TST {registrador1} VÁ_PARA {len(memoria_codigo_traduzido) + 24} SENÃO {(len(memoria_codigo_traduzido) + 23) - 21}",
        f"DEC {auxiliar1}",
        f"INC {registrador1}",
        f"TST {auxiliar1} VÁ_PARA {len(memoria_codigo_traduzido) + 27} SENÃO {(len(memoria_codigo_traduzido) + 26) - 2}"
    ]
    memoria_codigo_traduzido.extend(macro_traduzida)


def traduzir_codigo(memoria_codigo):
    lista_padroes = obter_lista_padroes_sintaxe()
    memoria_rotulos = {}
    memoria_codigo_traduzido = []
    for conteudo_linha in memoria_codigo:
        if not conteudo_linha:
            continue

        if re.fullmatch(lista_padroes[12], conteudo_linha):
            memoria_rotulos[conteudo_linha.removesuffix(":")] = len(memoria_codigo_traduzido)
            continue

        if re.fullmatch(lista_padroes[0], conteudo_linha) or re.fullmatch(lista_padroes[1], conteudo_linha) or re.fullmatch(lista_padroes[2], conteudo_linha):
            memoria_codigo_traduzido.append(conteudo_linha)
            continue

        condiz = re.fullmatch(lista_padroes[3], conteudo_linha)
        if condiz:
            registrador1 = conteudo_linha.split()[1]
            traduzir_zerar(registrador1, memoria_codigo_traduzido)
            continue

        condiz = re.fullmatch(lista_padroes[4], conteudo_linha)
        if condiz:
            partes = conteudo_linha.split(" := ")
            registrador1 = partes[0]
            valor = int(partes[1])
            traduzir_atribuicao(registrador1, valor, memoria_codigo_traduzido)
            continue

        condiz = re.fullmatch(lista_padroes[5], conteudo_linha)
        if condiz:
            registrador1, registrador2, auxiliar1 = condiz.groups()
            traduzir_soma_com_2_registradores(registrador1, registrador2, auxiliar1, memoria_codigo_traduzido)
            continue

        condiz = re.fullmatch(lista_padroes[6], conteudo_linha)
        if condiz:
            registrador3, registrador1, registrador2, auxiliar1, auxiliar2 = condiz.groups()
            traduzir_soma_com_3_registradores(registrador1, registrador2, registrador3, auxiliar1, auxiliar2, memoria_codigo_traduzido)
            continue

        condiz = re.fullmatch(lista_padroes[7], conteudo_linha)
        if condiz:
            registrador1, registrador2, auxiliar1 = condiz.groups()
            traduzir_subtracao_com_2_registradores(registrador1, registrador2, auxiliar1, memoria_codigo_traduzido)
            continue

        condiz = re.fullmatch(lista_padroes[8], conteudo_linha)
        if condiz:
            registrador3, registrador1, registrador2, auxiliar1, auxiliar2 = condiz.groups()
            traduzir_subtracao_com_3_registradores(registrador1, registrador2, registrador3, auxiliar1, auxiliar2, memoria_codigo_traduzido)
            continue

        condiz = re.fullmatch(lista_padroes[9], conteudo_linha)
        if condiz:
            registrador1, registrador2, auxiliar1, auxiliar2, auxiliar3 = condiz.groups()
            traduzir_multiplicacao_com_2_registradores(registrador1, registrador2, auxiliar1, auxiliar2, auxiliar3, memoria_codigo_traduzido)
            continue

        condiz = re.fullmatch(lista_padroes[10], conteudo_linha)
        if condiz:
            registrador3, registrador1, registrador2, auxiliar1, auxiliar2 = condiz.groups()
            traduzir_multiplicacao_com_3_registradores(registrador1, registrador2, registrador3, auxiliar1, auxiliar2, memoria_codigo_traduzido)
            continue

        condiz = re.fullmatch(lista_padroes[11], conteudo_linha)
        if condiz:
            quociente, registrador1, registrador2, resto, auxiliar1, auxiliar2, auxiliar3 = condiz.groups()
            traduzir_divisao(quociente, registrador1, registrador2, resto, auxiliar1, auxiliar2, auxiliar3, memoria_codigo_traduzido)
            continue

    for valor_linha, conteudo_linha in enumerate(memoria_codigo_traduzido):
        condiz = re.fullmatch(lista_padroes[2], conteudo_linha)
        if condiz:
            registrador1, salto_zero, salto_nao_zero = condiz.groups()

            salto_zero = memoria_rotulos.get(salto_zero, salto_zero)
            salto_nao_zero = memoria_rotulos.get(salto_nao_zero, salto_nao_zero)

            memoria_codigo_traduzido[valor_linha] = f"TST {registrador1} VÁ_PARA {salto_zero} SENÃO {salto_nao_zero}"

    return memoria_codigo_traduzido

def executar_codigo(memoria_codigo_traduzido, memoria_registradores, pc):
    lista_padroes = obter_lista_padroes_sintaxe()
    linha = memoria_codigo_traduzido[pc]
    condiz = re.fullmatch(lista_padroes[0], linha)
    if condiz:
        registrador1 = linha.split()[1]

        if not registrador_existe(registrador1, memoria_registradores):
            criar_registrador(registrador1, memoria_registradores, 0)

        pc = inc(registrador1, pc, memoria_registradores)

    condiz = re.fullmatch(lista_padroes[1], linha)
    if condiz:
        registrador1 = linha.split()[1]

        if not registrador_existe(registrador1, memoria_registradores):
            criar_registrador(registrador1, memoria_registradores, 0)

        pc = dec(registrador1, pc, memoria_registradores)

    condiz = re.fullmatch(lista_padroes[2], linha)
    if condiz:
        partes = linha.split()
        registrador1 = partes[1]

        if not registrador_existe(registrador1, memoria_registradores):
            criar_registrador(registrador1, memoria_registradores, 0)

        salto_zero = int(partes[3])
        salto_nao_zero = int(partes[5])
        pc = tst(registrador1, salto_zero, salto_nao_zero, memoria_registradores)

    return pc

pc = 0
memoria_registradores = {}
memoria_codigo = []

while True:
    print("\n1. Para carregar o arquivo .norma.")
    print("2. Para executar o código continuamente.")
    print("3. Para executar o código passo-a-passo.")
    print("4. Para sair do programa.")
    escolha_menu = int(input("\nEscolha uma opção: "))
    match escolha_menu:
        case 1:
            try:
                nome = input("\nDigite o nome do arquivo e a sua extensão: ")
                if not nome.endswith(".norma") and not nome.endswith(".txt"):
                    print("\nArquivo inválido! Por favor, escolha um arquivo .norma ou .txt!")
                    continue
                memoria_codigo = carregar_programa(nome)
                erros = validar_sintaxe(memoria_codigo)
            except FileNotFoundError:
                print("\nArquivo não encontrado!")
                continue
            if erros:
                print("Foram encontrados erros de sintaxe:\n")
                for erro in erros:
                    print(erro)
                memoria_codigo.clear()
            else:
                print("\nO arquivo foi carregado com sucesso!")
                memoria_codigo_traduzido = traduzir_codigo(memoria_codigo)

        case 2:
            if not memoria_codigo:
                print("\nNenhum arquivo foi carregado. Por favor, carregue um arquivo .norma para continuar.")
            else:
                contador = 1
                limite = int(input("\nDigite o valor do limite de execuções: "))
                while pc != len(memoria_codigo_traduzido) and contador <= limite:
                    pc = executar_codigo(memoria_codigo_traduzido, memoria_registradores, pc)
                    contador += 1
                for registrador, valor in memoria_registradores.items():
                    print(f"{registrador}: {valor} | ", end="")
                print("\n")
            pc = 0
            memoria_registradores.clear()

        case 3:
            if not memoria_codigo:
                print("\nNenhum arquivo foi carregado. Por favor, carregue um arquivo .norma para continuar.")
            else:
                contador = 1
                limite = int(input("\nDigite o valor do limite de execuções: "))
                while pc != len(memoria_codigo_traduzido) and contador <= limite:
                    print(f"\nInstrução atual do IP: {memoria_codigo_traduzido[pc]}\n")
                    escolha_passo_a_passo = int(input("Digite 1 para executar a instrução ou 2 para voltar para o menu: "))
                    if escolha_passo_a_passo == 2:
                        break
                    pc = executar_codigo(memoria_codigo_traduzido, memoria_registradores, pc)
                    print()
                    for registrador, valor in memoria_registradores.items():
                        print(f"{registrador}: {valor} | ", end="")
                    print()
                    contador += 1
            pc = 0
            memoria_registradores.clear()

        case 4:
            print("\nSaindo do simulador...")
            break

        case _:
            print("\nEscolha inválida! Por favor, digite um valor válido.")

    