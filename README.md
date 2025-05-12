
# Otimizando Entregas Urbanas com IA

## Objetivo
Este projeto tem como foco a simulação de entregas urbanas em um ambiente 4x4, utilizando dois agentes inteligentes e heurísticas simples para tomada de decisão. A proposta é demonstrar como conceitos de Inteligência Artificial podem ser aplicados em cenários reais, como a logística urbana.

## Tecnologias Utilizadas
- Python 3.10+
- VSCode
- Bibliotecas: `numpy`, `tabulate`

## Inteligência Artificial
O sistema utiliza heurísticas para escolher os melhores caminhos possíveis entre os pontos de entrega no mapa. Os agentes tomam decisões com base em custo estimado (distância de Manhattan) para otimizar o tempo de entrega.

## Estrutura do Projeto
```
UrbanDeliveryAi/
├── agents/
│   └── agent.py
├── map/
│   └── city_map.py
├── main.py
├── utils.py
├── README.md
├── requirements.txt
```

## Como Executar o projeto
- Inicie clonando o repositório para sua IDE de preferência (Estou utilizando VSCODE);
- Crie um ambiente virtual com o comando `python -m venv venv`;
- instale as dependencias pelo comando `pip install -r requirements.txt`;
- Rode o ___main.py___.

<br>

<div align="center">
<h3 align="center">Autor</h3>
<table>
  <tr>
    <td align="center"><a href="https://github.com/AoiteFoca"><img loading="lazy" src="https://avatars.githubusercontent.com/u/141975272?v=4" width="115"><br><sub>Nathan Cielusinski</sub></a></td>
  </tr>
</table>
