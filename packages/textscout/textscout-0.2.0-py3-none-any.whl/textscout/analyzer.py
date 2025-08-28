import re
from collections import Counter

# A simple set of English stop words
DEFAULT_STOP_WORDS = set([
    'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until',
    'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between',
    'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to',
    'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again',
    'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how',
    'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some',
    'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too',
    'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now', 'is', 'are'
])


class TextAnalysis:
    """
    Performs basic and advanced analysis on a given text.
    Version 2.0
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
        sentences = re.split(r'[.!?]+', self.text)
        return [s.strip() for s in sentences if s.strip()]

    def _count_syllables(self, word):
        """A simple heuristic to count syllables in a word."""
        word = word.lower()
        count = len(re.findall(r'[aeiouy]+', word))
        if word.endswith('e'):
            count -= 1
        if word.endswith('le') and len(word) > 2 and word[-3] not in 'aeiouy':
            count += 1
        if count == 0:
            count = 1
        return count

    def get_word_count(self):
        """Returns the total number of words."""
        return len(self.words)

    def get_sentence_count(self):
        """Returns the total number of sentences."""
        return len(self.sentences)

    def get_flesch_reading_ease(self):
        """
        Returns the Flesch Reading Ease score.
        Higher scores indicate easier to read text.
        90-100: Very easy (5th grader)
        60-70: Plain English (8th-9th grader)
        0-30: Very difficult (college graduate)
        """
        word_count = self.get_word_count()
        sentence_count = self.get_sentence_count()
        if word_count == 0 or sentence_count == 0:
            return 0.0

        total_syllables = sum(self._count_syllables(word) for word in self.words)

        score = 206.835 - 1.015 * (word_count / sentence_count) - 84.6 * (total_syllables / word_count)
        return round(score, 2)

    def get_word_frequency(self, n=10, use_stop_words=True):
        """
        Returns the N most common words and their counts.
        :param n: Number of top words to return.
        :param use_stop_words: If True, filters out common English stop words.
        """
        words_to_count = self.words
        if use_stop_words:
            words_to_count = [word for word in self.words if word not in DEFAULT_STOP_WORDS]

        return Counter(words_to_count).most_common(n)

    def analyze(self):
        """Returns a dictionary with a full analysis."""
        base_analysis = {
            "word_count": self.get_word_count(),
            "sentence_count": self.get_sentence_count(),
            "estimated_reading_time_minutes": round(self.get_word_count() / 200, 2)
        }

        # New features for 2.0
        advanced_analysis = {
            "flesch_reading_ease_score": self.get_flesch_reading_ease(),
            "word_frequency_top_10": self.get_word_frequency(n=10)
        }

        # Combine dictionaries
        base_analysis.update(advanced_analysis)
        return base_analysis