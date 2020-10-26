# IBGE Parser

## Visão Geral
---------------

**IBGE Parser** é uma biblioteca para a linguagem Python que tem por objetivo coletar os microdados do censo do IBGE - Instituto Brasileiro de Geografia e Estatística, disponibilizado em [Microdados IBGE](https://www.ibge.gov.br/estatisticas/sociais/populacao/25089-censo-1991-6.html?=&t=microdados) e convertê-los em arquivos CSV, facilitando o manuseio dos dados.

## Instalação

```
pip install ibge-parser
```

## Exemplos de uso

### Importando a biblioteca

`import ibgeparser`

### Obter os dados

```python
# import da classe principal
from ibgeparser.microdados import Microdados
# import dos enums para facilitar as buscas
from ibgeparser.enums import Anos, Estados, Modalidades

if __name__ == "__main__":
    # usando os unums
    ano = Anos.DEZ    
    estados = [Estados.SANTA_CATARINA, Estados.RONDONIA]
    modalidades = [Modalidades.EMIGRACAO]
    
    # instanciando a classe
    ibgeparser = Microdados()
    # obeter dados
    ibgeparser.obter_dados_ibge(ano, estados, modalidades)
```
O método `obter_dados_ibge` retorna os dados do censo no formato `.csv` das modalidades e estados solicitados. Utitlize os `enums` para selecionar corretamente as opções desejadas. Os arquivos `csv` são salvos na pasta `microdados-ibge` dentro do projeto.

#### Parâmetros
- ano: Enum.Ano
- estados: list(Enum.Estados)
- modalidades: list(Enum.Modalidades)
- (opcional: True) header: bool

### Obter especificação das colunas

```python

# import da classe principal
from ibgeparser.microdados import Microdados
# import dos enums para facilitar as buscas
from ibgeparser.enums import Modalidades

if __name__ == "__main__":
    # usando os unums
    modalidades = [Modalidades.EMIGRACAO]
    
    # instanciando a classe
    ibgeparser = Microdados()
    # especificação de coluna
    ibgeparser.obter_especificacao_coluna('palavra-chave', modalidades)
```

O método `obter_especificacao_coluna` retorna a especificação da coluna das modalidades solicitadas. Utitlize os `enums` para selecionar corretamente as opções desejadas.

#### Parâmetros
- palavra_de_busca: str
- modalidades: list(Enum.Modalidades)

## Contribuindo

O projeto IBGE Parser é mantido pela Senior Sistemas e disponibilizado como código-aberto à comunidade, estando sob a licença Apache 2.0.

### Requisitos

- Git
- Python 3

### Configuração

Configurar a _Python VirtualEnv_ e instalar as bibliotecas necessárias com o comando abaixo:

`pip install -r requirements.txt`

Mais informações sobre contribuição, como criação de _pull requests_, abertura de _issues_, etc. consultar [aqui](./CONTRIBUTING.md).