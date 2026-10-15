# -*- coding: utf-8 -*-
"""
grader.py — Sistema de correção automática do workshop de Computação Quântica.

Como funciona (e por que você NÃO consegue "colar"):
    As respostas corretas NÃO estão guardadas aqui em texto. Ficam apenas como
    hash SHA-256 no arquivo `respostas_hash.json`. Um hash é um caminho de mão
    única: dá para transformar a resposta em hash, mas é inviável fazer o
    contrário. Quando você chama `verificar(...)`, a SUA resposta é normalizada,
    transformada em hash e comparada com o gabarito.

Uso no notebook:
    from grader import verificar
    verificar("intro-3", {"0", "1"})

Tipos de resposta aceitos:
    "texto"     -> uma palavra/frase curta        ex.: "constante"
    "inteiro"   -> um número inteiro              ex.: 8
    "conjunto"  -> conjunto de strings            ex.: {"00", "11"}
    "multipla"  -> letra da alternativa           ex.: "c"
    "circuito"  -> um objeto QuantumCircuit do Qiskit
"""

import hashlib
import json
import os

_ARQUIVO_HASH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "respostas_hash.json")

try:
    with open(_ARQUIVO_HASH, "r", encoding="utf-8") as _f:
        RESPOSTAS = json.load(_f)
except FileNotFoundError:
    RESPOSTAS = {}
    print("[grader] Aviso: 'respostas_hash.json' não encontrado. "
          "Rode instrutor/gerar_grader.py para criá-lo.")

# Guarda os exercícios já resolvidos nesta sessão (apenas para o resumo).
_RESOLVIDOS = set()


# --------------------------------------------------------------------------
# Normalização: transforma respostas equivalentes na MESMA string canônica,
# para que "8", 8 e " 8 " contem como a mesma coisa.
# --------------------------------------------------------------------------
def _sha(texto):
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def _norm_texto(x):
    return " ".join(str(x).strip().lower().split())


def _norm_inteiro(x):
    return str(int(x))


def _norm_conjunto(x):
    if isinstance(x, str):
        # aceita "00, 11" ou "{00, 11}" digitado como texto
        x = x.replace("{", "").replace("}", "").replace("'", "").replace('"', "")
        x = [p for p in x.replace(",", " ").split() if p]
    itens = sorted(_norm_texto(i) for i in x)
    return "|".join(itens)


def _norm_multipla(x):
    return str(x).strip().lower().replace(")", "").replace(".", "")


def _norm_numero(x):
    """Aceita número decimal, com vírgula ou ponto, e opcional '%'. Ex.: 0,64 -> '0.64'."""
    s = str(x).strip().replace("%", "").replace(",", ".")
    return "{:.2f}".format(float(s))


def _round05_str(p):
    """Arredonda uma probabilidade para o múltiplo de 0.05 mais próximo (tolerância
    de ±0.025) e formata. Usado para comparar o RESULTADO de um circuito."""
    v = round(round(float(p) / 0.05) * 0.05, 2)
    return "{:.2f}".format(v)


def _prob_do_circuito(qc, alvo):
    """Simula o vetor de estado do circuito (sem medições) e devolve a
    probabilidade do resultado 'alvo' (uma bitstring, ex.: '1' ou '01')."""
    from qiskit.quantum_info import Statevector
    circuito = qc.remove_final_measurements(inplace=False)
    sv = Statevector.from_instruction(circuito)
    probs = {str(k): float(v) for k, v in sv.probabilities_dict().items()}
    return probs.get(str(alvo), 0.0)


def _norm_circuito(qc):
    """Canoniza a ESTRUTURA do circuito (portas + qubits), ignorando medições
    e barreiras. Ex.: estado de Bell -> 'cx(0, 1);h(0,)'."""
    linhas = []
    for instr in qc.data:
        nome = instr.operation.name
        if nome in ("measure", "barrier"):
            continue
        qidx = tuple(qc.find_bit(q).index for q in instr.qubits)
        linhas.append("{}{}".format(nome, qidx))
    linhas.sort()
    return ";".join(linhas)


_NORMALIZADORES = {
    "texto": _norm_texto,
    "inteiro": _norm_inteiro,
    "numero": _norm_numero,
    "conjunto": _norm_conjunto,
    "multipla": _norm_multipla,
    "circuito": _norm_circuito,
}


def _normalizar(tipo, resposta):
    if tipo not in _NORMALIZADORES:
        raise ValueError("Tipo de exercício desconhecido: {}".format(tipo))
    return _NORMALIZADORES[tipo](resposta)


# --------------------------------------------------------------------------
# Função principal chamada pelos participantes.
# --------------------------------------------------------------------------
def verificar(exercicio_id, resposta):
    """Verifica a resposta de um exercício e imprime o resultado.

    Retorna True se estiver correta, False caso contrário."""
    if exercicio_id not in RESPOSTAS:
        print("❓ Exercício '{}' não encontrado. Verifique o identificador."
              .format(exercicio_id))
        return False

    info = RESPOSTAS[exercicio_id]
    tipo = info["tipo"]

    try:
        if tipo == "prob":
            # Exercício funcional: simula o circuito do participante e compara a
            # PROBABILIDADE resultante (com tolerância). Assim dá para pedir "monte
            # um circuito que produza P(1)=0,25" sem revelar o ângulo da resposta.
            alvo = info.get("params", {}).get("alvo", "1")
            p = _prob_do_circuito(resposta, alvo)
            canonico = _round05_str(p)
        else:
            canonico = _normalizar(tipo, resposta)
    except Exception as erro:
        print("⚠️  Não consegui interpretar sua resposta para '{}'."
              .format(exercicio_id))
        print("    Esperado um valor do tipo '{}'. Detalhe: {}".format(tipo, erro))
        if tipo in ("circuito", "prob"):
            print("    Dica: passe o objeto do circuito, ex.: verificar('{}', qc)"
                  .format(exercicio_id))
        return False

    if _sha(canonico) == info["hash"]:
        _RESOLVIDOS.add(exercicio_id)
        print("✅ CORRETO — exercício {}".format(exercicio_id))
        print("   " + info.get("explicacao", ""))
        return True
    else:
        print("❌ AINDA NÃO — exercício {}".format(exercicio_id))
        print("   " + info.get("dica", "Revise o conceito e tente de novo."))
        print("   (Sua resposta foi lida como: {}). Tente novamente!"
              .format(repr(canonico)))
        return False


def progresso(prefixo=None):
    """Mostra um resumo dos exercícios resolvidos nesta sessão.

    Passe um prefixo (ex.: "intro") para contar apenas os exercícios daquele
    nível; sem prefixo, conta todos os exercícios carregados."""
    ids = [e for e in RESPOSTAS if prefixo is None or e.startswith(prefixo)]
    total = len(ids)
    feitos = len([e for e in _RESOLVIDOS if e in ids])
    escopo = "" if prefixo is None else " ({})".format(prefixo)
    print("📊 Progresso nesta sessão{}: {}/{} exercícios resolvidos."
          .format(escopo, feitos, total))
    if total > 0 and feitos == total:
        print("🎉 Você concluiu todos os exercícios deste nível. Parabéns!")
