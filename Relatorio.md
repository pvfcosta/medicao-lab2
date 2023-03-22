# Relatório 02 - Laboratório de Experimentação de Software

**Guilherme Luiz Carvalho Pinto**

**Pedro Vítor Felix da Costa**

---

_Curso de Engenharia de Software, Unidade Praça da Liberdade_

_Instituto de Informática e Ciências Exatas – Pontifícia Universidade de Minas Gerais (PUC MINAS), Belo Horizonte – MG – Brasil_

---
<br>

# 1. Introdução

O processo de desenvolvimento de sistemas open-source envolve contribuições de diferentes desenvolvedores, de modo que possa afetar a qualidade do interna do sistema. Para entender a influência do desenvolvimento nas características de qualidade de um software, é preciso analisar aspectos como modularidade, manutenabilidade ou legibilidade. Dessa forma, esse relatório analisa a correlação desses dois fatores considerando repositórios de código aberto do GitHub.

# 2. Hipóteses

**RQ 01. Qual a relação entre a popularidade dos repositórios e as suas características de qualidade?**

Considerando que os repositórios populares atraem a maior parte dos desenvolvedores incluindo desenvolvedores com diferentes níveis técnicos, pode-se concluir que um repositório popular possui fácil entendimento, o que indica em certos aspectos uma boa qualidade de software, pois códigos com grande grau de acoplamento e de espalhamento de mudanças possuem alta complexidade para ser entendida por desenvolvedores de qualquer nível técnico.

**RQ 02. Qual a relação entre a maturidade do repositórios e as suas características de qualidade?**

O fato do repositório ser considerado maduro envolve o tempo de sua existência, o qual considera-se que quanto maior sua idade mais tempo de trabalho envolvido e por consequência maior grau de qualidade de software. De forma que, os repositórios mais velhos possuem mais tempo de desenvolvimento aplicado para melhoria da qualidade do código quando comparado aos repositórios mais novos.

**RQ 03. Qual a relação entre a atividade dos repositórios e as suas características de qualidade?**

Considerando que o repositório que possui maior atividade realiza uma quantidade de entregas contínuas, pode-se concluir que implementam algum tipo de metodologia de ágil para o desenvolvimento do sistema, o qual também exerce influência sobre a qualidade do código, de modo que quanto maior a organização do time, maior é a organização e aspectos de qualidade do software desenvolvido pelo time.

**RQ 04. Qual a relação entre o tamanho dos repositórios e as suas características de qualidade?**

O fato do repositório ser grande envolve a alta quantidade de linhas de código e comentários contidos no mesmo, sendo que é necessário organização para manter uma quantidade alta de código entendível para mais de uma pessoa. Dessa forma, pode-se considerar que os repositórios maiores possuem maior necessidade de implementação de qualidade de código para a manutenção dos mesmos e por consequência devem se preocupar em manter aspectos de qualidade como baixo acoplamento e alta coesão entre a grande quantidade de código existente.