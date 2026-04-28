import tempfile
import unittest
from pathlib import Path

from sender import build_message, choose_variants, load_recipients


class SenderTests(unittest.TestCase):
    def test_load_recipients_reads_valid_rows(self) -> None:
        csv_content = "email,name\nuser1@example.com,Rahul\nuser2@example.com,\n"
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "recipients.csv"
            csv_path.write_text(csv_content, encoding="utf-8")

            recipients = load_recipients(csv_path)

        self.assertEqual(len(recipients), 2)
        self.assertEqual(recipients[0].email, "user1@example.com")
        self.assertEqual(recipients[0].name, "Rahul")
        self.assertEqual(recipients[1].name, "there")

    def test_load_recipients_requires_expected_headers(self) -> None:
        csv_content = "mail,full_name\nuser1@example.com,Rahul\n"
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = Path(tmpdir) / "invalid.csv"
            csv_path.write_text(csv_content, encoding="utf-8")

            with self.assertRaises(ValueError):
                load_recipients(csv_path)

    def test_build_message_personalizes_name(self) -> None:
        class Recipient:
            email = "user@example.com"
            name = "Priya"

        msg = build_message("sender@example.com", Recipient(), 0)
        self.assertEqual(msg["To"], "user@example.com")
        self.assertIn("Priya", msg.get_content())

    def test_choose_variants_cycles(self) -> None:
        variants = list(choose_variants(7))
        self.assertEqual(variants, [0, 1, 2, 0, 1, 2, 0])


if __name__ == "__main__":
    unittest.main()
