"""Seam: the text-task checkers, against real model outputs measured on 2026-10-28."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "bench" / "text"))
from tasks import check_t4, check_t5  # noqa: E402

GOOD_T4 = ('{"asistira": true, "total": 3, "adultos": 2, "ninos": 1, "restricciones": '
           '[{"persona": "Carlos", "restriccion": "vegetariano"}, {"persona": "yo", '
           '"restriccion": "no puedo con mariscos"}], "llegada": "20:00"}')


class T4(unittest.TestCase):
    def test_correct_extraction_passes(self):
        self.assertTrue(check_t4(GOOD_T4)[0])

    def test_code_fences_are_tolerated(self):
        self.assertTrue(check_t4("```json\n" + GOOD_T4 + "\n```")[0])

    def test_invented_person_fails(self):
        self.assertFalse(check_t4(GOOD_T4.replace('"yo"', '"Usuario"'))[0])

    def test_wrong_arrival_fails(self):
        self.assertFalse(check_t4(GOOD_T4.replace("20:00", "08:00"))[0])

    def test_not_json_fails(self):
        self.assertEqual(check_t4("Claro, aquí está el JSON"), (False, "not JSON"))


class T5(unittest.TestCase):
    def test_warm_rewrite_passes(self):
        text = ("Hola {nombre}, te recordamos que falta poquito para confirmar tu asistencia. "
                "Si puedes, completa el formulario en {link} cuando tengas un momentito.")
        self.assertTrue(check_t5(text)[0])

    def test_formal_rewrite_fails(self):
        text = ("Estimado(a) {nombre}: Te recordamos que el plazo para confirmar tu asistencia "
                "vence pronto. Agradecemos que diligencias el formulario en {link}.")
        self.assertFalse(check_t5(text)[0])

    def test_dropped_deadline_fails(self):
        self.assertFalse(check_t5("Hola {nombre}, confirma tu asistencia en {link}.")[0])

    def test_lost_placeholder_fails(self):
        self.assertFalse(check_t5("Hola {nombre}, el plazo vence pronto, confirma ya.")[0])


if __name__ == "__main__":
    unittest.main()
