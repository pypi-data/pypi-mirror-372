from typing import Tuple


def get_correct_indices(indices: str, max_count: int = 0) -> Tuple[int, ...]:
    """
    Convert arbitrary table or column indices from a string (e.g., "1, 3, 5-8, 10-end") to
    a tuple of correct integer indexes (e.g., (1, 3, 5, 6, 7, 8, 10, ...)).
    """
    correct_indices = []
    for item in indices.replace(" ", "").split(","):
        index_range = item.split("-")
        count = len(index_range)
        if count == 2:
            start, end = map(str, index_range)
            if start.isnumeric() and end.isnumeric():
                for index in range(int(start) - 1, int(end)):
                    correct_indices.append(index)
            if start.isnumeric() and end == "end":
                for index in range(int(start) - 1, max_count):
                    correct_indices.append(index)
        if count == 1 and index_range[0].isnumeric():
            correct_indices.append(int(index_range[0]) - 1)
    return tuple(correct_indices)
