
import unittest

from modules.normalization import (
    normalize_amount,
    normalize_date,
    normalize_project_id,
    normalize_text,
)


class TestNormalization(unittest.TestCase):

    # AMOUNT TESTS

    def test_amount_formats(self):
        self.assertEqual(normalize_amount("₹11,50,000"), 1150000)
        self.assertEqual(normalize_amount("Rs. 11,50,000"), 1150000)
        self.assertEqual(normalize_amount("1150000"), 1150000)
        self.assertEqual(normalize_amount("Rs 11,00,000"), 1100000)
        self.assertEqual(normalize_amount(750000), 750000)

    def test_missing_amount(self):
        self.assertIsNone(normalize_amount(None))
        self.assertIsNone(normalize_amount(""))

    def test_invalid_amount(self):
        with self.assertRaises(ValueError):
            normalize_amount("eleven lakh")

    # DATE TESTS

    def test_date_formats(self):
        self.assertEqual(normalize_date("2026-01-10"), "2026-01-10")
        self.assertEqual(normalize_date("10/01/2026"), "2026-01-10")
        self.assertEqual(normalize_date("10-01-2026"), "2026-01-10")
        self.assertEqual(normalize_date("10 Jan 2026"), "2026-01-10")

    def test_missing_date(self):
        self.assertIsNone(normalize_date(None))
        self.assertIsNone(normalize_date(""))

    def test_invalid_date(self):
        with self.assertRaises(ValueError):
            normalize_date("31/02/2026")

    # PROJECT ID TESTS

    def test_project_id(self):
        self.assertEqual(normalize_project_id(" mpl002 "), "MPL002")
        self.assertEqual(normalize_project_id("mpl001"), "MPL001")

    def test_missing_project_id(self):
        self.assertIsNone(normalize_project_id(None))

    # TEXT TESTS

    def test_text_normalization(self):
        self.assertEqual(
            normalize_text("  ABC   Construction  "),
            "ABC Construction"
        )

        self.assertEqual(
            normalize_text("ABC Construction", casefold=True),
            "abc construction"
        )

    def test_missing_text(self):
        self.assertIsNone(normalize_text(None))


if __name__ == "__main__":
    unittest.main(verbosity=2)
