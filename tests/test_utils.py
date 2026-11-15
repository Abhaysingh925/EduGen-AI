import unittest
from utils.categorizer import categorize
from utils.chunker import split_text, chunk_document
from utils.text_cleaner import clean_text


class UtilityTests(unittest.TestCase):
    def test_category_filename_rules(self):
        self.assertEqual(categorize("OS_Lecture_Notes.docx", "CPU scheduling"), "Notes")
        self.assertEqual(categorize("CPU_Scheduling_Textbook.pdf", "FCFS scheduling"), "Textbook")
        self.assertEqual(categorize("CPU_Scheduling_Question_Bank.docx", "Question one"), "Questions")
        self.assertEqual(categorize("CPU_Scheduling_Lab_Manual.pptx", "Aim: test algorithms"), "Labs")

    def test_clean_text(self):
        self.assertEqual(clean_text("A\u200b   B\n\nC"), "A B\nC")

    def test_chunk_overlap_coverage(self):
        text = "First paragraph about CPU scheduling. " * 40
        chunks = split_text(text, chunk_size=180, overlap=30)
        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(chunks))
        self.assertIn("CPU scheduling", " ".join(chunks))

    def test_chunk_metadata(self):
        result = chunk_document([{"page": 2, "text": "CPU scheduling runs processes."}], "OS_Notes.pdf", "Notes", 100, 10)
        self.assertEqual(result[0]["source"], "OS_Notes.pdf")
        self.assertEqual(result[0]["category"], "Notes")
        self.assertEqual(result[0]["page"], 2)


if __name__ == "__main__":
    unittest.main()
