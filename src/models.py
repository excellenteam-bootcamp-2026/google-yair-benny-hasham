from dataclasses import dataclass


@dataclass
class AutoCompleteData:
    completed_sentence: str
    source_text: str
    offset: int
    score: int

    def __str__(self):
        return f"{self.completed_sentence} ({self.source_text} {self.offset})"

    def sort_key(self):
        # Higher score first, and alphabetical order in case of a tie
        return (-self.score, self.completed_sentence)
