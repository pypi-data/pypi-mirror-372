import pytest

from trinity_3.core import (
    MicroShift,
    Regrewire,
    Metatune,
    Armonizador,
    FractalTensor,
    FractalKnowledgeBase,
)


def test_microshift_fills_none_and_matches_archetype():
    ms = MicroShift()
    arche = FractalTensor(nivel_3=[[1, 0, 1]])
    vec = [None, 0, None]

    out = ms.apply(vec, arche, kb=None)

    assert isinstance(out, list) and len(out) == 3
    # Should fill None slots from archetype root
    assert out == [1, 0, 1]


def test_regrewire_selects_matching_archetype_from_kb():
    kb = FractalKnowledgeBase()
    arche = FractalTensor(nivel_3=[[1, 1, 0]])
    kb.add_archetype('default', 'a', arche, Ss=arche.nivel_3[0])

    rw = Regrewire()
    query = [1, 1, None]
    out = rw.apply(query, None, kb=kb)

    assert out == [1, 1, 0]


def test_metatune_is_deterministic_and_returns_ternary():
    mt = Metatune()
    arche = FractalTensor(nivel_3=[[0, 1, 0]])
    vec = [1, None, 1]

    out1 = mt.apply(vec, arche, kb=None)
    out2 = mt.apply(vec, arche, kb=None)

    assert out1 == out2
    assert len(out1) == 3
    for v in out1:
        assert v in (0, 1, None)


def test_armonizador_harmonize_uses_kb_and_applies_steps():
    kb = FractalKnowledgeBase()
    arche = FractalTensor(nivel_3=[[0, 0, 0]])
    kb.add_archetype('default', 'zero', arche, Ss=arche.nivel_3[0])

    arm = Armonizador(knowledge_base=kb)
    # disable early stopping thresholds so all steps run
    arm.tau_1 = None
    arm.tau_2 = None
    arm.tau_3 = None

    input_vec = [None, None, None]
    res = arm.harmonize(input_vec, archetype=None, space_id='default')

    assert isinstance(res, dict)
    assert 'output' in res and 'score' in res and 'adjustments' in res
    # With archetype zeros the harmonizer should produce zeros and score 0
    assert res['output'] == [0, 0, 0]
    assert res['score'] == 0
    assert len(res['adjustments']) >= 1
