"""
Business logic for Typing Speed Tester
Handles calculations, validations, and text generation
"""

import random
from typing import Dict, List, Tuple
from datetime import datetime

class TypingLogic:
    
    # Text samples for different difficulty levels
    EASY_TEXTS = [
        "The quick brown fox jumps over the lazy dog.",
        "A cat sat on a mat and looked at the rat.",
        "The sun is bright and the sky is blue today.",
        "Dogs are loyal pets that love to play outside.",
        "I like to read books in the quiet library.",
        "The big red ball bounced down the long hill.",
        "She has a nice house with a beautiful garden.",
        "We went to the park to have a fun picnic.",
        "The old tree has many green leaves on it.",
        "My friend gave me a gift for my birthday party."
    ]
    
    MEDIUM_TEXTS = [
        "Programming requires patience, practice, and problem-solving skills to master effectively.",
        "The ancient civilizations built remarkable structures that still stand today as monuments.",
        "Climate change affects weather patterns globally, impacting agriculture and ecosystems worldwide.",
        "Technology advances rapidly, transforming how we communicate, work, and learn every day.",
        "Healthy eating habits combined with regular exercise contribute to better physical wellness.",
        "Literature provides insight into different cultures, perspectives, and historical time periods.",
        "Financial planning involves budgeting, saving, investing, and preparing for future expenses.",
        "Scientific research expands our understanding of nature, medicine, and the universe itself.",
        "Effective communication skills are essential for success in both personal and professional life.",
        "Learning new languages opens doors to different cultures and enhances cognitive abilities."
    ]
    
    HARD_TEXTS = [
        "Quantum mechanics revolutionized physics by introducing probabilistic interpretations of subatomic phenomena, challenging classical deterministic frameworks.",
        "Neuroplasticity demonstrates the brain's remarkable ability to reorganize itself by forming new neural connections throughout life.",
        "Cryptocurrency utilizes blockchain technology to enable decentralized, transparent, and secure peer-to-peer transactions globally.",
        "Anthropological studies reveal how cultural practices, social structures, and belief systems evolve across different societies.",
        "Biotechnology integrates biological systems with engineering principles to develop innovative solutions for medical challenges.",
        "Epistemology explores the nature, origin, and limits of human knowledge through philosophical inquiry and analysis.",
        "Macroeconomic policies influence inflation rates, employment levels, and overall economic stability within nations.",
        "Computational linguistics combines artificial intelligence with natural language processing to understand human communication patterns.",
        "Astrophysics investigates celestial phenomena, including stellar evolution, galactic dynamics, and cosmological theories of universe.",
        "Geopolitical tensions arise from competing national interests, resource distribution, and ideological differences between states."
    ]
    
    @staticmethod
    def get_random_text(difficulty: str = "medium") -> str:
        """Get a random text based on difficulty level"""
        difficulty = difficulty.lower()
        
        if difficulty == "easy":
            return random.choice(TypingLogic.EASY_TEXTS)
        elif difficulty == "hard":
            return random.choice(TypingLogic.HARD_TEXTS)
        else:  # medium
            return random.choice(TypingLogic.MEDIUM_TEXTS)
    
    @staticmethod
    def calculate_wpm(text_length: int, time_seconds: float) -> float:
        """
        Calculate Words Per Minute (WPM)
        Standard: 5 characters = 1 word
        """
        if time_seconds <= 0:
            return 0.0
        
        words = text_length / 5.0
        minutes = time_seconds / 60.0
        wpm = words / minutes
        
        return round(wpm, 2)
    
    @staticmethod
    def calculate_accuracy(original_text: str, typed_text: str) -> Tuple[float, int, int]:
        """
        Calculate typing accuracy
        Returns: (accuracy_percentage, correct_chars, total_chars)
        """
        if not original_text:
            return 100.0, 0, 0
        
        correct_chars = 0
        total_chars = len(original_text)
        
        # Compare character by character
        for i in range(min(len(original_text), len(typed_text))):
            if original_text[i] == typed_text[i]:
                correct_chars += 1
        
        # Penalty for length mismatch
        if len(typed_text) < len(original_text):
            # Incomplete typing
            accuracy = (correct_chars / total_chars) * 100
        else:
            # Extra characters typed (considered errors)
            extra_chars = len(typed_text) - len(original_text)
            total_chars_considered = len(original_text) + extra_chars
            accuracy = (correct_chars / total_chars_considered) * 100
        
        return round(accuracy, 2), correct_chars, total_chars
    
    @staticmethod
    def get_character_comparison(original_text: str, typed_text: str) -> List[Dict[str, any]]:
        """
        Compare texts character by character
        Returns list of dicts with character status
        """
        comparison = []
        max_length = max(len(original_text), len(typed_text))
        
        for i in range(max_length):
            original_char = original_text[i] if i < len(original_text) else ""
            typed_char = typed_text[i] if i < len(typed_text) else ""
            
            if original_char == typed_char:
                status = "correct"
            elif typed_char == "":
                status = "missing"
            elif original_char == "":
                status = "extra"
            else:
                status = "incorrect"
            
            comparison.append({
                "index": i,
                "original": original_char,
                "typed": typed_char,
                "status": status
            })
        
        return comparison
    
    @staticmethod
    def validate_test_result(wpm: float, accuracy: float) -> Tuple[bool, str]:
        """
        Validate test results
        Returns: (is_valid, error_message)
        """
        if wpm < 0:
            return False, "WPM cannot be negative"
        
        if wpm > 300:
            return False, "WPM seems unrealistically high (>300)"
        
        if accuracy < 0 or accuracy > 100:
            return False, "Accuracy must be between 0 and 100"
        
        return True, ""
    
    @staticmethod
    def get_performance_rating(wpm: float, accuracy: float) -> str:
        """Get performance rating based on WPM and accuracy"""
        if accuracy < 80:
            return "Poor - Focus on accuracy first"
        elif accuracy < 90:
            rating = "Fair - Good progress, keep practicing"
        else:
            if wpm < 20:
                rating = "Beginner - Great start!"
            elif wpm < 40:
                rating = "Intermediate - Nice progress!"
            elif wpm < 60:
                rating = "Advanced - Excellent typing!"
            elif wpm < 80:
                rating = "Expert - Outstanding speed!"
            else:
                rating = "Master - Incredible performance!"
        
        return rating
    
    @staticmethod
    def calculate_progress(current_wpm: float, previous_wpm: float) -> Dict[str, any]:
        """Calculate progress between tests"""
        if previous_wpm == 0:
            return {
                "improvement": 0.0,
                "percentage": 0.0,
                "message": "First test - baseline established!"
            }
        
        improvement = current_wpm - previous_wpm
        percentage = (improvement / previous_wpm) * 100
        
        if improvement > 0:
            message = f"Improved by {abs(improvement):.2f} WPM! Keep it up!"
        elif improvement < 0:
            message = f"Decreased by {abs(improvement):.2f} WPM. Don't worry, practice makes perfect!"
        else:
            message = "Same speed. Keep practicing!"
        
        return {
            "improvement": round(improvement, 2),
            "percentage": round(percentage, 2),
            "message": message
        }
    
    @staticmethod
    def get_typing_tips(wpm: float, accuracy: float) -> List[str]:
        """Get personalized typing tips"""
        tips = []
        
        if accuracy < 85:
            tips.append("Focus on accuracy before speed - slow down and type correctly")
            tips.append("Look at the keyboard less and keep your eyes on the screen")
        
        if wpm < 30:
            tips.append("Practice proper finger placement on home row keys (ASDF JKL;)")
            tips.append("Start with simple texts and gradually increase difficulty")
        
        if wpm >= 30 and wpm < 50:
            tips.append("Try to maintain a steady rhythm while typing")
            tips.append("Practice common word patterns and combinations")
        
        if wpm >= 50:
            tips.append("Challenge yourself with harder texts to improve further")
            tips.append("Work on your weakest keys and combinations")
        
        if accuracy >= 95 and wpm >= 60:
            tips.append("You're doing great! Try typing without looking at the keyboard")
            tips.append("Experiment with different typing techniques to increase speed")
        
        return tips if tips else ["Keep practicing regularly to improve!"]
    
    @staticmethod
    def format_time(seconds: float) -> str:
        """Format seconds into readable time string"""
        if seconds < 60:
            return f"{seconds:.1f}s"
        else:
            minutes = int(seconds // 60)
            remaining_seconds = seconds % 60
            return f"{minutes}m {remaining_seconds:.1f}s"
    
    @staticmethod
    def calculate_estimated_time(text: str, avg_wpm: float) -> float:
        """Estimate time to complete text based on average WPM"""
        if avg_wpm <= 0:
            avg_wpm = 40  # Default average WPM
        
        words = len(text) / 5.0
        minutes = words / avg_wpm
        seconds = minutes * 60
        
        return round(seconds, 1)