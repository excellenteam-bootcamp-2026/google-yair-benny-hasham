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
        # Highest score first, and ties are broken alphabetically
        return (-self.score, self.completed_sentence)
