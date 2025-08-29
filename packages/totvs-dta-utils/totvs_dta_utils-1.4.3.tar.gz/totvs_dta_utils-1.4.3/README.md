# Dta Utils 🧰 🛠️
**Agilize a integração entre serviços DTA**


### O que são Serviços DTA?

Uma coleção de serviços para facilitar e acelerar o desenvolvimento e monitoramento de Aplicações, com foco em aplicativos de IA generativa.


## Introdução

Esse pacote possui módulos extras que auxiliam o desenvolvimento de integrações com os serviços do DTA.

## Extra "Secrets"

### Instalação

Instale o módulo `secrets` com:
```shell
pip install "totvs-dta-utils[secrets]"
```

Ou utilizando `poetry`:
```shell
poetry add "totvs-dta-utils[secrets]"
```

### Configuração inicial:

Adicione as seguintes variaveis no `.env` do seu projeto:
```env
DTA_ENVIRONMENT="development"
DTA_INTEGRATION_URL="{DTA_INTEGRATION_URL}"
```
> NOTE: Para ambiente em cloud, onde terá acesso irrestrito aos secrets, o valor do `DTA_ENVIRONMENT`deve ser `production`.

### Utilização

```python
from dta_utils_python import DtaSecrets

auth = DTA_JWT  # CLIENT AUTHORIZATION

secrets = DtaSecrets(authorization=auth,
                     project="dta-empodera")

all_secrets = secrets.all()  # Get the latest version of all secrets
my_secret = secrets.get("MY_SECRET")  # Get the latest version of a secret
my_secret_v2 = secrets.get("MY_SECRET", version=2)  # Get a specific version of a secret
```
> Observação: Para ambiente em nuvem na rede DTA, nenhuma autenticação é necessária.

> Observação 2: Ainda em ambientes de nuvem, usando Cloud Run, lembrar de habilitar TODAS as chamadas de saída do serviço DEVEM passar pela VPC. Selecione `Route all traffic to the VPC` na configuração de Rede do serviço Cloud Run

### Demais configurações:
```python
DtaSecrets(
    authorization=auth,
    project="dta-empodera",
    raise_exception: bool = True,  # Default "False" - Levanta exceção em caso de erro ao obter a secret
    autoload: bool = False,  # Default "True" - Pré-carrega todas as secrets do projeto na inicialização da classe e as mantém em cache de memória
)
```

### Tipos de retorno:
- `.get("SECRET_2")`:
Retorna o valor da secret ou `None` caso a secret não exista.
```python
any: "321654"
```

- `.all()`:
Retorna um dicionário (hashmap) contendo a última versão de todas as secrets
```python
dict: {
    "SECRET_1": "123456",
    "SECRET_2": "321654",
    "SECRET_3": "My secret",
}
```
