import os
import requests
import tempfile
import pandas as pd
import ibgeparser.log as log
import zipfile, urllib.request, shutil
from urllib.request import urlopen

def criar_pasta_temporaria():
    try:
        return tempfile.mkdtemp()
    except OSError:
        log.exception('Falha ao criar pasta temporaria')

def remover_pasta_temporaria(pasta_temp):
    try:
        shutil.rmtree(pasta_temp)
    except OSError as e:
        log.exception('Falha ao remover pasta temporaria')

def obter_diretorio_trabalho():
    return os.getcwd()

def obter_dados_documentacao(pasta_temp, pasta_trab, modalidades_selecionadas, descricao_ano):
    # extraindo csv de documentação para as modalidades escolhidas
    url='ftp://ftp.ibge.gov.br/Censos/{}/Resultados_Gerais_da_Amostra/Microdados/Documentacao.zip'.format(descricao_ano)
    log.debug('Arquivo de documentacao extraído de: {}'.format(url))

    # download e extração do zip
    with urllib.request.urlopen(url) as response, open('{}/{}'.format(pasta_temp, url.split('/')[-1]), 'wb') as out_file:
        shutil.copyfileobj(response, out_file)
        with zipfile.ZipFile('{}/{}'.format(pasta_temp, url.split('/')[-1])) as zf:
            log.debug('Extraindo a documentação')
            zf.extract('Documentaç╞o/Layout/Layout_microdados_Amostra.xls', '{}/Documentacao'.format(pasta_temp))

    path='{}/Documentacao/Documentaç╞o/Layout/Layout_microdados_Amostra.xls'.format(pasta_temp)

    # baixando csv pelas abas de modalidade
    div_columns={}
    ibge_datasets={}

    for enum_modalidade in modalidades_selecionadas:
        valor_modalidade, descricao_modalidade = enum_modalidade.value

        ibge_desc=pd.read_excel(open(path, 'rb'),sheet_name=valor_modalidade,header=1).dropna(how='all',axis='columns')
        ibge_desc.to_csv('{}/Documentacao_{}.csv'.format(pasta_trab, descricao_modalidade))
        col_specification= list(zip(ibge_desc['POSIÇÃO INICIAL']-1, ibge_desc['POSIÇÃO FINAL']))
        ibge_datasets[descricao_modalidade]=ibge_desc
        div_columns[descricao_modalidade]=col_specification

        log.info('Baixando informações da documentacao sobre {}'.format(descricao_modalidade))

        return ibge_datasets, div_columns

def obter_dados_ibge(ano_selecionado, estados_selecionados, modalidades_selecionadas):
    # cria pasta temporaria no sistema
    pasta_temp = criar_pasta_temporaria()
   
    # obtem a pasta de trabalho para salvar o output (csv)
    pasta_trab = obter_diretorio_trabalho()
   
    # captura o ano selecionado
    ano, descricao_ano = ano_selecionado.value

    # dados de documentação
    ibge_datasets, div_columns = obter_dados_documentacao(pasta_temp, pasta_trab, modalidades_selecionadas, descricao_ano)

    # extraindo csv de todos os estados selecionados pelo usuario no pacote        
    for enum_estado in estados_selecionados:
        valor_estado, estado, sigla = enum_estado.value

        log.info('Baixando informações do estado de {}'.format(estado))
        
        url='ftp://ftp.ibge.gov.br/Censos/{}/Resultados_Gerais_da_Amostra/Microdados/{}.zip'.format(descricao_ano, sigla)
        log.debug('Arquivo referente ao estado de {} extraído de: {}'.format(estado, url))

        # download e extração do zip de dados do estado
        with urllib.request.urlopen(url) as response, open('{}/{}'.format(pasta_temp, url.split('/')[-1]), 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
            with zipfile.ZipFile('{}/{}'.format(pasta_temp, url.split('/')[-1])) as zf:
                log.info('Extraindo os arquivos desejados')
                for enum_modalidade in modalidades_selecionadas:
                    valor_modalidade, descricao_modalidade = enum_modalidade.value

                    zf.extract('{}/Amostra_{}_{}.txt'.format(sigla, descricao_modalidade, str(valor_estado)), '{}/Arquivo_{}'.format(pasta_temp, estado))
                    path='{}/Arquivo_{}/{}/Amostra_{}_{}.txt'.format(pasta_temp, estado, sigla, descricao_modalidade, str(valor_estado))

                    # conversão para csv
                    data=pd.read_fwf(path, colspecs=div_columns[descricao_modalidade])
                    data.columns=ibge_datasets[descricao_modalidade]['VAR'].tolist()

                    # salvando o csv
                    data.to_csv('{}/{}_{}.csv'.format(pasta_trab, path.split('/')[-1][:-4], sigla))

                    log.info('Arquivo de {} de modalidade {} extraído'.format(sigla, descricao_modalidade))

    # apaga a pasta criada no diretório temporario                               
    remover_pasta_temporaria(pasta_temp)