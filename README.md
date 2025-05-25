<p align="center">
    <img loading="lazy" src="https://files.engaged.com.br/5db0810e95b4f900077e887e/account/5db0810e95b4f900077e887e/xMCS8NFKTMqwhefy8WLd_catolica-horizontal.png" width="300">
</p>

# Otimizando Entregas Urbanas com Inteligência Artificial

Este projeto simula um sistema de entregas urbanas em uma grade 4x4 utilizando dois agentes inteligentes que tomam decisões com base em heurísticas simples e linguagem natural. A proposta é demonstrar como técnicas de Inteligência Artificial podem ser aplicadas em cenários reais, como a logística urbana de última milha (last mile delivery).

---

## Objetivo

Criar uma simulação onde dois agentes autônomos (x e y) se movem em uma grade 4x4 tentando atingir seus destinos com o menor custo possível, evitando colisões e respeitando os limites do ambiente. A movimentação é orientada por um modelo LLM (LLaMA 3.1 8B Instant via Groq API), que analisa as opções e escolhe a melhor ação possível em cada turno.

---

## Inteligência Artificial Utilizada

- **Modelos LLM (Language Model):** Cada agente é controlado por um modelo LLM que recebe opções de movimento e decide com base na menor distância de Manhattan, evitando colisões.
- **Fallback Heurístico:** Se a resposta do modelo for inválida, uma heurística local decide a melhor jogada válida.
- **Coordenação Assíncrona:** Os dois agentes atuam alternadamente em turnos, sendo orquestrados por um agente proxy sem intervenção humana.

---

## Estrutura do Projeto

```plaintext
UrbanDeliveryAI/
├── main.py
├── .env
├── requirements.txt
├── README.md
```

---

## Tecnologias Utilizadas

- Python 3.10+
- [AutoGen](https://github.com/microsoft/autogen) (Agentes de IA interativos)
- Groq API com modelo LLaMA 3.1 8B Instant
- Bibliotecas `os`, `time`, `random`, `warnings` e `dotenv`.
- Terminal para exibição em tempo real da movimentação dos agentes

---

## Como Executar o Projeto

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/AoiteFoca/UrbanDeliveryAI.git
   cd UrbanDeliveryAI
   ```

2. **Crie e ative um ambiente virtual:**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure a API Key:**
   - Crie um arquivo `.env` na raiz do projeto.
   - Adicione sua chave da Groq:
     ```
     GROQ_API_KEY=sua_chave_groq
     ```

5. **Execute a simulação:**
   ```bash
   python main.py
   ```

   O terminal exibirá a movimentação dos agentes na grade até que ambos cheguem aos seus objetivos.

---

## Exemplo de Saída no Terminal

```
Rodada 1:
+---+---+---+---+
| . | . | . | Y |
+---+---+---+---+
| . | . | . | . |
+---+---+---+---+
| . | . | 0 | 0 |
+---+---+---+---+
| X | . | . | . |
+---+---+---+---+

Rodada 2:
+---+---+---+---+
| . | . | Y | . |
+---+---+---+---+
| . | . | . | . |
+---+---+---+---+
| X | . | 0 | 0 |
+---+---+---+---+
| . | . | . | . |
+---+---+---+---+

... São executadas mais rodadas ...

Rodada 5:
+---+---+---+---+
| . | . | X | . |
+---+---+---+---+
| . | . | . | . |
+---+---+---+---+
| Y | . | 0 | 0 |
+---+---+---+---+
| . | . | . | . |
+---+---+---+---+

Rodada 6:
+---+---+---+---+
| . | . | . | X |
+---+---+---+---+
| . | . | . | . |
+---+---+---+---+
| . | . | 0 | 0 |
+---+---+---+---+
| Y | . | . | . |
+---+---+---+---+

Entrega concluida!
```

---

## 🔍 Lógica de Decisão dos Agentes

Cada agente avalia suas quatro opções possíveis (cima, baixo, esquerda, direita) com base nos seguintes critérios:

- A nova posição está dentro dos limites da grade?
- A nova posição colide com o outro agente?
- Qual a distância de Manhattan entre a nova posição e o objetivo?

A partir desses dados, o modelo LLM decide qual direção tomar.

---

<div align="center">
<h3 align="center">Autor</h3>
<table>
  <tr>
    <td align="center"><a href="https://github.com/AoiteFoca"><img loading="lazy" src="https://avatars.githubusercontent.com/u/141975272?v=4" width="115"><br><sub>Nathan Cielusinski</sub></a></td>
  </tr>
</table>