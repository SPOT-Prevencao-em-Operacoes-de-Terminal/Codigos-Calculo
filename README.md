# Cálculo Computacional

Repositório acadêmico desenvolvido para a disciplina de **Cálculo Computacional**, como parte do projeto **SPOT — Sistema de Prevenção Operacional de Terminais**.

O projeto SPOT tem como objetivo desenvolver uma solução de **monitoramento contínuo da infraestrutura computacional que sustenta sistemas operacionais de terminais portuários**, acompanhando métricas como CPU, memória RAM, disco e rede.

## Objetivo

Este repositório tem como objetivo desenvolver e armazenar os **scripts responsáveis pela captura, armazenamento, análise e visualização dos dados de hardware** utilizados no projeto SPOT.

Os scripts em **Python** realizam a coleta das informações do computador por meio da biblioteca `psutil`, enquanto os scripts em **R** são utilizados para analisar os dados coletados e gerar gráficos que auxiliam na compreensão do comportamento dos componentes monitorados.

Dessa forma, o repositório representa a parte de **coleta e análise computacional dos dados** do projeto acadêmico, contribuindo para o acompanhamento do desempenho dos recursos de hardware.

## Python

Os scripts em Python são responsáveis pela captura das métricas do computador utilizando a biblioteca **psutil**.

Entre os dados coletados estão:

*  Uso da CPU;
*  Uso da memória RAM;
*  Uso do disco;
*  Dados relacionados à rede.

Os dados coletados podem ser armazenados em arquivos **CSV**, permitindo sua utilização nas etapas posteriores de análise. A documentação do projeto define o uso de Python e da biblioteca `psutil` para a captura dos dados dos componentes.

## R

Os scripts em R são utilizados para **analisar os dados coletados pelo Python e gerar gráficos**, permitindo visualizar o comportamento e o desempenho dos componentes monitorados.

Essa etapa facilita a interpretação dos dados e contribui para a identificação de padrões e alterações no funcionamento do hardware.

## Projeto acadêmico

Este repositório faz parte do desenvolvimento acadêmico do **projeto SPOT**, sendo utilizado para aplicar conhecimentos de programação, coleta de dados, análise computacional e visualização de informações.

O objetivo é colocar em prática os conceitos estudados na disciplina de **Cálculo Computacional**, utilizando dados reais do computador para realizar análises e representações gráficas.
