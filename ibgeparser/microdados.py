import os
import requests
import tempfile
import pandas as pd
import ibgeparser.enums
from ibgeparser.log import _Log as Log
from ibgeparser.enums import Anos, Estados, Modalidades
import urllib.request, shutil
from zipfile import ZipFile
from urllib.request import urlopen

log = Log()
log.init()

URL_DOCUMENTACAO='ftp://ftp.ibge.gov.br/Censos/{}/Resultados_Gerais_da_Amostra/Microdados/Documentacao.zip'
URL_MICRODADOS='ftp://ftp.ibge.gov.br/Censos/{}/Resultados_Gerais_da_Amostra/Microdados/{}.zip'
ARQUIVO_LAYOUT='Layout_microdados_Amostra.xls'
DIRETORIO_SAIDA='microdados-ibge'

class Microdados:
    def __criar_pasta_temporariaoraria(self):
        try:
            return tempfile.mkdtemp()
        except OSError as e :
            log.exception('Falha ao criar pasta temporaria: {}'.format(e))

    def __remover_pasta_temporariaoraria(self, pasta_temporaria:str):
        try:
            shutil.rmtree(pasta_temporaria)
        except OSError as e:
            log.exception('Falha ao remover pasta temporaria: {}'.format(e))
        
    def __obter_diretorio_trabalho(self):
        try:
            pasta_trabalho = os.path.join(os.getcwd(), DIRETORIO_SAIDA)
            if not os.path.exists(pasta_trabalho):
                os.makedirs(pasta_trabalho)

            return pasta_trabalho
        except OSError as e:
            log.exception('Falha ao obter pasta de trabalho: {}'.format(e))
        except Exception as e:
            log.exception('Falha ao obter pasta de trabalho: {}'.format(e))

    def __download_arquivo(self, url:str, destino:str):
        try:
            with urllib.request.urlopen(url) as response, open(destino, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)

            return destino
        except Exception as e:
                log.error('Erro ao fazer o download dos dados de documentação: {}'.format(e))

    def __extrair_arquivo(self, caminho_origem:str, nome_arquivo:str, caminho_destino:str):
        try:
            with ZipFile(caminho_origem, 'r') as zf:
                log.debug('Extraindo o arquivo {}'.format(caminho_origem))

                for membro in zf.namelist():
                    if os.path.basename(membro) == nome_arquivo:
                        arquivo = zf.open(membro)
                        caminho_arquivo = os.path.join(caminho_destino, nome_arquivo)

                        destino = open(caminho_arquivo, "wb")

                        with arquivo, destino:
                            shutil.copyfileobj(arquivo, destino)

            return caminho_arquivo
        except Exception as e:
            log.error('Erro ao extrair os dados do arquivo desejado: {}'.format(e))

    def __validar_enums(self, ano:enumerate=Anos.DEZ, estados:list=[], modalidades:list=[]):
        if Estados.TODOS in estados:
            estados = list(Estados)[:-1]
        
        if Modalidades.TODOS in modalidades:
            modalidades = list(Modalidades)[:-1]

        return ano, estados, modalidades

    def __obter_dados_documentacao(self, pasta_temporaria:str, pasta_trabalho:str, modalidades:list, ano:str):
        # extraindo csv de documentação para as modalidades escolhidas
        url = URL_DOCUMENTACAO.format(ano)
        log.debug('Arquivo de documentacao obtido de: {}'.format(url))

        # download e extração do zip
        arquivo_documentacao = self.__download_arquivo(url, os.path.join(pasta_temporaria, url.split('/')[-1]))
        log.debug('Arquivo de documentacao salvo em: {}'.format(arquivo_documentacao))

        # extração do zip
        arquivo_layout = self.__extrair_arquivo(arquivo_documentacao, ARQUIVO_LAYOUT, pasta_temporaria)
        log.debug('Arquivo de documentacao extraído em: {}'.format(arquivo_layout))
        
        # baixando csv pelas abas de modalidade
        div_columns={}
        ibge_datasets={}

        for enum_modalidade in modalidades:
            try:
                valor_modalidade, descricao_modalidade = enum_modalidade.value

                arquivo_csv = os.path.join(pasta_trabalho, 'Documentacao_{}.csv'.format(descricao_modalidade))
                log.debug('Arquivo de documentacao convertido para csv gerado em: {}'.format(arquivo_csv))

                ibge_desc=pd.read_excel(open(arquivo_layout, 'rb'), sheet_name=valor_modalidade, header=1).dropna(how='all', axis='columns')
                ibge_desc.to_csv(arquivo_csv, encoding="utf-8-sig")

                col_specification = list(zip(ibge_desc['POSIÇÃO INICIAL']-1, ibge_desc['POSIÇÃO FINAL']))
                ibge_datasets[descricao_modalidade] = ibge_desc
                div_columns[descricao_modalidade] = col_specification

                log.info('Obtendo as informações da documentação sobre {}'.format(descricao_modalidade))
            except Exception as e:
                log.error('Erro ao acessar os dados de documentação: {}'.format(e))

        return ibge_datasets, div_columns

    def obter_dados_ibge(self, ano:enumerate, estados:list, modalidades:list, header:bool=True):
        """
        Retorna os dados do censo baseado no ano, nos estados e modalidades selecionadas. Os arquivos são salvos na pasta
        'microdados-ibge' dentro do projeto.
        \n\n
        Obs.: Se for utilizar a opção TODOS, utilize somente esta opção dentro do da lista.

        Parâmetros:
            ano (enumerate): enum do ano.
            estados (list): lista de enums com os estados.
            modalidades (list): lista de enums com as modalidades.
            header (bool): adicionar header no csv (opcional, True).
        """

        # valida os enums, caso todas as opções sejam selecionadas
        ano, estados, modalidades = self.__validar_enums(ano, estados, modalidades)

        # cria pasta temporaria no sistema
        pasta_temporaria = self.__criar_pasta_temporariaoraria()
        log.debug('Arquivos temporarios salvos em {}'.format(pasta_temporaria))
    
        # obtem a pasta de trabalho para salvar o output (csv)
        pasta_trabalho = self.__obter_diretorio_trabalho()
        log.debug('Arquivos de saída salvos em {}'.format(pasta_trabalho))
    
        # captura o ano selecionado
        valor_ano, descricao_ano = ano.value

        # dados de documentação
        ibge_datasets, div_columns = self.__obter_dados_documentacao(pasta_temporaria, pasta_trabalho, modalidades, descricao_ano)

        # extraindo csv de todos os estados selecionados pelo usuario no pacote        
        for enum_estado in estados:
            valor_estado, estado, sigla = enum_estado.value

            log.info('Baixando informações do estado de {}'.format(estado))
            
            url = URL_MICRODADOS.format(descricao_ano, sigla)
            log.debug('Arquivo referente ao estado de {} extraído de: {}'.format(estado, url))

            # download dos dados do estado
            arquivo_zip_estado = self.__download_arquivo(url, os.path.join(pasta_temporaria, url.split('/')[-1]))
            log.debug('Arquivo zip do estado salvo em: {}'.format(arquivo_zip_estado))
            
            for enum_modalidade in modalidades:
                valor_modalidade, descricao_modalidade = enum_modalidade.value

                nome_arquivo_modalidade = 'Amostra_{}_{}.txt'.format(descricao_modalidade, str(valor_estado))
                log.debug('Nome arquivo modalidade: {}'.format(nome_arquivo_modalidade))

                # extração do zip de dados do estado
                arquivo_estado = self.__extrair_arquivo(arquivo_zip_estado, nome_arquivo_modalidade, pasta_temporaria)
                log.debug('Arquivo do estado extraído em: {}'.format(arquivo_estado))

                # conversão para csv
                data = pd.read_fwf(arquivo_estado, colspecs=div_columns[descricao_modalidade])
                data.columns = ibge_datasets[descricao_modalidade]['VAR'].tolist()

                # salvando o csv
                arquivo_csv = os.path.join(pasta_trabalho, '{}_{}.csv'.format(nome_arquivo_modalidade[:-4], sigla))
                data.to_csv(arquivo_csv, encoding="utf-8-sig", header=header)

                log.info('Arquivo de {} de modalidade {} extraído'.format(sigla, descricao_modalidade))
                log.debug('Arquivo de {} de modalidade {} extraído em: {}'.format(sigla, descricao_modalidade, arquivo_csv))

        # apaga a pasta criada no diretório temporario                               
        self.__remover_pasta_temporariaoraria(pasta_temporaria)

    def obter_especificacao_coluna(self, palavra_de_busca:str, modalidades:list):
        """
        Retorna a específicação da coluna das modalidades selecionadas.\n\n
        Obs.: Se for utilizar a opção TODOS, utilize somente esta opção dentro do da lista.

        Parâmetros:
            palavra_de_busca (str): palavra para busca.
            modalidades (list): lista de enums com as modalidades.
        """

        # valida os enums, caso todas as opções sejam selecionadas
        ano, estados, modalidades = self.__validar_enums(modalidades=modalidades)

        # obtem a pasta de trabalho onde foram salvos os arquivos
        pasta_trabalho = self.__obter_diretorio_trabalho()
        log.debug('Arquivos estão salvos em {}'.format(pasta_trabalho))

        for enum_modalidade in modalidades:
            valor_modalidade, descricao_modalidade = enum_modalidade.value            

            doc = pd.read_csv(os.path.join(pasta_trabalho, 'Documentacao_{}.csv'.format(descricao_modalidade)))
            aux = doc.loc[doc['NOME'].str.contains(palavra_de_busca,case=False),['VAR','NOME']]

            for index, row in aux.iterrows():
                try:              
                    log.info('Procure por {} na modalidade de {} para: \n\n{} \n\nCom descrição da coluna de \n{}'
                        .format(row['VAR'], descricao_modalidade, row['NOME'].split(':')[0]," ".join(row['NOME'].split(':')[1:])))
                except IndexError:
                    log.error('Procure por {} na modalidade de {} para: \n\n{}\n\nCom descrição da coluna de \nsem descriçao'
                        .format(row['VAR'], descricao_modalidade, row['NOME'].split(':')[0:]))