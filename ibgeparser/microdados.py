import os
import requests
import tempfile
import pandas as pd
import ibgeparser.log as log
import zipfile, urllib.request, shutil
from urllib.request import urlopen

class Microdados:
    def __criar_pasta_temporaria(self):
        try:
            return tempfile.mkdtemp()
        except OSError:
            log.exception('Falha ao criar pasta temporaria')

    def __remover_pasta_temporaria(self, pasta_temp):
        try:
            shutil.rmtree(pasta_temp)
        except OSError as e:
            log.exception('Falha ao remover pasta temporaria')

    def __obter_diretorio_trabalho(self):
        return os.getcwd()

    def __obter_dados_documentacao(self, pasta_temp, pasta_trab, modalidades, ano):
        # extraindo csv de documentação para as modalidades escolhidas
        url = 'ftp://ftp.ibge.gov.br/Censos/{}/Resultados_Gerais_da_Amostra/Microdados/Documentacao.zip'.format(ano)
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

        for enum_modalidade in modalidades:
            valor_modalidade, descricao_modalidade = enum_modalidade.value

            ibge_desc=pd.read_excel(open(path, 'rb'), sheet_name=valor_modalidade, header=1).dropna(how='all', axis='columns')
            ibge_desc.to_csv('{}/Documentacao_{}.csv'.format(pasta_trab, descricao_modalidade))
            col_specification = list(zip(ibge_desc['POSIÇÃO INICIAL']-1, ibge_desc['POSIÇÃO FINAL']))
            ibge_datasets[descricao_modalidade] = ibge_desc
            div_columns[descricao_modalidade] = col_specification

            log.info('Baixando informações da documentacao sobre {}'.format(descricao_modalidade))

            return ibge_datasets, div_columns

    def obter_dados_ibge(self, ano, estados, modalidades):
        # cria pasta temporaria no sistema
        pasta_temp = self.__criar_pasta_temporaria()
    
        # obtem a pasta de trabalho para salvar o output (csv)
        pasta_trab = self.__obter_diretorio_trabalho()
    
        # captura o ano selecionado
        valor_ano, descricao_ano = ano.value

        # dados de documentação
        ibge_datasets, div_columns = self.__obter_dados_documentacao(pasta_temp, pasta_trab, modalidades, descricao_ano)

        # extraindo csv de todos os estados selecionados pelo usuario no pacote        
        for enum_estado in estados:
            valor_estado, estado, sigla = enum_estado.value

            log.info('Baixando informações do estado de {}'.format(estado))
            
            url='ftp://ftp.ibge.gov.br/Censos/{}/Resultados_Gerais_da_Amostra/Microdados/{}.zip'.format(descricao_ano, sigla)
            log.debug('Arquivo referente ao estado de {} extraído de: {}'.format(estado, url))

            # download e extração do zip de dados do estado
            with urllib.request.urlopen(url) as response, open('{}/{}'.format(pasta_temp, url.split('/')[-1]), 'wb') as out_file:
                shutil.copyfileobj(response, out_file)

                with zipfile.ZipFile('{}/{}'.format(pasta_temp, url.split('/')[-1])) as zf:
                    log.info('Extraindo os arquivos desejados')
                    for enum_modalidade in modalidades:
                        valor_modalidade, descricao_modalidade = enum_modalidade.value

                        zf.extract('{}/Amostra_{}_{}.txt'.format(sigla, descricao_modalidade, str(valor_estado)), '{}/Arquivo_{}'.format(pasta_temp, estado))
                        path='{}/Arquivo_{}/{}/Amostra_{}_{}.txt'.format(pasta_temp, estado, sigla, descricao_modalidade, str(valor_estado))

                        # conversão para csv
                        data = pd.read_fwf(path, colspecs=div_columns[descricao_modalidade])
                        data.columns = ibge_datasets[descricao_modalidade]['VAR'].tolist()

                        # salvando o csv
                        data.to_csv('{}/{}_{}.csv'.format(pasta_trab, path.split('/')[-1][:-4], sigla))

                        log.info('Arquivo de {} de modalidade {} extraído'.format(sigla, descricao_modalidade))

        # apaga a pasta criada no diretório temporario                               
        self.__remover_pasta_temporaria(pasta_temp)

    def obter_especificacao_coluna(self, palavra_de_busca, modalidades):    
        for enum_modalidade in modalidades:
            valor_modalidade, descricao_modalidade = enum_modalidade.value

            doc = pd.read_csv('{}/Documentacao_{}.csv'.format(self.__obter_diretorio_trabalho(), descricao_modalidade))
            aux = doc.loc[doc['NOME'].str.contains(palavra_de_busca,case=False),['VAR','NOME']]

            for index, row in aux.iterrows():
                try:              
                    log.info('Procure por {} na modalidade de {} para: \n\n{} \n\nCom descrição da coluna de \n{}'
                        .format(row['VAR'], descricao_modalidade, row['NOME'].split(':')[0]," ".join(row['NOME'].split(':')[1:])))
                except IndexError:
                    log.info('Procure por {} na modalidade de {} para: \n\n{}\n\nCom descrição da coluna de \nsem descriçao'
                        .format(row['VAR'], descricao_modalidade, row['NOME'].split(':')[0:]))