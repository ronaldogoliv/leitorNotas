from PyPDF2 import PdfReader
from openpyxl import Workbook
import re
import os
from datetime import datetime


titulo = ''
diretorios = [
    'C:/Users/ronal/OneDrive/IR/Notas de Corretagem/Rico/2016/',
    'C:/Users/ronal/OneDrive/IR/Notas de Corretagem/Rico/2017/',
    'C:/Users/ronal/OneDrive/IR/Notas de Corretagem/Rico/2018/',
    'C:/Users/ronal/OneDrive/IR/Notas de Corretagem/Rico/2019/',
    'C:/Users/ronal/OneDrive/IR/Notas de Corretagem/Rico/2020/',
    'C:/Users/ronal/OneDrive/IR/Notas de Corretagem/Rico/2021/',
    'C:/Users/ronal/OneDrive/IR/Notas de Corretagem/Rico/2022/',
    'C:/Users/ronal/OneDrive/IR/Notas de Corretagem/Rico/2023/',

    'C:/Users/ronal/OneDrive/IR/Notas de Corretagem/XP/2017/',
    'C:/Users/ronal/OneDrive/IR/Notas de Corretagem/XP/2018/',
    'C:/Users/ronal/OneDrive/IR/Notas de Corretagem/XP/2019/',
    'C:/Users/ronal/OneDrive/IR/Notas de Corretagem/XP/2021/',
    'C:/Users/ronal/OneDrive/IR/Notas de Corretagem/XP/2023/',

    'C:/Users/ronal/OneDrive/IR/Notas de Corretagem/Clear/',

    'C:/Users/ronal/OneDrive/IR/Notas de Corretagem/Modal/',

    'C:/Users/ronal/OneDrive/IR/Notas de Corretagem/Nu/2021/',
    'C:/Users/ronal/OneDrive/IR/Notas de Corretagem/Nu/2022/',

    'C:/Users/ronal/OneDrive/IR/Notas de Corretagem/Genial/2021/',
    'C:/Users/ronal/OneDrive/IR/Notas de Corretagem/Genial/2022/',
    'C:/Users/ronal/OneDrive/IR/Notas de Corretagem/Genial/2023/',

    'C:/Users/ronal/OneDrive/IR/Notas de Corretagem/Itaú/',
]

# Padrões genéricos
inteiro = re.compile(r'[0-9]{1,10}')
data = re.compile(r'[0-9]{2}\/[0-9]{2}\/[0-9]{4}')

operacoes = []
operacoes.append(re.compile(r'q *negociação.+(resumo  *d[a-z]*[a-z]* negócios)')) #0
operacoes.append(re.compile(r'(?<=c ).+')) #1
operacoes.append(re.compile(r'(?<=[0-9][0-9] )[cd]{1} ')) #2

operacoes.append(re.compile(r'c/v mercadoria .+(nota de negociação)|c/v mercadoria .+(nota de negociação)|c/v mercadoria .+(venda disponível)')) #3

cv = ' [cv]{1} *vista'
cv += '| [cv]{1} *fracionario'
cv += '| [cv]{1} *opcao'
cv += '| [cv]{1} *exerc'
cv = re.compile(cv)


p_ativo = '(?<=vista\s)(.*)(?=\s\d+\s)'
p_ativo += '|(?<=fracionario\s)(.*)(?=\s\d+\s)'
p_ativo += '|(?<=opcao de venda\s)(.*)(?=\s\d+\s)'
p_ativo += '|(?<=opcao de compra\s)(.*)(?=\s\d+\s)'
p_ativo += '|(?<=exercicio de opcao de venda\s)(.*)(?=\s\d+\s)'
p_ativo += '|(?<=exercicio de opcao de compra\s)(.*)(?=\s\d+\s)'
p_ativo += '|(?<=exerc opc  venda\s)(.*)(?=\s\d+\s)'
p_ativo += '|(?<=exerc opc compra\s)(.*)(?=\s\d+\s)'
p_ativo += '|(?<=exerc opc venda\s)(.*)(?=\s\d+\s)'
p_ativo += '|(?<=exerc opc  compra\s)(.*)(?=\s\d+\s)'
p_ativo = re.compile(p_ativo)

dt_inicio = None
dt_fim = None
numero_nota_old = None
numero_nota = None
corretora = None



def get_corretora(txt, arquivo):
    p_corretora = 'xp *investimentos *cctvm'
    p_corretora += '|xp *investimentos *corretora'
    p_corretora += '|clear *corretora'
    p_corretora += '|rico *investimentos'
    p_corretora += '|rico *corretora'
    p_corretora += '|modal *dtvm *ltda'
    p_corretora += '|genial *investimentos *corretora *de *valores *mobiliários'
    p_corretora += '|genial *institucional *cctvm *s\/a'
    p_corretora += '|genial *cctvm *s\/a'
    p_corretora += '|nuinvest corretora de valores'
    p_corretora += '|itaú *corretora  de valores  s\/a'
    p_corretora += '|toro xxx'
    p_corretora = re.compile(p_corretora)
                    
    if p_corretora.search(txt):
        corretora = p_corretora.search(txt).group(0).strip().split(" ")[0].capitalize()
    else:
        corretora = arquivo

    return corretora


def get_market(operacao):
    
    if 'vista' in operacao:
        market = 'Vista'
    elif 'fracionario' in operacao:
        market = 'Fracionario'
    elif 'opcao' in operacao:
        market = 'Opções'
    elif 'exerc opc' in operacao:
        market = 'Exercício de opções'
    else:
        market = 'Futuro'
    
    return market


def get_sufix(desc):
    tipos = {
            ' UNT ': '11',
            ' CI ': '11',
            ' ON ': '3',
            ' PNR N1 ': '11',
            ' PRB P ': '11',
            ' PNA ': '5',
            ' PNB ': '6',
            ' PNC ': '7',
            ' PND ': '8',
            ' PNE ': '11',
            ' PNV ': '11',
            ' PN ': '4',
            ' AGF ': '11',
            ' BDR ': '11',
            ' BNS ': '11',
            ' DIR ORD ': '1',
            ' DIR PRE ': '2',
            ' FIDC ': '11',
            ' GPT ': '11',
            ' IBO ': '11',
            ' IBR ': '11',
            ' IBS ': '11',
            ' IBX ': '11',
            ' ICO ': '11',
            ' IDI ': '11',
            ' IDV ': '11',
            ' IEE ': '11',
            ' IFI ': '11',
            ' IFN ': '11',
            ' IGC ': '11',
            ' IGN ': '11',
            ' IMA ': '11',
            ' IMO ': '11',
            ' IND ': '11',
            ' ISE ': '11',
            ' ITA ': '11',
            ' IVB ': '11',
            ' MLC ': '11',
            ' SML ': '11',
            ' TPR ': '11',
            ' UTI ': '11',
            ' DIR ': '11',
            ' DRN EDR ': '34',
            ' DR1 ED ': '31',
            ' DRN ED ': '34',
            ' DRE ED ': '39',
            ' DRN A ': '34',
            ' DRN C ': '35',
            ' DR3 B ': '35',
            ' DR3 A ': '36',
            ' DR1 ': '31',
            ' DR2 ': '32',
            ' DR3 ': '33',
            ' DRN ': '34',
            ' DRE ': '39'
        }
    sufixo = ""
    desc = desc.upper()

    for tipo, cod in tipos.items():
        if tipo in desc:
            sufixo = cod
            return sufixo
        
    return sufixo  


def get_ticker(desc):
    ticker = desc
    tickerRE = re.compile(r'\w{5}\d{1,3}[wW][1-5][eE]* |\w{5}\d{1,3}[eE]* |\w{4}\d{1,2}[fF]* ')

    if tickerRE.search(desc):
        ticker = tickerRE.search(desc).group(0).upper().strip()
        if ticker[-1:] == "E":
           ticker = ticker[0:len(ticker)-1]

    else:
        companys = {
            '3R PETROLEUM':'RRRP',
            'ADVANCE AUTO':'A1AP',
            'ADVANCED MIC':'A1MD',
            'AGILENT TECH':'A1GI',
            'AIR PRODUCTS':'A1PD',
            'AKAMAI TECHN':'A1KA',
            'ALASKA AIR G':'A1LK',
            'ALBEMARLE CO':'A1LB',
            'ALEXANDRIA R':'A1RE',
            'ALFA CONSORC':'BRGE',
            'ALFA HOLDING':'RPAD',
            'ALIANSCSONAE':'ALSO',
            'ALIGN TECHNO':'A1LG',
            'ALLEGION PLC':'A1GN',
            'ALLIANCE DAT':'A1LL',
            'ALLIANT ENER':'A1EN',
            'ALLSTATE COR':'A1TT',
            'ALNYLAM PHAR':'A1LN',
            'ALTRIA GROUP':'MOOO',
            'AMERICAMOVIL':'A1MX',
            'AMERICAN AIR':'AALL',
            'AMERICAN ELE':'A1EP',
            'AMERICAN EXP':'AXPB',
            'AMERICAN TOW':'T1OW',
            'AMERICAN WAT':'A1WK',
            'AMERIPRISE F':'A1MP',
            'AMERISOURCEB':'A1MB',
            'AMPHENOL COR':'A1PH',
            'ANALOG DEVIC':'A1DI',
            'ANGLOGOLD AS':'A1UA',
            'AO SMITH COR':'A1OS',
            'APARTMENT IN':'A1IV',
            'APPLIED MATE':'A1MT',
            'ARCHER DANIE':'A1DM',
            'ARISTA NETWO':'A1NE',
            'ARTHUR J GAL':'A1JG',
            'ASCENDIS PHA':'A1SN',
            'ASSURANT INC':'A1SU',
            'ATLASSIAN CO':'T1AM',
            'ATMOS ENERGY':'A1TM',
            'AUTODESK INC':'A1UT',
            'AUTOHOME INC':'A1TH',
            'AUTOMATIC DT':'ADPR',
            'AUTOZONE INC':'AZOI',
            'AVALONBAY CO':'A1VB',
            'AVERY DENNIS':'A1VY',
            'BAKER HUGHES':'B1KR',
            'BANCO SANTAN':'B1SA',
            'BANK AMERICA':'BOAC',
            'BARCLAYS PLC':'B1CS',
            'BAXTER INTER':'B1AX',
            'BB ETF SP DV':'BBSD',
            'BBMLOGISTICA':'BBML',
            'BBSEGURIDADE':'BBSE',
            'BECTON DICKI':'B1DX',
            'BHP GROUP PL':'B1BL',
            'BILIBILI INC':'B1IL',
            'BIOMARIN PHA':'B1MR',
            'BIO-TECHNE C':'T1CH',
            'BORGWARNER I':'B1WA',
            'BOSTON SCIEN':'B1SX',
            'BR MALLS PAR':'BRML',
            'BRAD IMA-B5M':'B5MB',
            'BRAZILIAN SC':'BSCS',
            'BRISTOLMYERS':'BMYB',
            'BRITISH AMER':'B1TI',
            'BROADCOM INC':'AVGO',
            'BROADRIDGE F':'B1RF',
            'BROOKFIELD A':'B1AM',
            'BROWN FORMAN':'B1FC',
            'CABINDA PART':'CABI',
            'CABLE ONE IN':'C1AB',
            'CACONDE PART':'CACO',
            'CADENCE DESI':'C1DN',
            'CAESARS ENTT':'C2ZR',
            'CAIXA SEGURI':'CXSE',
            'CAIXAETFXBOV':'XBOV',
            'CAMPBELL SOU':'C1PB',
            'CANAD NATION':'CNIC',
            'CANAD PACIFI':'CPRL',
            'CARDINAL HEA':'C1AH',
            'CARNIVAL COR':'C1CL',
            'CARREFOUR BR':'CRFB',
            'CARRIER GLOB':'C1RR',
            'CBRE GROUP I':'C1BR',
            'CELANESE COR':'C1NS',
            'CENTENE CORP':'C1NC',
            'CEPAC - CTBA':'CTBA',
            'CEPAC - MCRJ':'MCRJ',
            'CEPAC - PMSP':'PMSP',
            'CF INDUSTRIE':'C1FI',
            'CHARTER COMM':'CHCM',
            'CHINA LIFE I':'L1FC',
            'CHINA PETROL':'C1HI',
            'CHINALARGECA':'BFXI',
            'CHIPOTLE MEX':'C1MG',
            'CHUNGHWA TEL':'C1HT',
            'CHURCH DWIGH':'CHDC',
            'CHURCHILL DW':'C2HD',
            'CITIZENS FIN':'C1FG',
            'CITRIX SYSTE':'C1TX',
            'CMS ENERGY C':'C1MS',
            'COMERICA INC':'C1MA',
            'CONAGRA BRAN':'C1AG',
            'CONC RIO TER':'CRTE',
            'CONSOLIDATED':'E1DI',
            'CONST A LIND':'CALI',
            'CONSTELLATIO':'STZB',
            'COOPER COMPA':'C1OO',
            'CORE SP TOTA':'BITO',
            'CORE US REIT':'BUSR',
            'COREDIVGROWT':'BGWH',
            'COREMSCI EMK':'BIEM',
            'COREMSCI EUR':'BIEU',
            'COREMSCIEAFE':'BIEF',
            'CORESMALLCAP':'BIJR',
            'COSTAR GROUP':'C1GP',
            'COUPA SOFTWA':'C1OU',
            'CPFL ENERGIA':'CPFE',
            'CREDIT ACCEP':'CRDA',
            'CREDIT SUISS':'C1SU',
            'CROWN CASTLE':'C1CI',
            'CRUZEIRO EDU':'CSED',
            'CSNMINERACAO':'CMIN',
            'CSU CARDSYST':'CARD',
            'CURHEDGEMSCI':'BHEF',
            'CYRE COM-CCP':'CCPR',
            'CYRELA REALT':'CYRE',
            'CYRUSONE INC':'C2ON',
            'DANAHER CORP':'DHER',
            'DARDEN RESTA':'D1RI',
            'DELL TECHNOL':'D1EL',
            'DENTSPLY SIR':'XRAY',
            'DEVON ENERGY':'D1VN',
            'DIGITAL REAL':'D1LR',
            'DISCOVER FIN':'D1FS',
            'DISCOVERY IN':'DCVY',
            'DISH NETWORK':'D1IS',
            'DOCUSIGN INC':'D1OC',
            'DOLLAR GENER':'DGCO',
            'DOMINION ENE':'D1OM',
            'DR HORTON IN':'D1HI',
            'DR REDDYS LA':'R1DY',
            'DTCOM-DIRECT':'DTCY',
            'DTE ENERGY C':'D1TE',
            'DUPONT N INC':'DDNB',
            'DXC TECHNOLO':'D1XC',
            'EASTMAN CHEM':'E1MN',
            'EATON CORP P':'E1TN',
            'ECO SEC AGRO':'ECOA',
            'ECOPETROL SA':'E1CO',
            'EDISON INTER':'E1IX',
            'EDWARDS LIFE':'E1WL',
            'EMERSON ELEC':'E1MR',
            'ENEL AMERICA':'E1NI',
            'ENGIE BRASIL':'EGIE',
            'ENTERGY CORP':'E1TR',
            'EOG RESOURCE':'E1OG',
            'EQTLMARANHAO':'EQMA',
            'EQUITY RESID':'E1QR',
            'ESGMSCIUSA L':'BSUS',
            'ESSEX PROPER':'E1SS',
            'ESTACIO PART':'YDUQ',
            'ESTEE LAUDER':'ELCI',
            'ETF BRA IBOV':'BOVB',
            'ETF BTG GENB':'GENB',
            'EVEREST RE G':'E1VE',
            'EVERSOURCE E':'E1SE',
            'EXPEDIA GROU':'EXGR',
            'EXPEDITORS I':'E1XP',
            'EXPON TECHNL':'BXTC',
            'FDC KINEAINF':'KDIF',
            'FDC UNION AG':'UNAG',
            'FEDERAL REAL':'F1RI',
            'FER C ATLANT':'VSPT',
            'FER HERINGER':'FHER',
            'FIC INFR BTG':'BDIF',
            'FIDELITY NAT':'F1NI',
            'FII A BRANCA':'FPAB',
            'FII ABC IMOB':'ABCP',
            'FII ABSOLUTO':'BPFF',
            'FII AFHI CRI':'AFHI',
            'FII ALIANZFF':'AFOF',
            'FII ALMIRANT':'FAMB',
            'FII ANCAR IC':'ANCR',
            'FII ANH EDUC':'FAED',
            'FII ATHENA I':'FATN',
            'FII AUTONOMY':'AIEC',
            'FII B VAREJO':'BVAR',
            'FII BANRISUL':'BNFS',
            'FII BB PAPII':'RDPD',
            'FII BB PRGII':'BBPO',
            'FII BB PROGR':'BBFI',
            'FII BB R PAP':'RNDP',
            'FII BB RECIM':'BBIM',
            'FII BEES CRI':'BCRI',
            'FII BLUE CRI':'BLMC',
            'FII BLUE FOF':'BLMR',
            'FII BLUE LOG':'BLMG',
            'FII BM THERA':'THRA',
            'FII BMBRC LC':'BMLC',
            'FII BRASILIO':'BMII',
            'FII BRHOTEIS':'BRHT',
            'FII BRIO CRE':'BICE',
            'FII BRIO III':'BRIP',
            'FII BRLPROII':'BRLA',
            'FII BRREALTY':'BZLI',
            'FII BTG AGRO':'BTAL',
            'FII BTG SHOP':'BPML',
            'FII BTG TAGR':'BTRA',
            'FII C BRANCO':'CBOP',
            'FII C TEXTIL':'CTXT',
            'FII CAMPUSFL':'FCFL',
            'FII CAP REIT':'CPFF',
            'FII CAPI SEC':'CPTS',
            'FII CEF CORP':'CXCO',
            'FII CJCTOWER':'CJCT',
            'FII CORE MET':'CORM',
            'FII CSHG CRI':'HGCR',
            'FII CSHG FOF':'HGFF',
            'FII CSHG LOG':'HGLG',
            'FII CSHG URB':'HGRU',
            'FII CSHGPRIM':'HGPO',
            'FII CX CEDAE':'CXCE',
            'FII CX RBRA2':'CRFF',
            'FII CX RBRAV':'CXRI',
            'FII DEA CARE':'CARE',
            'FII DEVA FOF':'DVFF',
            'FII DIAMANTE':'DAMT',
            'FII DOMINGOS':'FISD',
            'FII ELDORADO':'ELDO',
            'FII ESTOQ RJ':'ERCR',
            'FII EV KINEA':'KINP',
            'FII EXCELLEN':'FEXC',
            'FII FATOR VE':'VRTA',
            'FII FL RECEB':'FLCR',
            'FII FOF BREI':'IBFF',
            'FII G TOWERS':'GTWR',
            'FII GALAPAGO':'GCFF',
            'FII GEN SHOP':'FIGS',
            'FII GGRCOVEP':'GGRC',
            'FII GLPG CRI':'GCRI',
            'FII GUARDIAN':'GALG',
            'FII H UNIMED':'HUSC',
            'FII HABIT II':'HABT',
            'FII HECT CRI':'HCHG',
            'FII HECT DES':'HCST',
            'FII HEDGEAAA':'HAAA',
            'FII HEDGELOG':'HLOG',
            'FII HEDGEPDP':'HPDP',
            'FII HEDGEREC':'HREC',
            'FII HIGIENOP':'SHPH',
            'FII HOTEL MX':'HTMX',
            'FII HSI MALL':'HSML',
            'FII HSIRENDA':'HSRE',
            'FII HTOPFOF3':'HFOF',
            'FII INFRA RE':'FINF',
            'INVESTO LFTS':'LFTS',
            'FII JBFO FOF':'JBFO',
            'FII JPP CAPI':'JPPC',
            'FII JPPMOGNO':'JPPA',
            'FII KII REAL':'KNRE',
            'FII KINEA HY':'KNHY',
            'FII KINEA IP':'KNIP',
            'FII KINEA RI':'KNCR',
            'FII KINEA SC':'KNSC',
            'FII KINEAFOF':'KFOF',
            'FII LGCP INT':'LGCP',
            'FII MALLS BP':'MALL',
            'FII MAXI REN':'MXRF',
            'FII MEMORIAL':'FMOF',
            'FII MERITO I':'MFII',
            'FII MERITOFA':'MFAI',
            'FII MINT EDU':'MINT',
            'FII MOGNO HG':'MGCR',
            'FII MOGNO HT':'MGHT',
            'FII MTGESTAO':'DRIT',
            'FII MULT OF1':'MTOF',
            'FII MULT REN':'HBRH',
            'FII MULTPROP':'PRTS',
            'FII MULTSHOP':'SHOP',
            'FII NAVI TOT':'NAVT',
            'FII NOVOHORI':'NVHO',
            'FII OPPORTUN':'FTCE',
            'FII OU RENDA':'OURE',
            'FII OURI FOF':'OUFF',
            'FII OURI JPP':'OUJP',
            'FII OURINVES':'EDFO',
            'FII OURO PRT':'ORPD',
            'FII P VARGAS':'PRSV',
            'FII PARQ ANH':'PQAG',
            'FII PATR LOG':'PATL',
            'FII PERFORMA':'PEMA',
            'FII PERSONAL':'PRSN',
            'FII PLURAL L':'PLOG',
            'FII PLURAL R':'PLCR',
            'FII POLO CRI':'PORD',
            'FII POLO SHO':'VPSI',
            'FII PROLOGIS':'PBLV',
            'FII QUASAR A':'QAGR',
            'FII QUASAR C':'QAMI',
            'FII R INCOME':'RBCO',
            'FII RB CAP I':'FIIP',
            'FII RB GSB I':'RBGS',
            'FII RB YIELD':'RBHY',
            'FII RBCAP LG':'RBLG',
            'FII RBCAP RI':'RRCI',
            'FII RBCRI IV':'RBIV',
            'FII RBR FEED':'RCFF',
            'FII RBR PCRI':'RBRY',
            'FII RBR PROP':'RBRP',
            'FII RBRALPHA':'RBRF',
            'FII RBRES IV':'RBIR',
            'FII RBRESID2':'RBDS',
            'FII RBRESID3':'RSPD',
            'FII RBRHGRAD':'RBRR',
            'FII REAGMULT':'RMAI',
            'FII REC RECE':'RECR',
            'FII REC REND':'RECT',
            'FII REIT RIV':'REIT',
            'FII RIOBCRI2':'RBVO',
            'FII RIONEGRO':'RNGO',
            'FII RIZA AKN':'RZAK',
            'FII S F LIMA':'FLMA',
            'FII SANT PAP':'SADI',
            'FII SANT REN':'SARE',
            'FII SHOP PDP':'SHDP',
            'FII SHOPJSUL':'JRDM',
            'FII SIA CORP':'SAIC',
            'FII SOLARIUM':'SOLR',
            'FII SP DOWNT':'SPTW',
            'FII SUNOFOFI':'SNFF',
            'FII TBOFFICE':'TBOF',
            'FII TEL PROP':'TEPP',
            'FII TG ATIVO':'TGAR',
            'FII TORDE EI':'TORD',
            'FII TORRE AL':'ALMI',
            'FII TORRE NO':'TRNT',
            'FII TOURMALE':'TORM',
            'FII TRANSINC':'TSNC',
            'FII TREECORP':'TCPF',
            'FII TRX R II':'TRXB',
            'FII TRX REAL':'TRXF',
            'FII TRXE COR':'XTED',
            'FII URCA REN':'URPR',
            'FII V MASTER':'VOTS',
            'FII V PARQUE':'FVPQ',
            'FII VALOR HE':'VGHF',
            'FII VALORAIP':'VGIP',
            'FII VALREIII':'VGIR',
            'FII VBI REIT':'RVBI',
            'FII VECT REN':'VCRR',
            'FII VERS CRI':'VSLH',
            'FII VIDANOVA':'FIVN',
            'FII VINCI IF':'VIFI',
            'FII VINCI IU':'VIUR',
            'FII VINCI LG':'VILG',
            'FII VINCI OF':'VINO',
            'FII VINCI SC':'VISC',
            'FII VOT SHOP':'VSHO',
            'FII VQ LAJES':'VLJS',
            'FII XP MACAE':'XPCM',
            'FII XP MALLS':'XPML',
            'FII XP SELEC':'XPSF',
            'FIP BKO BREI':'BKOI',
            'FIP BTGDV IE':'BDIV',
            'FIP END DEBT':'ENDD',
            'FIP INSTITUT':'OPEQ',
            'FIP NVRAPOSO':'NVRP',
            'FIP OPP HOLD':'OPHF',
            'FIP PATR INF':'PICE',
            'FIP PORT SUD':'FPOR',
            'FIP VINCI IE':'VIGT',
            'FIP XP INFRA':'XPIE',
            'FIRST REPUBL':'F1RC',
            'FISET FL REF':'FSRF',
            'FLAVOR FLAGR':'I1FF',
            'FLEETCOR TEC':'FLTC',
            'FLOWSERVE CO':'F1LS',
            'FORTINET INC':'F1TN',
            'FORTIVE CORP':'F1TV',
            'FORTUNE BRAN':'F1BH',
            'FRANKLIN RES':'F1RA',
            'GALAPAGOS NV':'G1LP',
            'GDS HOLDINGS':'G1DS',
            'GEN DYNAMICS':'GDBR',
            'GENERAL MILL':'G1MI',
            'GENERALSHOPP':'GSHP',
            'GENUINE PART':'G1PC',
            'GLAXOSMITHKL':'G1SK',
            'GLOBAL INFRA':'BIGF',
            'GLOBAL PAYME':'G1PI',
            'GLOBALHEALTH':'BIXJ',
            'GLOBE LIFE I':'G1LL',
            'GOL LINHAS A':'GOLL',
            'GOLDMANSACHS':'GSGI',
            'GRUPO MATEUS':'GMAT',
            'GRUPO NATURA':'NTCO',
            'HANOVER INSU':'THGI',
            'HARLEY-DAVID':'H1OG',
            'HARTFORD FIN':'H1IG',
            'HCA HEALTHCA':'H1CA',
            'HDFC BANK LT':'H1DB',
            'HEALTHPEAK P':'P1EA',
            'HENRY SCHEIN':'H1SI',
            'HER BLOCK IN':'H1RB',
            'HEWLETT PACK':'H1PE',
            'HILTON WORLD':'H1LT',
            'HOLLYFRONTIE':'H1FC',
            'HORIZON THER':'H1ZN',
            'HORMEL FOODS':'H1RL',
            'HOTEIS OTHON':'HOOT',
            'HSBC HOLDING':'H1SB',
            'HUAZHU GROUP':'H1TH',
            'HUNTINGTON B':'H1BA',
            'HUNTINGTON I':'H1II',
            'IAC INTERACT':'I1AC',
            'ICICI BANK L':'I1BN',
            'IDEXX LABORA':'I1DX',
            'IHS MARKIT L':'I1NF',
            'ILLINOIS TOO':'I1TW',
            'ILLUMINA INC':'I1LM',
            'INC ESG AWAR':'BEGE',
            'IND CATAGUAS':'CATA',
            'INT EXCHANGE':'I1HG',
            'INTERCONTINE':'I1CE',
            'INTERNATIONA':'I1PC',
            'INTUITIVE SU':'I1SR',
            'INVEST BCORP':'ISBC',
            'INVEST BEMGE':'FIGE',
            'INVESTO USTK':'USTK',
            'IOCHP-MAXION':'MYPK',
            'IPG PHOTONIC':'I1PG',
            'IQVIA HOLDIN':'I1QV',
            'IRBBRASIL RE':'IRBR',
            'IRON MOUNTAI':'I1RM',
            'ISHARE SP500':'IVVB',
            'ISHARES BOVA':'BOVA',
            'ISHARES BRAX':'BRAX',
            'ISHARES ECOO':'ECOO',
            'ISHARES SMAL':'SMAL',
            'ISUSTENTABIL':'ISEE',
            'IT NOW GREEN':'REVE',
            'IT NOW HCARE':'HTEK',
            'IT NOW IMA-B':'IMAB',
            'IT NOW IRF-M':'IRFM',
            'IT NOW SMALL':'SMAC',
            'ITAU UNIBANC':'ITUB',
            'ITAUUNIBANCO':'ITUB',
            'JACOBS ENGIN':'J1EG',
            'JALLESMACHAD':'JALL',
            'JB HUNT TRAN':'J1BH',
            'JEFFERIES FI':'J1EF',
            'JOHNSON CONT':'J1CI',
            'JUNIPER NETW':'J1NP',
            'KB FINANCIAL':'K1BF',
            'KEPLER WEBER':'KEPL',
            'KEYSIGHT TEC':'K1SG',
            'KIMCO REALTY':'K1IM',
            'KINDER MORGA':'KMIC',
            'KINGSOFT CHL':'K2CG',
            'L3HARRIS TEC':'L1HX',
            'LABORATORY C':'L1CA',
            'LAM RESEARCH':'L1RC',
            'LAS VEGAS SA':'L1VS',
            'LATIN AMER40':'BILF',
            'LE LIS BLANC':'LLIS',
            'LEIDOS HOLDI':'L1DO',
            'LIBERTY BROA':'LBRD',
            'LIBERTY GLOB':'L1BT',
            'LIBERTY MEDI':'LSXM',
            'LINCOLN NATI':'L1NC',
            'LLOYDS BANKI':'L1YG',
            'LOG COM PROP':'LOGG',
            'LOJAS AMERIC':'LAME',
            'LOJAS MARISA':'AMAR',
            'LOJAS RENNER':'LREN',
            'LOPES BRASIL':'LPSB',
            'LULULEMON AT':'L1UL',
            'LYONDELLBASE':'L1YB',
            'M.DIASBRANCO':'MDIA',
            'MALLS BRASIL':'MALL',
            'MANGELS INDL':'MGEL',
            'MARATHON OIL':'M1RO',
            'MARATHON PET':'M1PC',
            'MARRIOTT INT':'M1TT',
            'MARSH E MCLE':'M1MC',
            'MARTIN MARIE':'M1LM',
            'MAXIM INTEGR':'M1XI',
            'MCKESSON COR':'M1CK',
            'MEDICAL P TR':'M2PW',
            'MELCO RESORT':'M1LC',
            'MENEZES CORT':'MNZC',
            'MERCADOLIBRE':'MELI',
            'METAL IGUACU':'MTIG',
            'METTLER-TOLE':'M1TD',
            'MICROCHIP TE':'M1CH',
            'MICRON TECHN':'MUTC',
            'MIDLARGE CAP':'MLCX',
            'MINASMAQUINA':'MMAQ',
            'MITRE REALTY':'MTRE',
            'MITSUBISHI U':'M1UF',
            'MOBILE TELES':'M1BT',
            'MOHAWK INDUS':'M1HK',
            'MOLSON COORS':'M1CB',
            'MONDELEZ INT':'MDLZ',
            'MONSTER BEVE':'M1NS',
            'MOTOROLA SOL':'M1SI',
            'MOURA DUBEUX':'MDNE',
            'MSCI ASIA JP':'BAAX',
            'MSCI EMGMARK':'BEEM',
            'MSCI GERMANY':'BEWG',
            'MSCI SWITZER':'BEWL',
            'MSCI US MVOL':'BUSM',
            'MSCIAUSTRALI':'BEWA',
            'MSCIEAFEGROW':'BEFG',
            'MSCIEAFEVALU':'BEFV',
            'MSCIEUROZONE':'BEZU',
            'MSCIGLMIVOLF':'BCWV',
            'MSCIHONGKONG':'BEWH',
            'MSCIMINVOL F':'BFAV',
            'MSCISOUTHKOR':'BEWY',
            'MSCIUSAMOM F':'BMTU',
            'MSCIUSQUAL F':'BQUA',
            'MSCIUSVALUEF':'BVLU',
            'NATIONAL GRI':'N1GG',
            'NATWEST GROU':'N1WG',
            'NEUROCRINE B':'N1BI',
            'NEW ORIENTAL':'E1DU',
            'NEWELL BRAND':'N1WL',
            'NEWMONT GOLD':'N1EM',
            'NEXTERA ENER':'NEXT',
            'NIELSEN HOLD':'N1LS',
            'NISOURCE INC':'N1IS',
            'NORDSTROM IN':'J1WN',
            'NORFOLK SOUT':'N1SC',
            'NORTCQUIMICA':'NRTQ',
            'NORTHERN TRU':'N1TR',
            'NORTHROP GRU':'NOCG',
            'NORWEGIAN CR':'N1CL',
            'NOVO NORDISK':'N1VO',
            'NRG ENERGY I':'N1RG',
            'NXP SEMICOND':'N1XP',
            'OCCIDENT PTR':'OXYP',
            'OLD DOMINION':'O1DF',
            'OMNICOM GROU':'O1MC',
            'OPPORT ENERG':'OPHE',
            'OTIS WORLDWI':'O1TI',
            'OUROFINO S/A':'OFSA',
            'P.ACUCAR-CBD':'PCAR',
            'PACKAGING CO':'P1KG',
            'PACTUAL IBOV':'IBOB',
            'PANATLANTICA':'PATI',
            'PAR AL BAHIA':'PEAB',
            'PARANAPANEMA':'PMAM',
            'PARKER-HANNI':'P1HC',
            'PAYCOM SOFTW':'P1YC',
            'PENN NATIONL':'P2EN',
            'PEOPLES UNIT':'P1BC',
            'PERRIGO CO P':'P1RG',
            'PET MANGUINH':'RPMG',
            'PETROBRAS BR':'VBBR',
            'PHILIP MORRI':'PHMO',
            'PINDUODUO IN':'P1DD',
            'PINNACLE WES':'P1NW',
            'PIONEER NATU':'P1IO',
            'PLASCAR PART':'PLAS',
            'POLO CAP SEC':'PLSC',
            'PORTO SEGURO':'PSSA',
            'POSITIVO TEC':'POSI',
            'PPG INDUSTRI':'P1PG',
            'PRINCIPAL FI':'P1FG',
            'PROLOGIS INC':'P1LD',
            'PRUDENTIAL F':'P1DT',
            'PRUDENTIAL P':'P1UK',
            'PT TELEKOMUN':'T1LK',
            'PUBLIC SERVI':'P1EG',
            'PUBLIC STORA':'P1SA',
            'PULTEGROUP I':'P1HM',
            'QUALITY SOFT':'QUSW',
            'QUANTA SERVI':'Q1UA',
            'QUEST DIAGNO':'Q1UE',
            'RAIADROGASIL':'RADL',
            'RALPH LAUREN':'R1LC',
            'RAYMOND JAME':'R1JF',
            'RAYTHEONTECH':'RYTT',
            'RBCAPITALRES':'RBRA',
            'REALTY INCOM':'R1IN',
            'REDE ENERGIA':'REDE',
            'REGENCY CENT':'R1EG',
            'REGENERON PH':'REGN',
            'REGIONS FINA':'R1FC',
            'REPUBLIC SER':'R1SG',
            'ROCKWELL AUT':'R1OK',
            'ROPER TECHNO':'R1OP',
            'ROYAL CARIBB':'R1CL',
            'RUSSEL1000GR':'BIWF',
            'RUSSELL 2000':'BIWM',
            'RYANAIR HOLD':'R1YA',
            'SAFRAETFIBOV':'SAET',
            'SANTANDER BR':'SANB',
            'SAO MARTINHO':'SMTO',
            'SARAIVA LIVR':'SLED',
            'SAREPTA THER':'S1RP',
            'SBA COMMUNIC':'S1BA',
            'SCHLUMBERGER':'SLBG',
            'SEAGATE HOLD':'S1TX',
            'SEALED AIR C':'S1EA',
            'SEG AL BAHIA':'CSAB',
            'SELECT DIVID':'BDVY',
            'SIBANYE STIL':'S1BS',
            'SID NACIONAL':'CSNA',
            'SIGNATURE BK':'SBNY',
            'SILVER TRUST':'BSLV',
            'SIRIUS XM HD':'SRXM',
            'SK TELECOM C':'S1KM',
            'SKYWORKS SOL':'S1SL',
            'SL GREEN REA':'S1LG',
            'SLC AGRICOLA':'SLCE',
            'SONDOTECNICA':'SOND',
            'SOUTHWEST AI':'S1OU',
            'SPOTIFY TECH':'S1PO',
            'SPRINGS GLOB':'SGPS',
            'STANLEY BLAC':'S1WK',
            'STATE STREET':'S1TT',
            'STERLING BNC':'SLBC',
            'STRYKER CORP':'S1YK',
            'SUL 116 PART':'OPTS',
            'SUMITOMO MIT':'S1MF',
            'SUZANO PAPEL':'SUZB',
            'SVB FINANCIA':'S1IV',
            'SYNCHRONY FI':'S1YF',
            'SYNOPSYS INC':'S1NP',
            'T ROWE PRICE':'T1RO',
            'TAKE-TWO INT':'T1TW',
            'TAL EDUCATIO':'T1AL',
            'TAPESTRY INC':'TPRY',
            'TAURUS ARMAS':'TASA',
            'TE CONNECTIV':'T1EL',
            'TECHNIPFMC P':'T1EC',
            'TEGRA INCORP':'TEGA',
            'TELADOCHEALT':'T2DH',
            'TELEF BRASIL':'VIVT',
            'TELEFLEX INC':'T1FX',
            'TERRASANTAPA':'LAND',
            'TEVA PHARMAC':'T1EV',
            'THE JM SMUCK':'S1JM',
            'THE PROGRESS':'P1GR',
            'THE SOUTHERN':'T1SO',
            'THERMFISCHER':'TMOS',
            'TIM PART S/A':'TIMS',
            'TIME FOR FUN':'SHOW',
            'TJX COMPANIE':'TJXC',
            'TRACTOR SUPP':'T1SC',
            'TRAN PAULIST':'TRPL',
            'TRANSDIGM GR':'T1DG',
            'TREND EUROPA':'EURP',
            'TREND NASDAQ':'NASD',
            'TRIUNFO PART':'TPIS',
            'TRTMSCI EAFE':'BEGD',
            'TRUIST FINAN':'B1BT',
            'TRUSTMSCI US':'BEGU',
            'UBER TECH IN':'U1BE',
            'UNDER ARMOUR':'U1AI',
            'UNIONPACIFIC':'UPAC',
            'UNITED AIRLI':'U1AL',
            'UNITED RENTA':'U1RI',
            'UNITEDHEALTH':'UNHH',
            'UNITY SOFTWR':'U2ST',
            'UNIVERSAL HE':'U1HS',
            'US AEROSPACE':'BAER',
            'US FINANCIAL':'BIYF',
            'US TECHNOLOG':'BIYW',
            'USFINANCSERV':'BIYG',
            'USMEDICDEVIC':'BIHI',
            'VALLEY NTION':'VLYB',
            'VERISIGN INC':'VRSN',
            'VERISK ANALY':'V1RS',
            'VERTEX PHARM':'VRTX',
            'VIPSHOP HOLD':'V1IP',
            'VODAFONE GRO':'V1OD',
            'VORNADO REAL':'V1NO',
            'VULCABRAS/AZ':'VULC',
            'VULCAN MATER':'V1MC',
            'WARNER MUSIC':'W1MG',
            'WDC NETWORKS':'LVTC',
            'WEC ENERGY G':'W1EC',
            'WELLTOWER IN':'W1EL',
            'WESTERN BCOR':'WABC',
            'WESTERNUNION':'WUNI',
            'WESTPAC BANK':'W1BK',
            'WEYERHAEUSER':'W1YC',
            'WHIRLPOOL CO':'W1HR',
            'WILLIAMS COS':'W1MB',
            'WILLIS TOWER':'W1LT',
            'WR BERKLEY C':'W1RB',
            'WYNN RESORTS':'W1YN',
            'ZEBRA TECHNO':'Z1BR',
            'ZIMMER BIOME':'Z1BH',
            'ZIONSBANCORP':'Z1IO',
            'ALIANSCSONAE':'ALSO',
            'ESTACIO PART':'YDUQ',
            'CYRELA BRAZI':'CYRE',
            'ITAU UNIBANC':'ITUB',
            'ALIANSCSONAE':'ALSO',
            'ESTACIO PART':'YDUQ',
            'CYRELA BRAZI':'CYRE',
            'ITAU UNIBANC':'ITUB',
            'HYPERMARCAS':'HYPE',
            'RUMO LOG':'RAIL',
            'HYPERMARCAS':'HYPE',
            'ABIOMED INC':'A1BM',
            'ALFA FINANC':'CRIV',
            'ALFA INVEST':'BRIV',
            'ALGAR TELEC':'ALGT',
            'ALTERYX INC':'A1YX',
            'AMEREN CORP':'A1EE',
            'AMPLA ENERG':'CBEE',
            'ASTRAZENECA':'A1ZN',
            'BANCO INTER':'BIDI',
            'BB ETF IBOV':'BBOV',
            'BEIGENE LTD':'B1GN',
            'BEMOBI TECH':'BMOB',
            'BEYOND MEAT':'B2YN',
            'BIONTECH SE':'B1NT',
            'BOSTON PROP':'BOXP',
            'BR PARTNERS':'BRBI',
            'CAPITAL ONE':'CAON',
            'CAPRI HOLDI':'CAPH',
            'CARTERS INC':'CRIN',
            'CATERPILLAR':'CATP',
            'CBOE GLOBAL':'C1BO',
            'CENTERPOINT':'C1NP',
            'CERNER CORP':'C1ER',
            'CH ROBINSON':'C1HR',
            'CHECK POINT':'C1HK',
            'CINTAS CORP':'C1TA',
            'COR RIBEIRO':'CORR',
            'CORE MIDCAP':'BIJH',
            'CORE SP 500':'BIVB',
            'CORNING INC':'G1LW',
            'CORTEVA INC':'C1TV',
            'CUMMINS INC':'C1MI',
            'D1000VFARMA':'DMVF',
            'DATADOG INC':'D1DG',
            'DEUTSCHE AK':'DBAG',
            'DIAMONDBACK':'F1AN',
            'DOLLAR TREE':'DLTR',
            'DUKE ENERGY':'DUKB',
            'DUKE REALTY':'D1RE',
            'ECORODOVIAS':'ECOR',
            'ELECTR ARTS':'EAIN',
            'ELETROMIDIA':'ELMD',
            'ENAUTA PART':'ENAT',
            'ENERGIAS BR':'ENBR',
            'ENERGISA MT':'ENMT',
            'EQUIFAX INC':'E1FX',
            'EQUINIX INC':'EQIX',
            'EQUINOR ASA':'E1QN',
            'ERICSSON LM':'E1RI',
            'ESPACOLASER':'ESPA',
            'ETF ESG BTG':'ESGB',
            'EXELON CORP':'E1XC',
            'EXTRA SPACE':'E1XR',
            'EXXON MOBIL':'EXXO',
            'F5 NETWORKS':'F1FI',
            'FDC ITAU IE':'IFRA',
            'FIAGRO CPTR':'CPTR',
            'FIFTH THIRD':'FFTD',
            'FII AFINVCR':'AFCR',
            'FII ALIANZA':'ALZR',
            'FII ARCTIUM':'ARCT',
            'FII BARIGUI':'BARI',
            'FII BB CORP':'BBRC',
            'FII BC FFII':'BCFF',
            'FII BC FUND':'BRCR',
            'FII BLUECAP':'BLCP',
            'FII BLUEMAC':'BLMO',
            'FII BRE VIC':'BREV',
            'FII BRIO II':'BRIM',
            'FII BRLPROP':'BPRP',
            'FII BTG CRI':'BTCR',
            'FII BTOWERS':'BTWR',
            'FII CEO CCP':'CEOC',
            'FII CRIANCA':'HCRI',
            'FII D PEDRO':'PQDP',
            'FII EUROPAR':'EURO',
            'FII EVEN II':'KEVE',
            'FII FLORIPA':'FLRP',
            'FII GALERIA':'EDGA',
            'FII GEN SEV':'GESE',
            'FII GENERAL':'GSFI',
            'FII GP RCFA':'RCFA',
            'FII HATRIUM':'ATSA',
            'FII HBC REN':'HBCR',
            'FII HECTARE':'HCTR',
            'FII HEDGEBS':'HGBS',
            'FII HG REAL':'HGRE',
            'FII HGI CRI':'HGIC',
            'FII HREALTY':'HRDF',
            'FII HSI CRI':'HSAF',
            'FII HSI LOG':'HSLG',
            'FII INDL BR':'FIIB',
            'FII IRIDIUM':'IRDM',
            'FII JFL LIV':'JFLL',
            'FII JS REAL':'JSRE',
            'FII JT PREV':'JTPR',
            'FII LATERES':'LATR',
            'FII LEGATUS':'LASC',
            'FII LOFT II':'LFTT',
            'FII LOURDES':'NSLU',
            'FII MAUA HF':'MCHF',
            'FII MAX RET':'MAXR',
            'FII MERC BR':'MBRF',
            'FII MORE RE':'MORE',
            'FII NCH EQI':'EQIN',
            'FII NESTPAR':'NPAR',
            'FII NEWPORT':'NEWL',
            'FII OLIMPIA':'VLOL',
            'FII OURILOG':'OULG',
            'FII P NEGRA':'FPNG',
            'FII PANAMBY':'PABY',
            'FII RB CFOF':'RFOF',
            'FII RBR DES':'RBRM',
            'FII RBR LOG':'RBRL',
            'FII REC FOF':'RECX',
            'FII REC LOG':'RELG',
            'FII RIOB ED':'RBED',
            'FII RIOB FF':'RBFF',
            'FII RIOB RC':'RCRB',
            'FII RIOB RR':'RBRS',
            'FII RIOB VA':'RBVA',
            'FII RIZA TX':'RZTR',
            'FII SAO FER':'SFND',
            'FII SDI LOG':'SDIL',
            'FII SEQUOIA':'SEQR',
            'FII THE ONE':'ONEF',
            'FII TISHMAN':'TSER',
            'FII TOUR II':'TOUR',
            'FII V2 PROP':'VVPR',
            'FII VBI CON':'EVBI',
            'FII VBI CRI':'CVBI',
            'FII VBI LOG':'LVBI',
            'FII VBI PRI':'PVBI',
            'FII VOT LOG':'VTLT',
            'FII VOT SEC':'VSEC',
            'FII W PLAZA':'WPLZ',
            'FII XP CRED':'XPCI',
            'FII XP INDL':'XPIN',
            'FII XP PROP':'XPPR',
            'FIP IE KNOX':'KNOX',
            'FIRST SOLAR':'FSLR',
            'FIRSTENERGY':'F1EC',
            'FISET PESCA':'FSPE',
            'FORD MOTORS':'FDMO',
            'GARTNER INC':'G1AR',
            'GENERAL MOT':'GMCO',
            'GEOPARK LTD':'GPRK',
            'GER PARANAP':'GEPA',
            'GLOBAL REIT':'BGRT',
            'GLOBAL TECH':'BIXN',
            'GOLD FIELDS':'G1FI',
            'HALLIBURTON':'HALI',
            'HANESBRANDS':'H1BI',
            'HASHDEX NCI':'HASH',
            'HOLOGIC INC':'H1OL',
            'HOST HOTELS':'H1ST',
            'HOWMET AERO':'ARNC',
            'HYPERMARCAS':'HYPE',
            'IBRX BRASIL':'IBXX',
            'ICE BIOTECH':'BIBB',
            'IGOVERNANCA':'IGCX',
            'INCYTE CORP':'I1NC',
            'INFOSYS LTD':'I1FO',
            'INTERMEDICA':'GNDI',
            'INTERPUBLIC':'I1PH',
            'INVESCO LTD':'I1VZ',
            'IT NOW B5P2':'B5P2',
            'IT NOW IB5M':'IB5M',
            'IT NOW IBOV':'BOVV',
            'IT NOW IDIV':'DIVO',
            'IT NOW IFNC':'FIND',
            'IT NOW IGCT':'GOVE',
            'IT NOW IMAT':'MATB',
            'IT NOW MILL':'MILL',
            'IT NOW PIBB':'PIBB',
            'IT NOW SHOT':'SHOT',
            'IT NOW SPXI':'SPXI',
            'IT NOW TECK':'TECK',
            'JOAO FORTES':'JFEN',
            'KANSAS CITY':'K1CS',
            'KEMPER CORP':'KMPR',
            'KIMBERLY CL':'KMBB',
            'KRAFT HEINZ':'KHCB',
            'LAMB WESTON':'L1WH',
            'LENNAR CORP':'L1EN',
            'LIVE NATION':'L1YV',
            'LOWES COMPA':'LOWC',
            'MAGAZ LUIZA':'MGLU',
            'MARKEL CORP':'MKLC',
            'MARKETAXESS':'M1KT',
            'MATCH GROUP':'M1TC',
            'MERC BRASIL':'BMEB',
            'MERC FINANC':'MERC',
            'MERC INVEST':'BMIN',
            'METLIFE INC':'METB',
            'MGM RESORTS':'M1GM',
            'MID-AMERICA':'M1AA',
            'MODERNA INC':'M1RN',
            'MONGODB INC':'M1DB',
            'MONT ARANHA':'MOAR',
            'MOODYS CORP':'MCOR',
            'MORGAN STAN':'MSBR',
            'MSCI BRAZIL':'BEWZ',
            'MSCI CANADA':'BEWC',
            'MSCI FRANCE':'BEWQ',
            'MSCI MEXICO':'BEWW',
            'MSCI TAIWAN':'BEWT',
            'MSCIEMMRKMI':'BEMV',
            'MSCIUSASIZF':'BSIZ',
            'MT BANK COR':'M1TB',
            'NORD BRASIL':'BNBR',
            'NOVARTIS AG':'N1VS',
            'NVIDIA CORP':'NVDC',
            'OREILLY AUT':'ORLY',
            'PAGUE MENOS':'PGMN',
            'PAYCHEX INC':'P1AY',
            'PAYPAL HOLD':'PYPL',
            'PDG SECURIT':'PDGS',
            'PENTAIR PLC':'P1NR',
            'PEPSICO INC':'PEPB',
            'PERKINELMER':'P1KI',
            'PHILLIPS 66':'P1SX',
            'PLANOEPLANO':'PLPL',
            'PNCFNANCIAL':'PNCS',
            'PROMPT PART':'PRPT',
            'QUERO-QUERO':'LJQQ',
            'RANDON PART':'RAPT',
            'ROBERT HALF':'R1HI',
            'ROLLINS INC':'R1OL',
            'ROSS STORES':'ROST',
            'ROSSI RESID':'RSID',
            'SALUS INFRA':'SAIP',
            'SEQUOIA LOG':'SEQL',
            'SHOPIFY INC':'S2HO',
            'SNAP-ON INC':'S1NA',
            'SP500 VALUE':'BIVE',
            'SP500GROWTH':'BIVW',
            'SSC TECHNOL':'S1SN',
            'STO ANTONIO':'STEN',
            'SUDESTE S/A':'OPSE',
            'SUL AMERICA':'SULA',
            'SUZANO HOLD':'NEMO',
            'SUZANO PAPEL':'SUZB',
            'SUZANO S.A.':'SUZB',
            'TAIWANSMFAC':'TSMC',
            'TARGET CORP':'TGTB',
            'TEXTRON INC':'T1XT',
            'THE SHERWIN':'S1HW',
            'T-MOBILE US':'T1MU',
            'TRACK FIELD':'TFCO',
            'TREND CHINA':'XINA',
            'TREND IBOVX':'BOVX',
            'TREND SMALL':'XMAL',
            'TRIPADVISOR':'T1RI',
            'TYSON FOODS':'TSNF',
            'ULTA BEAUTY':'U1LT',
            'VALERO ENER':'VLOE',
            'VIVARA S.A.':'VIVA',
            'WABTEC CORP':'W1AB',
            'WALT DISNEY':'DISB',
            'WASTE MANAG':'W1MC',
            'WATERS CORP':'WATC',
            'WELLS FARGO':'WFCO',
            'WESTERN DIG':'W1DC',
            'WESTROCK CO':'W1RK',
            'WILSON SONS':'WSON',
            'WIX.COM LTD':'W1IX',
            'WLM IND COM':'WLMM',
            'WORKDAY INC':'W1DA',
            'WW GRAINGER':'G1WW',
            'XCEL ENERGY':'X1EL',
            'ZTO EXPRESS':'Z1TO',
            'ABC BRASIL':'ABCB',
            'ACO ALTONA':'EALT',
            'ACTIVISION':'ATVI',
            'AES BRASIL':'AESB',
            'AFLUENTE T':'AFLT',
            'AGRIBRASIL':'GRAO',
            'AGROGALAXY':'AGXY',
            'ALPARGATAS':'ALPA',
            'ALPER S.A.':'APER',
            'ALPHAVILLE':'AVLL',
            'AMERICANAS':'AMER',
            'AMETEK INC':'A1ME',
            'ANTHEM INC':'A1NT',
            'BIC MONARK':'BMKS',
            'BNY MELLON':'BONY',
            'BR BROKERS':'BBRK',
            'BR PROPERT':'BRPR',
            'BRAD IMA-B':'IMBB',
            'BRASILAGRO':'AGRO',
            'BTGP BANCO':'BPAC',
            'CARMAX INC':'K1MX',
            'CIA HERING':'HGTX',
            'CIGNA CORP':'C1IC',
            'CINCINNATI':'CINF',
            'CINESYSTEM':'CNSY',
            'COPART INC':'C1PR',
            'COPHILLIPS':'COPH',
            'COSAN SA I':'CSAN',
            'CVC BRASIL':'CVCB',
            'CVS HEALTH':'CVSH',
            'DAVITA INC':'DVAI',
            'DEXCOM INC':'D1EX',
            'DEXXOS PAR':'DEXP',
            'DIRECIONAL':'DIRR',
            'DOVER CORP':'D1OV',
            'DRAFTKINGS':'D2KN',
            'ECOLAB INC':'E1CL',
            'ELETROBRAS':'ELET',
            'EMBPAR S/A':'EPAR',
            'EMBRAER SA':'EMBR',
            'EQUATORIAL':'EQTL',
            'EUROPE ETF':'BIEV',
            'EVERGY INC':'E1VR',
            'FASTLY INC':'F1SL',
            'FDC BURITI':'OPIM',
            'FEDEX CORP':'FDXB',
            'FIC IE CAP':'CPTI',
            'FII BB FOF':'BBFO',
            'FII BRESCO':'BRCO',
            'FII CENESP':'CNES',
            'FII CX TRX':'CXTL',
            'FII DEVANT':'DEVA',
            'FII EUROPA':'ERPA',
            'FII KILIMA':'KISU',
            'FII NOVA I':'NVIF',
            'FII PATRIA':'PATC',
            'FII POLO I':'PLRI',
            'FII RB CRI':'RCRI',
            'FII RB TFO':'RBTS',
            'FII SC 401':'FISC',
            'FII TOUR V':'TCIN',
            'FII VECTIS':'VCJR',
            'FII VEREDA':'VERE',
            'FII VX XVI':'VXXV',
            'FII WTC SP':'WTSP',
            'FII XP HOT':'XPHT',
            'FII XP LOG':'XPLG',
            'FINANSINOS':'FNCN',
            'FIP BRZ IE':'BRZP',
            'FIP IE III':'ESUT',
            'FIP PERFIN':'PFIN',
            'FIP PRISMA':'PPEI',
            'FIRF XP IE':'XPID',
            'FISERV INC':'F1IS',
            'G2D INVEST':'G2DI',
            'GARMIN LTD':'G1RM',
            'GERDAU MET':'GOAU',
            'GOLD TRUST':'BIAU',
            'GRAZZIOTIN':'CGRA',
            'GRUAIRPORT':'AGRU',
            'GRUPO SOMA':'SOMA',
            'GUARARAPES':'GUAR',
            'HASBRO INC':'H1AS',
            'HBR REALTY':'HBRE',
            'HEICO CORP':'H1EI',
            'HERSHEY CO':'HSHY',
            'HOME DEPOT':'HOME',
            'HP COMPANY':'HPQB',
            'HUMANA INC':'H1UM',
            'IEELETRICA':'IEEX',
            'INDUSTRIAL':'INDX',
            'INTUIT INC':'INTU',
            'IT NOW DNA':'DNAI',
            'IT NOW ISE':'ISUS',
            'ITAG ALONG':'ITAG',
            'J B DUARTE':'JBDU',
            'JACK HENRY':'J1KH',
            'JEREISSATI':'JPSA',
            'KELLOGG CO':'K1EL',
            'KLABIN S/A':'KLBN',
            'KOHLS CORP':'K1SS',
            'LEGGETT PL':'L1EG',
            'LOCAMERICA':'LCAM',
            'LOEWS CORP':'L1OE',
            'LUMEN TECH':'L1MN',
            'MAESTROLOC':'MSRO',
            'MASCO CORP':'M1AS',
            'MASTERCARD':'MSCD',
            'METAL LEVE':'LEVE',
            'MIRAE FIXA':'FIXA',
            'MRS LOGIST':'MRSA',
            'MSCI CHINA':'BCHI',
            'MSCI INDIA':'BNDA',
            'MSCI JAPAN':'BEWJ',
            'MSCI SPAIN':'BEWP',
            'MULTILASER':'MLAS',
            'NASDAQ INC':'N1DA',
            'NEOENERGIA':'NEOE',
            'NETAPP INC':'N1TA',
            'NOKIA CORP':'NOKI',
            'NORDON MET':'NORD',
            'NORTONLIFE':'S1YM',
            'NUCOR CORP':'N1UE',
            'NUTRIPLANT':'NUTR',
            'ODONTOPREV':'ODPV',
            'OSX BRASIL':'OSXB',
            'PACCAR INC':'P1AC',
            'PETRORECSA':'RECV',
            'POMIFRUTAS':'FRTA',
            'PORTOBELLO':'PTBL',
            'QR BITCOIN':'QBTC',
            'RESMED INC':'R1MD',
            'RIOSULENSE':'RSUL',
            'SALESFORCE':'SSFO',
            'SANTANENSE':'CTSA',
            'SANTOS BRP':'STBP',
            'SAO CARLOS':'SCAR',
            'SERVICENOW':'N1OW',
            'SIMON PROP':'SIMN',
            'SMITH NEPH':'S1NN',
            'SONY GROUP':'SNEC',
            'SPLUNK INC':'S1PL',
            'SQUARE INC':'S2QU',
            'STERIS PLC':'S1TE',
            'SUN COMMUN':'S2UI',
            'SYSCO CORP':'S1YY',
            'TECHNOS SA':'TECN',
            'TENARIS SA':'T1SS',
            'TEX RENAUX':'TXRX',
            'TRADE DESK':'T2TD',
            'TRANE TECH':'I1RP',
            'TRANSOCEAN':'RIGG',
            'TREND ACWI':'ACWI',
            'TREND ASIA':'ASIA',
            'TREND EMEG':'EMEG',
            'TREND IFIX':'XFIX',
            'TREND OURO':'GOLD',
            'TWILIO INC':'T1WL',
            'UNUM GROUP':'U1NM',
            'US BANCORP':'USBC',
            'VENTAS INC':'V1TA',
            'VERTCIASEC':'VERT',
            'WATSCO INC':'W1SO',
            'WEIBO CORP':'W1BO',
            'WETZEL S/A':'MWET',
            'XEROX CORP':'XRXB',
            'XILINX INC':'X1LN',
            'YDUQS PART':'YDUQ',
            'YUM BRANDS':'YUMR',
            'ZOETIS INC':'Z1TS',
            'ZOOM VIDEO':'Z1OM',
            'ACCENTURE':'ACNB',
            'ADOBE INC':'ADBE',
            'AFLAC INC':'A1FL',
            'AIG GROUP':'AIGB',
            'ALIBABAGR':'BABA',
            'ALL NORTE':'FRRN',
            'AMBEV S/A':'ABEV',
            'AMCOR PLC':'A1CR',
            'ANSYS INC':'A1NS',
            'APTIV PLC':'APTV',
            'AREZZO CO':'ARZZ',
            'ARGENX SE':'A1RG',
            'ARMSTRONG':'AWII',
            'ASML HOLD':'ASML',
            'BAIDU INC':'BIDU',
            'BALL CORP':'B1LL',
            'BANCO BMG':'BMGB',
            'BANCO PAN':'BPAN',
            'BERKSHIRE':'BERK',
            'BHP GROUP':'BHPG',
            'BILBAOVIZ':'BILB',
            'BK BRASIL':'BKBR',
            'BLACKROCK':'BLAK',
            'BOA SAFRA':'SOJA',
            'BOA VISTA':'BOAS',
            'BRADESPAR':'BRAP',
            'BRB BANCO':'BSLI',
            'CABOT OIL':'C1OG',
            'CANON INC':'CAJI',
            'CEA MODAS':'CEAB',
            'CHUBB LTD':'C1BL',
            'CITIGROUP':'CTGP',
            'CLEARSALE':'CLSA',
            'CLOROX CO':'CLXC',
            'CME GROUP':'CHME',
            'COCA COLA':'COCA',
            'COGNIZANT':'CTSH',
            'COSAN LOG':'RLOG',
            'COTEMINAS':'CTNM',
            'DIAGEO PL':'DEOP',
            'ELETROPAR':'LIPR',
            'EQTL PARA':'EQPA',
            'EXCELSIOR':'BAUH',
            'FDC INFRA':'BBVH',
            'FDC LECCA':'LECA',
            'FII ATRIO':'ARRI',
            'FII DOVEL':'DOVL',
            'FII HOUSI':'HOSI',
            'FII IFI-D':'IFID',
            'FII IFI-E':'IFIE',
            'FII INTER':'BICR',
            'FII KINEA':'KNRI',
            'FII LUGGO':'LUGG',
            'FII MOGNO':'MGFF',
            'FII NEWRU':'NEWU',
            'FII QUATA':'QIFF',
            'FII RB II':'RBRD',
            'FII SJ AU':'SJAU',
            'FII STARX':'STRX',
            'FIP IE II':'ESUD',
            'FISET TUR':'FSTU',
            'FRESENIUS':'FMSC',
            'GAIA AGRO':'GAFL',
            'GAMA PART':'OPGM',
            'GETNINJAS':'NINJ',
            'GP INVEST':'GPIV',
            'GRUPO SBF':'SBFG',
            'HABITASUL':'HBTS',
            'HESS CORP':'H1ES',
            'HIDROVIAS':'HBSA',
            'HONEYWELL':'HONB',
            'IDEX CORP':'I1EX',
            'IHPARDINI':'PARD',
            'INDS ROMI':'ROMI',
            'INFRACOMM':'IFCM',
            'ING GROEP':'INGG',
            'INTELBRAS':'INTB',
            'IQIYI INC':'I1QY',
            'JHSF PART':'JHSF',
            'KOPHILIPS':'PHGN',
            'KROGER CO':'K1RC',
            'LIGHT S/A':'LIGT',
            'LINDE PLC':'L1IN',
            'MARCOPOLO':'POMO',
            'MATER DEI':'MATD',
            'MCCORMICK':'M1KC',
            'MCDONALDS':'MCDC',
            'MEDTRONIC':'MDTC',
            'MELHOR SP':'MSPA',
            'METALFRIO':'FRIO',
            'MICROSOFT':'MSFT',
            'MMX MINER':'MMXM',
            'MODALMAIS':'MODL',
            'MOSAIC CO':'MOSC',
            'MSCI ACWI':'BACW',
            'MSCI EAFE':'BEFA',
            'MULTIPLAN':'MULT',
            'NEWS CORP':'N1WS',
            'NOMURA HO':'NMRH',
            'OCEANPACT':'OPCT',
            'OMEGA GER':'OMGE',
            'ONEOK INC':'O1KE',
            'ORIX CORP':'I1XC',
            'PAGSEGURO':'PAGS',
            'PDG REALT':'PDGR',
            'PETROBRAS':'PETR',
            'PETROCHIN':'PTCH',
            'PETTENATI':'PTNT',
            'QORVO INC':'Q1RV',
            'QUALICORP':'QUAL',
            'REDE D OR':'RDOR',
            'RIO TINTO':'RIOT',
            'ROD TIETE':'RDVT',
            'RUMO S.A.':'RAIL',
            'SANTANDER':'BCSA',
            'SER EDUCA':'SEER',
            'SMALL CAP':'SMLL',
            'SMART FIT':'SMFT',
            'SNOWFLAKE':'S2NW',
            'SP GLOBAL':'SPGI',
            'STARBUCKS':'SBUB',
            'STATKRAFT':'STKF',
            'STMICROEL':'STMN',
            'TECNOSOLO':'TCNO',
            'TELEFONIC':'TLNC',
            'TERNIUMSA':'TXSA',
            'TESLA INC':'TSLA',
            'TEXAS INC':'TEXA',
            'TRAVELERS':'TRVC',
            'UBS GROUP':'UBSG',
            'VIACOMCBS':'C1BS',
            'VIAVAREJO':'VVAR',
            'VULCABRAS':'VULC',
            'WALGREENS':'WGBA',
            'WHIRLPOOL':'WHRL',
            'XYLEM INC':'X1YL',
            'YBYRA S/A':'YBRA',
            'AB INBEV':'ABUD',
            'AEGON NV':'A1EG',
            'AES CORP':'A1ES',
            'ALIANSCE':'ALSO',
            'ALIPERTI':'APTI',
            'ALPHABET':'GOGL',
            'AMAZONIA':'BAZA',
            'APA CORP':'A1PA',
            'AURA 360':'AURA',
            'BANESTES':'BEES',
            'BANRISUL':'BRSR',
            'BARDELLA':'BDLL',
            'BEST BUY':'BBYY',
            'BETAPART':'BETP',
            'BRADESCO':'BBDC',
            'BRISANET':'BRIT',
            'CDW CORP':'C1DW',
            'CENTAURO':'SBFG',
            'CIBRASEC':'CBSC',
            'COGNA ON':'COGN',
            'COTY INC':'COTY',
            'CSX CORP':'CSXC',
            'CTC S.A.':'CTCA',
            'CTRIPCOM':'CRIP',
            'CURY S/A':'CURY',
            'DEERE CO':'DEEC',
            'ENCORPAR':'ECPR',
            'ENERGISA':'ENGI',
            'FACEBOOK':'FBOK',
            'FASTENAL':'FASL',
            'FDC POLO':'PLPF',
            'FII BCIA':'BCIA',
            'FII BTLG':'BTLG',
            'FII HUSI':'HUSI',
            'FII MAUA':'MCCI',
            'FII ZION':'ZIFI',
            'FIP IE I':'ESUU',
            'FLEX S/A':'FLEX',
            'FMC CORP':'F1MC',
            'FOCUS ON':'POWE',
            'FOX CORP':'FOXC',
            'FREEPORT':'FCXO',
            'GRENDENE':'GRND',
            'HAGA S/A':'HAGA',
            'HERCULES':'HETA',
            'HONDA MO':'HOND',
            'IBOVESPA':'IBOV',
            'ICONSUMO':'ICON',
            'IGUATEMI':'IGTA',
            'INTER SA':'INNT',
            'JPMORGAN':'JPMC',
            'KLA CORP':'K1LA',
            'L BRANDS':'LBRN',
            'LKQ CORP':'L1KQ',
            'LOCALIZA':'RENT',
            'LOCKHEED':'LMTB',
            'LUPATECH':'LUPA',
            'MSCI INC':'M1SC',
            'NICE LTD':'N1IC',
            'OKTA INC':'O1KT',
            'PETRORIO':'PRIO',
            'PORTO VM':'PSVM',
            'PPL CORP':'P1PL',
            'PROFARMA':'PFRM',
            'PVH CORP':'P1VH',
            'QR ETHER':'QETH',
            'QUALCOMM':'QCOM',
            'RD SHELL':'RDSA',
            'RECRUSUL':'RCSL',
            'RELX PLC':'R1EL',
            'RODOBENS':'RBNS',
            'ROKU INC':'R1KU',
            'RUMO LOG':'RAIL',
            'STONE CO':'STOC',
            'TAKEDAPH':'TAKP',
            'TELEBRAS':'TELB',
            'TOYOTAMO':'TMCO',
            'ULTRAPAR':'UGPA',
            'UNIFIQUE':'FIQE',
            'UNILEVER':'ULEV',
            'US STEEL':'USSX',
            'USIMINAS':'USIM',
            'VISA INC':'VISA',
            'WAL MART':'WALM',
            'WESTWING':'WEST',
            'WIZ S.A.':'WIZS',
            'ZYNGA INC':'Z2NG',
            '3TENTOS':'TTEN',
            'ABB LTD':'A1BB',
            'AMBIPAR':'AMBP',
            'AON PLC':'A1ON',
            'ARCELOR':'ARMT',
            'ATOMPAR':'ATOM',
            'ATT INC':'ATTB',
            'AUTOBAN':'ANHB',
            'AZEVEDO':'AZEV',
            'BANPARA':'BPAR',
            'BOMBRIL':'BOBR',
            'BOOKING':'BKNG',
            'BRASKEM':'BRKM',
            'CAMBUCI':'CAMB',
            'CEEE-GT':'EEEL',
            'CELGPAR':'GPAR',
            'CHEVRON':'CHVX',
            'COLGATE':'COLG',
            'COMCAST':'CMCS',
            'CRH PLC':'CRHP',
            'CRISTAL':'CRPG',
            'DESKTOP':'DESK',
            'DOTZ SA':'DOTZ',
            'DOW INC':'D1OW',
            'DURATEX':'DTEX',
            'ECOVIAS':'ECOV',
            'ELEKTRO':'EKTR',
            'EMBRAER':'EMBR',
            'ESTAPAR':'ALPK',
            'ESTRELA':'ESTR',
            'ETERNIT':'ETER',
            'EUCATEX':'EUCA',
            'FERBASA':'FESA',
            'FII CF2':'CFHI',
            'FII HAZ':'ATCR',
            'FII MAC':'DMAC',
            'FII SCP':'SCPF',
            'FII SPA':'SPAF',
            'FRAS-LE':'FRAS',
            'HAPVIDA':'HAPV',
            'IBRX 50':'IBXL',
            'IGB S/A':'IGBR',
            'IGUA SA':'IGSN',
            'IMC S/A':'MEAL',
            'INVEPAR':'IVPR',
            'JOHNSON':'JNJB',
            'JOSAPAR':'JOPA',
            'KARSTEN':'CTKA',
            'KEYCORP':'K1EY',
            'KT CORP':'K1TC',
            'LIFEMED':'LMED',
            'LOCAWEB':'LWSA',
            'MARFRIG':'MRFG',
            'MELNICK':'MELK',
            'MINERVA':'BEEF',
            'MINUPAR':'MNPR',
            'MOSAICO':'MOSI',
            'MSCI UK':'BEWU',
            'MUNDIAL':'MNDL',
            'NEOGRID':'NGRD',
            'NETEASE':'NETE',
            'NETFLIX':'NFLX',
            'NOV INC':'N1OV',
            'NVR INC':'N1VR',
            'ODERICH':'ODER',
            'PRATICA':'PTCA',
            'RUMO SA':'RAIL',
            'SANEPAR':'SAPR',
            'SEA LTD':'S2EA',
            'SPRINGS':'SGPS',
            'SPTURIS':'AHEB',
            'TECHNOS':'TECN',
            'TECNISA':'TCSA',
            'TREVISA':'LUXM',
            'TRUESEC':'APCS',
            'TWITTER':'TWTR',
            'UDR INC':'U1DR',
            'UNICASA':'UCAS',
            'VERIZON':'VERZ',
            'VF CORP':'VFCO',
            'WPP PLC':'W1PP',
            'ABBOTT':'ABTT',
            'ABBVIE':'ABBV',
            'AIRBNB':'AIRB',
            'ALLIAR':'AALR',
            'ALLIED':'ALLD',
            'ALUPAR':'ALUP',
            'AMAZON':'AMZO',
            'ATMASA':'ATMP',
            'BAHEMA':'BAHI',
            'BANESE':'BGIP',
            'BAUMER':'BALM',
            'BIOGEN':'BIIB',
            'BOEING':'BOEI',
            'BP PLC':'B1PP',
            'BRASIL':'BBAS',
            'BRF SA':'BRFS',
            'CCR SA':'CCRO',
            'CEEE-D':'CEED',
            'CELESC':'CLSC',
            'CEMEPE':'MAPT',
            'COELBA':'CEEB',
            'COELCE':'COCE',
            'COMGAS':'CGAS',
            'COPASA':'CSMG',
            'COSERN':'CSRN',
            'COSTCO':'COWC',
            'DOHLER':'DOHL',
            'ENJOEI':'ENJU',
            'FLEURY':'FLRY',
            'FUNDES':'FDES',
            'GAFISA':'GFSA',
            'GERDAU':'GGBR',
            'GILEAD':'GILD',
            'HELBOR':'HBOR',
            'HYPERA':'HYPE',
            'INEPAR':'INEP',
            'ITAUSA':'ITSA',
            'JD COM':'JDCO',
            'KALLAS':'KLAS',
            'KROTON':'KROT',
            'LITELA':'LTLA',
            'LOG-IN':'LOGN',
            'MACY S':'MACY',
            'MELIUZ':'CASH',
            'METISA':'MTSA',
            'MOVIDA':'MOVI',
            'ORACLE':'ORCL',
            'ORIZON':'ORVR',
            'PADTEC':'PDTC',
            'PFIZER':'PFIZ',
            'POLPAR':'PPAR',
            'PRINER':'PRNR',
            'PROMAN':'PRMN',
            'RENOVA':'RNEW',
            'SABESP':'SBSP',
            'SANSUY':'SNSY',
            'SAP SE':'SAPP',
            'SCHULZ':'SHUL',
            'SCHWAB':'SCHW',
            'SEAGEN':'S1GE',
            'SEMPRA':'S1RE',
            'SIMPAR':'SIMH',
            'SINQIA':'SQIA',
            'TRISUL':'TRIS',
            'UNIPAR':'UNIP',
            'UPTICK':'UPKP',
            'NATURA':'NTCO',
            'FIBRIA':'FIBR',
            'AERIS':'AERI',
            'AMGEN':'AMGN',
            'ANIMA':'ANIM',
            'APPLE':'AAPL',
            'ARMAC':'ARML',
            'ASSAI':'ASAI',
            'BIOMM':'BIOM',
            'CAMIL':'CAML',
            'CASAN':'CASN',
            'CEDRO':'CEDO',
            'CELPE':'CEPE',
            'CEMIG':'CMIG',
            'CIELO':'CIEL',
            'CISCO':'CSCO',
            'COPEL':'CPLE',
            'COSAN':'CSAN',
            'DELTA':'DEAI',
            'DIMED':'PNVL',
            'DOMMO':'DMMO',
            'ENEVA':'ENEV',
            'EZTEC':'EZTC',
            'FEMSA':'FMXB',
            'FINAM':'FNAM',
            'FINOR':'FNOR',
            'GOPRO':'GPRO',
            'INTEL':'ITLC',
            'IRANI':'RANI',
            'IVBX2':'IVBX',
            'LAVVI':'LAVV',
            'LIGHT':'LIGH',
            'LILLY':'LILY',
            'LITEL':'LTEL',
            'MERCK':'MRCK',
            'MILLS':'MILS',
            'MOBLY':'MBLY',
            'POSCO':'P1KX',
            'STARA':'STTR',
            'TAESA':'TAEE',
            'TEGMA':'TGMA',
            'TEKNO':'TKNO',
            'TENDA':'TEND',
            'TOTVS':'TOTS',
            'VALID':'VLID',
            'VAMOS':'VAMO',
            'VIBRA':'VBBR',
            'VIVER':'VIVR',
            'AZUL':'AZUL',
            'BLAU':'BLAU',
            'CESP':'CESP',
            'CIMS':'CMSA',
            'DASA':'DASA',
            'EBAY':'EBAY',
            'EMAE':'EMAE',
            'EVEN':'EVEN',
            'LINX':'LINX',
            'NIKE':'NIKE',
            'PETZ':'PETZ',
            'PINE':'PINE',
            'PPLA':'PPLA',
            'TEKA':'TEKA',
            'TUPY':'TUPY',
            'VALE':'VALE',
            'BRQ':'BRQB',
            'CBA':'CBAV',
            'CEB':'CEBR',
            'CEG':'CEGR',
            'CR2':'CRDE',
            'GAP':'GPSI',
            'GOL':'GOLL',
            'GPS':'GGPS',
            'IBM':'IBMB',
            'JBS':'JBSS',
            'JSL':'JSLG',
            'MRV':'MRVE',
            'RNI':'RDNI',
            'TIM':'TIMS',
            'UPS':'UPSS',
            'WEG':'WEGE',
            '3M':'MMMC',
            'B3':'B3SA',
            'GE':'GEOO',
            'OI':'OIBR',
            'PG':'PGCO',
            'TC':'TRAD',
            'XP INC':'XPBR'
        }
        desc = desc.upper() + " "

        for company, cod in companys.items():
            if company in desc:
                ticker = cod + get_sufix(desc)
                return ticker.upper()
               
    return ticker.upper()


def set_row(corretora, numero_nota, data_pregao, lado, mercado, ativo, quantidade, preco, total, taxa = '0'):
    taxa = str(taxa)
    corretora = corretora.strip()
    numero_nota = numero_nota.strip()
    data_pregao = datetime.strptime(data_pregao.strip(), '%d/%m/%Y')

    lado = lado.strip().upper()
    mercado = mercado.strip()
    if ativo[:3] in "wdo/win": ativo = ativo.upper().replace(" ", "")
    ativo = ativo.strip()
    quantidade = float(quantidade.strip().replace(',','.'))
    preco = float(preco.strip().replace(',','.'))
    total = float(total.strip().replace(',','.'))
    taxa = float(taxa.strip().replace(',','.'))
    
    if lado == "C":
        total = -total
    else:
        quantidade = -quantidade

    ws.append([corretora, numero_nota, data_pregao, lado, mercado, ativo, quantidade, preco, total, taxa])
    

def set_exercicio(corretora, numero_nota, data_pregao, lado, mercado, cod_neg, quantidade, preco, total, especificacao_titulo):
    # Inclui lançamento do ativo
    ativo = get_sufix(especificacao_titulo)
    if ativo != "":
        ativo = cod_neg[0:4] + ativo
    else:
        ativo = cod_neg
        
    mercado = mercado + ' (ativo)'
    set_row(corretora, numero_nota, data_pregao, lado, mercado, ativo, quantidade, preco, total)
   
    # Zera lançamento de opção
    callRE = re.compile('[A-L]')

    if callRE.search(cod_neg[5:6]):
        if lado == 'c':
            lado = 'v'
        else: 
            lado = 'c' 
    
    

    mercado = mercado.replace(' (ativo)', ' ( ajuste )')

    set_row(corretora, numero_nota, data_pregao, lado, mercado, cod_neg, quantidade, '0', '0')
    
    
def set_lancamento(corretora, numero_nota, data_pregao, lado, mercado, cod_neg, quantidade, preco, total, especificacao_titulo, taxa = 0):
    if mercado == 'Exercício de opções':
        set_exercicio(corretora, numero_nota, data_pregao, lado, mercado, cod_neg, quantidade, preco, total, especificacao_titulo)
    else:
        set_row(corretora, numero_nota, data_pregao, lado, mercado, cod_neg, quantidade, preco, total, taxa)  


def ler_xp(txt):
    global numero_nota_old, dt_inicio, dt_fim, dt_fim, data_pregao, numero_nota

    p_dt_pregao = re.compile(r'(data *pregão) * *[0-9]{2}\/[0-9]{2}\/[0-9]{4}')
    data_pregao = p_dt_pregao.search(txt).group(0).strip()
    data_pregao = data.search(data_pregao).group(0).strip()

    p_nota = re.compile(r'nr *nota ([0-9]{0,3}\.*[0-9]{0,3}\.*[0-9]{2,3})')
    numero_nota = p_nota.search(txt).group(0).strip()
    numero_nota = inteiro.search(numero_nota).group(0).strip()

    if numero_nota_old == None:
        numero_nota_old = numero_nota
    
    if dt_inicio == None: 
        dt_inicio = data_pregao.split('/')
        dt_inicio = dt_inicio[2] + "-" + dt_inicio[1] + "-" + dt_inicio[0]
        dt_fim = dt_inicio
    else:
        dt = data_pregao.split('/')
        dt = dt[2] + "-" + dt[1] + "-" + dt[0]
        
        if dt < dt_inicio:
            dt_inicio = dt
        
        if dt > dt_fim:
            dt_fim = dt
    
    if operacoes[0].search(txt):
        ler_xp_bovespa(txt, data_pregao, numero_nota)
    else:
        ler_xp_bmf(txt, data_pregao, numero_nota)


def ler_xp_bmf(txt, data_pregao, numero_nota):
    if operacoes[3].search(txt):
        dados_operacao = operacoes[3].search(txt).group(0).strip()
        dados_operacao = operacoes[1].search(dados_operacao).group(0).strip()
        dados_operacao = dados_operacao.replace(' c win ', '; c win ')
        dados_operacao = dados_operacao.replace(' v win ', '; v win ')
        dados_operacao = dados_operacao.replace(' c wdo ', '; c wdo ')
        dados_operacao = dados_operacao.replace(' v wdo ', '; v wdo ')
        dados_operacao = dados_operacao.split(';')
        

        p_ativo = re.compile(r'(wdo|win) [a-z][0-9]{2}')
        p_qtd = re.compile(r'[0-9] [0-9]{1,2} [0-9]')
        p_vlr = re.compile(r' [0-9]{1,4},[0-9]{2} [dc]')
        p_taxa = re.compile(r'[dc] [0-9]{1,4},[0-9]{2}')

        for operacao in dados_operacao:
            if p_ativo.search(operacao):
                lado = operacao[1:2]
                ativo = p_ativo.search(operacao).group(0).strip()
                qtd =  p_qtd.search(operacao).group(0).strip().split(" ")[1]
                vlr =  p_vlr.search(operacao).group(0).strip().split(" ")[0]
                taxa =  p_taxa.search(operacao).group(0).strip().split(" ")[1]

                set_row(corretora,  numero_nota, data_pregao, lado , "Futuro", ativo, qtd, vlr, vlr, taxa)
    else:
        print(f'O arquivo {corretora}-{data_pregao}-{numero_nota} ainda não pode ser lido!')

def ler_xp_bovespa(txt, data_pregao, numero_nota):
    taxa = '0'
    txt = re.sub(r"\s+", " ", txt)
    resumo_financeiro = txt.split(' l - precatório ')
    resumo_financeiro = resumo_financeiro [len(resumo_financeiro)-1]
    resumo_financeiro = re.findall(r'\d{1,3}(?:\.\d{3})*,\d{2}'  , resumo_financeiro)
    if len(resumo_financeiro) > 16: taxa = resumo_financeiro[9].replace(".","").replace(",",".")


    dados_operacao = operacoes[0].search(txt).group(0).strip()
    dados_operacao = operacoes[1].search(dados_operacao).group(0).strip()
    dados_operacao = operacoes[2].split(dados_operacao)

    if float(taxa) > 0: taxa = str(float(taxa) / (len(dados_operacao) -1)).replace(".",",")

    for operacao in dados_operacao:
        if cv.search(operacao):
            lado = cv.search(operacao).group(0).strip()[0:1]
            mercado = get_market(operacao)
            especificacao_titulo = p_ativo.search(operacao).group(0).strip()
            cod_neg = get_ticker(especificacao_titulo) 
            valores = f'(?<={especificacao_titulo}).+'
            valores = re.compile(valores).search(operacao).group(0).strip()
            valores = valores.split(" ")
            nPos = len(valores)
            quantidade = valores[nPos-3]
            preco = valores[nPos-2]
            total = valores[nPos-1]

            
            set_lancamento(corretora, numero_nota, data_pregao, lado, mercado, cod_neg, quantidade, preco, total, especificacao_titulo, taxa)


def ler_modal(txt):
    global numero_nota_old, dt_inicio, dt_fim, dt_fim, data_pregao, numero_nota

    p_dt_pregao = re.compile(r'(data *pregão) *[0-9]{2,10} [0-9] [0-9]{2}\/[0-9]{2}\/[0-9]{4}')
    data_pregao = p_dt_pregao.search(txt).group(0).strip()
    data_pregao = data.search(data_pregao).group(0).strip()

    p_nota = re.compile(r'nr nota folha data pregão ([0-9]{0,3}\.*[0-9]{0,3}\.*[0-9]{2,3})')
    numero_nota = p_nota.search(txt).group(0).strip()
    numero_nota = inteiro.search(numero_nota).group(0).strip()

    if numero_nota_old == None:
        numero_nota_old = numero_nota
    
    if dt_inicio == None: 
        dt_inicio = data_pregao.split('/')
        dt_inicio = dt_inicio[2] + "-" + dt_inicio[1] + "-" + dt_inicio[0]
        dt_fim = dt_inicio
    else:
        dt = data_pregao.split('/')
        dt = dt[2] + "-" + dt[1] + "-" + dt[0]
        
        if dt < dt_inicio:
            dt_inicio = dt
        
        if dt > dt_fim:
            dt_fim = dt
    
    if operacoes[0].search(txt):
        ler_modal_bovespa(txt, data_pregao, numero_nota)
    else:
        print('ler_bmf_modal(txt, data_pregao, numero_nota)')


def ler_modal_bovespa(txt, data_pregao, numero_nota):
    dados_operacao = operacoes[0].search(txt).group(0).strip()
    dados_operacao = operacoes[1].search(dados_operacao).group(0).strip()
    dados_operacao = operacoes[2].split(dados_operacao)

    p_ativo = re.compile(r' [a-z]{4}[1-9]{1,2}f* | [a-z]{5}[0-9]{2,3}w*[1-4]* ')
    p_vlr = re.compile(r' [0-9]{1,5},[0-9]{2}')

    for operacao in dados_operacao:
        if cv.search(operacao):
            lado = cv.search(operacao).group(0).strip()[0:1]

            mercado = get_market(operacao)

            especificacao_titulo = p_ativo.search(operacao).group(0).strip()
            cod_neg = get_ticker(especificacao_titulo)

            valores = p_vlr.findall(operacao)

            nPos = len(valores)
                
            quantidade = valores[nPos-3]
            preco = valores[nPos-2]
            total = valores[nPos-1]

            set_lancamento(corretora, numero_nota, data_pregao, lado, mercado, cod_neg, quantidade, preco, total, especificacao_titulo)


def ler_nu(txt):
    global numero_nota_old, dt_inicio, dt_fim, dt_fim, data_pregao, numero_nota

    p_dt_pregao = re.compile(r'(data *pregão) * *[0-9]{2}\/[0-9]{2}\/[0-9]{4}')
    data_pregao = p_dt_pregao.search(txt).group(0).strip()
    data_pregao = data.search(data_pregao).group(0).strip()

    p_nota = re.compile(r'(número da nota) [0-9]{2,10} ')
    numero_nota = p_nota.search(txt).group(0).strip()
    numero_nota = inteiro.search(numero_nota).group(0).strip()

    if numero_nota_old == None:
        numero_nota_old = numero_nota
    
    if dt_inicio == None: 
        dt_inicio = data_pregao.split('/')
        dt_inicio = dt_inicio[2] + "-" + dt_inicio[1] + "-" + dt_inicio[0]
        dt_fim = dt_inicio
    else:
        dt = data_pregao.split('/')
        dt = dt[2] + "-" + dt[1] + "-" + dt[0]
        
        if dt < dt_inicio:
            dt_inicio = dt
        
        if dt > dt_fim:
            dt_fim = dt
    p_operacoes = re.compile(r'd/c d/c.+(resumo dos negócios)')

    if p_operacoes.search(txt):
        ler_nu_bovespa(txt, data_pregao, numero_nota)
    else:
        print('ler_bmf_nu(txt, data_pregao, numero_nota)')


def ler_nu_bovespa(txt, data_pregao, numero_nota):
    p_operacoes = re.compile(r'd/c d/c.+(resumo dos negócios)')
    dados_operacao = p_operacoes.search(txt).group(0).strip()
    dados_operacao = operacoes[2].split(dados_operacao)

    p_vlr = re.compile(r' [0-9]{1,5},[0-9]{2}| [0-9]{1,5}')

    for operacao in dados_operacao:
        if cv.search(operacao):
            lado = cv.search(operacao).group(0).strip()[0:1]
            mercado = get_market(operacao)

            especificacao_titulo = p_ativo.search(operacao).group(0).strip()
            cod_neg = get_ticker(especificacao_titulo)
            valores = p_vlr.findall(operacao)

            nPos = len(valores)
                
            quantidade = valores[nPos-3]
            preco = valores[nPos-2]
            total = valores[nPos-1]

            set_lancamento(corretora, numero_nota, data_pregao, lado, mercado, cod_neg, quantidade, preco, total, especificacao_titulo)


def ler_genial(txt):
    global numero_nota_old, dt_inicio, dt_fim, dt_fim, data_pregao, numero_nota

    p_dt_pregao = re.compile(r' nr *nota [0-9]{2}\/[0-9]{2}\/[0-9]{4}| nr *nota [0-9]* [0-9]{2}\/[0-9]{2}\/[0-9]{4}')
    data_pregao = p_dt_pregao.search(txt).group(0).strip()
    data_pregao = data.search(data_pregao).group(0).strip()

    p_nota = re.compile(r' nr *nota *[0-9]{2}\/[0-9]{2}\/[0-9]{4} [0-9] [0-9]{2,10} | nr *nota *[0-9]* *[0-9]{2}\/[0-9]{2}\/[0-9]{4} [0-9]{2,10} ')
    numero_nota = p_nota.search(txt).group(0)
    numero_nota = re.search(r' [0-9]{2,10} ',numero_nota ).group(0).strip()

    if numero_nota_old == None:
        numero_nota_old = numero_nota
    
    if dt_inicio == None: 
        dt_inicio = data_pregao.split('/')
        dt_inicio = dt_inicio[2] + "-" + dt_inicio[1] + "-" + dt_inicio[0]
        dt_fim = dt_inicio
    else:
        dt = data_pregao.split('/')
        dt = dt[2] + "-" + dt[1] + "-" + dt[0]
        
        if dt < dt_inicio:
            dt_inicio = dt
        
        if dt > dt_fim:
            dt_fim = dt
    p_operacoes = re.compile(r'q* *negociação.+(resumo dos negócios)')
    if p_operacoes.search(txt):
        ler_genial_bovespa(txt, data_pregao, numero_nota)
    else:
        ler_genial_bmf(txt, data_pregao, numero_nota)


def ler_genial_bovespa(txt, data_pregao, numero_nota):
    
    p_operacoes = re.compile(r'[0-9]-bovespa.+(resumo dos negócios)')
    if p_operacoes.search(txt):
        dados_operacao = p_operacoes.search(txt).group(0).strip()

        if 'exerc opc' in dados_operacao:
            p_split = re.compile(r'(?<=[0-9][0-9] )[cd]{1} [0-9]-')
        else:
            p_split = operacoes[2]

        dados_operacao = p_split.split(dados_operacao)

        p_vlr = re.compile(r' [0-9]{1,5},[0-9]{2}| [0-9]{1,5}')
        
        for operacao in dados_operacao:
            if cv.search(operacao):
                lado = cv.search(operacao).group(0).strip()[0:1]
                mercado = get_market(operacao)

                especificacao_titulo = p_ativo.search(operacao).group(0).strip()
                cod_neg = get_ticker(especificacao_titulo)
                valores = p_vlr.findall(operacao)
                nPos = len(valores)

                quantidade = valores[nPos-3]
                preco = valores[nPos-2]
                total = valores[nPos-1]

                set_lancamento(corretora, numero_nota, data_pregao, lado, mercado, cod_neg, quantidade, preco, total, especificacao_titulo)
    else:
        ler_xp_bmf(txt)


def ler_genial_bmf(txt, data_pregao, numero_nota):
    operacoes = re.compile(r'd\/c taxa operacional.+venda disponível')
    dados_operacao = operacoes.search(txt).group(0)
    dados_operacao = dados_operacao.replace(' cwin ', '; c win ')
    dados_operacao = dados_operacao.replace(' vwin ', '; v win ')
    dados_operacao = dados_operacao.replace(' cwdo ', '; c wdo ')
    dados_operacao = dados_operacao.replace(' vwdo ', '; v wdo ')
    dados_operacao = dados_operacao.split(';')
    
    p_ativo = re.compile(r'(wdo|win) [a-z][0-9]{2}')
    p_qtd = re.compile(r'[0-9] [0-9]{1,2} [0-9]')
    p_vlr = re.compile(r' [0-9]{1,4},[0-9]{2} *[dc]')
    p_taxa = re.compile(r'[dc] [0-9]{1,4},[0-9]{2}')
    p_float = re.compile(r'\d{1,10},\d{2}')

    for operacao in dados_operacao:
        if p_ativo.search(operacao):
            lado = operacao[1:2]
            ativo = p_ativo.search(operacao).group(0).strip()
            qtd =  p_qtd.search(operacao).group(0).strip().split(" ")[1]
            total =  p_vlr.search(operacao).group(0).strip().split(" ")[0]
            total = p_float.search(total).group(0)
            vlr = str(float(total.replace(",","."))/float(qtd.replace(",",".")))
            taxa =  p_taxa.search(operacao).group(0).strip().split(" ")[1]

            set_row(corretora,  numero_nota, data_pregao, lado , "Futuro", ativo, qtd, vlr, total, taxa)

def ler_itau(txt):
    global numero_nota_old, dt_inicio, dt_fim, dt_fim, data_pregao, numero_nota

    p_dt_pregao = re.compile(r'data  pregão [0-9]{2,10} [0-9] [0-9]{2}\/[0-9]{2}\/[0-9]{4}')
    data_pregao = p_dt_pregao.search(txt).group(0).strip()
    data_pregao = data.search(data_pregao).group(0).strip()

    numero_nota = p_dt_pregao.search(txt).group(0).strip()
    numero_nota = inteiro.search(numero_nota).group(0).strip()

    if numero_nota_old == None:
        numero_nota_old = numero_nota
    
    if dt_inicio == None: 
        dt_inicio = data_pregao.split('/')
        dt_inicio = dt_inicio[2] + "-" + dt_inicio[1] + "-" + dt_inicio[0]
        dt_fim = dt_inicio
    else:
        dt = data_pregao.split('/')
        dt = dt[2] + "-" + dt[1] + "-" + dt[0]
        
        if dt < dt_inicio:
            dt_inicio = dt
        
        if dt > dt_fim:
            dt_fim = dt
    
    if operacoes[0].search(txt):
        ler_xp_bovespa(txt, data_pregao, numero_nota)
    else:
        ler_xp_bmf(txt, data_pregao, numero_nota)


wb = Workbook()
ws = wb.active
ws.append(['Corretora', 'Nº Nota', 'Data', 'Compra/Venda', 'Mercado', 'Ativo', 'Quantidade', 'Preço', 'Total', 'Taxa'])

dt_inicio = None
dt_fim = None

for diretorio in diretorios:
    arquivos = os.listdir(diretorio)

    for arquivo in arquivos:
        if arquivo.lower()[-3:] == "pdf":
            print("Lendo " + diretorio + arquivo)

            with open(diretorio + arquivo, 'rb') as pdf_file:
                pdf_reader = PdfReader(pdf_file)

                for page in pdf_reader.pages:
                    
                    txt = page.extract_text()
                    txt = txt.replace('\r','').replace('\n', ' ').replace('.','').lower().replace('\xa0', ' ')

                    corretora = get_corretora(txt, diretorio + arquivo)
                    
                    if corretora.lower() in ['xp', 'clear', 'rico']:
                        ler_xp(txt)
                    elif 'modal' in corretora.lower():
                        ler_modal(txt)
                    elif 'genial' in corretora.lower():
                        ler_genial(txt)
                    elif 'nuinvest' in corretora.lower():
                        ler_nu(txt)
                    elif 'itaú' in corretora.lower():
                        ler_itau(txt)
                    elif 'itau' in corretora.lower():
                        ler_itau(txt)
                    else:
                        print('O arquivo ' + corretora + ' ainda não pode ser lido!')

                titulo = titulo + corretora +"_"
                titulo +=  dt_inicio + "_a_" + dt_fim 
                i = 2

                while os.path.isfile(titulo + ".xlsx"):
                    titulo = titulo.replace(" (" + str(i-1) +")", "")
                    titulo = titulo + " (" + str(i) +")"
                    i += 1

titulo = 'Notas Importadas'
wb.save(titulo + ".xlsx")


