# Computação Quântica na Prática

Workshop prático de computação quântica com [Qiskit](https://www.ibm.com/quantum/qiskit).

## Conteúdo

| Notebook | Nível | Tópicos |
|---|---|---|
| [`01_introducao_computacao_quantica.ipynb`](01_introducao_computacao_quantica.ipynb) | Introdutório | Qubit e vetor de estado, regra de Born, esfera de Bloch, portas (X, H, Rx, Ry, Rz), fase, medição e bases, produto tensorial, estado de Bell |
| [`02_intermediario.ipynb`](02_intermediario.ipynb) | Intermediário | Múltiplos qubits, estado GHZ, interferência, phase kickback, Deutsch–Jozsa, Bernstein–Vazirani, busca de Grover |
| [`03_completo.ipynb`](03_completo.ipynb) | Completo | Era NISQ, ruído e decoerência, mitigação de erros de leitura, teletransporte, amplificação de amplitude, VQE, aplicações, projeto final (GHZ de 4 qubits) |

Os notebooks são independentes, mas foram pensados para serem feitos em ordem.

## Pré-requisitos

- Python 3.10+
- Conhecimento básico de Python e álgebra linear elementar (vetores e matrizes). Nenhuma experiência prévia com computação quântica é necessária.

## Como executar

### Opção A — local

```bash
# clone o repositório e entre na pasta
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
jupyter notebook
```

Abra o notebook do nível desejado e execute as células em ordem (a primeira prepara o ambiente).

### Opção B — Google Colab

1. Abra o notebook no Colab e faça **Arquivo → Salvar uma cópia no Drive** (cada participante usa a própria cópia).
2. Rode a célula de setup no topo do notebook, que instala as dependências e baixa os arquivos de apoio (`qutils.py`, `grader.py`, `respostas_hash.json`).

## Exercícios e correção automática

Ao longo dos notebooks há exercícios verificados pela função `verificar`:

```python
from grader import verificar, progresso

verificar("intro-3", {"0", "1"})   # corrige um exercício
progresso("intro")                 # mostra quantos você já resolveu
```

O gabarito **não** fica em texto claro. O arquivo `respostas_hash.json` guarda apenas hashes SHA-256 das respostas, então é possível corrigir sem que ninguém consiga ler as soluções. Tipos de resposta aceitos: texto, inteiro, número, conjunto, múltipla escolha e circuito do Qiskit.

## Estrutura do projeto

```
├── 01_introducao_computacao_quantica.ipynb   # notebook nível introdutório
├── 02_intermediario.ipynb                    # notebook nível intermediário
├── 03_completo.ipynb                         # notebook nível completo
├── qutils.py                                 # funções auxiliares (simulação, leitura de resultados)
├── grader.py                                 # corretor automático dos exercícios
├── respostas_hash.json                       # hashes das respostas (sem gabarito em texto claro)
├── requirements.txt                          # dependências
└── instrutor/                                # material do instrutor — NÃO distribuir
    ├── gabarito.py                           # respostas em texto claro
    ├── gerar_grader.py                       # gera respostas_hash.json a partir do gabarito
    └── 01_..._RESOLVIDO.ipynb                # notebook resolvido
```

