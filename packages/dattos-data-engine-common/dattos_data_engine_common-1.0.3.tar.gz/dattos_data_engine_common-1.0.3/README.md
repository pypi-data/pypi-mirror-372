# dattos data engine common

Biblioteca comum para microserviços do ecossistema Dattos Data Engine. Fornece utilitários, tipos e integrações compartilhadas entre diferentes serviços.

## Índice

- [Visão Geral](#visão-geral)
- [Instalação](#instalação)
- [Uso](#uso)
- [Exemplos](#exemplos)
- [Testes](#testes)
- [Contribuição](#contribuição)
- [Licença](#licença)
- [Contato](#contato)

## Visão Geral

Esta biblioteca centraliza funcionalidades comuns utilizadas pelos microserviços do dattos Data Engine, promovendo reutilização de código, padronização e facilidade de manutenção.

Principais recursos:

- Utilitários para manipulação de dados
- Tipos e classes Python compartilhados
- Integrações com serviços internos
- Helpers para logging, validação e tratamento de erros

## Instalação

Adicione ao seu projeto via pip:

### Instalação via PyPI

```bash
pip install dattos-data-engine-common=={version}
```

### Instalação via TestPyPI

```bash
pip install -i https://test.pypi.org/simple/ dattos-data-engine-common=={version}
```

## Uso

Importe os módulos necessários no seu serviço:

```python
from dattos_data_engine_common import exemplo_util, TipoCompartilhado

# Uso do utilitário
resultado = exemplo_util(dados)

# Uso do tipo compartilhado
item = TipoCompartilhado(...)
```

## Exemplos

### Utilizando um utilitário

```python
from dattos_data_engine_common import formatar_data

data_formatada = formatar_data(datetime.now())

print(data_formatada)
```

### Usando tipos compartilhados

```python
from dattos_data_engine_common.storage import StorageConfig, StorageProvider

storage_config = StorageConfig(
    provider=StorageProvider.Aws,
    connection_string="AccessKeyId=XXX;SecretAccessKey=XXX;BucketName=XXX"
)
```

### Utilizando StorageStrategy

```python
from dattos_data_engine_common.storage import StorageProviderFactory, StorageConfig

# Cria a configuração de storage (ajuste conforme necessário)
storage_config = StorageConfig()

# Cria a estratégia de storage apropriada a partir da configuração
storage_strategy = StorageProviderFactory.create_storage_strategy(storage_config)

# Métodos disponíveis em `storage_strategy`:
# storage_strategy.read_dataframe(path)
# storage_strategy.write_dataframe(df, path)
# storage_strategy.exists_file(path)
# storage_strategy.delete_file(path)
# storage_strategy.copy_file(source_path, target_path)
# storage_strategy.get_storage_options()
```

> **Nota:** Consulte a documentação da classe `StorageStrategy` para detalhes dos métodos disponíveis.

## Testes

Execute os testes automatizados com:

```bash
pytest
```

Ou:

```bash
python -m unittest
```

## Contribuição

Contribuições são bem-vindas! Para contribuir:

1. Fork este repositório
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas alterações (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

Consulte o arquivo [`CONTRIBUTING`](./CONTRIBUTING.md) para mais detalhes.

## Licença

Este projeto está licenciado sob a licença MIT. Veja o arquivo [LICENSE](./LICENSE) para mais informações.

## Contato

Dúvidas ou sugestões? Entre em contato pelo e-mail: [dev@dattos.com.br](mailto:dev@dattos.com.br)

---

Dattos © 2025
