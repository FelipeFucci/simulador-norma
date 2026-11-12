import re

PADROES_SINTAXE = {
    "INC" : r"INC [A-Z]",
    "DEC" : r"DEC [A-Z]",
    "TST" : r"TST ([A-Z]) VÁ_PARA ([A-Z0-9]+) SENÃO ([A-Z0-9]+)",

    "MACRO_ZERAR" : r"ZER [A-Z]",

    "MACRO_ATRIBUIÇÃO" : r"[A-Z] := \d+",

    "MACRO_SOMA_COM_2_REGISTRADORES" : r"([A-Z]) := \1 \+ ([A-Z]) com ([A-Z])",
    "MACRO_SOMA_COM_3_REGISTRADORES" : r"([A-Z]) := ([A-Z]) \+ ([A-Z]) com ([A-Z]), ([A-Z])",

    "MACRO_SUBTRAÇÃO_COM_2_REGISTRADORES" : r"([A-Z]) := \1 - ([A-Z]) com ([A-Z])",
    "MACRO_SUBTRAÇÃO_COM_3_REGISTRADORES" : r"([A-Z]) := ([A-Z]) - ([A-Z]) com ([A-Z]), ([A-Z])",

    "MACRO_MULTIPLICAÇÃO_COM_2_REGISTRADORES" : r"([A-Z]) := \1 \* ([A-Z]) com ([A-Z]), ([A-Z]), ([A-Z])",
    "MACRO_MULTIPLICAÇÃO_COM_3_REGISTRADORES" : r"([A-Z]) := ([A-Z]) \* ([A-Z]) com ([A-Z]), ([A-Z])",

    "MACRO_DIVISÃO" : r"([A-Z]) := ([A-Z]) div ([A-Z]), ([A-Z]) := \2 mod \3 com ([A-Z]), ([A-Z]), ([A-Z])",

    "RÓTULO" : r"[A-Z0-9]+:"
}

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

def criar_registrador(registrador, memoria_registradores):
    memoria_registradores[registrador] = 0

def carregar_programa(caminho_arquivo):
    memoria_codigo = []
    # Abre o arquivo e disponibiliza seu conteúdo para leitura.
    with open(caminho_arquivo, "r", encoding="utf-8") as arquivo:
        # Percorre as linhas do arquivo, remove espaços desnecessários e armazena o resultado em memoria_codigo.
        for conteudo_linha in arquivo:
            memoria_codigo.append(" ".join(conteudo_linha.split()))
    return memoria_codigo

def validar_sintaxe(memoria_codigo):
    memoria_rotulos = {}

    # Percorre as linhas do código até achar um rótulo.
    for conteudo_linha in memoria_codigo:
        condiz = re.fullmatch(PADROES_SINTAXE["RÓTULO"], conteudo_linha)
        # Se um rótulo for encontrado, ele é armazenado em memoria_rotulos sem os dois pontos.
        if condiz:
            memoria_rotulos[conteudo_linha.removesuffix(":")] = memoria_codigo.index(conteudo_linha)

    rotulos_vistos = set()
    memoria_erros_sintaxe = []

    for numero_linha, conteudo_linha in enumerate(memoria_codigo, start=1):

        # Se o conteúdo da linha estiver vazio, passa para a próxima linha.
        if not conteudo_linha:
            continue

        # Verifica se a linha corresponde a algum dos padrões de sintaxe.
        if not any(re.fullmatch(padrao, conteudo_linha) for padrao in PADROES_SINTAXE.values()):
            # Caso contrário, armazena a mensagem de erro em memoria_erros_sintaxe.
            memoria_erros_sintaxe.append(
                f"Linha {numero_linha}, ID {numero_linha - 1}: sintaxe inválida: {conteudo_linha}"
            )
            continue

        # Verifica se a linha corresponde ao padrão de um rótulo.
        if re.fullmatch(PADROES_SINTAXE["RÓTULO"], conteudo_linha):
            # Remove os dois-pontos para obter o nome do rótulo.
            rotulo = conteudo_linha.removesuffix(":")
            # Verifica se o rótulo já foi declarado anteriormente.
            if rotulo in rotulos_vistos:
                memoria_erros_sintaxe.append(
                    f"Linha {numero_linha}, ID {numero_linha - 1}: rótulo já existe: {conteudo_linha}"
                )
            # Armazena o rótulo para futuras verificações.
            rotulos_vistos.add(rotulo)
            continue

        # Verifica se a linha corresponde ao padrão da instrução TST.
        condiz = re.fullmatch(PADROES_SINTAXE["TST"], conteudo_linha)
        if condiz:
            # Extrai os destinos dos saltos para zero e diferente de zero.
            _, salto_zero, salto_nao_zero = condiz.groups()
            # Verifica se o rótulo de destino para zero existe.
            if not salto_zero.isdigit() and salto_zero not in memoria_rotulos:
                memoria_erros_sintaxe.append(f"Linha {numero_linha}: rótulo inexistente: {salto_zero}: {conteudo_linha}")
            # Verifica se o rótulo de destino para diferente de zero existe.
            if not salto_nao_zero.isdigit() and salto_nao_zero not in memoria_rotulos:
                memoria_erros_sintaxe.append(f"Linha {numero_linha}: rótulo inexistente: {salto_nao_zero}: {conteudo_linha}")

    return memoria_erros_sintaxe

def traduzir_zerar(registrador, memoria_codigo_traduzido):
    # Gera a tradução com as instruções necessárias
    macro_traduzida = [
    f"DEC {registrador}",
    f"TST {registrador} VÁ_PARA {len(memoria_codigo_traduzido) + 2} SENÃO {(len(memoria_codigo_traduzido) + 1) - 1}"
        ]
    # Adiciona a tradução à memória de código traduzido.
    memoria_codigo_traduzido.extend(macro_traduzida)

def traduzir_atribuicao(registrador, valor, memoria_codigo_traduzido):
    # Impede a atribuição de valores negativos.
    if valor < 0:
        return False
    # Zera o registrador antes de atribuir o novo valor.
    traduzir_zerar(registrador, memoria_codigo_traduzido)
    # Gera uma instrução INC para cada unidade do valor desejado.
    for i in range(valor):
        instrucao = f"INC {registrador}"
        memoria_codigo_traduzido.append(instrucao)
    return True

def traduzir_soma_com_3_registradores(registrador1, registrador2, registrador3, auxiliar1, auxiliar2, memoria_codigo_traduzido):
    traduzir_zerar(registrador3, memoria_codigo_traduzido)
    traduzir_zerar(auxiliar1, memoria_codigo_traduzido)
    traduzir_zerar(auxiliar2, memoria_codigo_traduzido)
    macro_traduzida = [
    # Se o primeiro registrador estiver zerado, pula sua transferência e segue para o segundo.
    # Caso contrário, inicia a transferência de seu conteúdo para o destino e o auxiliar.
    f"TST {registrador1} VÁ_PARA {len(memoria_codigo_traduzido) + 8} SENÃO {len(memoria_codigo_traduzido) + 1}",
    f"DEC {registrador1}",
    f"INC {registrador3}",
    f"INC {auxiliar1}",
    # Verifica se o primeiro registrador já foi zerado.
    # Se ainda possuir valor, repete a transferência. Caso contrário, inicia sua restauração.
    f"TST {registrador1} VÁ_PARA {len(memoria_codigo_traduzido) + 5} SENÃO {(len(memoria_codigo_traduzido) + 4) - 3}",
    f"DEC {auxiliar1}",
    f"INC {registrador1}",
    # Verifica se o auxiliar já foi zerado durante a restauração.
    # Se ainda possuir valor, continua restaurando o registrador original. Caso contrário, segue para o segundo.
    f"TST {auxiliar1} VÁ_PARA {len(memoria_codigo_traduzido) + 8} SENÃO {(len(memoria_codigo_traduzido) + 7) - 2}",
    # Se o segundo registrador estiver zerado, encerra a soma.
    # Caso contrário, inicia a transferência de seu conteúdo para o destino e o auxiliar.
    f"TST {registrador2} VÁ_PARA {len(memoria_codigo_traduzido) + 16} SENÃO {(len(memoria_codigo_traduzido) + 8) + 1}",
    f"DEC {registrador2}",
    f"INC {registrador3}",
    f"INC {auxiliar2}",
    # Verifica se o segundo registrador já foi zerado.
    # Se ainda possuir valor, repete a transferência. Caso contrário, inicia sua restauração.
    f"TST {registrador2} VÁ_PARA {len(memoria_codigo_traduzido) + 13} SENÃO {(len(memoria_codigo_traduzido) + 12) - 3}",
    f"DEC {auxiliar2}",
    f"INC {registrador2}",
    # Verifica se o auxiliar já foi zerado durante a restauração.
    # Se ainda possuir valor, continua restaurando o registrador original. Caso contrário, encerra a soma.
    f"TST {auxiliar2} VÁ_PARA {len(memoria_codigo_traduzido) + 16} SENÃO {(len(memoria_codigo_traduzido) + 15) - 2}"
        ]
    memoria_codigo_traduzido.extend(macro_traduzida)

def traduzir_soma_com_2_registradores(registrador1, registrador2, auxiliar, memoria_codigo_traduzido):
    traduzir_zerar(auxiliar, memoria_codigo_traduzido)
    macro_traduzida = [
    # Se o segundo registrador estiver zerado, encerra a soma.
    # Caso contrário, inicia a transferência de seu conteúdo para o primeiro registrador e o auxiliar.
    f"TST {registrador2} VÁ_PARA {len(memoria_codigo_traduzido) + 8} SENÃO {len(memoria_codigo_traduzido) + 1}",
    f"DEC {registrador2}",
    f"INC {registrador1}",
    f"INC {auxiliar}",
    # Verifica se o segundo registrador já foi zerado.
    # Se ainda possuir valor, repete a transferência. Caso contrário, inicia sua restauração.
    f"TST {registrador2} VÁ_PARA {len(memoria_codigo_traduzido) + 5} SENÃO {(len(memoria_codigo_traduzido) + 4) - 3}",
    f"DEC {auxiliar}",
    f"INC {registrador2}",
    # Verifica se o auxiliar já foi zerado durante a restauração.
    # Se ainda possuir valor, continua restaurando o segundo registrador. Caso contrário, encerra a soma.
    f"TST {auxiliar} VÁ_PARA {len(memoria_codigo_traduzido) + 8} SENÃO {(len(memoria_codigo_traduzido) + 7) - 2}"
        ]
    memoria_codigo_traduzido.extend(macro_traduzida)

def traduzir_subtracao_com_3_registradores(registrador1, registrador2, registrador3, auxiliar1, auxiliar2, memoria_codigo_traduzido):
    traduzir_zerar(registrador3, memoria_codigo_traduzido)
    traduzir_zerar(auxiliar1, memoria_codigo_traduzido)
    traduzir_zerar(auxiliar2, memoria_codigo_traduzido)
    macro_traduzida = [
    # Verifica se o primeiro registrador está zerado.
    # Se estiver, encerra a subtração, pois não há valor para subtrair. Caso contrário, verifica o segundo registrador.
    f"TST {registrador1} VÁ_PARA {len(memoria_codigo_traduzido) + 19} SENÃO {len(memoria_codigo_traduzido) + 1}",
    # Verifica se o segundo registrador está zerado.
    # Se estiver, não há valor a retirar, então segue diretamente para calcular o restante. Caso contrário, inicia a subtração simultânea.
    f"TST {registrador2} VÁ_PARA {len(memoria_codigo_traduzido) + 12} SENÃO {(len(memoria_codigo_traduzido) + 1) + 1}",
    # Verifica se o primeiro registrador ainda possui valor.
    # Se estiver zerado, pula seu decremento e não contabiliza uma unidade no primeiro auxiliar.
    # Caso contrário, decrementa o registrador e registra a unidade retirada para restaurá-lo posteriormente.
    f"TST {registrador1} VÁ_PARA {len(memoria_codigo_traduzido) + 5} SENÃO {(len(memoria_codigo_traduzido) + 2) + 1}",
    f"DEC {registrador1}",
    f"INC {auxiliar1}",
    f"DEC {registrador2}",
    f"INC {auxiliar2}",
    # Verifica se o segundo registrador já foi zerado.
    # Se ainda possuir valor, repete a subtração simultânea. Caso contrário, inicia a restauração do segundo registrador.
    f"TST {registrador2} VÁ_PARA {len(memoria_codigo_traduzido) + 8} SENÃO {(len(memoria_codigo_traduzido) + 7) - 5}",
    f"DEC {auxiliar2}",
    f"INC {registrador2}",
    # Verifica se todas as unidades do segundo auxiliar já foram devolvidas ao segundo registrador.
    # Se ainda houver unidades, continua a restauração. Caso contrário, segue para calcular o restante da subtração.
    f"TST {auxiliar2} VÁ_PARA {len(memoria_codigo_traduzido) + 11} SENÃO {(len(memoria_codigo_traduzido) + 10) - 2}",
    # Verifica se o primeiro registrador chegou a zero durante a subtração simultânea.
    # Se estiver zerado, não há mais diferença a calcular e a execução segue para restaurá-lo. Caso contrário, começa a calcular o restante.
    f"TST {registrador1} VÁ_PARA {len(memoria_codigo_traduzido) + 16} SENÃO {(len(memoria_codigo_traduzido) + 11) + 1}",
    f"DEC {registrador1}",
    f"INC {registrador3}",
    f"INC {auxiliar1}",
    # Verifica se o primeiro registrador já foi zerado.
    # Se ainda possuir valor, continua calculando a diferença. Caso contrário, inicia sua restauração.
    f"TST {registrador1} VÁ_PARA {len(memoria_codigo_traduzido) + 16} SENÃO {(len(memoria_codigo_traduzido) + 15) - 3}",
    f"DEC {auxiliar1}",
    f"INC {registrador1}",
    # Verifica se todas as unidades do primeiro auxiliar já foram devolvidas ao primeiro registrador.
    # Se ainda houver unidades, continua a restauração. Caso contrário, encerra a subtração.
    f"TST {auxiliar1} VÁ_PARA {len(memoria_codigo_traduzido) + 19} SENÃO {(len(memoria_codigo_traduzido) + 18) - 2}"
        ]
    memoria_codigo_traduzido.extend(macro_traduzida)

def traduzir_subtracao_com_2_registradores(registrador1, registrador2, auxiliar, memoria_codigo_traduzido):
    traduzir_zerar(auxiliar, memoria_codigo_traduzido)
    macro_traduzida = [
    # Verifica se o primeiro registrador está zerado.
    # Se estiver, encerra a subtração, pois não há valor para subtrair. Caso contrário, verifica o segundo registrador.
    f"TST {registrador1} VÁ_PARA {len(memoria_codigo_traduzido) + 9} SENÃO {len(memoria_codigo_traduzido) + 1}",
    # Verifica se o segundo registrador está zerado.
    # Se estiver, encerra a subtração, pois não há valor a retirar. Caso contrário, inicia a subtração simultânea.
    f"TST {registrador2} VÁ_PARA {len(memoria_codigo_traduzido) + 9} SENÃO {(len(memoria_codigo_traduzido) + 1) + 1}",
    f"DEC {registrador2}",
    f"DEC {registrador1}",
    f"INC {auxiliar}",
    # Verifica se o segundo registrador já foi zerado.
    # Se ainda possuir valor, repete a subtração simultânea. Caso contrário, inicia sua restauração.
    f"TST {registrador2} VÁ_PARA {len(memoria_codigo_traduzido) + 6} SENÃO {(len(memoria_codigo_traduzido) + 5) - 3}",
    f"DEC {auxiliar}",
    f"INC {registrador2}",
    # Verifica se todas as unidades do auxiliar já foram devolvidas ao segundo registrador.
    # Se ainda houver unidades, continua a restauração. Caso contrário, encerra a subtração.
    f"TST {auxiliar} VÁ_PARA {len(memoria_codigo_traduzido) + 9} SENÃO {(len(memoria_codigo_traduzido) + 8) - 2}"
        ]
    memoria_codigo_traduzido.extend(macro_traduzida)

def traduzir_multiplicacao_com_3_registradores(registrador1, registrador2, registrador3, auxiliar1, auxiliar2, memoria_codigo_traduzido):
    traduzir_zerar(registrador3, memoria_codigo_traduzido)
    traduzir_zerar(auxiliar1, memoria_codigo_traduzido)
    traduzir_zerar(auxiliar2, memoria_codigo_traduzido)
    macro_traduzida = [
        # Verifica se o segundo registrador está zerado.
        # Se estiver, encerra a multiplicação, pois qualquer número multiplicado por zero resulta em zero.
        # Caso contrário, verifica se o primeiro registrador também está zerado.
        f"TST {registrador2} VÁ_PARA {len(memoria_codigo_traduzido) + 15} SENÃO {len(memoria_codigo_traduzido) + 1}",
        # Verifica se o primeiro registrador está zerado.
        # Se estiver, encerra a multiplicação, pois o resultado também será zero.
        # Caso contrário, inicia uma repetição da soma do primeiro registrador ao resultado.
        f"TST {registrador1} VÁ_PARA {len(memoria_codigo_traduzido) + 15} SENÃO {(len(memoria_codigo_traduzido) + 1) + 1}",
        # Decrementa o segundo registrador para contabilizar uma repetição da multiplicação.
        f"DEC {registrador2}",
        f"DEC {registrador1}",
        f"INC {registrador3}",
        f"INC {auxiliar1}",
        # Verifica se o primeiro registrador já foi zerado durante a transferência.
        # Se ainda possuir valor, continua transferindo suas unidades para o resultado.
        # Caso contrário, inicia a restauração do primeiro registrador.
        f"TST {registrador1} VÁ_PARA {len(memoria_codigo_traduzido) + 7} SENÃO {(len(memoria_codigo_traduzido) + 6) - 3}",
        f"DEC {auxiliar1}",
        f"INC {registrador1}",
        # Verifica se todas as unidades do primeiro auxiliar já foram devolvidas ao primeiro registrador.
        # Se ainda houver unidades, continua a restauração.
        # Caso contrário, contabiliza uma repetição concluída e verifica o segundo registrador.
        f"TST {auxiliar1} VÁ_PARA {len(memoria_codigo_traduzido) + 10} SENÃO {(len(memoria_codigo_traduzido) + 9) - 2}",
        # Registra no segundo auxiliar uma repetição concluída da multiplicação.
        f"INC {auxiliar2}",
        # Verifica se o segundo registrador já foi zerado.
        # Se ainda possuir valor, inicia outra repetição da soma.
        # Caso contrário, inicia a restauração do segundo registrador.
        f"TST {registrador2} VÁ_PARA {len(memoria_codigo_traduzido) + 12} SENÃO {(len(memoria_codigo_traduzido) + 11) - 9}",
        f"DEC {auxiliar2}",
        f"INC {registrador2}",
        # Verifica se todas as repetições contabilizadas no segundo auxiliar já foram restauradas ao segundo registrador.
        # Se ainda houver unidades, continua a restauração.
        # Caso contrário, encerra a multiplicação.
        f"TST {auxiliar2} VÁ_PARA {len(memoria_codigo_traduzido) + 15} SENÃO {(len(memoria_codigo_traduzido) + 14) - 2}"
    ]
    memoria_codigo_traduzido.extend(macro_traduzida)

def traduzir_multiplicacao_com_2_registradores(registrador1, registrador2, auxiliar1, auxiliar2, auxiliar3, memoria_codigo_traduzido):
    traduzir_zerar(auxiliar1, memoria_codigo_traduzido)
    traduzir_zerar(auxiliar2, memoria_codigo_traduzido)
    traduzir_zerar(auxiliar3, memoria_codigo_traduzido)
    macro_traduzida = [
        # Verifica se o segundo registrador está zerado.
        # Se estiver, pula diretamente para a etapa de zerar o primeiro registrador, pois o produto será zero.
        # Caso contrário, verifica se o primeiro registrador também está zerado.
        f"TST {registrador2} VÁ_PARA {len(memoria_codigo_traduzido) + 16} SENÃO {len(memoria_codigo_traduzido) + 1}",
        # Verifica se o primeiro registrador está zerado.
        # Se estiver, encerra a multiplicação, pois o produto será zero.
        # Caso contrário, inicia as repetições da multiplicação.
        f"TST {registrador1} VÁ_PARA {len(memoria_codigo_traduzido) + 21} SENÃO {(len(memoria_codigo_traduzido) + 1) + 1}",
        # Decrementa o segundo registrador para contabilizar uma repetição da multiplicação.
        f"DEC {registrador2}",
        f"DEC {registrador1}",
        f"INC {auxiliar1}",
        f"INC {auxiliar2}",
        # Verifica se o primeiro registrador já foi zerado durante a transferência.
        # Se ainda possuir valor, continua transferindo as suas unidades.
        # Caso contrário, inicia a restauração do primeiro registrador.
        f"TST {registrador1} VÁ_PARA {len(memoria_codigo_traduzido) + 7} SENÃO {(len(memoria_codigo_traduzido) + 6) - 3}",
        f"DEC {auxiliar2}",
        f"INC {registrador1}",
        # Verifica se todas as unidades do segundo auxiliar já foram devolvidas.
        # Se ainda houver unidades, continua a restauração.
        # Caso contrário, considera concluída uma repetição da multiplicação.
        f"TST {auxiliar2} VÁ_PARA {len(memoria_codigo_traduzido) + 10} SENÃO {(len(memoria_codigo_traduzido) + 9) - 2}",
        # Contabiliza uma repetição concluída no terceiro auxiliar.
        f"INC {auxiliar3}",
        # Verifica se o segundo registrador já foi zerado.
        # Se ainda possuir valor, inicia outra repetição da multiplicação.
        # Caso contrário, inicia sua restauração.
        f"TST {registrador2} VÁ_PARA {len(memoria_codigo_traduzido) + 12} SENÃO {(len(memoria_codigo_traduzido) + 11) - 9}",
        f"DEC {auxiliar3}",
        f"INC {registrador2}",
        # Verifica se todas as repetições contabilizadas no terceiro auxiliar já foram restauradas ao segundo registrador.
        # Se ainda houver unidades, continua a restauração.
        # Caso contrário, segue para zerar o primeiro registrador.
        f"TST {auxiliar3} VÁ_PARA {len(memoria_codigo_traduzido) + 15} SENÃO {(len(memoria_codigo_traduzido) + 14) - 2}",
        f"DEC {registrador1}",
        # Verifica se o primeiro registrador já foi zerado.
        # Se ainda possuir valor, continua zerando.
        # Caso contrário, verifica se o segundo registrador também está zerado.
        f"TST {registrador1} VÁ_PARA {len(memoria_codigo_traduzido) + 17} SENÃO {(len(memoria_codigo_traduzido) + 16) - 1}",
        # Verifica se o segundo registrador está zerado.
        # Se estiver, encerra a multiplicação, pois o resultado já é zero.
        # Caso contrário, inicia a transferência do produto acumulado no primeiro auxiliar.
        f"TST {registrador2} VÁ_PARA {len(memoria_codigo_traduzido) + 21} SENÃO {(len(memoria_codigo_traduzido) + 17) + 1}",
        f"DEC {auxiliar1}",
        f"INC {registrador1}",
        # Verifica se o primeiro auxiliar já foi zerado durante a transferência.
        # Se ainda possuir valor, continua transferindo o produto ao primeiro registrador.
        # Caso contrário, encerra a multiplicação.
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
        # Verifica se o dividendo está zerado.
        # Se estiver, encerra a divisão, pois o quociente e o resto serão zero.
        # Caso contrário, verifica se o divisor também está zerado.
        f"TST {registrador1} VÁ_PARA {len(memoria_codigo_traduzido) + 26} SENÃO {len(memoria_codigo_traduzido) + 1}",
        # Verifica se o divisor está zerado.
        # Se estiver, encerra a divisão para evitar uma divisão por zero.
        # Caso contrário, inicia o cálculo.
        f"TST {registrador2} VÁ_PARA {len(memoria_codigo_traduzido) + 26} SENÃO {(len(memoria_codigo_traduzido) + 1) + 1}",
        f"DEC {registrador1}",
        f"INC {resto}",
        f"INC {auxiliar1}",

        f"DEC {resto}",
        f"DEC {registrador2}",
        f"INC {auxiliar2}",
        f"INC {auxiliar3}",

        # Inicia a comparação de igualdade entre o resto e o divisor.
        # Os dois registradores são decrementados simultaneamente para verificar se chegam a zero ao mesmo tempo.

        # Verifica se o resto está zerado.
        # Se estiver, verifica se o divisor também chegou a zero.
        # Caso contrário, continua a comparação.
        f"TST {resto} VÁ_PARA {len(memoria_codigo_traduzido) + 11} SENÃO {(len(memoria_codigo_traduzido) + 9) + 1}",
        # Verifica se o divisor está zerado.
        # Se estiver, inicia a restauração do resto, pois ele ainda possui valor.
        # Caso contrário, retorna ao decremento do resto para continuar a comparação.
        f"TST {registrador2} VÁ_PARA {len(memoria_codigo_traduzido) + 12} SENÃO {(len(memoria_codigo_traduzido) + 10) - 5}",
        # Verifica se o divisor está zerado após o resto também ter chegado a zero.
        # Se estiver, os dois valores eram iguais e inicia a restauração do divisor.
        # Caso contrário, inicia a restauração do resto.
        f"TST {registrador2} VÁ_PARA {len(memoria_codigo_traduzido) + 15} SENÃO {(len(memoria_codigo_traduzido) + 11) + 1}",
        f"DEC {auxiliar2}",
        f"INC {resto}",
        # Verifica se o segundo auxiliar está zerado.
        # Se estiver, conclui a restauração do resto.
        # Caso contrário, continua devolvendo as unidades retiradas.
        f"TST {auxiliar2} VÁ_PARA {len(memoria_codigo_traduzido) + 15} SENÃO {(len(memoria_codigo_traduzido) + 14) - 2}",
        f"DEC {auxiliar3}",
        f"INC {registrador2}",
        # Verifica se o terceiro auxiliar está zerado.
        # Se estiver, conclui a restauração do divisor.
        # Caso contrário, continua devolvendo as unidades retiradas.
        f"TST {auxiliar3} VÁ_PARA {len(memoria_codigo_traduzido) + 18} SENÃO {(len(memoria_codigo_traduzido) + 17) - 2}",
        f"DEC {auxiliar2}",
        # Verifica se o segundo auxiliar está zerado.
        # Se estiver, segue para verificar o resto.
        # Caso contrário, continua decrementando até zerar o segundo auxiliar.
        f"TST {auxiliar2} VÁ_PARA {len(memoria_codigo_traduzido) + 20} SENÃO {(len(memoria_codigo_traduzido) + 19) - 1}",
        # Verifica se o resto está zerado após a comparação.
        # Se estiver, significa que o resto e o divisor eram iguais, então incrementa o quociente.
        # Caso contrário, não houve igualdade e segue para restaurar o dividendo.
        f"TST {resto} VÁ_PARA {len(memoria_codigo_traduzido) + 21} SENÃO {(len(memoria_codigo_traduzido) + 20) + 2}",
        f"INC {quociente}",
        # Verifica se o dividendo está zerado.
        # Se estiver, inicia a restauração do valor original.
        # Caso contrário, retorna ao início do cálculo para retirar outra unidade.
        f"TST {registrador1} VÁ_PARA {len(memoria_codigo_traduzido) + 23} SENÃO {(len(memoria_codigo_traduzido) + 22) - 20}",
        f"DEC {auxiliar1}",
        f"INC {registrador1}",
        # Verifica se o primeiro auxiliar está zerado.
        # Se estiver, encerra a divisão.
        # Caso contrário, continua restaurando o dividendo.
        f"TST {auxiliar1} VÁ_PARA {len(memoria_codigo_traduzido) + 26} SENÃO {(len(memoria_codigo_traduzido) + 25) - 2}"
    ]
    memoria_codigo_traduzido.extend(macro_traduzida)


def traduzir_codigo(memoria_codigo):
    memoria_rotulos = {}
    memoria_codigo_traduzido = []
    # Percorre todas as linhas do código não traduzido.
    for conteudo_linha in memoria_codigo:
        # Ignora linhas vazias.
        if not conteudo_linha:
            continue

        if re.fullmatch(PADROES_SINTAXE["RÓTULO"], conteudo_linha):
            memoria_rotulos[conteudo_linha.removesuffix(":")] = len(memoria_codigo_traduzido)
            continue

        # Mantém as instruções primitivas da Máquina Norma sem alterações.
        if re.fullmatch(PADROES_SINTAXE["INC"], conteudo_linha) or re.fullmatch(PADROES_SINTAXE["DEC"], conteudo_linha) or re.fullmatch(PADROES_SINTAXE["TST"], conteudo_linha):
            memoria_codigo_traduzido.append(conteudo_linha)
            continue

        # Identifica as macros e extrai os seus argumentos para realizar a tradução.

        condiz = re.fullmatch(PADROES_SINTAXE["MACRO_ZERAR"], conteudo_linha)
        if condiz:
            registrador1 = conteudo_linha.split()[1]
            traduzir_zerar(registrador1, memoria_codigo_traduzido)
            continue

        condiz = re.fullmatch(PADROES_SINTAXE["MACRO_ATRIBUIÇÃO"], conteudo_linha)
        if condiz:
            partes = conteudo_linha.split(" := ")
            registrador1 = partes[0]
            valor = int(partes[1])
            traduzir_atribuicao(registrador1, valor, memoria_codigo_traduzido)
            continue

        condiz = re.fullmatch(PADROES_SINTAXE["MACRO_SOMA_COM_2_REGISTRADORES"], conteudo_linha)
        if condiz:
            registrador1, registrador2, auxiliar1 = condiz.groups()
            traduzir_soma_com_2_registradores(registrador1, registrador2, auxiliar1, memoria_codigo_traduzido)
            continue

        condiz = re.fullmatch(PADROES_SINTAXE["MACRO_SOMA_COM_3_REGISTRADORES"], conteudo_linha)
        if condiz:
            registrador3, registrador1, registrador2, auxiliar1, auxiliar2 = condiz.groups()
            traduzir_soma_com_3_registradores(registrador1, registrador2, registrador3, auxiliar1, auxiliar2, memoria_codigo_traduzido)
            continue

        condiz = re.fullmatch(PADROES_SINTAXE["MACRO_SUBTRAÇÃO_COM_2_REGISTRADORES"], conteudo_linha)
        if condiz:
            registrador1, registrador2, auxiliar1 = condiz.groups()
            traduzir_subtracao_com_2_registradores(registrador1, registrador2, auxiliar1, memoria_codigo_traduzido)
            continue

        condiz = re.fullmatch(PADROES_SINTAXE["MACRO_SUBTRAÇÃO_COM_3_REGISTRADORES"], conteudo_linha)
        if condiz:
            registrador3, registrador1, registrador2, auxiliar1, auxiliar2 = condiz.groups()
            traduzir_subtracao_com_3_registradores(registrador1, registrador2, registrador3, auxiliar1, auxiliar2, memoria_codigo_traduzido)
            continue

        condiz = re.fullmatch(PADROES_SINTAXE["MACRO_MULTIPLICAÇÃO_COM_2_REGISTRADORES"], conteudo_linha)
        if condiz:
            registrador1, registrador2, auxiliar1, auxiliar2, auxiliar3 = condiz.groups()
            traduzir_multiplicacao_com_2_registradores(registrador1, registrador2, auxiliar1, auxiliar2, auxiliar3, memoria_codigo_traduzido)
            continue

        condiz = re.fullmatch(PADROES_SINTAXE["MACRO_MULTIPLICAÇÃO_COM_3_REGISTRADORES"], conteudo_linha)
        if condiz:
            registrador3, registrador1, registrador2, auxiliar1, auxiliar2 = condiz.groups()
            traduzir_multiplicacao_com_3_registradores(registrador1, registrador2, registrador3, auxiliar1, auxiliar2, memoria_codigo_traduzido)
            continue

        condiz = re.fullmatch(PADROES_SINTAXE["MACRO_DIVISÃO"], conteudo_linha)
        if condiz:
            quociente, registrador1, registrador2, resto, auxiliar1, auxiliar2, auxiliar3 = condiz.groups()
            traduzir_divisao(quociente, registrador1, registrador2, resto, auxiliar1, auxiliar2, auxiliar3, memoria_codigo_traduzido)
            continue

    # Percorre o código traduzido para resolver os rótulos utilizados nas instruções TST.
    for valor_linha, conteudo_linha in enumerate(memoria_codigo_traduzido):
        condiz = re.fullmatch(PADROES_SINTAXE["TST"], conteudo_linha)
        if condiz:
            registrador1, salto_zero, salto_nao_zero = condiz.groups()

            # Substitui os nomes dos rótulos pelos índices das instruções correspondentes.
            salto_zero = memoria_rotulos.get(salto_zero, salto_zero)
            salto_nao_zero = memoria_rotulos.get(salto_nao_zero, salto_nao_zero)

            # Atualiza a instrução TST com os destinos dos saltos já resolvidos.
            memoria_codigo_traduzido[valor_linha] = f"TST {registrador1} VÁ_PARA {salto_zero} SENÃO {salto_nao_zero}"

    return memoria_codigo_traduzido

def executar_instrucao(memoria_codigo_traduzido, memoria_registradores, pc):
    # Obtém a instrução correspondente ao contador de programa (PC).
    linha = memoria_codigo_traduzido[pc]

    # Verifica se a instrução é INC.
    condiz = re.fullmatch(PADROES_SINTAXE["INC"], linha)
    if condiz:
        registrador1 = linha.split()[1]

        # Cria o registrador caso ele ainda não exista na memória.
        if not registrador_existe(registrador1, memoria_registradores):
            criar_registrador(registrador1, memoria_registradores)

        # Executa o incremento e atualiza o contador de programa.
        pc = inc(registrador1, pc, memoria_registradores)

    # Verifica se a instrução é DEC.
    condiz = re.fullmatch(PADROES_SINTAXE["DEC"], linha)
    if condiz:
        registrador1 = linha.split()[1]

        # Cria o registrador caso ele ainda não exista na memória.
        if not registrador_existe(registrador1, memoria_registradores):
            criar_registrador(registrador1, memoria_registradores)

        # Executa o decremento e atualiza o contador de programa.
        pc = dec(registrador1, pc, memoria_registradores)

    # Verifica se a instrução é TST.
    condiz = re.fullmatch(PADROES_SINTAXE["TST"], linha)
    if condiz:
        partes = linha.split()
        registrador1 = partes[1]

        # Cria o registrador caso ele ainda não exista na memória.
        if not registrador_existe(registrador1, memoria_registradores):
            criar_registrador(registrador1, memoria_registradores)

        # Obtém os destinos dos saltos para os casos de valor zero e diferente de zero.
        salto_zero = int(partes[3])
        salto_nao_zero = int(partes[5])

        # Executa o teste e atualiza o contador de programa conforme o resultado.
        pc = tst(registrador1, salto_zero, salto_nao_zero, memoria_registradores)

    return pc

pc = 0
memoria_registradores = {}
memoria_codigo = []

# Mantém o menu principal ativo até que o usuário escolha sair.
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
                # Carrega o arquivo e verifica se existem erros de sintaxe.
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
                # Traduz as macros para as instruções primitivas da Máquina Norma.
                memoria_codigo_traduzido = traduzir_codigo(memoria_codigo)

        case 2:
            if not memoria_codigo:
                print("\nNenhum arquivo foi carregado. Por favor, carregue um arquivo .norma ou .txt para continuar.")
            else:
                contador = 1
                limite = int(input("\nDigite o valor do limite de execuções: "))
                # Executa as instruções continuamente até o término do código ou o limite de execuções.
                while pc != len(memoria_codigo_traduzido) and contador <= limite:
                    pc = executar_instrucao(memoria_codigo_traduzido, memoria_registradores, pc)
                    contador += 1
                # Exibe os valores finais dos registradores.
                for registrador, valor in memoria_registradores.items():
                    print(f"{registrador}: {valor} | ", end="")
                print("\n")
            # Reinicia o estado da máquina para uma próxima execução.
            pc = 0
            memoria_registradores.clear()

        case 3:
            if not memoria_codigo:
                print("\nNenhum arquivo foi carregado. Por favor, carregue um arquivo .norma ou .txt para continuar.")
            else:
                contador = 1
                limite = int(input("\nDigite o valor do limite de execuções: "))
                # Permite executar uma instrução por vez, exibindo o estado da máquina após cada execução.
                while pc != len(memoria_codigo_traduzido) and contador <= limite:
                    print(f"\nInstrução atual do IP: {memoria_codigo_traduzido[pc]}\n")
                    escolha_passo_a_passo = int(input("Digite 1 para executar a instrução ou 2 para voltar para o menu: "))
                    if escolha_passo_a_passo == 2:
                        break
                    pc = executar_instrucao(memoria_codigo_traduzido, memoria_registradores, pc)
                    print()
                    for registrador, valor in memoria_registradores.items():
                        print(f"{registrador}: {valor} | ", end="")
                    print()
                    contador += 1
            # Reinicia o estado da máquina para uma próxima execução.
            pc = 0
            memoria_registradores.clear()

        case 4:
            print("\nSaindo do simulador...")
            break

        case _:
            print("\nEscolha inválida! Por favor, digite um valor válido.")

    