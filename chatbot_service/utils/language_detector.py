from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
from typing import Optional

class LanguageDetector:
    def __init__(self):
        self.supported_languages = {'en', 'ar'}
        self.default_language = 'en'
    
    def detect_language(self, text: str) -> str:
        """Detect language of the input text"""
        try:
            # Clean text for better detection
            cleaned_text = self._clean_text(text)
            
            if not cleaned_text:
                return self.default_language
            
            # Detect language
            detected = detect(cleaned_text)
            
            # Map detected language to supported languages
            if detected in self.supported_languages:
                return detected
            else:
                # Default fallback
                return self.default_language
                
        except LangDetectException:
            # If detection fails, return default
            return self.default_language
        except Exception as e:
            print(f"Language detection error: {e}")
            return self.default_language
    
    def _clean_text(self, text: str) -> str:
        """Clean text for better language detection"""
        if not text:
            return ""
        
        # Remove extra whitespace
        cleaned = " ".join(text.split())
        
        # Remove very short texts that might cause detection issues
        if len(cleaned) < 3:
            return ""
        
        return cleaned
    
    def is_arabic(self, text: str) -> bool:
        """Check if text contains Arabic characters"""
        arabic_range = range(0x0600, 0x06FF + 1)  # Arabic Unicode range
        return any(ord(char) in arabic_range for char in text)
    
    def is_english(self, text: str) -> bool:
        """Check if text contains primarily English characters"""
        english_chars = sum(1 for char in text if char.isalpha() and ord(char) < 128)
        total_chars = sum(1 for char in text if char.isalpha())
        
        if total_chars == 0:
            return True  # Default to English for non-alphabetic text
        
        return (english_chars / total_chars) > 0.7
    
    def get_language_confidence(self, text: str) -> dict:
        """Get language detection with confidence scores"""
        try:
            from langdetect import detect_langs
            
            cleaned_text = self._clean_text(text)
            if not cleaned_text:
                return {'en': 1.0}
            
            detected_langs = detect_langs(cleaned_text)
            
            # Convert to dictionary with supported languages only
            result = {}
            for lang_obj in detected_langs:
                if lang_obj.lang in self.supported_languages:
                    result[lang_obj.lang] = lang_obj.prob
            
            # If no supported language detected, default to English
            if not result:
                result = {'en': 1.0}
            
            return result
            
        except Exception as e:
            print(f"Language confidence detection error: {e}")
            return {'en': 1.0}
