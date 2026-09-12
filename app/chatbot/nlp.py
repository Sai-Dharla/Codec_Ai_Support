import re
import sys
import string
import types
from typing import List, Set, Tuple

# Safe regex compatibility layer for environments where C-extension DLLs might be restricted
if 'regex' not in sys.modules or not hasattr(sys.modules['regex'], 'compile'):
    try:
        import regex
    except (ImportError, OSError):
        class _SafeRegexModule:
            def compile(self, pattern, *args, **kwargs):
                # Map \p{L}\p{N} to standard Unicode \w equivalents for standard re library
                cleaned_pat = (
                    pattern.replace(r'[^\p{L}\p{N}]', r'[^\w]')
                           .replace(r'[\p{L}\p{N}]', r'[\w]')
                           .replace(r'\p{L}', r'[a-zA-Z]')
                           .replace(r'\p{N}', r'[0-9]')
                )
                return re.compile(cleaned_pat, *args, **kwargs)
            def __getattr__(self, name):
                return getattr(re, name)
        sys.modules['regex'] = _SafeRegexModule()

import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag

def ensure_nltk_resources():
    """Downloads necessary NLTK datasets if not already present."""
    required_packages = ['punkt', 'stopwords', 'wordnet', 'averaged_perceptron_tagger', 'punkt_tab']
    for pkg in required_packages:
        try:
            nltk.data.find(f'tokenizers/{pkg}' if 'punkt' in pkg else f'corpora/{pkg}' if pkg in ['stopwords', 'wordnet'] else f'taggers/{pkg}')
        except LookupError:
            try:
                nltk.download(pkg, quiet=True)
            except Exception:
                pass

class NLPProcessor:
    """NLTK-powered NLP preprocessing and token analysis pipeline."""
    def __init__(self):
        ensure_nltk_resources()
        self.lemmatizer = WordNetLemmatizer()
        try:
            self.stop_words = set(stopwords.words('english'))
        except Exception:
            self.stop_words = {
                'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', 'as', 'at',
                'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', 'could', 'did',
                'do', 'does', 'doing', 'down', 'during', 'each', 'few', 'for', 'from', 'further', 'had', 'has', 'have',
                'having', 'he', 'her', 'here', 'hers', 'herself', 'him', 'himself', 'his', 'how', 'i', 'if', 'in', 'into',
                'is', 'it', 'its', 'itself', 'just', 'me', 'more', 'most', 'my', 'myself', 'no', 'nor', 'not', 'now',
                'of', 'off', 'on', 'once', 'only', 'or', 'other', 'our', 'ours', 'ourselves', 'out', 'over', 'own',
                's', 'same', 'she', 'should', 'so', 'some', 'such', 't', 'than', 'that', 'the', 'their', 'theirs',
                'them', 'themselves', 'then', 'there', 'these', 'they', 'this', 'those', 'through', 'to', 'too', 'under',
                'until', 'up', 'very', 'was', 'we', 'were', 'what', 'when', 'where', 'which', 'while', 'who', 'whom',
                'why', 'will', 'with', 'you', 'your', 'yours', 'yourself', 'yourselves'
            }

    def clean_text(self, text: str) -> str:
        """Sanitizes and normalizes input text."""
        if not text:
            return ""
        text = text.strip().lower()
        # Remove repeated punctuation
        text = re.sub(r'([!?.])\1+', r'\1', text)
        return text

    def tokenize(self, text: str) -> List[str]:
        """Tokenizes text using NLTK word_tokenize with regex fallback."""
        cleaned = self.clean_text(text)
        if not cleaned:
            return []
        try:
            return word_tokenize(cleaned)
        except Exception:
            return re.findall(r'\b\w+\b', cleaned)

    def extract_keywords(self, text: str) -> List[str]:
        """Extracts normalized lemmatized keywords excluding punctuation and stopwords."""
        tokens = self.tokenize(text)
        keywords = []
        for token in tokens:
            if token not in string.punctuation and token not in self.stop_words and len(token) > 1:
                try:
                    lemmatized = self.lemmatizer.lemmatize(token)
                except Exception:
                    lemmatized = token
                keywords.append(lemmatized)
        return keywords

    def pos_tagging(self, text: str) -> List[Tuple[str, str]]:
        """Extracts Part-of-Speech tags for input text using NLTK pos_tag."""
        tokens = self.tokenize(text)
        try:
            return pos_tag(tokens)
        except Exception:
            return [(token, 'NOUN') for token in tokens]

    def compute_token_overlap(self, query_tokens: List[str], target_tokens: List[str]) -> float:
        """Calculates Jaccard overlap similarity between two token sets."""
        if not query_tokens or not target_tokens:
            return 0.0
        set_q = set(query_tokens)
        set_t = set(target_tokens)
        intersection = set_q.intersection(set_t)
        union = set_q.union(set_t)
        return len(intersection) / len(union) if union else 0.0

