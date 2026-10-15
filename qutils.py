# -*- coding: utf-8 -*-
"""
qutils.py — funções auxiliares do workshop de Computação Quântica.

O objetivo é deixar o código dos notebooks limpo, escondendo detalhes
repetitivos (transpilação, leitura de resultados) sem esconder as PARTES
importantes para o aprendizado. As funções são propositalmente pequenas e
comentadas — sinta-se à vontade para abri-las e ler.
"""

from qiskit import QuantumCircuit, transpile


# ==========================================================================
# 1) SIMULAÇÃO LOCAL (ideal, sem ruído)
# ==========================================================================
def simular(qc: QuantumCircuit, shots: int = 1024) -> dict:
    """Executa o circuito num simulador local IDEAL e devolve as contagens.

    'shots' é o número de repetições da medição. Como cada medição é
    aleatória, repetimos muitas vezes para enxergar as probabilidades.
    Devolve um dicionário {resultado: quantas_vezes}, ex.: {'00': 512, '11': 512}.
    """
    from qiskit_aer import AerSimulator
    sim = AerSimulator()
    qc_transpilado = transpile(qc, sim)
    resultado = sim.run(qc_transpilado, shots=shots).result()
    return resultado.get_counts()


# ==========================================================================
# 2) SIMULAÇÃO COM RUÍDO (imita um computador quântico real)
# ==========================================================================
def simular_com_ruido(qc: QuantumCircuit, shots: int = 1024, backend_falso=None) -> dict:
    """Executa o circuito num simulador que IMITA o ruído de um chip real.

    Usa um 'fake backend' da IBM: um modelo de ruído medido de um computador
    quântico verdadeiro. Ótimo para ver o efeito do ruído sem gastar tempo
    de fila no hardware real.
    """
    from qiskit_aer import AerSimulator
    if backend_falso is None:
        from qiskit_ibm_runtime.fake_provider import FakeManilaV2
        backend_falso = FakeManilaV2()
    sim_ruidoso = AerSimulator.from_backend(backend_falso)
    qc_transpilado = transpile(qc, sim_ruidoso)
    resultado = sim_ruidoso.run(qc_transpilado, shots=shots).result()
    return resultado.get_counts()


# ==========================================================================
# 3) VISUALIZAÇÃO
# ==========================================================================
def plotar(contagens, titulo: str = "Resultados"):
    """Desenha um histograma das contagens. Aceita um dicionário ou uma
    lista de dicionários (para comparar dois resultados lado a lado)."""
    from qiskit.visualization import plot_histogram
    return plot_histogram(contagens, title=titulo)


def probabilidades(contagens: dict) -> dict:
    """Converte contagens em probabilidades (fração de cada resultado)."""
    total = sum(contagens.values())
    return {k: round(v / total, 3) for k, v in sorted(contagens.items())}


# ==========================================================================
# 4) COMPUTADOR QUÂNTICO REAL (IBM Quantum)
# ==========================================================================
def conectar_ibm(token: str = None, instance: str = None):
    """Conecta-se à IBM Quantum Platform e devolve o 'service'.

    Se você já salvou a conta em disco (veja o README), pode chamar sem
    argumentos: conectar_ibm(). Caso contrário, passe o token (API key) e,
    se necessário, o instance (CRN).

    IMPORTANTE: use o canal 'ibm_quantum_platform' (o antigo 'ibm_quantum'
    foi desativado em 1 de julho de 2025).
    """
    from qiskit_ibm_runtime import QiskitRuntimeService
    if token is None:
        return QiskitRuntimeService()  # usa a conta salva em disco
    kwargs = {"channel": "ibm_quantum_platform", "token": token}
    if instance:
        kwargs["instance"] = instance
    return QiskitRuntimeService(**kwargs)


def rodar_no_hardware(qc: QuantumCircuit, service, shots: int = 1024,
                      min_qubits: int = 2):
    """Roda o circuito num computador quântico REAL da IBM.

    Passos (os mesmos que qualquer projeto profissional faz):
      1. escolhe o computador menos ocupado (menor fila);
      2. TRANSPILA: reescreve o circuito nas portas físicas daquele chip;
      3. executa com o primitive Sampler (padrão atual do Qiskit).

    Devolve (contagens, nome_do_backend, id_do_job). Pode levar de segundos
    a alguns minutos, dependendo da fila.
    """
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
    from qiskit_ibm_runtime import SamplerV2 as Sampler

    # 1. computador real menos ocupado
    backend = service.least_busy(operational=True, simulator=False,
                                 min_num_qubits=min_qubits)
    print("Computador escolhido: {} ({} qubits)".format(backend.name, backend.num_qubits))

    # 2. transpilação para as portas físicas do chip
    pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
    circuito_isa = pm.run(qc)

    # 3. execução
    sampler = Sampler(mode=backend)
    job = sampler.run([circuito_isa], shots=shots)
    print("Job enviado! id = {}. Aguardando a fila...".format(job.job_id()))
    resultado = job.result()

    # leitura das contagens (o registrador de measure_all() se chama 'meas')
    dados = resultado[0].data
    registrador = next(iter(dados.__dict__)) if hasattr(dados, "__dict__") else "meas"
    try:
        contagens = dados.meas.get_counts()
    except AttributeError:
        contagens = getattr(dados, registrador).get_counts()
    return contagens, backend.name, job.job_id()
