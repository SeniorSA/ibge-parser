from enum import Enum

class Anos(Enum):
    DEZ = [2010, 'Censo_Demografico_2010']

class Estados(Enum):
    RONDONIA = [11, 'Rondônia', 'RO']
    ACRE = [12, 'Acre', 'AC']
    AMAZONAS = [13,'Amazonas', 'AM']
    RORAIMA = [14,'Roraima', 'RR']
    PARA = [15, 'Pará', 'PA']
    AMAPA = [16,'Amapá', 'AP']
    TOCANTINS = [17,'Tocantins', 'TO']
    MARANHAO = [21,'Maranhão', 'MA']
    PIAUI = [22,'Piauí', 'PI']
    CEARA = [23,'Ceará', 'CE']
    RIO_GRANDE_DO_NORTE = [24,'Rio Grande do Norte', 'RN']
    PARAIBA = [25,'Paraíba', 'PB']
    PERNAMBUCO = [26,'Pernambuco', 'PE']
    ALAGOAS = [27,'Alagoas', 'AL']
    SERGIPE = [28,'Sergipe', 'SE']
    BAHIA = [29,'Bahia', 'BA']
    MINAS_GERAIS = [31,'Minas Gerais', 'MG']
    ESPIRITO_SANTO = [32, 'Espírito Santo', 'ES']
    RIO_DE_JANEIRO = [33,'Rio de Janeiro', 'RJ']
    SAO_PAULO = [35, 'São Paulo', 'SP']
    SAO_PAULO_SP1 = ['35_outras', 'São Paulo', 'SP1']
    SAO_PAULO_SP2_RM = ['35_RMSP', 'São Paulo', 'SP2_RM']
    PARANA = [41,'Paraná', 'PR']
    SANTA_CATARINA = [42, 'Santa Catarina', 'SC']
    RIO_GRANDE_DO_SUL = [43,'Rio Grande do Sul', 'RS']
    MATO_GROSSO_DO_SUL = [50,'Mato Grosso do Sul', 'MS']
    MATO_GROSSO = [51,'Mato Grosso', 'MT']
    GOIAS = [52,'Goiás', 'GO']
    DISTRITO_FEDERAL = [53,'Distrito Federal', 'DF']
    TODOS = [0,'Todos', None]


class Modalidades(Enum):
    DOMICILIOS = ['DOMI', 'Domicilios']
    PESSOAS = ['PESS', 'Pessoas']
    EMIGRACAO = ['EMIG', 'Emigracao']
    MORATALIDADE = ['MORT', 'Mortalidade']
    TODOS = [None, 'Todos']