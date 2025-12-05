# MC656: Marketplace de Livros

#### Arquitetura do Sistema

O projeto segue o padrão **Model-View-Template (MVT)** do Django. Este padrão é uma variação do MVC (Model-View-Controller) e naturalmente implementa a separação de responsabilidades em camadas. As responsabilidades no sistema são:

- **Model (Data / Data Access):** models do Django e o banco SQLite que persistem e validam os dados.  
- **View (Business Logic):** views que processam requisições, aplicam regras de negócio e orquestram operações.  
- **Template (Presentation):** templates, URLs e assets que cuidam da renderização e da interface do usuário.  

---
Além disso, o projeto é organizado segundo o princípio de **Separação de Responsabilidades (Separation of Concerns)**, de forma que cada componente tem uma responsabilidade específica:
- Models para definição de dados e regras de negócio
- Views para lógica de controle e processamento de requisições  
- Templates para apresentação
- URLs para roteamento de requisições

Esta combinação de estilos arquiteturais proporciona:
- **Escalabilidade**: Possibilidade de expansão modular
- **Testabilidade**: Componentes isolados facilitam testes unitários
- **Reusabilidade**: Módulos podem ser reutilizados em outros contextos

### Diagramas C4 da Arquitetura

A arquitetura do sistema é representada através de diagramas C4 em três níveis de abstração:

#### Nível 1 - Diagrama de Contexto
O diagrama de contexto mostra a visão geral do sistema e seus usuários principais:

![Diagrama C4 - Contexto](images/C4/C4_Context.drawio.png)

#### Nível 2 - Diagrama de Container
O diagrama de container detalha os principais componentes tecnológicos do sistema:

![Diagrama C4 - Container](images/C4/C4_Container.drawio.png)

#### Nível 3 - Diagrama de Componente
O diagrama de componente decompõe a Aplicação Web Django em seus módulos internos:

![Diagrama C4 - Componente](images/C4/C4_Component.drawio.png)

### Descrição dos Principais Componentes

#### **Accounts Component**
Módulo dedicado ao gerenciamento de usuários, incluindo landing page, cadastro, autenticação e controle de sessões. Implementa tanto interfaces web quanto APIs REST para operações de usuário.

#### **Books Component**
Responsável por todo o ciclo de vida dos livros no marketplace: cadastro, listagem, busca avançada (por título, autor e curso) e gerenciamento do catálogo. Inclui interface administrativa para gestão de conteúdo.

#### **Authentication Middleware**
Sistema de segurança que protege rotas sensíveis, gerencia sessões de usuário e implementa validações de permissão através de decorators como `@login_required` e proteção CSRF.

#### **URL Router**
Componente de roteamento que direciona requisições HTTP para os módulos apropriados, organizando tanto endpoints web quanto APIs REST de forma centralizada e hierárquica.

#### **ORM Data Layer**
Camada de abstração de dados que utiliza o Django ORM para interagir com o banco SQLite, gerenciando modelos User e Book, migrações de esquema e operações de consulta complexas.

### Books Component - Padrão de Projeto _Strategy_
Usuários podem ter expectativas diferentes ao buscar livros: podem estar interessados em um único livro cujo título é conhecido, ou em qualquer livro relacionado a alguma disciplina, ou, ainda, apenas em livros relacionados a uma disciplina escritos por um determinado autor. Para atender a essas necessidades diversas, o componente Books adota diferentes estratégias de busca dependendo do contexto da pesquisa. O usuário pode escolher um tipo de busca por meio da interface da aplicação, e o componente Books identifica o contexto correspondente a partir do request HTTP. Por enquanto, foram criadas cinco estratégia, cada uma implementando sua própria lógica de busca:
- *Title*: retorna livros cujo título corresponde à string informada pelo usuário;
- *Author*: retorna livros cujo autor corresponde à string informada pelo usuário;
- *Course*: retorna livros cujo curso ou disciplina corresponde à string informada pelo usuário;
- *Combined*: retorna livros para os quais qualquer campo (título, autor ou curso) corresponde à string informada pelo usuário;
- *Advanced*: retorna livros cujo título, autor e curso correspondem cada um a uma string diferente. Neste caso, é possível ignorar um ou mais campos informando uma string vazia (que corresponde a qualquer valor).

Essa abordagem desacopla a implementação de cada estratégia do contexto, o que simplifica a criação de novas estratégias.
