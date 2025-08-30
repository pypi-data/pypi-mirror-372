"""
LoSearch - Advanced Persian/English Search Engine
سیستم جستجوی پیشرفته فارسی/انگلیسی با سرعت بالا
"""

from .core.engine import LoSearchEngine
from .utils.text_processor import TextProcessor

class LoSearch:
    """
    LoSearch - High-Performance Search Engine
    موتور جستجوی پرسرعت با دقت بالا
    """
    
    def __init__(self, enable_optimization: bool = True):
        """Initialize LoSearch engine"""
        self.engine = LoSearchEngine(enable_optimization=enable_optimization)
        self.text_processor = TextProcessor()
        
    def add_documents(self, documents: list) -> dict:
        """Add documents to search index"""
        return self.engine.add_documents(documents)
    
    def search(self, query: str, limit: int = 10) -> list:
        """Fast search with all optimizations"""
        return self.engine.search(query, limit=limit)
    
    def smart_search(self, query: str, documents: list = None, limit: int = 10) -> dict:
        """Intelligent search with auto-correction and analysis"""
        return self.engine.smart_search(query, documents, limit=limit)
    
    def analyze_text(self, text: str) -> dict:
        """Complete text analysis"""
        return self.text_processor.analyze_text(text)
    
    def fix_query(self, query: str, documents: list = None) -> dict:
        """Query correction and suggestions"""
        return self.engine.fix_query(query, documents)
    
    def contextual_search(self, query: str, documents: list = None, limit: int = 10, mode: str = 'simple', top_sentences: int = 3) -> dict:
        """Contextual search with sentence extraction"""
        return self.engine.contextual_search(query, documents, limit=limit, mode=mode, top_sentences=top_sentences)
    
    def contextual_search_with_scores(self, query: str, documents: list = None, limit: int = 10, mode: str = 'simple', top_sentences: int = 3) -> dict:
        """Contextual search with sentence scores"""
        return self.engine.contextual_search_with_scores(query, documents, limit=limit, mode=mode, top_sentences=top_sentences)

# Simple functions for direct use
def search(query: str, documents: list, limit: int = 10):
    """Simple search function"""
    engine = LoSearch()
    engine.add_documents(documents)
    return engine.search(query, limit=limit)

def smart_search(query: str, documents: list = None, limit: int = 10):
    """Smart search with all features"""
    engine = LoSearch()
    if documents:
        engine.add_documents(documents)
    return engine.smart_search(query, documents, limit=limit)

def analyze_text(text: str):
    """Text analysis function"""
    engine = LoSearch()
    return engine.analyze_text(text)

__version__ = "0.1.2"
__all__ = [
    'LoSearch',
    'TextProcessor',
    'search',
    'smart_search', 
    'analyze_text'
]