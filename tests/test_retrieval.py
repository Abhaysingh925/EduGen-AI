import unittest
from retrieval import search_chunks
from llm import local_evidence_explanation

SAMPLES = [
    {"text": "CPU scheduling selects a process from the ready queue for CPU execution. FCFS schedules arrival order.", "source": "CPU_Scheduling_Textbook_Excerpt.pdf", "category": "Textbook", "page": 1, "chunk_id": 1, "file_type": "pdf", "location_type": "page"},
    {"text": "Round Robin allocates a small time quantum to each ready process. It improves response time.", "source": "OS_Lecture_Notes.docx", "category": "Notes", "page": 2, "chunk_id": 1, "file_type": "docx", "location_type": "section"},
    {"text": "Compare FCFS and Round Robin scheduling algorithms for exams.", "source": "CPU_Scheduling_Question_Bank.docx", "category": "Questions", "page": 1, "chunk_id": 1, "file_type": "docx", "location_type": "section"},
    {"text": "Lab activity: draw Gantt charts and calculate waiting time for scheduling algorithms.", "source": "CPU_Scheduling_Lab_Manual.docx", "category": "Labs", "page": 1, "chunk_id": 1, "file_type": "docx", "location_type": "section"},
]

class RetrievalTests(unittest.TestCase):
    def test_topic_retrieval_returns_sources(self):
        results = search_chunks(SAMPLES, "Explain CPU scheduling and compare FCFS with Round Robin", top_k=4)
        self.assertGreaterEqual(len(results), 3)
        self.assertTrue(any(r["category"] == "Textbook" for r in results))
        self.assertTrue(any(r["category"] == "Notes" for r in results))

    def test_category_filter(self):
        results = search_chunks(SAMPLES, "CPU scheduling algorithms", top_k=5, category="Questions")
        self.assertTrue(results)
        self.assertTrue(all(r["category"] == "Questions" for r in results))

    def test_extractive_answer_mentions_evidence(self):
        results = search_chunks(SAMPLES, "CPU scheduling FCFS Round Robin", top_k=3)
        answer = local_evidence_explanation("CPU scheduling FCFS Round Robin", results)
        self.assertIn("Topic overview", answer)
        self.assertTrue("FCFS" in answer or "Round Robin" in answer)

if __name__ == "__main__":
    unittest.main()
