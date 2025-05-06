"""
Custom NLP utilities for the Motion Q&A application.
Provides fallbacks when NLTK or other NLP libraries are not available.
"""

import re
from typing import List


def custom_sent_tokenize(text: str) -> List[str]:
    """
    Simple sentence tokenizer that splits text on common sentence delimiters.
    Used as a fallback when NLTK's punkt tokenizer is not available.
    """
    if not text:
        return []
        
    # Replace common patterns that might cause incorrect splits
    text = re.sub(r'(\w\.\w\.)', r'\1_DOT_', text)  # e.g., U.S. -> U.S_DOT_
    text = re.sub(r'(\w\.\w\.)', r'\1_DOT_', text)  # double pass for nested cases
    text = re.sub(r'(Mr\.|Mrs\.|Dr\.|Prof\.)', r'\1_DOT_', text)
    text = re.sub(r'(Inc\.|Ltd\.|Co\.)', r'\1_DOT_', text)
    text = re.sub(r'(\d+\.\d+)', r'\1_DOT_', text)  # e.g., 3.14 -> 3.14_DOT_
    
    # Split on sentence delimiters
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    # Restore original dots
    sentences = [s.replace('_DOT_', '.') for s in sentences]
    
    # Filter out empty sentences
    return [s for s in sentences if s.strip()]


def custom_tokenize(text: str) -> List[str]:
    """
    Simple word tokenizer that splits text on whitespace and punctuation.
    Used as a fallback when more sophisticated tokenizers are not available.
    """
    if not text:
        return []
        
    # Convert to lowercase and remove excess whitespace
    text = text.lower().strip()
    
    # Replace punctuation with spaces
    for char in '.,;:!?()[]{}"\'':
        text = text.replace(char, ' ')
    
    # Split on whitespace and filter out empty tokens
    return [token for token in text.split() if token]


def get_stopwords() -> List[str]:
    """
    Returns a list of common English stopwords.
    Used as a fallback when NLTK stopwords are not available.
    """
    return [
        'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 
        'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between',
        'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to',
        'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again',
        'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how',
        'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some',
        'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too',
        'very', 'will', 'just', 'should', 'now', 'be', 'is', 'are', 'was', 'were',
        'have', 'has', 'had', 'do', 'does', 'did', 'can', 'could', 'would', 'may',
        'might', 'must', 'shall', 'should', 'what', 'which', 'who', 'whom',
        'this', 'that', 'these', 'those', 'i', 'me', 'my', 'myself', 'we', 'our',
        'ours', 'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves',
        'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it',
        'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves'
    ] 