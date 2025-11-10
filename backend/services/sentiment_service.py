import string

class SimpleSentimentService:
    """
    A simple, rule-based sentiment classification service.
    This is pluggable and can be replaced with a more complex ML model.
    """
    def __init__(self):
        # Simple keyword matching. Can be expanded significantly.
        self.positive_words = {
            "good", "great", "excellent", "amazing", "friendly", "polite",
            "clean", "safe", "fast", "easy", "love", "best", "happy"
        }
        self.negative_words = {
            "bad", "terrible", "horrible", "rude", "unprofessional", "dirty",
            "unsafe", "slow", "hard", "hate", "worst", "sad", "angry",
            "late", "dangerous"
        }
        # Emojis can also be included
        # self.positive_emojis = {"😊", "👍", "❤️"}
        # self.negative_emojis = {"😞", "👎", "😠"}

    def classify(self, text: str) -> float:
        """
        Classifies text and returns a score from 1 (very negative) to 5 (very positive).
        
        Algorithm:
        - Start at a neutral score of 3.0.
        - Add points for positive words, subtract for negative.
        - Clamp the result between 1.0 and 5.0.
        """
        if not text:
            return 3.0  # Neutral for empty feedback

        # Normalize text: lowercase, remove punctuation
        normalized_text = text.lower().translate(str.maketrans('', '', string.punctuation))
        words = set(normalized_text.split())

        score = 3.0  # Start neutral
        
        # Simple word counting
        positive_hits = len(words.intersection(self.positive_words))
        negative_hits = len(words.intersection(self.negative_words))

        # Adjust score. Each hit moves the score by 1.0.
        score_adjustment = positive_hits - negative_hits
        
        final_score = score + score_adjustment
        
        # Clamp the score between 1.0 and 5.0
        return max(1.0, min(5.0, final_score))