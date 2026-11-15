
"""Algorithm identification and explanation engine for EduGen-AI."""

import re


ALGORITHM_DATABASE = {
    "FCFS": {
        "name": "First Come First Served",
        "category": "CPU Scheduling",
        "steps": [
            "Arrange processes according to arrival time.",
            "Select the process that arrived first.",
            "Execute it until completion.",
            "Calculate waiting and turnaround time.",
        ],
        "time_complexity": "O(n log n) including sorting",
        "space_complexity": "O(n)",
    },
    "SJF": {
        "name": "Shortest Job First",
        "category": "CPU Scheduling",
        "steps": [
            "Check the processes available in the ready queue.",
            "Select the process with the shortest CPU burst.",
            "Execute the selected process.",
            "Repeat until all processes are completed.",
        ],
        "time_complexity": "O(n log n) including sorting",
        "space_complexity": "O(n)",
    },
    "SRTF": {
        "name": "Shortest Remaining Time First",
        "category": "CPU Scheduling",
        "steps": [
            "Check the remaining CPU burst of ready processes.",
            "Select the process with the shortest remaining time.",
            "Preempt the running process if a shorter job arrives.",
            "Continue until all processes finish.",
        ],
        "time_complexity": "Depends on scheduling implementation",
        "space_complexity": "O(n)",
    },
    "ROUND_ROBIN": {
        "name": "Round Robin",
        "category": "CPU Scheduling",
        "steps": [
            "Place ready processes in a queue.",
            "Assign a fixed time quantum.",
            "Execute the first process for one quantum or until completion.",
            "Move unfinished processes to the queue's end.",
            "Repeat until all processes finish.",
        ],
        "time_complexity": "Depends on number of processes and time quantum",
        "space_complexity": "O(n)",
    },
    "BINARY_SEARCH": {
        "name": "Binary Search",
        "category": "Searching",
        "steps": [
            "Ensure the input array is sorted.",
            "Find the middle element.",
            "Compare the middle element with the target.",
            "If equal, return its position.",
            "If the target is smaller, search the left half.",
            "Otherwise, search the right half.",
            "Repeat until found or the search range becomes empty.",
        ],
        "time_complexity": "O(log n)",
        "space_complexity": "O(1) for iterative implementation",
    },
    "LINEAR_SEARCH": {
        "name": "Linear Search",
        "category": "Searching",
        "steps": [
            "Start from the first array element.",
            "Compare each element with the target.",
            "Return the position when a match is found.",
            "If no match exists, return not found.",
        ],
        "time_complexity": "O(n)",
        "space_complexity": "O(1)",
    },
}


KEYWORDS = {
    "FCFS": ["fcfs", "first come first served"],
    "SJF": ["sjf", "shortest job first"],
    "SRTF": ["srtf", "shortest remaining time first"],
    "ROUND_ROBIN": ["round robin", "round-robin", "rr scheduling"],
    "BINARY_SEARCH": ["binary search"],
    "LINEAR_SEARCH": ["linear search"],
}


def detect_algorithms(text: str) -> list:
    """Identify supported algorithms mentioned in text."""

    text = (text or "").lower()
    detected = []

    for algorithm_id, keywords in KEYWORDS.items():
        if any(re.search(r"(?<!\w)" + re.escape(word) + r"(?!\w)", text)
               for word in keywords):
            detected.append(algorithm_id)

    return detected


def explain_algorithm(algorithm_id: str) -> dict:
    """Return the step-by-step explanation of a supported algorithm."""

    algorithm_id = (algorithm_id or "").upper().replace(" ", "_")

    if algorithm_id not in ALGORITHM_DATABASE:
        return {
            "found": False,
            "message": "Algorithm not supported yet.",
        }

    return {
        "found": True,
        "algorithm_id": algorithm_id,
        **ALGORITHM_DATABASE[algorithm_id],
    }


def analyze_algorithms(text: str) -> dict:
    """Detect algorithms and return their explanations."""

    algorithm_ids = detect_algorithms(text)

    return {
        "algorithm_count": len(algorithm_ids),
        "algorithms": [
            explain_algorithm(algorithm_id)
            for algorithm_id in algorithm_ids
        ],
    }

def dry_run_binary_search(arr: list, target: int) -> dict:
    """Execute binary search and return each step."""

    if not arr:
        return {
            "found": False,
            "steps": [],
            "message": "Array cannot be empty."
        }

    if arr != sorted(arr):
        return {
            "found": False,
            "steps": [],
            "message": "Array must be sorted."
        }

    left = 0
    right = len(arr) - 1
    steps = []

    while left <= right:
        mid = (left + right) // 2

        steps.append({
            "left": left,
            "right": right,
            "middle": mid,
            "middle_value": arr[mid],
            "target": target
        })

        if arr[mid] == target:
            return {
                "found": True,
                "index": mid,
                "steps": steps,
                "message": f"Target found at index {mid}."
            }

        elif arr[mid] < target:
            left = mid + 1

        else:
            right = mid - 1

    return {
        "found": False,
        "steps": steps,
        "message": "Target not found."
    }
def simulate_cpu_scheduling(processes, algorithm, quantum=None):
    """
    Simulate FCFS, SJF, SRTF and Round Robin scheduling.

    processes format:
    [
        {"pid": "P1", "arrival": 0, "burst": 5},
        {"pid": "P2", "arrival": 1, "burst": 3}
    ]
    """

    algorithm = algorithm.upper().replace(" ", "_")

    supported = ["FCFS", "SJF", "SRTF", "ROUND_ROBIN"]

    if algorithm not in supported:
        return {"error": "Unsupported scheduling algorithm."}

    if not processes:
        return {"error": "At least one process is required."}

    if algorithm == "ROUND_ROBIN":
        if not isinstance(quantum, int) or isinstance(quantum, bool) or quantum <= 0:
            return {"error": "Round Robin requires a positive integer quantum."}

    data = []

    for process in processes:
        try:
            arrival = process["arrival"]
            burst = process["burst"]
            pid = str(process["pid"])
        except (KeyError, TypeError):
            return {"error": "Each process needs pid, arrival and burst."}

        if (not isinstance(arrival, int) or isinstance(arrival, bool)
                or not isinstance(burst, int) or isinstance(burst, bool)
                or arrival < 0 or burst <= 0 or not pid):
            return {"error": "Arrival must be non-negative and burst must be positive integers."}

        data.append({
            "pid": pid,
            "arrival": arrival,
            "burst": burst,
            "remaining": burst,
            "completion": 0,
            "first_start": None
        })

    if len({p["pid"] for p in data}) != len(data):
        return {"error": "Process IDs must be unique."}

    timeline = []
    time = 0

    def add_segment(pid, start, end):
        if start == end:
            return

        if timeline and timeline[-1]["pid"] == pid:
            timeline[-1]["end"] = end
        else:
            timeline.append({
                "pid": pid,
                "start": start,
                "end": end
            })

    if algorithm == "FCFS":
        ordered = sorted(data, key=lambda p: (p["arrival"], p["pid"]))

        for p in ordered:
            start = max(time, p["arrival"])
            if start > time:
                add_segment("IDLE", time, start)

            if p["first_start"] is None:
                p["first_start"] = start

            add_segment(p["pid"], start, start + p["burst"])
            time = start + p["burst"]
            p["completion"] = time

    elif algorithm == "SJF":
        completed = 0

        while completed < len(data):
            ready = [
                p for p in data
                if p["arrival"] <= time and p["completion"] == 0
            ]

            if not ready:
                next_arrival = min(
                    p["arrival"] for p in data if p["completion"] == 0
                )
                add_segment("IDLE", time, next_arrival)
                time = next_arrival
                continue

            p = min(ready, key=lambda x: (x["burst"], x["arrival"], x["pid"]))

            p["first_start"] = time
            add_segment(p["pid"], time, time + p["burst"])
            time += p["burst"]
            p["completion"] = time
            completed += 1

    elif algorithm == "SRTF":
        completed = 0

        while completed < len(data):
            ready = [
                p for p in data
                if p["arrival"] <= time and p["remaining"] > 0
            ]

            if not ready:
                next_arrival = min(
                    p["arrival"] for p in data if p["remaining"] > 0
                )
                add_segment("IDLE", time, next_arrival)
                time = next_arrival
                continue

            p = min(
                ready,
                key=lambda x: (x["remaining"], x["arrival"], x["pid"])
            )

            if p["first_start"] is None:
                p["first_start"] = time

            add_segment(p["pid"], time, time + 1)
            p["remaining"] -= 1
            time += 1

            if p["remaining"] == 0:
                p["completion"] = time
                completed += 1

    elif algorithm == "ROUND_ROBIN":
        from collections import deque

        ordered = sorted(data, key=lambda p: (p["arrival"], p["pid"]))
        ready_queue = deque()
        index = 0

        while index < len(ordered) or ready_queue:
            if not ready_queue and index < len(ordered):
                if time < ordered[index]["arrival"]:
                    add_segment("IDLE", time, ordered[index]["arrival"])
                    time = ordered[index]["arrival"]

                while index < len(ordered) and ordered[index]["arrival"] <= time:
                    ready_queue.append(ordered[index])
                    index += 1

            p = ready_queue.popleft()

            if p["first_start"] is None:
                p["first_start"] = time

            run_time = min(quantum, p["remaining"])
            start = time
            end = time + run_time

            add_segment(p["pid"], start, end)
            time = end
            p["remaining"] -= run_time

            while index < len(ordered) and ordered[index]["arrival"] <= time:
                ready_queue.append(ordered[index])
                index += 1

            if p["remaining"] > 0:
                ready_queue.append(p)
            else:
                p["completion"] = time

    results = []

    for p in data:
        turnaround = p["completion"] - p["arrival"]
        waiting = turnaround - p["burst"]
        response = p["first_start"] - p["arrival"]

        results.append({
            "pid": p["pid"],
            "arrival_time": p["arrival"],
            "burst_time": p["burst"],
            "completion_time": p["completion"],
            "turnaround_time": turnaround,
            "waiting_time": waiting,
            "response_time": response
        })

    count = len(results)

    return {
        "algorithm": algorithm,
        "gantt_chart": timeline,
        "process_results": results,
        "average_waiting_time": sum(p["waiting_time"] for p in results) / count,
        "average_turnaround_time": sum(p["turnaround_time"] for p in results) / count,
        "average_response_time": sum(p["response_time"] for p in results) / count
    }
