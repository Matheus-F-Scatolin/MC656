# Benchmarking

## [Skoob](https://www.skoob.com.br)

O Skoob é uma rede social brasileira de leitores que funciona como uma estante virtual, permitindo catalogar livros, registrar leituras, trocar exemplares e interagir com a comunidade.

Nesse site, analisaremos as seguintes funcionalidades: **cadastro de novo usuário**, **página de perfil** e **ferramenta de busca em tempo real**.

---

### Documentação de Features e Funcionalidades  

#### Cadastro de novo usuário  
A tela de registro permite a criação rápida de conta com e-mail e senha, exigindo requisitos mínimos de segurança (como comprimento mínimo e validação de formato de e-mail). O fluxo é direto, sem etapas adicionais complexas, o que facilita o onboarding de novos usuários.  

![Skoob - Cadastro](images/benchmark/skoob-cadastro.png)

---

#### Página de perfil do usuário  
Na página de perfil, o usuário pode visualizar e organizar suas leituras em categorias como **lidos**, **lendo**, **quero ler**, **favoritos** e até estatísticas como **livros trocados** e **páginas lidas**. Esse recurso cria uma sensação de rede social, incentivando o engajamento pela gamificação (progresso, metas de leitura).  

![Skoob - Perfil](images/benchmark/skoob-perfil.png)

---

#### Ferramenta de busca em tempo real  
A barra de busca exibe resultados dinâmicos conforme o usuário digita, sem necessidade de pressionar *enter*. A pré-visualização mostra título, autor e capa do livro, ajudando a evitar confusões e acelerando o acesso à obra desejada.  

![Skoob - Busca](images/benchmark/skoob-busca.png)

---

### Pontos positivos e negativos  

#### Pontos Positivos:  
- Processo de cadastro rápido e intuitivo.  
- Perfil do usuário funciona como uma estante virtual, incentivando engajamento.  
- Busca dinâmica e responsiva, com pré-visualização de resultados.  

#### Pontos Negativos:  
- Interface um pouco poluída, com excesso de informações em uma mesma tela.  
- Design sem a fluidez de apps mais modernos.  
- Demora para carregar os resultados da busca e para efetuar o registro de novo usuário.

---

### Requisitos  

A partir das informações acima, temos alguns requisitos que podemos extrair da análise:  
- Criar **fluxo de cadastro simples**, mas com validações de segurança.  
- Implementar **busca em tempo real com pré-visualização**, garantindo fluidez e desempenho.  
- Adotar **design mais limpo e moderno**, evitando sobrecarga de informações.  
- Oferecer **filtros avançados** para busca de livros.  

---


## [Amazon](https://www.amazon.com.br)

A Amazon é um marketplace geral com alto volume de catálogo, mecanismos de recomendação e páginas de produto (PDP) muito completas.

Nesse site, analisaremos as seguintes funcionalidades: **catálogo / recomendações**, **barra de busca**, **resultado de busca**, **descrição do produto (PDP)**, **recomendações relacionadas**, **detalhes técnicos do produto**, **avaliações do produto** e **sistema de login**.

---

### Documentação de Features e Funcionalidades  

#### Catálogo — destaque e recomendações na homepage  
A homepage apresenta blocos com produtos recomendados (com base no histórico) e seções temáticas. Esses blocos são visualmente proeminentes e servem tanto para descoberta quanto para reengajamento.

O que observar / capturar: homepage com blocos “Compre novamente”, “Continue de onde parou”, banners promocionais.
Uso observado: recomenda produtos com base em histórico e comportamento.
UX notes: bom para incentivar a descoberta; pode poluir se houver muitas seções.

![Amazon - Catálogo](images/benchmark/amazon-catalogo.png)

---

#### Barra de busca (auto-complete / sugestões)  
A barra de busca mostra sugestões enquanto digita e resultados rápidos (pré-visualização com capa/título).

O que observar / capturar: campo de busca aberto com sugestão/preview.
Uso observado: acelera o encontro do livro pelo título/autor/termo.
UX notes: útil para evitar erros de digitação; permite acesso direto ao PDP sem precisar carregar a página de resultados. 

![Amazon - Barra de busca](images/benchmark/amazon-barra_busca.png)

---

#### Resultado de busca  
Página com lista de resultados e painel lateral de filtros (departamentos, entrega, Prime etc.). Exibe preço, avaliação e selo (ex.: Prime, mais vendido).

O que observar / capturar: lista de resultados com filtros à esquerda; ordenação e contagem de resultados.
Uso observado: usuários refinam por condição (novo/usado), preço, tempo de entrega.
UX notes: filtros poderosos — importante replicar filtros relevantes (curso, edição, condição para marketplace universitário).
  
![Amazon - Resultado da busca](images/benchmark/amazon-resultado_busca.png)

---

#### Página de detalhe do produto (PDP) — descrição e ações  
PDP concentra imagem/capas, título, autores, sinopse, formatos disponíveis (Kindle, físico), preço e botões de ação (Adicionar ao carrinho / Comprar agora). Mostra ofertas alternativas (outros vendedores/usado).

O que observar / capturar: PDP completa (imagem, sinopse, bloco de compra, “outros usados/novos”).
Uso observado: consolida informação sobre edições/formato e múltiplas ofertas.
UX notes: muito completa — ótima inspiração, porém excessiva para um fluxo de troca simples (pode confundir).

![Amazon - Página de detalhamento do produto](images/benchmark/amazon-pdp.png)

---

#### Recomendações relacionadas (frequentemente comprados juntos / vistos juntos)  
Exposição de produtos relacionados e bundles (frequentemente comprados juntos).

O que observar / capturar: seção “Frequentemente comprados juntos” e “Produtos relacionados comprados pelos clientes”.
Uso observado: promove vendas cruzadas e ajuda na descoberta de material complementar.
UX notes: útil para sugerir livros de mesma disciplina ou materiais de referência.
  
![Amazon - Recomendações relacionadas](images/benchmark/amazon-recomendacao_relacionada.png)

---

#### Detalhes técnicos do produto  
Seção com dados técnicos: ISBN-10 / ISBN-13, número de páginas, editora, dimensões, data de publicação.

O que observar / capturar: bloco “Detalhes do produto” com ISBNs e especificações.
Uso observado: importante para distinguir edições — crítico em livros acadêmicos.
UX notes: no marketplace universitário, mostrar edição/ISBN/ano deve ser prioridade (evita confusões entre edições).
  
![Amazon - Detalhes técnicos do produto](images/benchmark/amazon-detalhes_produto.png)

---

#### Avaliações do produto (estrelas, comentários e imagens)  
Sistema de classificação com barra de distribuição por estrelas, comentários textuais e imagens enviadas por compradores.

O que observar / capturar: gráfico de distribuição por estrelas, avaliações com imagens e comentários mais relevantes.
Uso observado: auxilia a confiança do comprador; imagens de usuários ajudam a avaliar a condição do item (no caso de usados).
UX notes: extremamente útil para reputação; para trocas entre alunos, incorporar avaliação do usuário e fotos da condição do livro é essencial.
  
![Amazon - Avaliação do produto](images/benchmark/amazon-avaliacao_produto.png)

---

#### Login / criação de conta  
Fluxo de login simples (e-mail/telefone) antes de prosseguir para ações críticas (contato, compra).

O que observar / capturar: tela de login/registro.
Uso observado: gating de funcionalidades (mensageria/checkout) através de conta.
UX notes: para a plataforma universitária, usar verificação institucional (email da universidade) melhora confiança/controle da comunidade.
  
![Amazon - Login / criação de conta](images/benchmark/amazon-login.png)

---

### Pontos positivos e negativos  

#### Pontos Positivos:  
- Catálogo e PDP robustos: consolidação de edições/formatos e múltiplas ofertas — inspira como mostrar alternativas (novo/usado/permuta).
- Busca e auto-complete: acelera a descoberta; pré-visualização com capa ajuda muito.
- Filtros detalhados: possibilitam refinar por entrega/condição/preço — adaptar para filtros por curso/semestre/edição.
- Avaliações ricas: estrelas + comentários + fotos aumentam confiança — muito relevante para troca de livros usados.
- Recomendações: identificam livros complementares (úteis para sugerir livros de uma mesma disciplina).
- Mensageria e conta: controle de comunicação e histórico de transações.
 
#### Pontos Negativos:  
- Excesso de elementos na PDP pode confundir usuários que buscam trocar rapidamente.
- Complexidade de fluxo de venda (Seller Central, logística, taxas) é muito além do necessário para um sistema P2P universitário.
- Dependência de infraestrutura de pagamento e logística — para trocas presenciais entre alunos, simplificar (ou deixar opcional) evita atrito.
- Privacidade / segurança: Amazon é corporativa e possui políticas; replicar sem adaptação pode trazer burocracia desnecessária para um ambiente estudantil.

---

### Requisitos  

A partir das informações acima, temos alguns requisitos que podemos extrair da análise:  
- Criar fluxo de cadastro simples, mas com verificação institucional (e-mail da universidade).
- Implementar busca em tempo real com pré-visualização (capa + título + edição).
- Oferecer filtros avançados (curso/disciplinas, condição do livro, campus/localidade, preço, disponibilidade).
- Adotar PDP simplificada para trocas (foto, edição, estado, opção “troca por”).
- Implementar mensageria interna com templates e sistema de reputação leve (estrelas + comentário + foto).
- Opção de reserva/calendário para marcar retirada no campus.
- Painel simples para cadastrar/anunciar livro com fotos e campo “troca/venda/doação”.

---


## [Acervus UNICAMP](https://acervus.unicamp.br/)

O Acervus UNICAMP é o acervo digital de obras literárias da UNICAMP. Nele, é possível visualizar novas obras, acessar periódicos e reservar obras de interesse.

Nesse site, analisaremos as seguintes funcionalidades: **sistema de busca**, **histórico de empréstimos**, **acesso à produção científica**, **acessibilidade** e **Feedback de empréstimo**.

---

### Documentação de Features e Funcionalidades 

#### Sistema de busca

O acervus UNICAMP possui um robusto sistema de busca de obras, com vários campos a serem especificados, o que facilita encontrar uma obra específica. É possível especificar o título, autoria, edição, editora, entre outros.

![Acervus - Busca](images/benchmark/acervus-filtros-busca.png)

Além disso, é possível filtrar as obras por localização, ou seja, por biblioteca, o que possibilita o usuário escolher a biblioteca de preferência.

![Acervus - Filtor Biblioteca](images/benchmark/acervus-filtro-biblio.png)

---

#### Histórico de Empréstimos

A plataforma conta com uma página, dentro do perfil, que mostra todo o histórico de empréstimo de livros, facilitando o controle de empréstimo pelo usuário e a renovação de empréstimos recorrentes.

![Acervus - Empréstimos](images/benchmark/acervus-emprestimos.png)

---

#### Acesso à produção científica

Além de livros acadêmicos e artísticos, também é possível acessar teses e papers a partir da plataforma. Isso permite o sistema abrangir uma maior diversidade de obras, e facilita o acesso de produções científicas aos usuários.

![Acervus - Produção científica](images/benchmark/acervus-prod-cientifica.png)

---

#### Acessibilidade

Um ponto importante sobre o sistema é que ele dispõe de várias opções de acessibilidade, incluindo um modo de alto contraste da página e um modo fácil de mudar o idioma da página.

![Acervus - Acessibilidade](images/benchmark/acervus-acessibilidade.png)

---

#### Feedback de empréstimo

Ao realizar um empréstimo, o usuário recebe feedback em seu e-mail, cadastrado na página de login. Os principais e-mails contém comprovante de reserva, no momento da reserva, recibo de empréstimo, recebido no momento em que a obra foi emprestada, e aviso de devolução, recebido nos dias próximos à data de devolução da obra emprestada. Esse sistema automático de feedback ajuda o usuário a acompanhar o processo de empréstimo e devolver a obra dentro do prazo.

![Acervus - Feedback](images/benchmark/acervus-feedback.png)

---

### Pontos positivos e negativos

#### Pontos positivos:
- Sistema de busca robusto, com possibilidade de alto detalhamento na busca
- Alta diversidade de obras
- Preocupação com acessibilidade
- Feedback sobre o processo de empréstimo

#### Pontos negativos:
- Exclusividade de login para discentes e doscentes da UNICAMP
- Baixa responsividade em aparelhos mobile
- Demora de atualização de obras disponíveis/reservadas

---

### Requisitos

Podemos extrair alguns requisitos a partir dos pontos levantados:
- Criar página de **histórico de empréstimos** que facilite visualização e renovação
- Adicionar opções de **acessibilidade** que facilitem o uso da plataforma, como idioma da página e modo de alto contraste
- Assegurar **responsividade** da plataforma a dispositivos mobile
- Implementar sistema automático de **feedback** sobre empréstimo, lembrando sobre prazo de devolução

---

## [Livra Livro](https://livralivro.com.br/)
O Livra Livro é uma plataforma brasileira dedicada à doação e troca de livros usados. 
O serviço é baseado em um sistema de pontos, no qual os usuários ganham pontos ao doar livros e gastam-nos para solicitar livros oferecidos por outros membros da comunidade.
Nesse site, analisaremos as seguintes funcionalidades: 
**Adição e Remoção de Livros da Estante**, **Visualização da Estante**, **Cadastro de Livro**, **Disponibilização de Livro** e **Solicitação de Livro**.

---

### Documentação de Features e Funcionalidades  

#### Adição e Remoção de Livros da Estante
Para adicionar um livro à sua estante, o usuário deve primeiro encontrar o livro desejado através da barra de busca. 
Se o livro estiver cadastrado na plataforma, basta clicar no botão "Pôr na Estante" e escolher uma das quatro tags (Quero &nbsp; ler **[sic]**, Já Li, Lendo, Abandonado).
Para removê-lo, basta clicar novamente na tag.

![Livra_Livro - por_estante](images/benchmark/livra_livro_por_estante.png)

---
#### Visualização da Estante
Para visualizar sua estante, o usuário deve abrir o menu "Livros" e clicar em "Estante".
Na estante, não há separação por tags, todos os livros adicionados são exibidos juntos. Para verificar a tag
de um livro específico, o usuário precisa abrir a página desse livro clicando em sua capa ou título. Embora exista a opção
de filtrar específicamente pelas tags "Já Li" e "Quero Ler" (por que não as outras duas?), só é possível
escolher um único filtro ou ordenação por vez. Para estantes com muitos livros, isso pode dificultar a navegação.

![Livra_Livro - estante](images/benchmark/livra_livro_estante.png)

---
#### Cadastro de Livro
Caso um livro ainda não esteja cadastrado na plataforma, o usuário pode adicioná-lo manualmente selecionando a opção "Adicionar Livro" no menu "Livros".
Para realizar o cadastro, o usuário precisa preencher apenas o IBSN do livro, e o sistema busca automaticamente as informações do livro (título, autor, capa, editora, etc.) em uma base de dados externa.
Opcionalmente, o usuário pode inserir informações adicionais, como categoria, sub-categoria e sinopse.
Uma vez que o cadastro é realizado, o livro é automaticamente adicionado ao banco de dados do LivraLivro.

![Livra_Livro - cadastro_livro](images/benchmark/livra_livro_cadastro_livro.png)

---
#### Disponibilização de Livro
Para disponibilizar um livro para doação, o usuário deve abrir a página do livro e clicar
no botão "Tenho para troca". Após marcar um checkbox confirmando que possui
o livro e o disponibilizará exclusivamente pelo LivraLivro, o usuário deve informar o estado de conservação do livro
e eventuais discrepâncias em relação às informações previamente cadastradas e, finalmente, clicar em "Adicionar".

![Livra_Livro - disponibilizar_livro](images/benchmark/livra_livro_disponibilizacao.png)

Uma vez que o livro foi disponibilizado, o usuário deve receber uma notificação quando outro usuário o solicitar.
Também é possível visualizar todos os livros disponibilizados na página "Disponíveis", acessível pelo meno "Livros". Nessa página,
é possível cancelar a disponibilização de um livro clicando no ícone de lixeira ao lado do título do livro. Apertar esse botão cancela
imediatamente a disponibilização, sem qualquer confirmação adicional.

![Livra_Livro - cancelar_disponibilizacao](images/benchmark/livra_livro_cancelar_disponibilizacao.png)    

---
#### Solicitação de Livro
Para solicitar um livro, o usuário deve acessar a página do livro desejado e, caso ele esteja disponível,
clicar no botão "Solicitar" (na busca, é possível filtrar por disponibilidade).
Em seguida, o usuário pode escolher de qual usuário deseja solicitar o livro (caso haja mais de um).
São exibidas informações sobre o dono do livro, como nome, cidade, estado e último acesso à plataforma.
Também é possível abrir o perfil completo do dono, onde são exibidas informações como avaliações e livros disponíveis.
Para concluir a solicitação, o usuário deve estabelecer uma data limite para que o dono aceite a solicitação, e clicar em "Solicitar".

![Livra_Livro - solicitar_livro](images/benchmark/livra_livro_solicitacao.png)

Caso o usuário não tenha nenhum ponto (como foi o meu caso), é exibida uma mensagem de erro, e a solitação é impedida.
Embora bem intencionado, o sistema de pontos é fundamentalmente falho, e acaba sendo um obstáculo praticamente intransponível para o uso da plataforma.
Isso porque, para ganhar pontos, o usuário precisa:
- cadastrar um livro como solicitável;
- esperar que outro usário (que tenha pontos disponíveis) solicite o livro;
- enviar o livro via correios;
- esperar o outro usuário confirmar o recebimento do livro.

Na maioria das vezes, isso significa que usuários novos nunca conseguem doar seus livros,
pois os demais usuários também não têm pontos para solicitá-los. Isso levanta a pergunta:
como novos pontos entram em circulação? Segundo as FAQs do site,
a única forma de obtê-los é concluindo uma doação e, ainda por cima, os pontos tem validade de 6 meses.
Se cada ponto ganho por um usuário é um ponto gasto por outro, e os pontos expiram, o número de pontos
em circulação tende a diminuir com o tempo, o que torna o sistema insustentável.

![Livra_Livro - solicitar_livro_sem_pontos](images/benchmark/livra_livro_sem_pontos.png)

---

### Pontos positivos e negativos
#### Pontos Positivos:
- Processo de adição de livros à estante é simples e rápido.
- A seleção de tags disponíveis parece ser razoavelmente abrangente.
- Cadastro de livros é facilitado pela busca automática de informações via IBSN.
- Exibir a localização e data do último acesso do dono do livro ajuda
a evitar solicitações para usuários inativos ou muito distantes.
- Há uma tentativa de garantir trocas justas através do sistema de pontos.

#### Pontos Negativos:
- Sistema de pontos com falhas graves.
- Falta de separação clara por tags prejudica a organização da estante.
- Remoção de livros da estante não é intuitiva (por que isso não é feito na própria estante?).
- Opções de filtragem e ordenação limitadas.

---
### Requisitos

A partir da análise feita, alguns requisitos que podem ser extraídos são:

- Implementar uma sistema de troca/doação mais flexível do que o sistema de pontos.
- Indicar a tag de cada livro da estante.
- Oferecer opções mais avançadas para organização da estante, como filtros 
e ordenações mutualmente compatíveis, e remoção de livros diretamente da estante.
- Permitir o cadastro automático de livros por ISBN.
- Exibir informações relevantes do outro usuário, como localização, avaliação e último acesso,
durante o processo de doação/troca.
