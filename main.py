import PyPDF2
import re

import io
from correpy.parsers.brokerage_notes.parser_factory import ParserFactory

import csv

caminho_arquivo = 'samples/2017-XPINC_NOTA_NEGOCIACAO_B3_2_2017.pdf'  

# with open(caminho_arquivo, 'rb') as f:
#     content = io.BytesIO(f.read())
#     content.seek(0)
    
#     brokerage_notes = ParserFactory(brokerage_note=content, password="password").parse()

#     print('fim')

def pdf_to_txt(caminho_pdf):
    texto = ""
    try:
        with open(caminho_pdf, 'rb') as arquivo_pdf:
            leitor_pdf = PyPDF2.PdfReader(arquivo_pdf)
            num_paginas = len(leitor_pdf.pages)

            for num_pagina in range(num_paginas):
                pagina = leitor_pdf.pages[num_pagina]
                texto += pagina.extract_text()
        return texto
    except FileNotFoundError:
        return "Arquivo não encontrado."
    except Exception as e:
        return f"Ocorreu um erro: {e}"

def teste():
    
    txt_base = pdf_to_txt(caminho_arquivo)
    txt_base = txt_base.replace('\n', '\t')

    data_bovespa_xp = r"(Data pregão\t\d{2}/\d{2}/\d{4}\t)"

    if "Ocorreu um erro" in txt_base or "Arquivo não encontrado." in txt_base:
        print(txt_base) # Imprime a mensagem de erro
    else:
        # XP Bovespa
        inicio_bovespa = "Negócios realizados\tQ\tNegociação\tC/V\tTipo mercado\tPrazo\tEspecificação do título\tObs. (*)\tQuantidade\tPreço / Ajuste\tValor Operação / Ajuste\tD/C\t"
        inicio_bvmf = "C/V\tMercadoria\tVencimento\tQuantidade\tPreço/Ajuste\tTipo Negócio\tVlr de Operação/Ajuste\tD/C\tTaxa Operacional\t"

        nota_bovespa = ""
        nota_bvmf = ""

        book = []
        nota = []

        while txt_base:
            if (txt_base[:143] == inicio_bovespa):
                f1 = txt_base[143:].find(inicio_bovespa) + 143
                f2 = txt_base.find(inicio_bvmf)

                if f1 == 142: f1 = 1000000
                if f2 == 106: f2 = 1000000

                if f1 < f2:
                    f3 = f1
                else:
                    f3 = f2

                nota_bovespa += (txt_base[:f3])
                txt_base = txt_base[f3:]
            elif (txt_base[:107] == inicio_bvmf):
                f1 = txt_base[107:].find(inicio_bvmf) + 107
                f2 = txt_base.find(inicio_bovespa)

                if f1 == 106: f1 = 1000000
                if f2 == 142: f2 = 1000000

                if f1 < f2:
                    f3 = f1
                else:
                    f3 = f2

                nota_bvmf += (txt_base[:f3])
                txt_base = txt_base[f3:]
            else :
                print("fim", txt_base)
                txt_base = ""


        if nota_bovespa:
            b3_SINACOR(nota_bovespa)
            # nota_bovespa = nota_bovespa.replace('\tD/C\t', '\tD/C\n')
            # nota_bovespa = nota_bovespa.replace('\t1-BOVESPA\t', '\n1-BOVESPA\t')
            # nota_bovespa = nota_bovespa.replace('\tNOTA DE NEGOCIAÇÃO\t', '\nNOTA DE NEGOCIAÇÃO\t')
            # nota_bovespa = re.sub(data_bovespa_xp, r"\1\n", nota_bovespa)
            # nota_bovespa = nota_bovespa.replace('\tP. Vinc\tN\t', '\nP. Vinc N\t')
            # nota_bovespa = nota_bovespa.replace('\tResumo dos Negócios\t', '\nResumo dos Negócios\t')
            # nota_bovespa = nota_bovespa.replace('\tL - Precatório\t', '\nL - Precatório\t')
            # nota_bovespa = nota_bovespa.replace('\tResumo Financeiro\t', '\nResumo Financeiro\t')
            # linhas = nota_bovespa.split('\n')

            
            # for linha in linhas:
                
            #     # Operações
            #     if linha[:9] == "1-BOVESPA":
            #         linha = linha.split('\t')
            #         tam = len(linha)

            #         cv = linha[1]
            #         ativo = linha[3]
            #         qtd = linha[tam-4]
            #         preco = linha[tam-3]
            #         valor = linha[tam-2]

            #         lanc = [cv, ativo, qtd, preco, valor]

            #         nota.append(lanc)
            #     # Data e Nº
            #     if linha[:18] == "NOTA DE NEGOCIAÇÃO":
            #         dados = linha.split('\t')

            #         for i in range(len(nota)):
            #             nota[i].append(dados[2]) # Nº Nota
            #             nota[i].append(dados[6]) # Data Pregão

            #     # Resumo
            #     if linha[:7] == "P. Vinc":
            #         dados = linha.split('\t')
                    
            #         nota[i].append(dados[7]) # Valor das operações
            #         for i in range(len(nota)):
            #             for x in range(8):
            #                 nota[i].append(dados[(x+1)]) # Debêntures, Vendas à vista,Compras à vista, Opções -compras, Opções - vendas, Operaçõesàtermo, Valor das oper.c/ títulos públ. (v. nom.), Valor das operações

            #     # Tarifas
            #     if linha[:14] == "L - Precatório":
            #         dados = linha.split('\t')
                    
            #         for i in range(len(nota)):
            #             # nota[i].append(dados[1])  # Total CBLC      C       
            #             nota[i].append(dados[4])  # Valor líquido das operações     C       
            #             nota[i].append(dados[7])  # Taxa de liquidação      D       
            #             nota[i].append(dados[10]) # Taxa de Registro        D       
            #             # nota[i].append(dados[13]) # Total Bovespa / Soma    D       
            #             nota[i].append(dados[16]) # Taxa de termo/opções    D       
            #             nota[i].append(dados[19]) # Taxa A.N.A.     D       
            #             nota[i].append(dados[22]) # Emolumentos     D               
            #             # nota[i].append(dados[26]) # Total Custos / Despesas D               
            #             nota[i].append(dados[30]) # Taxa Operacional        D      
            #             nota[i].append(dados[33]) # Execução         
            #             nota[i].append(dados[35]) # Taxa de Custódia        
            #             nota[i].append(dados[37]) # Impostos        D       
            #             nota[i].append(dados[40]) # I.R.R.F. s/ operações, base R$2.310,00  
            #             nota[i].append(dados[42]) # Outros  D       
            #             nota[i].append(dados[45])  if nota[i].append(dados[47]) == "C" else nota[i].append("-"+dados[45])# Líquido para 07/03/2017 C

            #             # print(nota[i])

            #         book.append(nota)
            #         nota = []
            
            # print(f'Quantidade de notas: {len(book)}')
            # print("==========================================================")
            # for i in range(len(book)):
            #     print(f'Nota {book[i][0][5]} de {book[i][0][6]} possui {len(book[i])} lançamentos com valor líquido de R$ {book[i][0][len(book[i][0])-1]}')
                        

            # print("fim")
            # nota_bvmf = nota_bvmf.replace("\tTaxa Operacional\t", "tTaxa Operacional\n")

                    

                
        


        # print(txt_base)
        # print(txt_base[:5000]) # Imprime os primeiros 500 caracteres para visualização rápida
        # Para salvar em um arquivo de texto
        # with open("txt_base.txt", "w", encoding="utf-8") as arquivo_texto:
        #    arquivo_texto.write(txt_base)





def b3_SINACOR(nota_bovespa):
    nota_bovespa = nota_bovespa.replace("\tQ\t", "\nQ\t")
    nota_bovespa = nota_bovespa.replace("Negócios realizados", "\nNegócios realizados")
    nota_bovespa = nota_bovespa.replace("Ajuste\tD/C\t","Ajuste\tD/C\n")
    nota_bovespa = nota_bovespa.replace("1-BOVESPA\t", "\n1-BOVESPA\t")
    nota_bovespa = nota_bovespa.replace("\tNOTA DE NEGOCIAÇÃO\t", "\nNOTA DE NEGOCIAÇÃO\t")
    nota_bovespa = nota_bovespa.replace("\tP. Vinc\t", "\nP. Vinc\t")
    nota_bovespa = nota_bovespa.replace("\tResumo dos Negócios\t", "\nResumo dos Negócios\t")
    nota_bovespa = nota_bovespa.replace("\tL - Precatório\t", "\nL - Precatório\t")
    nota_bovespa = nota_bovespa.replace("\tResumo Financeiro\t", "\nResumo Financeiro\t")
    nota_bovespa = nota_bovespa.replace("\n\n", "\n")
    nota_bovespa = nota_bovespa.split("\n")

    date_pattern = r'\b\d{2}/\d{2}/\d{4}\b'
    number_pattern = r'\t\d{2,10}\t|\t\d{1,3}?\.\d{1,3}?\.\d{1,3}\t'
    valor_pattern = r'\d{1,3}(?:\.\d{3})*,\d{2}'
    corretora_pattern = r"\b\d{2}/\d{2}/\d{4}\b\s+(\w+)"

    notas = []
    operacao = []
    data_pregao = ""
    num_nota = ""
    corretora = ""
    negocios = []
    financeiro = []
    
    for i in nota_bovespa:
        
        if i.startswith("\t") : i = i[1:]
        if i.endswith("\t") : i = i[:-1]

        if i.startswith("1-BOVESPA"):
            i = i.split("\t")
            n = len(i)
            operacao.append([
                i[1],                                                                       # 00 C/V
                i[2],                                                                       # 01 Mercado
                i[3] if "FRACIONADO/VISTA".find(i[2]) == -1 else "",                        # 02 Prazo
                "",                                                                         # 03 Ticker
                i[3] if "FRACIONADO/VISTA".find(i[2]) >= 0 else i[4],                       # 04 Ativo
                i[n-4],                                                                     # 05 Qtd
                i[n-3],                                                                     # 06 Preço
                i[n-2]]                                                                     # 07 Valor
            ) 
        elif i.startswith("NOTA DE NEGOCIAÇÃO"):
            data_pregao = re.findall(date_pattern, i)[0]                                    # 08 Data Pregao
            num_nota = re.findall(number_pattern , i)[0].replace("\t","")                   # 09 Número Nota
            corretora = re.findall(corretora_pattern  , i)[0]                               # 10 Corretora
            # for reg in range(len(operacao)):
            #     operacao[reg].append( re.findall(date_pattern, i)[0])                       # 08 Data Pregao
            #     operacao[reg].append( re.findall(number_pattern , i)[0].replace("\t",""))   # 09 Número Nota
            #     operacao[reg].append( re.findall(corretora_pattern  , i)[0])                # 10 Corretora
                 
        elif i.startswith("P. Vinc"):
            negocios = re.findall(valor_pattern  , i)
            # if len(negocios) > 7:
            #     for reg in range(len(operacao)):
            #         operacao[reg].append(negocios[0])                                           # 11 Debêntures
            #         operacao[reg].append(negocios[1])                                           # 12 Vendas à vista
            #         operacao[reg].append(negocios[2])                                           # 13 Compras à vista
            #         operacao[reg].append(negocios[3])                                           # 14 Opções - compras
            #         operacao[reg].append(negocios[4])                                           # 15 Opções - vendas
            #         operacao[reg].append(negocios[5])                                           # 16 Operações à termo
            #         operacao[reg].append(negocios[6])                                           # 17 Valor das oper. c/ títulos públ. (v. nom.)
            #         operacao[reg].append(negocios[7])                                           # 18 Valor das operações
                
        elif i.startswith("L - Precatório"):
            financeiro = re.findall(valor_pattern  , i)
            if len(financeiro) > 16:
                for reg in range(len(operacao)):
                    operacao[reg].append(data_pregao)                                           # 08 Data Pregao
                    operacao[reg].append(num_nota)                                              # 09 Número Nota
                    operacao[reg].append(corretora)                                             # 10 Corretora

                    operacao[reg].append(negocios[0])                                           # 11 Debêntures
                    operacao[reg].append(negocios[1])                                           # 12 Vendas à vista
                    operacao[reg].append(negocios[2])                                           # 13 Compras à vista
                    operacao[reg].append(negocios[3])                                           # 14 Opções - compras
                    operacao[reg].append(negocios[4])                                           # 15 Opções - vendas
                    operacao[reg].append(negocios[5])                                           # 16 Operações à termo
                    operacao[reg].append(negocios[6])                                           # 17 Valor das oper. c/ títulos públ. (v. nom.)
                    operacao[reg].append(negocios[7])                                           # 18 Valor das operações

                    operacao[reg].append(financeiro[0])                                         # 19 Total CBLC 
                    operacao[reg].append(financeiro[1])                                         # 20 Valor líquido das operações 
                    operacao[reg].append(financeiro[2])                                         # 12 Taxa de liquidação 
                    operacao[reg].append(financeiro[3])                                         # 22 Taxa de Registro 
                    operacao[reg].append(financeiro[4])                                         # 23 Total Bovespa / Soma
                    operacao[reg].append(financeiro[5])                                         # 24 Taxa de termo/opções
                    operacao[reg].append(financeiro[6])                                         # 25 Taxa A.N.A.
                    operacao[reg].append(financeiro[7])                                         # 26 Emolumentos
                    operacao[reg].append(financeiro[8])                                         # 27 Total Custos / Despesas
                    operacao[reg].append(financeiro[9])                                         # 29 Taxa Operacional
                    operacao[reg].append(financeiro[10])                                        # 30 Execução
                    operacao[reg].append(financeiro[11])                                        # 31 Taxa de Custódia
                    operacao[reg].append(financeiro[12])                                        # 32 Impostos
                    operacao[reg].append(financeiro[13])                                        # 33 I.R.R.F. s/ operações
                    operacao[reg].append(financeiro[14])                                        # 34 Base I.R.R.F 
                    operacao[reg].append(financeiro[15])                                        # 35 Outros
                    operacao[reg].append(financeiro[16])                                        # 36 Total Líquido

                notas.append(operacao)
                
                data_pregao = ""
                num_nota = ""
                corretora = ""
                negocios = []
                financeiro = []
                operacao = []

    

    with open("notas.csv", mode='a', newline='', encoding='utf-8') as arquivo_csv:
        escritor_csv = csv.writer(arquivo_csv)
        for row in notas:
            escritor_csv.writerows(row)

    print(f"Arquivo CSV 'notas.csv' criado com sucesso!")


cabecalho = [[
"C/V",
"Mercado",
"Prazo",
"Ticker",
"Ativo",
"Qtd",
"Preço",
"Valor",
"Data Pregao",
"Número Nota",
"Corretora",
"Debêntures",
"Vendas à vista",
"Compras à vista",
"Opções - compras",
"Opções - vendas",
"Operações à termo",
"Valor das oper. c/ títulos públ. (v. nom.)",
"Valor das operações",
"Total CBLC ",
"Valor líquido das operações ",
"Taxa de liquidação ",
"Taxa de Registro ",
"Total Bovespa / Soma",
"Taxa de termo/opções",
"Taxa A.N.A.",
"Emolumentos",
"Total Custos / Despesas",
"Taxa Operacional",
"Execução",
"Taxa de Custódia",
"Impostos",
"I.R.R.F. s/ operações",
"Base I.R.R.F ",
"Outros",
"Total Líquido"
]]

with open("notas.csv", mode='w', newline='', encoding='utf-8') as arquivo_csv:
    escritor_csv = csv.writer(arquivo_csv)
    # Escrever cada linha de dados no arquivo CSV
    escritor_csv.writerows(cabecalho)
teste()
