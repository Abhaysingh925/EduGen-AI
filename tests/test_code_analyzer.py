
import unittest

from utils.code_analyzer import analyze_text, detect_language, extract_code_blocks


class TestCodeAnalyzer(unittest.TestCase):

    def test_fenced_python_block(self):
        text = "```python\ndef greet():\n    print('Hello')\n```"
        result = analyze_text(text)

        self.assertTrue(result["contains_code"])
        self.assertEqual(result["code_block_count"], 1)
        self.assertEqual(
            result["code_blocks"][0]["detected_language"], "Python"
        )

    def test_unfenced_python_code(self):
        text = "def greet():\n    print('Hello')"
        result = analyze_text(text)

        self.assertTrue(result["contains_code"])
        self.assertEqual(
            result["code_blocks"][0]["detected_language"], "Python"
        )

    def test_java_detection(self):
        code = (
            "public class Main { "
            "public static void main(String[] args) { "
            "System.out.println(1); } }"
        )
        self.assertEqual(detect_language(code)["language"], "Java")

    def test_cpp_detection(self):
        code = "#include <iostream>\nint main() { std::cout << 1; }"
        self.assertEqual(detect_language(code)["language"], "C++")

    def test_normal_text(self):
        text = "The operating system manages memory and processes."
        result = analyze_text(text)

        self.assertFalse(result["contains_code"])
        self.assertEqual(result["code_block_count"], 0)

    def test_empty_text(self):
        result = analyze_text("")

        self.assertFalse(result["contains_code"])
        self.assertEqual(result["code_block_count"], 0)

    def test_extract_preserves_indentation(self):
        text = "```python\ndef greet():\n    print('Hello')\n```"
        blocks = extract_code_blocks(text)

        self.assertEqual(len(blocks), 1)
        self.assertIn("    print('Hello')", blocks[0]["code"])


if __name__ == "__main__":
    unittest.main()
