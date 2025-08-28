# akari-textscout/analyzer.py

import re

class TextAnalysis:
    """
    A simple class to perform basic analysis on a given text.
    """
    def __init__(self, text):
        if not isinstance(text, str):
            raise TypeError("Input must be a string.")
        self.text = text
        self.words = self._get_words()
        self.sentences = self._get_sentences()

    def _get_words(self):
        """Returns a list of words."""
        return re.findall(r'\b\w+\b', self.text.lower())

    def _get_sentences(self):
        """Returns a list of sentences."""
        # A simple regex to split by sentences, handling ., !, ?
        sentences = re.split(r'[.!?]+', self.text)
        return [s.strip() for s in sentences if s.strip()]

    def get_word_count(self):
        """Returns the total number of words."""
        return len(self.words)

    def get_character_count(self, with_spaces=True):
        """Returns the total number of characters."""
        if with_spaces:
            return len(self.text)
        else:
            return sum(len(word) for word in self.words)

    def get_sentence_count(self):
        """Returns the total number of sentences."""
        return len(self.sentences)

    def get_paragraph_count(self):
        """Returns the total number of paragraphs."""
        # Paragraphs are separated by one or more blank lines.
        paragraphs = [p for p in self.text.split('\n\n') if p.strip()]
        return len(paragraphs) if len(paragraphs) > 0 else 1

    def get_estimated_reading_time(self, wpm=200):
        """
        Returns the estimated reading time in minutes.
        wpm: Words per minute, average is around 200.
        """
        word_count = self.get_word_count()
        if word_count == 0:
            return 0.0
        return round(word_count / wpm, 2)

    def analyze(self):
        """Returns a dictionary with a full analysis."""
        return {
            "word_count": self.get_word_count(),
            "character_count": {
                "with_spaces": self.get_character_count(with_spaces=True),
                "without_spaces": self.get_character_count(with_spaces=False),
            },
            "sentence_count": self.get_sentence_count(),
            "paragraph_count": self.get_paragraph_count(),
            "estimated_reading_time_minutes": self.get_estimated_reading_time(),
        }