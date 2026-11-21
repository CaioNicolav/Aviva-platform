import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lambda_function import parse_measurement

class TestMeasurement(unittest.TestCase):
    def sample(self, cm):
        return {"data_hora": "2026-11-19T18:00:00Z", "nivel_agua_cm": cm}
    def test_normal(self):
        self.assertEqual(parse_measurement(self.sample(50))["situacao"], "NORMAL")
    def test_atencao(self):
        self.assertEqual(parse_measurement(self.sample(130))["situacao"], "ATENCAO")
    def test_critico(self):
        self.assertEqual(parse_measurement(self.sample(225))["situacao"], "CRITICO")
    def test_chuva_critica(self):
        self.assertEqual(parse_measurement({**self.sample(30), "chuva_simulada_mm_h": 55})["situacao"], "CRITICO")
    def test_risco_combinado(self):
        self.assertEqual(parse_measurement({**self.sample(130), "chuva_simulada_mm_h": 30})["situacao"], "CRITICO")
    def test_dados_ausentes(self):
        with self.assertRaises(ValueError):
            parse_measurement({"nivel_agua_cm": 225})
    def test_nivel_negativo(self):
        with self.assertRaises(ValueError):
            parse_measurement(self.sample(-1))

if __name__ == "__main__":
    unittest.main()
