    # === Patch Pattern 0 stubs after class definitions ===
# ===================== PATRÓN 0: SEMILLA ONTOLÓGICA CANÓNICA =====================
import hashlib
import random
import itertools
from typing import List, Union, Optional, Tuple, Dict

PHI = 0.6180339887

def apply_ethical_constraint(vector, space_id, kb):
    # Placeholder: fetch ethical rules from KB, default to [-1, -1, -1]
    rules = getattr(kb, 'get_ethics', lambda sid: [-1, -1, -1])(space_id) or [-1, -1, -1]
    return [v ^ r if r != -1 else v for v, r in zip(vector, rules)]

def compute_ethical_signature(cluster):
    base = str([t.nivel_3[0] for t in cluster]).encode()
    return hashlib.sha256(base).hexdigest()

def golden_ratio_select(N, seed):
    step = int(max(1, round(N * PHI)))
    return [(seed + i * step) % N for i in range(3)]

def pattern0_create_fractal_cluster(
    *,
    input_data=None,
    space_id="default",
    num_tensors=3,
    context=None,
    entropy_seed=PHI,
    depth_max=3,
):
    random.seed(entropy_seed * 1e9)
    kb = FractalKnowledgeBase()
    armonizador = Armonizador(knowledge_base=kb)
    pool = TensorPoolManager()

    # 1. Generación / Importación
    tensors = []
    for i in range(num_tensors):
        if input_data and i < len(input_data):
            vec = apply_ethical_constraint(input_data[i], space_id, kb)
            tensor = FractalTensor(nivel_3=[vec])
        else:
            # If FractalTensor.random supports constraints, pass space_id; else fallback
            try:
                tensor = FractalTensor.random(space_constraints=space_id)
            except TypeError:
                tensor = FractalTensor.random()
        tensors.append(tensor)
        pool.add_tensor(tensor)

    # 2. Armonización recursiva
    def harmonize_fractal(t, depth=0):
        if depth >= depth_max:
            return t
        t.nivel_3[0] = armonizador.harmonize(t.nivel_3[0], space_id=space_id)["output"]
        # Recursively harmonize sublevels if method exists
        if hasattr(t, 'get_sublevels'):
            for sub in t.get_sublevels():
                harmonize_fractal(sub, depth + 1)
        return t

    tensors = [harmonize_fractal(t) for t in tensors]

    # 3. Selección de trío óptimo
    idx = golden_ratio_select(len(tensors), int(entropy_seed * 1e6))
    cluster = [tensors[i] for i in idx]

    # 4. Registro en KB
    signature = compute_ethical_signature(cluster)
    if hasattr(kb, 'register_pattern0'):
        kb.register_pattern0(
            space_id=space_id,
            cluster=cluster,
            entropy_seed=entropy_seed,
            ethical_hash=signature,
        )
    # Attach metadata to each tensor
    for t in cluster:
        if not hasattr(t, 'metadata') or t.metadata is None:
            t.metadata = {}
        t.metadata["ethical_hash"] = signature
        t.metadata["entropy_seed"] = entropy_seed
        t.metadata["space_id"] = space_id
    return cluster

# --- STUBS for Pattern 0 integration (to be implemented in KB and FractalTensor) ---
def _stub_get_sublevels(self):
    # Returns all sublevels (nivel_9 and nivel_27) as FractalTensor if possible
    subs = []
    if hasattr(self, 'nivel_9'):
        subs.extend([FractalTensor(nivel_3=[v]) for v in self.nivel_9])
    if hasattr(self, 'nivel_27'):
        subs.extend([FractalTensor(nivel_3=[v]) for v in self.nivel_27])
    return subs

def _stub_register_pattern0(self, space_id, cluster, entropy_seed, ethical_hash):
    # Placeholder for registering Pattern 0 cluster in KB
    if not hasattr(self, 'pattern0_registry'):
        self.pattern0_registry = {}
    self.pattern0_registry[space_id] = {
        'cluster': cluster,
        'entropy_seed': entropy_seed,
        'ethical_hash': ethical_hash,
    }

def _stub_get_ethics(self, space_id):
    # Placeholder: return default ethical rules
    return [-1, -1, -1]

# Patch stubs if not present


"""
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

'''
NO BORRAR ESTA NOTAS:
librereria trinity-3: Classes pare el nuecleo de modelo Aurora de inteligencia electronica
El nucleo hacer 3 operaciones fundamentales:
1. Obtner la inteligencia de la realcion entre los valores de las dimension de los tnensores fractales y su relacion con el contexto.
2. Almacenar la inteligencia como knowledge base que deber ser utilizar para de forma recursiva obtener la inteligencia de los tensores fractales.
3. Extender la inteligencia a nuevos tensores fractales y contextos en base a dinamicas y devolverlo como output al usuario.

PRINCIPIOS DE DESARROLLO:
1. Simplicidad, el codigo nunca debe basar en cadenas larga de if and else. Tienes que ser elegante y en todo caso bascar soluciones recusivas/Fracta.
2. Autosimilitud. El codigo debe buscar que todos los mecanimso de emergencia y aprendizaje de relgas sigan patrones similares en cada uno de sus componentes
3. Reversibilidad triple. El codigo de transcendiencia, extension y aprendizaje, debe tener la misma logica pero en direccion inversa.

Cada uno de los elementos del sistema deber usar el trigate, como atomo fundamental de la logica ternaria.

Los tensores fractales son la entrada del sistema, se analizan desde el transcenders, se analizar tensores de 3 en tres  que realiza una triple accion:

1. Obtiene la relacion entre los tensores fractales y su contexto.
2. Emerge los tensores fractales base a un nivel superior.
3. ?????


La informacion de relaciones obtenidas por el transceder pasa al extender que se encarga de reconstruir los tensores apartir de 

Una vez el tensor llega al sinteizarse en un solo tensor, pasa al extender, que realiza la extension de los tensores fractales a partir de la informacion de la KB y el tensor sintetizado.

Una vez el ciclo esta completo, se puede realizar un test de integridad y coherencia del flujo de trabajo. De eso se encarga el armonizador, un comprobando que el sistema esta armonizado y los tenosres de salida so coherentes.
Si no es asi inicia un proces de correccion o armonizacion, en el que se incia un ciclo de recurisova de prueba hasta que el sistema es coherente:
1. En primer lugar busca una correccion de los tensores fractales.
2. Si no es posible, busca una correccion de las relaciones.
3. Si no es posible, busca una correccion de los valores del sistema.

Los tensores fractales son los que aportan la inteligencia al sistema.  Esta formado por vectores ternarios de 3 dimensiones, que representan la relacion entre los valores de las dimensiones y su contexto.
Cada valor dimensional represnta la forma, la estructura y la funcion del vector.
Cada valor dimensional esta compuesto por 3trits (0, 1, None) que representan la relacion entre los valores de las dimensiones y su contexto.

Cada valor dimensional tiene una doble funcion: Por un lado representa el valor de la dimension y por otro identifica el espacion dimensional inferior.
Cada valor dimensional tiene asocidado se vector inferior. Los aximoas del espacio inferior depende de valor de la dimension superior.

La forma de tensor es 1 3 9 donde cada nivel es un vector de 3 dimensiones. Cada ima de las dimensione represtan la forma, la estructura y la funcion del elemento.



Documentacion extensas para seguir en : documentation/documentation.txt


'''



# === Reversibilidad completa en InverseEvolver (jerárquica) ===
class InverseEvolver:
    # ...existing code...
    def reconstruct_fractal(self, synthesized):
        """Reconstruye tres tensores fractales a partir de uno sintetizado (nivel 3, 9, 27)."""
        ms_key = synthesized.nivel_3[0]
        # Deducir A, B usando lógica inversa de Trigate (ejemplo simplificado)
        A, B = self.reconstruct_vectors(ms_key) if hasattr(self, 'reconstruct_vectors') else (ms_key, ms_key)
        C = [a ^ b if a is not None and b is not None else None for a, b in zip(A, B)]
        # Para niveles superiores, aplicar recursividad similar si existen
        return [FractalTensor(nivel_3=[A]), FractalTensor(nivel_3=[B]), FractalTensor(nivel_3=[C])]

# === Imputación contextual optimizada (ponderando niveles fractales) ===
def impute_none(vec, context, tensor=None):
    from statistics import mode
    result = []
    for i, v in enumerate(vec):
        if v is not None:
            result.append(v)
        else:
            col = [c[i] for c in context if c[i] is not None]
            # Añadir valores de niveles superiores si tensor está disponible
            if tensor and hasattr(tensor, 'nivel_9') and tensor.nivel_9 and i < len(tensor.nivel_9[0]):
                col.extend([x for x in tensor.nivel_9[i] if x is not None])
            result.append(mode(col) if col else 0)
    return result

# === Utilidad: Imputación contextual de None ===
from statistics import mode
def impute_none(vec, context):
    """Imputa None usando la moda de valores adyacentes en el contexto."""
    result = []
    for i, v in enumerate(vec):
        if v is not None:
            result.append(v)
        else:
            col = [c[i] for c in context if c[i] is not None]
            result.append(mode(col) if col else 0)
    return result

# === Validación centralizada de entradas ternarias ===
def validate_ternary_input(vec, expected_len=3, name="input"):
    if not isinstance(vec, (list, tuple)) or len(vec) != expected_len:
        print(f"Warning: Invalid {name}: {vec}, using default {[0]*expected_len}")
        return [0] * expected_len
    return [None if x is None else int(x) % 2 for x in vec]

# === Refactorización autosimilar del Armonizador ===
class AdjustmentStep:
    def apply(self, vec, archetype, kb=None):
        raise NotImplementedError

class MicroShift(AdjustmentStep):
    def apply(self, vec, archetype, kb=None):
        # Ejemplo: corrige un valor si difiere en 1 posición
        return [a if v is None else v for v, a in zip(vec, archetype)]

class Regrewire(AdjustmentStep):
    def apply(self, vec, archetype, kb=None):
        # Ejemplo: fuerza coincidencia si hay 2/3 iguales
        if sum(1 for v, a in zip(vec, archetype) if v == a) >= 2:
            return list(archetype)
        return vec

class Metatune(AdjustmentStep):
    def apply(self, vec, archetype, kb=None):
        # Ejemplo: si kb está presente, busca el arquetipo más cercano
        if kb is not None:
            matches = kb.find_archetype_by_ms(archetype)
            if matches:
                return matches[0]
        return vec

# === Heurísticas de selección: Golden Ratio Skip y Fibonacci Stepping ===
import math

def golden_ratio_skip_indices(N, k, trios=3):
    """Devuelve una lista de índices para formar un trío usando saltos áureos."""
    phi = (1 + math.sqrt(5)) / 2
    skip = max(1, int(N / phi))
    indices = []
    idx = k
    for _ in range(trios):
        indices.append(idx % N)
        idx = (idx + skip) % N
    return indices

def fibonacci(n):
    a, b = 1, 1
    for _ in range(n):
        a, b = b, a + b
    return a

def fibonacci_stepping_indices(N, k, trios=3, start_step=0):
    """Devuelve una lista de índices para formar un trío usando pasos de Fibonacci."""
    indices = []
    idx = k
    for i in range(start_step, start_step + trios):
        step = fibonacci(i)
        indices.append(idx % N)
        idx = (idx + step) % N
    return indices

# === Ejemplo de uso: formación de tríos con heurística ===
def formar_trio_golden(tensores, k):
    N = len(tensores)
    idxs = golden_ratio_skip_indices(N, k)
    return [tensores[i] for i in idxs]

def formar_trio_fibonacci(tensores, k, start_step=0):
    N = len(tensores)
    idxs = fibonacci_stepping_indices(N, k, start_step=start_step)
    return [tensores[i] for i in idxs]
# --- Dependencias globales ---
import numpy as np
# ===================== TRIAGE FUNCIONAL AURORA: COMPOSICIÓN Y REVERSIBILIDAD =====================

import operator


# === HOT-FIX: Utilidades de validación robusta para vectores y secuencias funcionales ===
def normalize_ternary_vector(vec, default=[0, 0, 0]):
    """Normaliza un vector a ternario de longitud 3."""
    if not isinstance(vec, (list, tuple)):
        return default.copy()
    return [
        None if x is None else int(x) if x in (0, 1) else 0
        for x in list(vec)[:3]
    ] + [0] * (3 - len(vec))

def validate_function_sequence(M, allowed_functions, max_len=2):
    """Valida que M sea una lista de listas de funciones permitidas."""
    if not isinstance(M, (list, tuple)) or len(M) != 3:
        return [[f_id] for _ in range(3)]
    return [
        list(seq)[:max_len] if isinstance(seq, (list, tuple)) and all(f in allowed_functions for f in seq) else [f_id]
        for seq in M[:3]
    ] + [[f_id]] * (3 - len(M))

def aurora_apply_sequence(val, sequence):
    """Aplica una secuencia de funciones a un valor."""
    for func in sequence:
        val = func(val)
    return val

def aurora_triage_inferencia(A, B, M):
    """Inferencia: Aplica la composición M a A y/o B y retorna el resultado emergente."""
    logger.info("Iniciando inferencia funcional", extra={'stage': 'inferencia', 'ambiguity': 0})
    allowed_functions = [f_not, f_inc, f_id]
    A = normalize_ternary_vector(A)
    B = normalize_ternary_vector(B)
    M = validate_function_sequence(M, allowed_functions)
    R = []
    for i in range(3):
        rA = aurora_apply_sequence(A[i], M[i])
        rB = aurora_apply_sequence(B[i], M[i])
        if rA is not None and rB is not None:
            R.append(rA + rB)
        else:
            R.append(0)
    logger.info(f"Inferencia completada: R={R}", extra={'stage': 'inferencia', 'ambiguity': R.count(None)})
    return R

def aurora_triage_aprendizaje(A, B, R, funciones_permitidas, max_len=2):
    """Aprendizaje: Busca una composición de funciones (por bit) que aplicada a A y B da R."""
    logger.info("Iniciando aprendizaje funcional", extra={'stage': 'aprendizaje', 'ambiguity': 0})
    import itertools
    A = normalize_ternary_vector(A)
    B = normalize_ternary_vector(B)
    R = normalize_ternary_vector(R)
    M = []
    for i in range(3):
        found = False
        for l in range(1, max_len+1):
            for seq in itertools.product(funciones_permitidas, repeat=l):
                rA = aurora_apply_sequence(A[i], seq)
                rB = aurora_apply_sequence(B[i], seq)
                if rA is not None and rB is not None and rA + rB == R[i]:
                    M.append(list(seq))
                    found = True
                    break
            if found:
                break
        if not found:
            M.append([f_id])
            logger.warning(f"No se encontró secuencia para bit {i}, usando identidad", extra={'stage': 'aprendizaje', 'ambiguity': 1})
    logger.info(f"Aprendizaje completado: M={M}", extra={'stage': 'aprendizaje', 'ambiguity': sum(len(m) for m in M)})
    return M

def aurora_triage_deduccion(M, R, known, known_is_A=True):
    """Deducción: Dado M, R y A (o B), deduce B (o A) aplicando las inversas."""
    logger.info("Iniciando deducción funcional", extra={'stage': 'deduccion', 'ambiguity': 0})
    allowed_functions = [f_not, f_inc, f_id]
    R = normalize_ternary_vector(R)
    known = normalize_ternary_vector(known)
    M = validate_function_sequence(M, allowed_functions)
    deduced = []
    for i in range(3):
        val = R[i] - aurora_apply_sequence(known[i], M[i]) if R[i] is not None and known[i] is not None else 0
        for func in reversed(M[i]):
            if hasattr(func, 'inverse'):
                val = func.inverse(val)
            else:
                logger.warning(f"No hay inversa para función en bit {i}, asumiendo identidad", extra={'stage': 'deduccion', 'ambiguity': 1})
        deduced.append(val if val in (0, 1, None) else 0)
    logger.info(f"Deducción completada: {deduced}", extra={'stage': 'deduccion', 'ambiguity': deduced.count(None)})
    return deduced

# Ejemplo de funciones ternarias simples con inversa
def f_not(x):
    return 1 - x if x in (0, 1) else 0
def f_not_inv(x):
    return 1 - x if x in (0, 1) else 0
f_not.inverse = f_not_inv

def f_inc(x):
    return (x + 1) % 2 if x in (0, 1) else 0
def f_inc_inv(x):
    return (x - 1) % 2 if x in (0, 1) else 0
f_inc.inverse = f_inc_inv

def f_id(x):
    return x
f_id.inverse = f_id

# Ejemplo de uso experimental:
# A = [1, 0, 1]
# B = [0, 1, 1]
# M = [[f_not, f_inc], [f_inc], [f_id]]
# R = aurora_triage_inferencia(A, B, M)
# M_learned = aurora_triage_aprendizaje(A, B, R, [f_not, f_inc, f_id])
# B_deduced = aurora_triage_deduccion(M, R, A, known_is_A=True)


# ===================== AUTOCURACIÓN: HOT-FIX, REAXIOMATIZACIÓN Y CONSEJO TERNARIO =====================

# Mini-test para ExpertRelator tuple return
def test_relator_returns_tuple():
    kb = FractalKnowledgeBase()
    ext = Extender(kb)
    ok, rel = ext.relator.contextualizar([1,0,1], 'default')
    assert isinstance(ok, bool)
    assert ok is False and rel is None  # vacío porque la KB está vacía
# ===============================================================================
# IMPORTS AGRUPADOS
# ===============================================================================
import random
import time
import warnings
import copy
import math
from typing import List, Dict, Any, Tuple, Optional

# === NOTA SOBRE TESTS Y CONCURRENCIA ===
# Para concurrencia real, proteger la KB con locks o usar una base de datos transaccional.
# Añadir casos de prueba unitarios (ejemplo: PyTest) para cada clase principal.

# ===============================================================================
# AURORA TRINITY-3 - ARQUITECTURA CANÓNICA COMPLETA Y REFACTORIZADA
################################################################################
# AURORA – Módulo Armonizador ##################################################
################################################################################
"""
Armonizador
===========
Complemento autosimilar para Aurora Trinity‑3 que afina 
coherencia y corrige ambigüedades a tres escalones:

1. *Vector*  – Micro‑ajusta las coordenadas Ss/Ms/MetaM.
2. *Regla*   – Re‑encamina entradas en LUT / Knowledge‑Base.
3. *Valor*   – Sintoniza parámetros globales (umbral, pesos…).

El módulo está pensado como *post‑hook* del `Extender`;
llámese después de cada reconstrucción para garantizar
consonancia.
"""
from typing import List, Tuple, Dict, Any, Optional
import itertools
import warnings
import logging

# Logger central para Aurora
logger = logging.getLogger("aurora.arq")
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(levelname)s][%(stage)s][ambig=%(ambiguity)s] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

Vector = List[Optional[int]]  # Ternary value: 0 | 1 | None

class AmbiguityScore(int):
    """Int sub‑class → permite añadir meta‑datos si hiciera falta."""
    pass

class Armonizador:
    """Afinador jerárquico que aplica **MicroShift → RegRewire → MetaTune**."""

    def __init__(self, knowledge_base=None, *,
                 tau_1: int = 1, tau_2: int = 2, tau_3: int = 3):
        self.kb = knowledge_base  # Puede ser None si sólo MicroShift
        self.tau_1, self.tau_2, self.tau_3 = tau_1, tau_2, tau_3

    @staticmethod
    def ambiguity_score(t: Vector, a: Vector) -> AmbiguityScore:
        """Suma de diferencias ternarias *ignorando* `None`."""
        if len(t) != len(a):
            raise ValueError("Vector size mismatch in ambiguity check")
        score = 0
        for x, y in zip(t, a):
            if x is None or y is None:
                score += 1
            elif x != y:
                score += 1
        return AmbiguityScore(score)

    _neighbor_mask_cache = {}
    def _microshift(self, vec: Vector, archetype: Vector) -> Vector:
        """
        Microshift recursivo con poda inteligente y logging estructurado.
        Explora vecinos ternarios de vec, buscando el de menor ambigüedad respecto a archetype.
        Early exit si score==0. Usa un set para evitar repeticiones.
        Cachea los masks de vecinos por longitud y solo explora ±1 donde hay NULLs.
        """
        seen = set()
        best = vec
        best_score = self.ambiguity_score(vec, archetype)

        def neighbor_masks(length):
            if length not in self._neighbor_mask_cache:
                masks = []
                for i in range(length):
                    mask = [0]*length
                    mask[i] = 1
                    masks.append(mask)
                self._neighbor_mask_cache[length] = masks
            return self._neighbor_mask_cache[length]

        def dfs(v):
            nonlocal best, best_score
            v_tuple = tuple(v)
            if v_tuple in seen:
                return
            seen.add(v_tuple)
            score = self.ambiguity_score(v, archetype)
            logger.debug(f"Vecino: {v} | Score: {score}", extra={'stage':'microshift','ambiguity':score})
            if score < best_score:
                best, best_score = v.copy(), score
                if best_score == 0:
                    return
            # Solo explora ±1 donde hay None
            for i in range(len(v)):
                if v[i] is not None:
                    continue
                for delta in (-1, 1):
                    nv = v.copy()
                    nv[i] = 0 if delta == -1 else 1
                    dfs(nv)

        dfs(list(vec))
        logger.info(f"Microshift final: {best} | Score: {best_score}", extra={'stage':'microshift','ambiguity':best_score})
        return best

    def _regrewire(self, vec: Vector, space_id: str = "default") -> Vector:
        """Busca todos los arquetipos candidatos y selecciona el más cercano por ambigüedad (nivel_3[0])."""
        if self.kb is None:
            return vec
        matches = self.kb._get_space(space_id).find_archetype_by_ms(vec)
        if matches:
            best_entry = min(matches, key=lambda e: self.ambiguity_score(vec, e.nivel_3[0]))
            return best_entry.nivel_3[0]
        return vec

    def _metatune(self, vec: Vector) -> Vector:
        """Ajuste grosero: si continúa ambigüedad, aplica heurística φ."""
        phi = (1 + 5 ** 0.5) / 2
        tuned = []
        for v in vec:
            if v is None:
                tuned.append(None)
            else:
                tuned.append(int(round(v / phi)) % 2)
        return tuned

    def harmonize(self, tensor: Vector, *, archetype: Vector | None = None,
                  space_id: str = "default") -> Dict[str, Any]:
        """Afinado completo. Devuelve dict con info para tracing."""
        if archetype is None:
            if self.kb is not None:
                entries = self.kb._get_space(space_id).find_archetype_by_ms(tensor)
                if entries:
                    if isinstance(entries, list):
                        archetype = entries[0].nivel_3[0]
                    elif hasattr(entries, 'nivel_3'):
                        archetype = entries.nivel_3[0]
        archetype = archetype or tensor

        vec_step1 = self._microshift(tensor, archetype)
        score1 = self.ambiguity_score(vec_step1, archetype)
        if score1 <= self.tau_1:
            return {
                "output": vec_step1,
                "stage": "vector",
                "ambiguity": int(score1),
            }

        vec_step2 = self._regrewire(vec_step1, space_id=space_id)
        score2 = self.ambiguity_score(vec_step2, archetype)
        if score2 <= self.tau_2:
            return {
                "output": vec_step2,
                "stage": "regla",
                "ambiguity": int(score2),
            }

        vec_step3 = self._metatune(vec_step2)
        score3 = self.ambiguity_score(vec_step3, archetype)
        if score3 <= self.tau_3:
            stage = "valor"
        else:
            stage = "falla_critica"
            warnings.warn("Armonizador: falla crítica – no se pudo reducir ambigüedad")
        return {
            "output": vec_step3,
            "stage": stage,
            "ambiguity": int(score3),
        }
'''
    Muy imporante:

 Principios que se deben aplicar para el desarrollo de esta libreria:

 Simplicidad, el codigo nunca debe basar en cadenas larga de if and else. Tienes que ser elegante y en todo caso bascar soluciones recusivas.
 Autosimilitud. El codigo debe buscar que todos los mecanimso de emergencia y aprendizaje de relgas sigan patrones similares en cada uno de sus componentes
 Solucion inversa. El codigo de transcendiencia y extension debe tener la misma logica pero en direccion inversa.
 
'''






# ===============================================================================
# NIVEL 1: LÓGICA FUNDAMENTAL
# ===============================================================================

class TernaryLogic:
    """
    Lógica ternaria Aurora con manejo correcto de incertidumbre.
    Implementa Honestidad Computacional propagando NULL apropiadamente.
    """
    NULL = None  # Representación canónica de NULL en Aurora

    @staticmethod
    def ternary_xor(a: Optional[int], b: Optional[int]) -> Optional[int]:
        """XOR ternario con propagación de NULL."""
        if a is TernaryLogic.NULL or b is TernaryLogic.NULL:
            return TernaryLogic.NULL
        return a ^ b

    @staticmethod
    def ternary_xnor(a: Optional[int], b: Optional[int]) -> Optional[int]:
        """XNOR ternario con propagación de NULL."""
        if a is TernaryLogic.NULL or b is TernaryLogic.NULL:
            return TernaryLogic.NULL
        return 1 if a == b else 0

# ===============================================================================
# NIVEL 2: COMPONENTES BÁSICOS DE PROCESAMIENTO
# ===============================================================================

# Inicializar las LUTs una sola vez al cargar el script
# Trigate se inicializa más adelante en el archivo

class Transcender:
    def relate_vectors(self, A: list, B: list, context: dict = None) -> list:
        """
        Calcula un vector de relación Aurora-native entre A y B, incorporando ventana de contexto y relaciones cruzadas si se proveen.
        """
        if len(A) != len(B):
            return [0, 0, 0]
        diff_vector = []
        for i in range(len(A)):
            a_val = A[i] if A[i] is not None else 0
            b_val = B[i] if B[i] is not None else 0
            diff = b_val - a_val
            # Normalize to ternary: 1 if diff > 0, 0 if diff == 0, None if diff < 0
            if diff > 0:
                diff_vector.append(1)
            elif diff == 0:
                diff_vector.append(0)
            else:
                diff_vector.append(None)
        # --- Aurora-native: ventana de contexto y relaciones cruzadas ---
        # Si context contiene 'prev' y 'next', añade relaciones cruzadas
        if context and 'prev' in context and 'next' in context:
            v_prev = context['prev']
            v_next = context['next']
            rel_cross = []
            for vp, vn in zip(v_prev, v_next):
                vp_val = vp if vp is not None else 0
                vn_val = vn if vn is not None else 0
                diff_cross = vp_val - vn_val
                if diff_cross > 0:
                    rel_cross.append(1)
                elif diff_cross == 0:
                    rel_cross.append(0)
                else:
                    rel_cross.append(None)
            # Concatenar: [diff_vector, rel_cross, A, B]
            return list(diff_vector) + list(rel_cross) + list(A) + list(B)
        return diff_vector
    """
    Componente de síntesis que implementa la síntesis jerárquica
    de Tensores Fractales completos.
    """
    def __init__(self, fractal_vector: Optional[List[int]] = None):
        self.trigate = Trigate()
        # Se guarda por si algún test antiguo lo inspecciona,
        # pero NO es obligatorio para el funcionamiento.
        self.seed_vector = fractal_vector

    def compute_vector_trio(self, A: List[int], B: List[int], C: List[int]) -> Dict[str, Any]:
        """Procesa un trío de vectores simples (operación base)."""
        M_AB, _ = self.trigate.synthesize(A, B)
        M_BC, _ = self.trigate.synthesize(B, C)
        M_CA, _ = self.trigate.synthesize(C, A)
        M_emergent, _ = self.trigate.synthesize(M_AB, M_BC)
        M_intermediate, _ = self.trigate.synthesize(M_emergent, M_CA)
        MetaM = [TernaryLogic.ternary_xor(a, b) for a, b in zip(M_intermediate, M_emergent)]
        return {'M_emergent': M_emergent, 'MetaM': MetaM}
    
        # ------------------------------------------------------------------
    #  MODO “DEEP LEARNING”  (compatibilidad con suites heredadas)
    # ------------------------------------------------------------------
    def deep_learning(
        self,
        A: List[int],
        B: List[int],
        C: List[int],
        M_emergent: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """
        • Calcula M_emergent y MetaM tal como exige el modelo Trinity-3.
        • Genera R_hipotesis = Trigate.infer(A, B, M_emergent).
        • Devuelve un diccionario con claves que los tests integrales esperan.
        """
        trio = self.compute_vector_trio(A, B, C)

        # Si el caller no aporta M_emergent, usa el calculado.
        if M_emergent is None:
            M_emergent = trio["M_emergent"]

        R_hipotesis = self.trigate.infer(A, B, M_emergent)

        return {
            "M_emergent": M_emergent,
            "MetaM":      trio["MetaM"],
            "R_hipotesis": R_hipotesis,
        }
    


    def compute_full_fractal(self, A: 'FractalTensor', B: 'FractalTensor', C: 'FractalTensor') -> 'FractalTensor':
        """
        Sintetiza tres tensores fractales en uno, de manera jerárquica y elegante.
        Prioriza una raíz de entrada válida por encima de la síntesis.
        """
        out = FractalTensor.neutral()

        def synthesize_trio(vectors: list) -> list:
            # Only use first 3 elements of each vector
            while len(vectors) < 3:
                vectors.append([0, 0, 0])
            trimmed = [v[:3] if isinstance(v, (list, tuple)) else [0,0,0] for v in vectors[:3]]
            r = self.compute_vector_trio(*trimmed)
            m_emergent = r.get('M_emergent', [0, 0, 0])
            return [bit if bit is not None else 0 for bit in m_emergent[:3]]

        inter_from_27 = []
        for i in range(27):
            context = {'prev': A.nivel_27[i - 1] if i > 0 else [0,0,0], 'next': A.nivel_27[i + 1] if i < 26 else [0,0,0]}
            enriched_a = self.relate_vectors(A.nivel_27[i], B.nivel_27[i], context)[:3]
            enriched_b = self.relate_vectors(B.nivel_27[i], C.nivel_27[i], context)[:3]
            enriched_c = self.relate_vectors(C.nivel_27[i], A.nivel_27[i], context)[:3]
            inter_from_27.append(synthesize_trio([enriched_a, enriched_b, enriched_c]))
        out.nivel_27 = inter_from_27

        inter_from_9 = [synthesize_trio(inter_from_27[i:i+3]) for i in range(0, 27, 3)]
        out.nivel_9 = inter_from_9
        out.nivel_3 = [synthesize_trio(inter_from_9[i:i+3]) for i in range(0, 9, 3)]

        # Ensure all nivel_3 vectors are length 3
        out.nivel_3 = [v[:3] if isinstance(v, (list, tuple)) else [0,0,0] for v in out.nivel_3]

        input_roots = [t.nivel_3[0] for t in (A, B, C) if hasattr(t, 'nivel_3') and t.nivel_3 and t.nivel_3[0] and len(t.nivel_3[0]) == 3]
        valid_roots = [r for r in input_roots if all(bit is not None for bit in r)]
        if valid_roots:
            final_root = [0, 0, 0]
            for i in range(3):
                votes = [r[i] for r in valid_roots]
                final_root[i] = 1 if votes.count(1) > votes.count(0) else 0
            out.nivel_3[0] = final_root
            out.Ms = final_root
        return out

# ===============================================================================
# NIVEL 3: ESTRUCTURAS DE DATOS Y CONOCIMIENTO
# ===============================================================================

class FractalTensor:
    """
    Representa un tensor fractal con 3 niveles de profundidad (3, 9, 27).
    """



    def __init__(
        self,
        nivel_3=None,
        nivel_9=None,
        nivel_27=None,
        *,
        Ms=None,
        Ss=None,
        dMs=None
    ):
        def norm3(v):
            # Normalize a vector to length 3, fill with 0 if needed
            if not isinstance(v, (list, tuple)):
                return [0, 0, 0]
            return [(0 if x is None else int(x) if x in (0, 1) else 0) for x in list(v)[:3]] + [0] * (3 - len(v))

        def expand_nivel_3(n3):
            # Always returns a list of 3 vectors of length 3
            if not isinstance(n3, (list, tuple)) or len(n3) == 0:
                return [[0, 0, 0] for _ in range(3)]
            if len(n3) == 1 and isinstance(n3[0], (list, tuple)) and len(n3[0]) == 3:
                # If only one vector, repeat it
                return [list(n3[0]) for _ in range(3)]
            return [norm3(v) for v in list(n3)[:3]] + [[0, 0, 0]] * (3 - len(n3))

        def expand_nivel_9(n9):
            # Always returns a list of 9 vectors of length 3
            if not isinstance(n9, (list, tuple)) or len(n9) == 0:
                return [[0, 0, 0] for _ in range(9)]
            # If only one vector, repeat it
            if len(n9) == 1 and isinstance(n9[0], (list, tuple)) and len(n9[0]) == 3:
                return [list(n9[0]) for _ in range(9)]
            return [norm3(v) for v in list(n9)[:9]] + [[0, 0, 0]] * (9 - len(n9))

        def expand_nivel_27(n27):
            # Always returns a list of 27 vectors of length 3
            if not isinstance(n27, (list, tuple)) or len(n27) == 0:
                return [[0, 0, 0] for _ in range(27)]
            if len(n27) == 1 and isinstance(n27[0], (list, tuple)) and len(n27[0]) == 3:
                return [list(n27[0]) for _ in range(27)]
            return [norm3(v) for v in list(n27)[:27]] + [[0, 0, 0]] * (27 - len(n27))

        # If only nivel_3 is provided, expand to all levels
        if nivel_3 is not None and (nivel_9 is None and nivel_27 is None):
            n3 = expand_nivel_3(nivel_3)
            n9 = [list(n3[i // 3]) for i in range(9)]
            n27 = [list(n3[i // 9]) for i in range(27)]
        elif nivel_9 is not None and nivel_27 is None:
            n9 = expand_nivel_9(nivel_9)
            n3 = [list(n9[i * 3]) for i in range(3)]
            n27 = [list(n9[i // 3]) for i in range(27)]
        elif nivel_27 is not None:
            n27 = expand_nivel_27(nivel_27)
            n9 = [list(n27[i * 3]) for i in range(9)]
            n3 = [list(n27[i * 9]) for i in range(3)]
        else:
            n3 = expand_nivel_3(nivel_3)
            n9 = expand_nivel_9(nivel_9)
            n27 = expand_nivel_27(nivel_27)

        self.nivel_3 = n3
        self.nivel_9 = n9
        self.nivel_27 = n27

        self.Ms  = Ms if Ms is not None else (self.nivel_3[0] if self.nivel_3 and isinstance(self.nivel_3[0], (list, tuple)) and len(self.nivel_3[0]) == 3 else [0,0,0])
        self.Ss  = Ss
        self.dMs = dMs

    @staticmethod
    def random():
        """Crea un FractalTensor aleatorio."""
        rand_vec = lambda: [random.choice([0, 1]) for _ in range(3)]
        return FractalTensor(
            nivel_3=[rand_vec() for _ in range(3)],
            nivel_9=[rand_vec() for _ in range(9)],
            nivel_27=[rand_vec() for _ in range(27)]
        )

    @staticmethod
    def neutral():
        """Crea un FractalTensor neutro (ceros)."""
        zero_vec = lambda: [0, 0, 0]
        return FractalTensor(
            nivel_3=[zero_vec() for _ in range(3)],
            nivel_9=[zero_vec() for _ in range(9)],
            nivel_27=[zero_vec() for _ in range(27)]
        )

    def __repr__(self):
        def short(vs):
            return vs[:2] + ['...'] if len(vs) > 2 else vs
        return (f"FT(root={self.nivel_3}, "
                f"mid={short(self.nivel_9)}, "
                f"detail={short(self.nivel_27)})")

# ===============================================================================
# NIVEL 4: MOTOR DE ABSTRACCIÓN Y APRENDIZAJE (EVOLVER)
# ===============================================================================

class Evolver:
    """
    Motor de visión fractal unificada para Arquetipos, Dinámicas y Relatores.
    """
    def __init__(self):
        self.base_transcender = Transcender()

    def _perform_full_tensor_synthesis(self, tensors: List["FractalTensor"]) -> "FractalTensor":
        """
        Motor de síntesis fractal: reduce una lista de tensores a uno solo.
        """
        if not tensors:
            return FractalTensor.neutral()
        
        current_level_tensors = list(tensors)
        while len(current_level_tensors) > 1:
            next_level_tensors = []
            for i in range(0, len(current_level_tensors), 3):
                trio = current_level_tensors[i:i+3]
                while len(trio) < 3:
                    trio.append(FractalTensor.neutral())
                synthesized_tensor = self.base_transcender.compute_full_fractal(*trio)
                next_level_tensors.append(synthesized_tensor)
            current_level_tensors = next_level_tensors
            
        return current_level_tensors[0]

    def compute_fractal_archetype(self, tensor_family: List["FractalTensor"]) -> "FractalTensor":
        """Perspectiva de ARQUETIPO: Destila la esencia de una familia de conceptos."""
        if len(tensor_family) < 2:
            warnings.warn("Se requieren al menos 2 tensores para computar un arquetipo.")
            return FractalTensor.neutral() if not tensor_family else tensor_family[0]
        return self._perform_full_tensor_synthesis(tensor_family)

    def analyze_fractal_dynamics(
        self,
        temporal_sequence: List["FractalTensor"]
    ) -> "FractalTensor":
        """
        Perspectiva de DINÁMICA: Sintetiza el patrón de evolución de una secuencia
        y calcula el gradiente lógico dMs = Ms_fin XOR Ms_ini.
        """
        if len(temporal_sequence) < 2:
            warnings.warn(
                "Se requiere una secuencia de al menos 2 tensores para analizar dinámicas."
            )
            return (
                FractalTensor.neutral()
                if not temporal_sequence
                else temporal_sequence[0]
            )

        # ---------- síntesis de la secuencia (lo que ya hacías) ----------
        tensor_dyn = self._perform_full_tensor_synthesis(temporal_sequence)

        # ---------- ➊  nuevo: calcular y guardar dMs ----------
        Ms_ini = temporal_sequence[0].Ms or temporal_sequence[0].nivel_3[0]
        Ms_fin = temporal_sequence[-1].Ms or temporal_sequence[-1].nivel_3[0]
        dMs    = [a ^ b for a, b in zip(Ms_ini, Ms_fin)]

        tensor_dyn.dMs = dMs          # gradiente temporal
        tensor_dyn.Ms  = Ms_fin       # Ms más reciente
        tensor_dyn.nivel_3[0] = Ms_fin    # coherencia con la raíz

        return tensor_dyn

    def analyze_fractal_relations(self, contextual_cluster: List["FractalTensor"]) -> "FractalTensor":
        """Perspectiva de RELATOR: Obtiene el mapa conceptual de un clúster."""
        if len(contextual_cluster) < 2:
            warnings.warn("Se requieren al menos 2 tensores para el análisis relacional.")
            return FractalTensor.neutral() if not contextual_cluster else contextual_cluster[0]
        return self._perform_full_tensor_synthesis(contextual_cluster)
        
    @staticmethod
    def fractal_relate(tensor_group: List["FractalTensor"], level: int = 27) -> Optional[List[List[Optional[int]]]]:
        """
        Calcula una firma relacional por mayoría de votos entre un grupo de tensores.
        """
        if not tensor_group:
            return None

        # Seleccionar el nivel correcto del tensor
        try:
            dim_vectors = [getattr(t, f'nivel_{level}') for t in tensor_group]
        except AttributeError:
            raise ValueError(f"El nivel {level} no es válido. Debe ser 3, 9 o 27.")

        num_vectors = len(dim_vectors[0])
        signature = []
        for pos in range(num_vectors):
            bit_result = []
            for bit in range(3): # Asume vectores de 3 bits
                bit_vals = [t[pos][bit] for t in dim_vectors if t and t[pos] and t[pos][bit] is not None]
                if not bit_vals:
                    bit_result.append(None)
                    continue
                
                # Lógica de mayoría ternaria
                count_1 = bit_vals.count(1)
                count_0 = bit_vals.count(0)
                if count_1 > count_0: bit_result.append(1)
                elif count_0 > count_1: bit_result.append(0)
                else: bit_result.append(None)
            signature.append(bit_result)
        return signature

# ===============================================================================
# NIVEL 5: BASE DE CONOCIMIENTO Y EXTENSIÓN
# ===============================================================================

class _SingleUniverseKB:
    """Gestiona el conocimiento de un único espacio lógico (universo)."""
    def __init__(self):
        self.archetypes = []
        self.ms_index = {}
        self.name_index = {}
        self.coherence_violations = 0
        self.ss_index = {}
        self.models = {}  # Nuevo: modelos genéricos

    def store_model(self, model_name: str, model_data: dict):
        """Almacena un modelo de decisión genérico en este universo."""
        self.models[model_name] = model_data
        return True

    def get_model(self, model_name: str) -> Optional[dict]:
        """Recupera un modelo de decisión."""
        return self.models.get(model_name)

    def add_archetype(self, archetype_tensor: "FractalTensor", Ss: List[int], name: Optional[str] = None, **kwargs) -> bool:
        """Añade un arquetipo (Tensor Fractal) al universo, almacenando Ss (memoria factual)."""
        if not isinstance(archetype_tensor, FractalTensor):
            raise ValueError("La entrada debe ser un objeto FractalTensor.")
        # Normalize keys to int(0 if x is None else x) for robust lookup
        ms_key = tuple(int(0 if x is None else x) for x in archetype_tensor.nivel_3[0][:3])
        # Robustly flatten Ss if it is a list of lists (e.g., [[0,1,1], ...])
        ss_source = Ss
        if isinstance(Ss, list) and len(Ss) > 0 and isinstance(Ss[0], list):
            ss_source = Ss[0]
        ss_key = tuple(int(0 if x is None else x) for x in (ss_source[:3] if ss_source else archetype_tensor.nivel_3[0][:3]))
        # Permitir múltiples arquetipos por clave Ms/Ss
        if name and name in self.name_index:
            warnings.warn(f"Violación de Coherencia: Ya existe un arquetipo con el nombre '{name}'. No se añadió el nuevo.")
            self.coherence_violations += 1
            return False
        metadata = kwargs.copy()
        if name: metadata['name'] = name
        setattr(archetype_tensor, 'metadata', metadata)
        setattr(archetype_tensor, 'timestamp', time.time())
        setattr(archetype_tensor, 'Ss', list(ss_key))
        self.archetypes.append(archetype_tensor)
        if ms_key not in self.ms_index:
            self.ms_index[ms_key] = []
        self.ms_index[ms_key].append(archetype_tensor)
        if ss_key not in self.ss_index:
            self.ss_index[ss_key] = []
        self.ss_index[ss_key].append(archetype_tensor)
        if name: self.name_index[name] = archetype_tensor
        return True

    def find_archetype_by_ms(self, Ms_query: List[int]) -> list:
        """Busca arquetipos por su clave Ms (vector raíz, normalizado a 3 ints). Devuelve siempre lista."""
        res = self.ms_index.get(tuple(Ms_query[:3]))
        if res is None:
            return []
        if isinstance(res, list):
            return res
        return [res]

    def find_archetype_by_ss(self, Ss_query: List[int]) -> list:
        """Busca arquetipos por su clave Ss (memoria factual, normalizado a 3 ints). Devuelve siempre lista."""
        res = self.ss_index.get(tuple(Ss_query[:3]))
        if res is None:
            return []
        if isinstance(res, list):
            return res
        return [res]

    def find_archetype_by_name(self, name: str) -> Optional["FractalTensor"]:
        """Busca un arquetipo por su nombre asignado."""
        return self.name_index.get(name)

    def register_patch(self, ms_key, ttl=10_000):
        """Registra un parche temporal para un vector raíz con TTL."""
        if not hasattr(self, '_patches'):
            self._patches = {}
        self._patches[tuple(ms_key)] = {'ttl': ttl, 'timestamp': time.time()}

    def supersede_axiom(self, ms_key, new_axiom):
        """Reemplaza el axioma raíz y versiona el anterior."""
        if not hasattr(self, '_axiom_versions'):
            self._axiom_versions = {}
        old = self.ms_index.get(tuple(ms_key))
        if old:
            self._axiom_versions[tuple(ms_key)] = old
        self.ms_index[tuple(ms_key)] = new_axiom
        # También actualizar en archetypes si está
        for i, t in enumerate(self.archetypes):
            if t.nivel_3[0] == list(ms_key):
                self.archetypes[i] = new_axiom
                break

class FractalKnowledgeBase:
    def add_archetype(self, space_id: str, name: str, archetype_tensor: "FractalTensor", Ss: list, **kwargs) -> bool:
        """Delegado: añade un arquetipo fractal al universo correcto."""
        return self._get_space(space_id).add_archetype(archetype_tensor, Ss, name=name, **kwargs)
    
    def get_archetype(self, space_id: str, name: str) -> Optional["FractalTensor"]:
        """Obtiene un arquetipo por space_id y nombre."""
        return self._get_space(space_id).find_archetype_by_name(name)
    
    def store_model(self, space_id: str, model_name: str, model_data: dict):
        return self._get_space(space_id).store_model(model_name, model_data)

    def get_model(self, space_id: str, model_name: str):
        return self._get_space(space_id).get_model(model_name)
    """Gestor de múltiples universos de conocimiento fractal."""


    def __init__(self):
        self.universes = {}

    def _get_space(self, space_id: str = 'default'):
        if space_id not in self.universes:
            self.universes[space_id] = _SingleUniverseKB()
        return self.universes[space_id]

    


 # ===================== MÓDULO DE EVOLVER INVERSO =====================
class InverseEvolver:
    def __init__(self):
        self.trigate = Trigate()

    def infer_inputs_from_meta(self, Ms: list, MetaM: list) -> list:
        """
        Dado Ms (emergente) y MetaM, deduce M_AB, M_BC, M_CA compatibles.
        """
        M_intermediate = [TernaryLogic.ternary_xor(m, mm) for m, mm in zip(Ms, MetaM)]
        # Heurística simple: replicamos M_AB = M_BC = M_CA = M_intermediate
        return [M_intermediate, M_intermediate, M_intermediate]

    def reconstruct_vectors(self, Ms: list) -> tuple:
        """
        Deduce todas las combinaciones posibles de A y B que generan Ms usando lógica inversa del Trigate.
        Selecciona la combinación con menor cantidad de valores None.
        """
        import itertools, warnings
        if not isinstance(Ms, list) or len(Ms) != 3:
            Ms = [0, 0, 0]  # Normalizar entrada inválida
        possible_pairs = []
        states = [0, 1, None]
        # Explorar todas las combinaciones de A y B
        for a in itertools.product(states, repeat=3):
            a = list(a)
            # Deducir B desde A y Ms usando LUT
            b = [self.trigate._LUT_DEDUCE_B.get((a_i, 1, m), None) for a_i, m in zip(a, Ms)]
            if all(x is not None for x in b):  # Solo aceptar si B es válido
                none_count = a.count(None) + b.count(None)
                possible_pairs.append((a, b, none_count))
        if not possible_pairs:
            warnings.warn("No se encontraron combinaciones válidas para Ms. Devolviendo valores neutros.")
            return [0, 0, 0], [0, 0, 0]
        # Seleccionar la pareja con menor cantidad de None (criterio de simplicidad)
        best_pair = min(possible_pairs, key=lambda x: x[2])
        return list(best_pair[0]), list(best_pair[1])

# ===================== NUEVO EXTENDER: CONSEJO DE EXPERTOS =====================

class Extender:
    """
    Orquestador Aurora refactorizado con expertos como métodos internos para
    simplificar el alcance y la gestión de estado.

    Opera como de forma inversa a Evolver, extendiendo el conocimiento fractal
    a partir de consultas simples y contexto, utilizando expertos para validar, 
    utiliza trigate de form inversa al transcender.
    """
    def __init__(self, knowledge_base: "FractalKnowledgeBase"):
        self.kb = knowledge_base
        self.transcender = Transcender()  # El relator necesita un transcender
        self._lut_tables = {}
        self.armonizador = Armonizador(knowledge_base=self.kb)

    # --- Experto Arquetipo como método ---
    def _validate_archetype(self, ss_query: list, space_id: str) -> Tuple[bool, Optional['FractalTensor']]:
        universe = self.kb._get_space(space_id)
        ss_key = tuple(int(x) if x in (0, 1) else 0 for x in ss_query[:3])
        print(f"DEBUG: Looking up archetype with ss_key={ss_key} in space={space_id}")
        # Buscar por Ss
        archi_ss = universe.find_archetype_by_ss(list(ss_key))
        if archi_ss:
            print(f"DEBUG: Found archetype by Ss: {archi_ss}")
            return True, archi_ss
        # Buscar por Ms
        archi_ms = universe.find_archetype_by_ms(list(ss_key))
        if archi_ms:
            print(f"DEBUG: Found archetype by Ms: {archi_ms}")
            return True, archi_ms
        print("DEBUG: No archetype found")
        return False, None

    # --- Experto Dinámica como método ---
    def _project_dynamics(self, ss_query: list, space_id: str) -> Tuple[bool, Optional['FractalTensor']]:
        universe = self.kb._get_space(space_id)
        best, best_sim = None, -1.0
        for archetype in universe.archetypes:
            dMs = getattr(archetype, 'dMs', None)
            if dMs and getattr(archetype, 'Ss', None):
                sim = sum(1 for a, b in zip(archetype.Ss, ss_query) if a == b) / len(ss_query)
                if sim > best_sim:
                    best_sim, best = sim, archetype
        if best and best_sim > 0.7:
            return True, best
        return False, None

    # --- Experto Relator como método ---
    def _contextualize_relations(self, ss_query: list, space_id: str) -> Tuple[bool, Optional['FractalTensor']]:
        universe = self.kb._get_space(space_id)
        if not universe.archetypes:
            print("DEBUG: No archetypes in universe")
            return False, None
        best, best_score = None, float('-inf')
        for archetype in universe.archetypes:
            if not getattr(archetype, 'Ss', None):
                continue
            rel = self.transcender.relate_vectors(ss_query, archetype.Ss)
            score = sum(1 for bit in rel if bit == 0)
            if score > best_score:
                best_score, best = score, archetype
        if best:
            # Create a deep copy to avoid modifying the original
            result = copy.deepcopy(best)
            result.nivel_3[0] = list(ss_query[:3])  # Explicitly preserve root
            print(f"DEBUG: Contextualized with score={best_score}, root preserved={result.nivel_3[0]}")
            return True, result
        print("DEBUG: No relational match found")
        return False, None

    # --- Orquestador Principal ---
    def extend_fractal(self, input_ss, contexto: dict) -> dict:
        log = [f"Extensión Aurora: espacio '{contexto.get('space_id', 'default')}'"]
        # Validación y normalización de ss_query
        if isinstance(input_ss, FractalTensor):
            ss_query = getattr(input_ss, 'Ss', input_ss.nivel_3[0])
        else:
            ss_query = input_ss
        # Normalizar a un vector ternario de longitud 3
        if not isinstance(ss_query, (list, tuple, np.ndarray)):
            log.append("⚠️ Entrada inválida, usando vector neutro [0,0,0]")
            ss_query = [0, 0, 0]
        else:
            ss_query = [
                None if x is None else int(x) if x in (0, 1) else 0
                for x in list(ss_query)[:3]
            ] + [0] * (3 - len(ss_query))
        space_id = contexto.get('space_id', 'default')
        STEPS = [
            lambda q, s: (self.lookup_lut(s, q) is not None, self.lookup_lut(s, q)),
            self._validate_archetype,
            self._project_dynamics,
            self._contextualize_relations
        ]
        METHODS = [
            "reconstrucción por LUT",
            "reconstrucción por arquetipo (axioma)",
            "proyección por dinámica (raíz preservada)",
            "contextualización por relator (raíz preservada)"
        ]
        for step, method in zip(STEPS, METHODS):
            ok, tensor = step(ss_query, space_id)
            if ok and tensor is not None:
                log.append(f"✅ {method}.")
                # Si tensor es lista, seleccionar el más cercano
                if isinstance(tensor, list):
                    armonizador = self.armonizador
                    tensor = min(tensor, key=lambda t: armonizador.ambiguity_score(ss_query, t.nivel_3[0]))
                # For dynamic/relator, preserve root
                if method.startswith("proyección") or method.startswith("contextualización"):
                    result = copy.deepcopy(tensor)
                    result.nivel_3[0] = ss_query
                    root_vector = result.nivel_3[0]
                    harm = self.armonizador.harmonize(root_vector, archetype=root_vector, space_id=space_id)
                    result.nivel_3[0] = harm["output"]
                    return {
                        "reconstructed_tensor": result,
                        "reconstruction_method": method + " + armonizador",
                        "log": log
                    }
                tensor_c = copy.deepcopy(tensor)
                root_vector = tensor_c.nivel_3[0]
                harm = self.armonizador.harmonize(root_vector, archetype=root_vector, space_id=space_id)
                tensor_c.nivel_3[0] = harm["output"]
                return {
                    "reconstructed_tensor": tensor_c,
                    "reconstruction_method": method + " + armonizador",
                    "log": log
                }
        # Fallback
        log.append("🤷 No se encontraron coincidencias. Devolviendo tensor neutro.")
        tensor_n = FractalTensor.neutral()
        root_vector = tensor_n.nivel_3[0]
        harm = self.armonizador.harmonize(root_vector, archetype=root_vector, space_id=space_id)
        tensor_n.nivel_3[0] = harm["output"]
        return {
            "reconstructed_tensor": tensor_n,
            "reconstruction_method": "tensor neutro (sin coincidencias) + armonizador",
            "log": log
        }

    # --- LUT methods moved into Extender as proper methods ---
    def lookup_lut(self, space_id: str, ss_query: list):
        """
        Consulta la LUT para el espacio dado y la firma ss_query.
        """
        lut = getattr(self, '_lut_tables', {}).get(space_id, None)
        if lut is None:
            return None
        key = tuple(ss_query)
        return lut.get(key, None)

    def learn_lut_from_data(self, space_id: str, data: list):
        """
        Aprende una LUT auto-didacta a partir de datos [(ss_query, tensor_result)].
        Si hay conflicto, usa voto por mayoría.
        """
        lut = {}
        votes = {}
        for ss_query, tensor_result in data:
            # Ensure key is always a tuple of ints (flatten if needed)
            if isinstance(ss_query, list) and len(ss_query) > 0 and isinstance(ss_query[0], list):
                key = tuple(ss_query[0])
            else:
                key = tuple(ss_query)
            if key not in votes:
                votes[key] = []
            votes[key].append(tensor_result)
        # Votar por mayoría (por nivel_3[0])
        for key, tensors in votes.items():
            # Si solo hay uno, usarlo
            if len(tensors) == 1:
                lut[key] = tensors[0]
            else:
                # Votar por mayoría en nivel_3[0]
                root_votes = [t.nivel_3[0] if hasattr(t, 'nivel_3') else t for t in tensors]
                # Simple: moda por componente
                majority = []
                for i in range(3):
                    vals = [rv[i] for rv in root_votes if rv and len(rv) > i]
                    if vals:
                        count_1 = vals.count(1)
                        count_0 = vals.count(0)
                        if count_1 > count_0:
                            majority.append(1)
                        elif count_0 > count_1:
                            majority.append(0)
                        else:
                            majority.append(None)
                    else:
                        majority.append(None)
                # Crear tensor neutro y ponerle la raíz votada
                tensor_majority = FractalTensor.neutral()
                tensor_majority.nivel_3[0] = majority
                lut[key] = tensor_majority
        self.patch_lut(space_id, lut)
        return lut

    def patch_lut(self, space_id, lut):
        """Actualiza o crea la LUT para el espacio dado."""
        if not hasattr(self, '_lut_tables') or self._lut_tables is None:
            self._lut_tables = {}
        self._lut_tables[space_id] = lut

    def vote_candidates(self, candidates: list):
        """
        Vota entre varios tensores candidatos y devuelve el tensor con mayoría en la raíz.
        """
        if not candidates:
            return FractalTensor.neutral()
        root_votes = [c.nivel_3[0] if hasattr(c, 'nivel_3') else c for c in candidates]
        majority = []
        for i in range(3):
            vals = [rv[i] for rv in root_votes if rv and len(rv) > i]
            if vals:
                count_1 = vals.count(1)
                count_0 = vals.count(0)
                if count_1 > count_0:
                    majority.append(1)
                elif count_0 > count_1:
                    majority.append(0)
                else:
                    majority.append(None)
            else:
                majority.append(None)
        tensor_majority = FractalTensor.neutral()
        tensor_majority.nivel_3[0] = majority
        return tensor_majority

# Move these expert classes to top-level scope
class ExpertArquetipo:
    def __init__(self, kb):
        self.kb = kb
    def validar_axioma(self, ss_query, space_id):
        """
        Valida si existe un axioma. Es más robusto:
        1. Busca por Ss (memoria factual) en ss_index.
        2. Si falla, busca por Ms (raíz) en ms_index.
        """
        universe = self.kb._get_space(space_id)
        # --- FIX: Normalización de tipo reforzada con int() ---
        ss_query_fixed = tuple(int(0 if x is None else x) for x in ss_query[:3])
        # Búsqueda primaria por Ss/Ms en el índice (ahora ambos usan la misma clave)
        exact_match_list = universe.ss_index.get(ss_query_fixed)
        if exact_match_list:
            return True, exact_match_list[0]
        # Búsqueda de respaldo (aunque debería ser redundante si el índice es el mismo)
        exact_by_ms = universe.find_archetype_by_ms(list(ss_query_fixed))
        if exact_by_ms:
            return True, exact_by_ms
        return False, None

class ExpertDinamica:
    def __init__(self, kb):
        self.kb = kb
    def proyectar_dinamica(self, ss_query, space_id):
        # Busca tensor con dMs compatible o genera proyección neutra
        universe = self.kb._get_space(space_id)
        best, best_sim = None, 0.0
        for archetype in universe.archetypes:
            dMs = getattr(archetype, 'dMs', None)
            if dMs:
                sim = sum(1 for a, b in zip(getattr(archetype, 'Ss', []), ss_query) if a == b) / len(ss_query)
                if sim > best_sim:
                    best_sim, best = sim, archetype
        if best and best_sim > 0.7:
            return True, best
        return False, None

class ExpertRelator:
    def __init__(self, kb):
        self.kb = kb
        self.transcender = Transcender()
    def contextualizar(self, ss_query, space_id):
        # Busca relaciones semánticas entre ss_query y todos los arquetipos
        universe = self.kb._get_space(space_id)
        best, best_score = None, float('-inf')
        for archetype in universe.archetypes:
            rel = self.transcender.relate_vectors(ss_query, getattr(archetype, 'Ss', [0,0,0]))
            score = -sum(abs(x) if x is not None else 0 for x in rel)
            if score > best_score:
                best_score, best = score, archetype
        if best:
            return True, best
        return False, None


# ===================== MÓDULO DE ROTACIÓN DE TENSORES (ARC - Aurean Rotation Cycle)
# ===============================================================================
PHI = (1 + 5**0.5) / 2
PHI_INVERSE = 1 / PHI

class TensorRotor:
    """Genera secuencias de índices para la selección de tensores."""
    def __init__(self, N: int, mode: str = "hybrid", start_k: int = 0):
        self.N = max(1, N)
        self.k = start_k % self.N
        self.i = 0
        self.mode = mode
        self.phi_step = max(1, round(PHI_INVERSE * self.N))
        self.fib_cache = {n: self._fib(n) for n in range(16)}

    def _fib(self, n: int) -> int:
        if n <= 1: return 1
        a, b = 1, 1
        for _ in range(2, n + 1): a, b = b, a + b
        return b

    def next(self) -> int:
        """Calcula el siguiente índice según la estrategia de rotación."""
        if self.mode == "phi":
            self.k = (self.k + self.phi_step) % self.N
        elif self.mode == "fibonacci":
            fib_step = self.fib_cache[self.i % 16]
            self.k = (self.k + fib_step) % self.N
        else: # hybrid
            if self.i % 2 == 0:
                self.k = (self.k + self.phi_step) % self.N
            else:
                fib_step = self.fib_cache[(self.i // 2) % 16]
                self.k = (self.k + fib_step) % self.N
        self.i += 1
        return self.k

class TensorPoolManager:
    """Gestor de pools de tensores con rotación estratificada."""
    def __init__(self):
        self.pools: Dict[str, List['FractalTensor']] = {
            'deep27': [], 'mid9': [], 'shallow3': [], 'mixed': []
        }
        self.rotors: Dict[str, TensorRotor] = {
            'deep27': TensorRotor(0, mode="fibonacci"),
            'mid9': TensorRotor(0, mode="hybrid"),
            'shallow3': TensorRotor(0, mode="phi"),
            'mixed': TensorRotor(0, mode="hybrid")
        }

    def add_tensor(self, tensor: 'FractalTensor'):
        """Añade un tensor al pool apropiado según su profundidad."""
        # Un tensor se considera "profundo" si tiene datos en el nivel 27
        if any(any(bit is not None for bit in vec) for vec in tensor.nivel_27):
            pool_name = 'deep27'
        elif any(any(bit is not None for bit in vec) for vec in tensor.nivel_9):
            pool_name = 'mid9'
        else:
            pool_name = 'shallow3'

        self.pools[pool_name].append(tensor)
        self.pools['mixed'].append(tensor)
        self.rotors[pool_name].N = len(self.pools[pool_name])
        self.rotors['mixed'].N = len(self.pools['mixed'])

    def get_tensor_trio(self, task_type: str = "arquetipo") -> List['FractalTensor']:
        """Obtiene un trío de tensores optimizado para una tarea específica."""
        task_to_pool = {
            'arquetipo': 'mixed', 'dinamica': 'shallow3',
            'relator': 'mid9', 'axioma': 'deep27'
        }
        pool_name = task_to_pool.get(task_type, 'mixed')
        
        # Fallback inteligente si el pool preferido no tiene suficientes tensores
        if len(self.pools[pool_name]) < 3:
            fallback_order = ['mixed', 'shallow3', 'mid9', 'deep27']
            for fb_pool_name in fallback_order:
                if len(self.pools[fb_pool_name]) >= 3:
                    pool_name = fb_pool_name
                    break
        
        pool = self.pools[pool_name]
        rotor = self.rotors[pool_name]

        if len(pool) < 3:
            trio = list(pool)
            while len(trio) < 3: trio.append(FractalTensor.neutral())
            return trio
        
        indices = [rotor.next() for _ in range(3)]
        return [pool[i] for i in indices]


KnowledgeBase = FractalKnowledgeBase


# ===============================================================================
# DEMOSTRACIÓN FRACTAL COMPLETA
# ===============================================================================

if __name__ == "__main__":
    print("🌌 DEMOSTRACIÓN FRACTAL AURORA: Arquetipos, Dinámicas y Relatores 🌌")
    print("=" * 80)
    print("Análisis de conocimiento desde tres perspectivas con datos coherentes.")
    print("=" * 80)

    # === INICIALIZACIÓN DEL ECOSISTEMA AURORA ===
    kb = FractalKnowledgeBase()
    evolver = Evolver()
    extender = Extender(kb)
    pool_manager = TensorPoolManager()

    # === FASE 1: ANÁLISIS DE ARQUETIPOS ===
    print("\n🏛️ FASE 1: ANÁLISIS DE ARQUETIPOS")
    print("-" * 50)
    familia_movimiento = [
        FractalTensor(nivel_3=[[1,0,1]], nivel_9=[[1,0,0]]*9, nivel_27=[[0,0,1]]*27),
        FractalTensor(nivel_3=[[1,0,1]], nivel_9=[[1,1,0]]*9, nivel_27=[[0,1,0]]*27),
        FractalTensor(nivel_3=[[1,0,1]], nivel_9=[[0,1,1]]*9, nivel_27=[[1,1,1]]*27)
    ]
    for t in familia_movimiento: pool_manager.add_tensor(t)
    
    trio_para_arquetipo = pool_manager.get_tensor_trio('arquetipo')
    arquetipo_movimiento = evolver.compute_fractal_archetype(trio_para_arquetipo)
    print(f"• Analizando {len(trio_para_arquetipo)} conceptos de 'movimiento'...")
    print(f"• ARQUETIPO resultante: {arquetipo_movimiento}")
    # Extraer Ss del tensor raíz del arquetipo (ejemplo: primer vector de nivel_3)
    Ss_movimiento = arquetipo_movimiento.nivel_3[0] if hasattr(arquetipo_movimiento, 'nivel_3') else [0,0,0]
    kb.add_archetype('fisica_conceptual', 'movimiento_universal', arquetipo_movimiento, Ss=Ss_movimiento)
    print("  └─ Arquetipo almacenado en el espacio 'fisica_conceptual'.")
    # Initialize LUT for archetype
    extender.learn_lut_from_data('fisica_conceptual', [([1, 0, 1], arquetipo_movimiento)])
    # Print KB indices for debug
    print("DEBUG: ss_index:", kb._get_space('fisica_conceptual').ss_index)
    print("DEBUG: ms_index:", kb._get_space('fisica_conceptual').ms_index)

    # === FASE 2: ANÁLISIS DE DINÁMICAS ===
    print("\n⚡ FASE 2: ANÁLISIS DE DINÁMICAS")
    print("-" * 50)
    
    estado_t0 = FractalTensor.random()
    estado_t1 = evolver.base_transcender.compute_full_fractal(estado_t0, estado_t0, FractalTensor.neutral())
    estado_t2 = evolver.base_transcender.compute_full_fractal(estado_t1, estado_t1, FractalTensor.neutral())
    secuencia_temporal_logica = [estado_t0, estado_t1, estado_t2]
    
    print(f"• Analizando secuencia temporal de {len(secuencia_temporal_logica)} estados.")
    firma_dinamica = evolver.analyze_fractal_dynamics(secuencia_temporal_logica)
    print(f"• DINÁMICA resultante: {firma_dinamica}")
    Ss_dinamica = firma_dinamica.nivel_3[0] if hasattr(firma_dinamica, 'nivel_3') else [0,0,0]
    kb.add_archetype('dinamicas_sistemas', 'evolucion_sistema_X', firma_dinamica, Ss=Ss_dinamica)
    print("  └─ Dinámica almacenada en 'dinamicas_sistemas'.")

    # === FASE 3: ANÁLISIS DE RELATORES ===
    print("\n🔗 FASE 3: ANÁLISIS DE RELATORES")
    print("-" * 50)
    
    concepto_base = FractalTensor.random()
    concepto_fuerza = evolver.base_transcender.compute_full_fractal(concepto_base, FractalTensor.random(), FractalTensor.neutral())
    concepto_energia = evolver.base_transcender.compute_full_fractal(concepto_base, concepto_fuerza, FractalTensor.neutral())
    cluster_contextual = [concepto_base, concepto_fuerza, concepto_energia]
    
    print(f"• Analizando clúster de {len(cluster_contextual)} conceptos relacionados.")
    firma_relacional = evolver.analyze_fractal_relations(cluster_contextual)
    print(f"• RELATOR resultante: {firma_relacional}")
    Ss_relator = firma_relacional.nivel_3[0] if hasattr(firma_relacional, 'nivel_3') else [0,0,0]
    kb.add_archetype('mapas_conceptuales', 'mecanica_basica', firma_relacional, Ss=Ss_relator)
    print("  └─ Relator almacenado en 'mapas_conceptuales'.")


    # === FASE 4: EXTENSIÓN BASADA EN CONOCIMIENTO ===
    print("\n🧩 FASE 4: EXTENSIÓN POR ARQUETIPO")
    print("-" * 50)

    # Usar directamente el vector raíz del arquetipo como consulta
    query_vector = arquetipo_movimiento.nivel_3[0][:3]
    print(f"• Vector a extender (solo con raíz): {query_vector}")

    # Extensión robusta: la función copiará todos los niveles del arquetipo encontrado
    resultado_extension = extender.extend_fractal(
        query_vector,
        contexto={'space_id': 'fisica_conceptual'}
    )

    tensor_reconstruido = resultado_extension['reconstructed_tensor']
    print(f"• Método de reconstrucción: {resultado_extension['reconstruction_method']}")
    print(f"• Tensor reconstruido: {tensor_reconstruido}")
    print("  └─ Los niveles 3, 9 y 27 se han rellenado desde la KB.")

    print("\n" + "=" * 80)
    print("🎯 DEMOSTRACIÓN FINALIZADA.")
    print("=" * 80)

################################################################################################
# ===================== INTEGRACIÓN DE REVERSIBILIDAD Y AUTOSIMILARIDAD ========================
################################################################################################

# --- UTILIDADES DE IMPUTACIÓN Y VALIDACIÓN ---
from statistics import mode
def impute_none(vec, context, tensor=None):
    """Imputa valores None usando contexto y niveles superiores del tensor."""
    result = []
    for i, v in enumerate(vec):
        if v is not None:
            result.append(v)
            continue
        col = [c[i] for c in context if i < len(c) and c[i] is not None]
        if tensor:
            if hasattr(tensor, 'nivel_9') and i < len(tensor.nivel_9):
                col.extend([x for x in tensor.nivel_9[i] if x is not None])
            if hasattr(tensor, 'nivel_3') and i < len(tensor.nivel_3[0]):
                col.append(tensor.nivel_3[0][i % 3])
        result.append(mode(col) if col else 0)
    return result

def validate_ternary_input(vec, expected_len=3, name="input"):
    """Valida y normaliza entradas ternarias."""
    if not isinstance(vec, (list, tuple)) or len(vec) != expected_len:
        print(f"Warning: Invalid {name}: {vec}, using default {[0]*expected_len}")
        return [0] * expected_len
    return [None if x is None else int(x) % 2 for x in vec]

# --- ESTRATEGIAS DE SELECCIÓN AUTOSIMILARES ---
def golden_ratio_skip_indices(N, k, trios=3):
    """Devuelve una lista de índices para formar un trío usando saltos áureos."""
    phi = (1 + math.sqrt(5)) / 2
    skip = max(1, int(N / phi))
    indices = []
    idx = k
    for _ in range(trios):
        indices.append(idx % N)
        idx = (idx + skip) % N
    return indices

def fibonacci(n):
    a, b = 1, 1
    for _ in range(n):
        a, b = b, a + b
    return a

def fibonacci_stepping_indices(N, k, trios=3, start_step=0):
    """Devuelve una lista de índices para formar un trío usando pasos de Fibonacci."""
    indices = []
    idx = k
    for i in range(start_step, start_step + trios):
        step = fibonacci(i)
        indices.append(idx % N)
        idx = (idx + step) % N
    return indices

# --- AJUSTE AUTOSIMILAR (OPCIONAL, SI SE DESEA USAR EN ARMONIZADOR) ---
class AdjustmentStep:
    def apply(self, vec, archetype, kb=None):
        raise NotImplementedError

class MicroShift(AdjustmentStep):
    def apply(self, vec, archetype, kb=None):
        return [a if v is None else v for v, a in zip(vec, archetype)]

class Regrewire(AdjustmentStep):
    def apply(self, vec, archetype, kb=None):
        if sum(1 for v, a in zip(vec, archetype) if v == a) >= 2:
            return list(archetype)
        return vec

class Metatune(AdjustmentStep):
    def apply(self, vec, archetype, kb=None):
        if kb is not None:
            matches = kb.find_archetype_by_ms(archetype)
            if matches:
                return matches[0]
        return vec

# --- TRIAGE FUNCIONAL UNIFICADO (INFERENCIA, APRENDIZAJE, DEDUCCIÓN) ---
def f_not(x):
    return 1 - x if x in (0, 1) else 0
def f_not_inv(x):
    return 1 - x if x in (0, 1) else 0
f_not.inverse = f_not_inv

def f_inc(x):
    return (x + 1) % 2 if x in (0, 1) else 0
def f_inc_inv(x):
    return (x - 1) % 2 if x in (0, 1) else 0
f_inc.inverse = f_inc_inv

def f_id(x):
    return x
f_id.inverse = f_id

def aurora_apply_sequence(val, sequence):
    for func in sequence:
        val = func(val)
    return val

def aurora_triage_inferencia(A, B, M):
    allowed_functions = [f_not, f_inc, f_id]
    def normalize_ternary_vector(vec, default=[0,0,0]):
        if not isinstance(vec, (list, tuple)):
            return default.copy()
        return [None if x is None else int(x) if x in (0,1) else 0 for x in list(vec)[:3]] + [0]*(3-len(vec))
    def validate_function_sequence(M, allowed_functions, max_len=2):
        if not isinstance(M, (list, tuple)) or len(M) != 3:
            return [[f_id] for _ in range(3)]
        return [list(seq)[:max_len] if isinstance(seq, (list, tuple)) and all(f in allowed_functions for f in seq) else [f_id] for seq in M[:3]] + [[f_id]]*(3-len(M))
    A = normalize_ternary_vector(A)
    B = normalize_ternary_vector(B)
    M = validate_function_sequence(M, allowed_functions)
    R = []
    for i in range(3):
        rA = aurora_apply_sequence(A[i], M[i])
        rB = aurora_apply_sequence(B[i], M[i])
        if rA is not None and rB is not None:
            R.append(rA + rB)
        else:
            R.append(0)
    return R

def aurora_triage_aprendizaje(A, B, R, funciones_permitidas, max_len=2):
    import itertools
    def normalize_ternary_vector(vec, default=[0,0,0]):
        if not isinstance(vec, (list, tuple)):
            return default.copy()
        return [None if x is None else int(x) if x in (0,1) else 0 for x in list(vec)[:3]] + [0]*(3-len(vec))
    A = normalize_ternary_vector(A)
    B = normalize_ternary_vector(B)
    R = normalize_ternary_vector(R)
    M = []
    for i in range(3):
        found = False
        for l in range(1, max_len+1):
            for seq in itertools.product(funciones_permitidas, repeat=l):
                rA = aurora_apply_sequence(A[i], seq)
                rB = aurora_apply_sequence(B[i], seq)
                if rA is not None and rB is not None and rA + rB == R[i]:
                    M.append(list(seq))
                    found = True
                    break
            if found:
                break
        if not found:
            M.append([f_id])
    return M

def aurora_triage_deduccion(M, R, known, known_is_A=True):
    allowed_functions = [f_not, f_inc, f_id]
    def normalize_ternary_vector(vec, default=[0,0,0]):
        if not isinstance(vec, (list, tuple)):
            return default.copy()
        return [None if x is None else int(x) if x in (0,1) else 0 for x in list(vec)[:3]] + [0]*(3-len(vec))
    def validate_function_sequence(M, allowed_functions, max_len=2):
        if not isinstance(M, (list, tuple)) or len(M) != 3:
            return [[f_id] for _ in range(3)]
        return [list(seq)[:max_len] if isinstance(seq, (list, tuple)) and all(f in allowed_functions for f in seq) else [f_id] for seq in M[:3]] + [[f_id]]*(3-len(M))
    R = normalize_ternary_vector(R)
    known = normalize_ternary_vector(known)
    M = validate_function_sequence(M, allowed_functions)
    deduced = []
    for i in range(3):
        val = R[i] - aurora_apply_sequence(known[i], M[i]) if R[i] is not None and known[i] is not None else 0
        for func in reversed(M[i]):
            if hasattr(func, 'inverse'):
                val = func.inverse(val)
        deduced.append(val if val in (0,1,None) else 0)
    return deduced

# --- INVERSE EVOLVER: REVERSIBILIDAD FRACTAL ---
class InverseEvolver:
    """Reconstruye tensores originales desde sintetizados usando lógica inversa."""
    def __init__(self, knowledge_base=None):
        self.kb = knowledge_base
        self.trigate = Trigate()
        self.armonizador = Armonizador(knowledge_base=knowledge_base) if knowledge_base else None

    def reconstruct_vectors(self, Ms):
        """Deduce A y B desde Ms usando lógica inversa del Trigate."""
        A, B = [], []
        for m in Ms:
            if m == 0:
                A.append(0)
                B.append(0)
            elif m == 1:
                A.append(1)
                B.append(0)
            else:
                A.append(None)
                B.append(None)
        return A, B

    def reconstruct_fractal(self, synthesized):
        """Reconstruye tres tensores fractales desde uno sintetizado (niveles 3, 9, 27)."""
        ms_key = synthesized.nivel_3[0]
        A_l3, B_l3 = self.reconstruct_vectors(ms_key)
        C_l3 = [TernaryLogic.ternary_xor(a, b) for a, b in zip(A_l3, B_l3)]

        def reconstruct_level(level_vectors):
            A_vectors, B_vectors, C_vectors = [], [], []
            for vec in level_vectors:
                a, b = self.reconstruct_vectors(vec)
                c = [TernaryLogic.ternary_xor(x, y) for x, y in zip(a, b)]
                A_vectors.append(a)
                B_vectors.append(b)
                C_vectors.append(c)
            return A_vectors, B_vectors, C_vectors

        A_l9, B_l9, C_l9 = reconstruct_level(synthesized.nivel_9)
        A_l27, B_l27, C_l27 = reconstruct_level(synthesized.nivel_27)

        def create_tensor(n3, n9, n27, ss):
            tensor = FractalTensor(nivel_3=n3, nivel_9=n9, nivel_27=n27)
            if self.armonizador:
                harm = self.armonizador.harmonize(
                    tensor.nivel_3[0],
                    archetype=tensor.nivel_3[0],
                    space_id="inverse"
                )
                tensor.nivel_3[0] = harm["output"]
            tensor.Ss = ss
            return tensor

        return [
            create_tensor([A_l3], A_l9, A_l27, ss="A"),
            create_tensor([B_l3], B_l9, B_l27, ss="B"),
            create_tensor([C_l3], C_l9, C_l27, ss="C")
        ]


# ===================== TRIGATE IMPLEMENTATION =====================

# Ternary values
NULL = None
TERNARY_VALUES = [0, 1, NULL]


class Trigate:
    """
    Fundamental Aurora logic module implementing ternary operations.
    
    Supports three operational modes:
    1. Inference: A + B + M -> R (given inputs and control, compute result)
    2. Learning: A + B + R -> M (given inputs and result, learn control)
    3. Deduction: M + R + A -> B (given control, result, and one input, deduce other)
    
    All operations are O(1) using precomputed lookup tables (LUTs).
    """
    
    # Class-level LUTs (computed once at module load)
    _LUT_INFER: Dict[Tuple, int] = {}
    _LUT_LEARN: Dict[Tuple, int] = {}
    _LUT_DEDUCE_A: Dict[Tuple, int] = {}
    _LUT_DEDUCE_B: Dict[Tuple, int] = {}
    _initialized = False
    
    def __init__(self):
        """Initialize Trigate and ensure LUTs are computed."""
        if not Trigate._initialized:
            Trigate._initialize_luts()
    
    @classmethod
    def _initialize_luts(cls):
        """
        Initialize all lookup tables for O(1) operations.
        
        Based on extended XOR logic with NULL propagation:
        - 0 XOR 0 = 0, 0 XOR 1 = 1, 1 XOR 0 = 1, 1 XOR 1 = 0
        - Any operation with NULL propagates NULL
        - Control bit M determines XOR (1) or XNOR (0)
        """
        print("Initializing Trigate LUTs...")
        
        # Generate all possible combinations for ternary logic
        for a, b, m, r in itertools.product(TERNARY_VALUES, repeat=4):
            
            # INFERENCE LUT: (a, b, m) -> r
            computed_r = cls._compute_inference(a, b, m)
            cls._LUT_INFER[(a, b, m)] = computed_r
            
            # LEARNING LUT: (a, b, r) -> m
            # Find control M that produces R given A, B
            learned_m = cls._compute_learning(a, b, r)
            cls._LUT_LEARN[(a, b, r)] = learned_m
            
            # DEDUCTION LUTS: (m, r, a) -> b and (m, r, b) -> a
            deduced_b = cls._compute_deduction_b(m, r, a)
            deduced_a = cls._compute_deduction_a(m, r, b)
            
            cls._LUT_DEDUCE_B[(m, r, a)] = deduced_b
            cls._LUT_DEDUCE_A[(m, r, b)] = deduced_a
        
        cls._initialized = True
        print(f"Trigate LUTs initialized: {len(cls._LUT_INFER)} entries each")
    
    @staticmethod
    def _compute_inference(a: Union[int, None], b: Union[int, None], m: Union[int, None]) -> Union[int, None]:
        """
        Compute R given A, B, M using ternary logic.
        
        Logic:
        - If any input is NULL, result is NULL
        - If M is 1: R = A XOR B
        - If M is 0: R = A XNOR B (NOT(A XOR B))
        """
        if a is NULL or b is NULL or m is NULL:
            return NULL
        
        if m == 1:  # XOR mode
            return a ^ b
        else:  # XNOR mode (m == 0)
            return 1 - (a ^ b)
    
    @staticmethod
    def _compute_learning(a: Union[int, None], b: Union[int, None], r: Union[int, None]) -> Union[int, None]:
        """
        Learn control M given A, B, R.
        
        Logic:
        - If any input is NULL, cannot learn -> NULL
        - If A XOR B == R, then M = 1 (XOR)
        - If A XOR B != R, then M = 0 (XNOR)
        """
        if a is NULL or b is NULL or r is NULL:
            return NULL
        
        xor_result = a ^ b
        if xor_result == r:
            return 1  # XOR mode produces correct result
        else:
            return 0  # XNOR mode produces correct result
    
    @staticmethod
    def _compute_deduction_a(m: Union[int, None], r: Union[int, None], b: Union[int, None]) -> Union[int, None]:
        """
        Deduce A given M, R, B.
        
        Logic:
        - If any input is NULL, cannot deduce -> NULL
        - If M is 1: A = R XOR B (since R = A XOR B)
        - If M is 0: A = NOT(R) XOR B (since R = NOT(A XOR B))
        """
        if m is NULL or r is NULL or b is NULL:
            return NULL
        
        if m == 1:  # XOR mode: A XOR B = R -> A = R XOR B
            return r ^ b
        else:  # XNOR mode: NOT(A XOR B) = R -> A XOR B = NOT(R) -> A = NOT(R) XOR B
            return (1 - r) ^ b
    
    @staticmethod
    def _compute_deduction_b(m: Union[int, None], r: Union[int, None], a: Union[int, None]) -> Union[int, None]:
        """
        Deduce B given M, R, A.
        
        Logic: Same as deduce_a but solving for B instead of A.
        """
        if m is NULL or r is NULL or a is NULL:
            return NULL
        
        if m == 1:  # XOR mode: A XOR B = R -> B = R XOR A
            return r ^ a
        else:  # XNOR mode: NOT(A XOR B) = R -> A XOR B = NOT(R) -> B = NOT(R) XOR A
            return (1 - r) ^ a
    
    def infer(self, A: List[Union[int, None]], B: List[Union[int, None]], M: List[Union[int, None]]) -> List[Union[int, None]]:
        """
        Inference mode: Compute R given A, B, M.
        
        Args:
            A: First input vector (3 bits)
            B: Second input vector (3 bits)
            M: Control vector (3 bits)
            
        Returns:
            R: Result vector (3 bits)
        """
        if not (len(A) == len(B) == len(M) == 3):
            raise ValueError("All vectors must have exactly 3 elements")
        
        return [self._LUT_INFER[(a, b, m)] for a, b, m in zip(A, B, M)]
    
    def learn(self, A: List[Union[int, None]], B: List[Union[int, None]], R: List[Union[int, None]]) -> List[Union[int, None]]:
        """
        Learning mode: Learn control M given A, B, R.
        
        Args:
            A: First input vector (3 bits)
            B: Second input vector (3 bits)
            R: Target result vector (3 bits)
            
        Returns:
            M: Learned control vector (3 bits)
        """
        if not (len(A) == len(B) == len(R) == 3):
            raise ValueError("All vectors must have exactly 3 elements")
        
        return [self._LUT_LEARN[(a, b, r)] for a, b, r in zip(A, B, R)]
    
    def deduce_a(self, M: List[Union[int, None]], R: List[Union[int, None]], B: List[Union[int, None]]) -> List[Union[int, None]]:
        """
        Deduction mode: Deduce A given M, R, B.
        
        Args:
            M: Control vector (3 bits)
            R: Result vector (3 bits)
            B: Known input vector (3 bits)
            
        Returns:
            A: Deduced input vector (3 bits)
        """
        if not (len(M) == len(R) == len(B) == 3):
            raise ValueError("All vectors must have exactly 3 elements")
        
        return [self._LUT_DEDUCE_A[(m, r, b)] for m, r, b in zip(M, R, B)]
    
    def deduce_b(self, M: List[Union[int, None]], R: List[Union[int, None]], A: List[Union[int, None]]) -> List[Union[int, None]]:
        """
        Deduction mode: Deduce B given M, R, A.
        
        Args:
            M: Control vector (3 bits)
            R: Result vector (3 bits)
            A: Known input vector (3 bits)
            
        Returns:
            B: Deduced input vector (3 bits)
        """
        if not (len(M) == len(R) == len(A) == 3):
            raise ValueError("All vectors must have exactly 3 elements")
        
        return [self._LUT_DEDUCE_B[(m, r, a)] for m, r, a in zip(M, R, A)]
    
    def validate_triangle_closure(self, A: List[Union[int, None]], B: List[Union[int, None]], 
                                  M: List[Union[int, None]], R: List[Union[int, None]]) -> bool:
        """
        Validate that A, B, M, R form a valid logical triangle.
        
        This ensures geometric coherence: the triangle "closes" properly.
        
        Args:
            A, B, M, R: The four vectors forming the logical triangle
            
        Returns:
            True if triangle is valid, False otherwise
        """
        # Compute expected R from A, B, M
        expected_R = self.infer(A, B, M)
        
        # Check if computed R matches provided R
        for expected, actual in zip(expected_R, R):
            if expected != actual:
                return False
        
        return True
    
    def get_truth_table(self, operation: str = "infer") -> str:
        """
        Generate human-readable truth table for debugging.
        
        Args:
            operation: "infer", "learn", "deduce_a", or "deduce_b"
            
        Returns:
            Formatted truth table string
        """
        if operation == "infer":
            lut = self._LUT_INFER
            header = "A | B | M | R"
        elif operation == "learn":
            lut = self._LUT_LEARN
            header = "A | B | R | M"
        elif operation == "deduce_a":
            lut = self._LUT_DEDUCE_A
            header = "M | R | B | A"
        elif operation == "deduce_b":
            lut = self._LUT_DEDUCE_B
            header = "M | R | A | B"
        else:
            raise ValueError(f"Unknown operation: {operation}")
        
        def format_val(v):
            return "N" if v is NULL else str(v)
        
        lines = [header, "-" * len(header)]
        
        for key, value in sorted(lut.items()):
            key_str = " | ".join(format_val(k) for k in key)
            val_str = format_val(value)
            lines.append(f"{key_str} | {val_str}")
        
        return "\n".join(lines)
    
    def synthesize(self, A: List[int], B: List[int]) -> Tuple[List[Optional[int]], List[Optional[int]]]:
        """Síntesis Aurora: genera M (lógica) y S (forma) desde A y B."""
        M = [TernaryLogic.ternary_xor(a, b) for a, b in zip(A, B)]
        S = [TernaryLogic.ternary_xnor(a, b) for a, b in zip(A, B)]
        return M, S

    def recursive_synthesis(
        self,
        vectors: List[List[int]]
    ) -> Tuple[List[Optional[int]], List[List[Optional[int]]]]:
        """
        Reduce secuencialmente una lista ≥2 de vectores ternarios.

        Devuelve:
          • resultado_final – vector M después de la última combinación
          • history – lista de cada resultado intermedio (M-k) para depuración
        """
        if len(vectors) < 2:
            raise ValueError("Se necesitan al menos 2 vectores")

        history: List[List[Optional[int]]] = []
        current = vectors[0]

        for nxt in vectors[1:]:
            current, _ = self.synthesize(current, nxt)
            history.append(current)

        return current, history
    
    def __repr__(self) -> str:
        return f"Trigate(initialized={self._initialized}, lut_size={len(self._LUT_INFER)})"