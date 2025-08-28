
import unittest
from aurora_trinity import FractalTensor, Evolver, Extender, FractalKnowledgeBase

class TestAuroraBasics(unittest.TestCase):
    def setUp(self):
        self.kb = FractalKnowledgeBase()
        self.evolver = Evolver()
        self.extender = Extender(self.kb)

    def test_tensor_creation(self):
        t = FractalTensor(nivel_3=[[1,0,1]])
        self.assertIsInstance(t, FractalTensor)
        self.assertEqual(t.nivel_3[0], [1,0,1])

    def test_archetype_synthesis_and_storage(self):
        T1 = FractalTensor(nivel_3=[[1,0,1]])
        T2 = FractalTensor(nivel_3=[[0,1,1]])
        T3 = FractalTensor(nivel_3=[[1,1,0]])
        archetype = self.evolver.compute_fractal_archetype([T1, T2, T3])
        self.kb.add_archetype("demo", "archetype1", archetype, Ss=archetype.nivel_3[0])
        stored = self.kb.get_archetype("demo", "archetype1")
        self.assertIsNotNone(stored)
        self.assertEqual(stored.nivel_3[0], archetype.nivel_3[0])

    def test_extension(self):
        T1 = FractalTensor(nivel_3=[[1,0,1]])
        T2 = FractalTensor(nivel_3=[[0,1,1]])
        T3 = FractalTensor(nivel_3=[[1,1,0]])
        archetype = self.evolver.compute_fractal_archetype([T1, T2, T3])
        self.kb.add_archetype("demo", "archetype1", archetype, Ss=archetype.nivel_3[0])
        result = self.extender.extend_fractal(archetype.nivel_3[0], context={"space_id": "demo"})
        self.assertIn("reconstructed_tensor", result)
        self.assertIsInstance(result["reconstructed_tensor"], list)

if __name__ == "__main__":
    unittest.main()
