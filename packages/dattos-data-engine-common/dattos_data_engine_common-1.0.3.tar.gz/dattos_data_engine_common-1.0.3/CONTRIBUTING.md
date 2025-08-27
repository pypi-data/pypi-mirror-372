# Guia de Contribuição

Obrigado por considerar contribuir com o **dattos Data Engine Common Lib**! Este guia irá ajudá-lo a contribuir de forma eficiente e padronizada.

## Como Contribuir

1. **Fork o repositório**
2. **Crie uma branch** para sua feature ou correção:
   ```bash
   git checkout -b feature/nome-da-feature
   ```
3. **Implemente sua alteração** seguindo as diretrizes abaixo.
4. **Adicione ou atualize testes** para cobrir sua alteração.
5. **Garanta que todos os testes passem**:
   ```bash
   pytest
   ```
6. **Faça commit das alterações**:
   ```bash
   git commit -am 'chore: Descrição clara da alteração'
   ```
7. **Envie sua branch para o GitHub**:
   ```bash
   git push origin feature/nome-da-feature
   ```
8. **Abra um Pull Request** e descreva sua alteração.

## Padrões de Código

- Siga o [PEP8](https://pep8.org/) para estilo de código Python.
- Use nomes de variáveis e funções descritivos.
- Documente funções, classes e módulos com docstrings.
- Prefira tipagem estática (type hints) sempre que possível.

## Estrutura do Projeto

- **src/dattos_data_engine_common/**: Código-fonte principal da biblioteca.
- **tests/**: Testes automatizados.
- **docs/**: Documentação adicional (quando aplicável).

## Testes

- Escreva testes para novas funcionalidades ou correções.
- Utilize `pytest` ou `unittest`.
- Para rodar todos os testes:
  ```bash
  pytest
  ```
  ou
  ```bash
  python -m unittest
  ```

## Commits

- Mensagens de commit devem ser claras e concisas.
- Use o imperativo: "Adiciona suporte a novo provedor", "Corrige bug em validação", etc.

## Pull Requests

- Descreva claramente o que foi alterado e por quê.
- Relacione issues relevantes, se houver.
- Aguarde revisão de código antes do merge.

## Revisão de Código

- Feedbacks serão fornecidos via comentários no Pull Request.
- Faça ajustes conforme necessário e atualize o PR.

## Código de Conduta

- Seja respeitoso e colaborativo.
- Não serão tolerados comportamentos ofensivos ou discriminatórios.

## Dúvidas?

Abra uma issue ou envie um e-mail para [dev@dattos.com.br](mailto:dev@dattos.com.br).

---

Dattos © 2024
