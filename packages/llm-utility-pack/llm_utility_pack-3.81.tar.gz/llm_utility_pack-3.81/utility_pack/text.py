from strive.reranker import Reranker, EmbeddingType, deduplicate_results
from compressor.semantic import compress_text as compress_text_semantic
import re, pickle, unicodedata, shortuuid, importlib, fasttext
from thefuzz import fuzz, process
from chonkie import TokenChunker
from markdown import markdown
from html import unescape
from typing import List
from enum import Enum

en_stopwords = pickle.load(open(str(importlib.resources.files('utility_pack').joinpath('resources/en_stopwords.pkl')), "rb"))
pt_stopwords = pickle.load(open(str(importlib.resources.files('utility_pack').joinpath('resources/pt_stopwords.pkl')), "rb"))

langdetect_model = fasttext.load_model(str(importlib.resources.files('utility_pack').joinpath('resources/lid.176.ftz')))

textual_reranker = None
semantic_reranker = None

def initialize_reranker():
    global textual_reranker, semantic_reranker
    textual_reranker = Reranker(embedding_type=EmbeddingType.TEXTUAL)
    semantic_reranker = Reranker(embedding_type=EmbeddingType.SEMANTIC)

def detect_language(text, force_en_pt=True):
    detected_lang = langdetect_model.predict(text.replace('\n', ' '), k=1)[0][0]
    if force_en_pt:
        return 'pt' if (str(detected_lang) == '__label__pt' or str(detected_lang) == 'portuguese') else 'en'

    return str(detected_lang).replace('__label__', '')

def get_uuid():
    return shortuuid.uuid()

def remove_stopwords(input_string, language="en"):
    """
    Removes stopwords from the input string.
    """
    if language == "en":
        stopwords = en_stopwords
    elif language == "pt":
        stopwords = pt_stopwords
    else:
        raise ValueError("Invalid language. Use 'en' or 'pt'.")
    return ' '.join([word for word in input_string.split() if word not in stopwords])

def remove_accents_replace(input_string):
    """
    Removes accents from characters by replacing them with their base character.
    Example: "á" becomes "a".
    """
    nfkd_form = unicodedata.normalize('NFKD', input_string)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])

def remove_accents_completely(input_string):
    """
    Removes accented characters entirely.
    Example: "á" becomes "".
    """
    return ''.join(c for c in input_string if c.isascii())

def remove_special_characters(input_string):
    """
    Removes special characters such as "!", "$", etc., leaving only alphanumeric and spaces.
    """
    return re.sub(r'[^a-zA-Z0-9\s]', '', input_string)

def remove_asian_characters(input_string):
    """
    Removes Asian characters (e.g., Japanese, Chinese, Korean).
    """
    return re.sub(r'[\u3000-\u9FFF\uAC00-\uD7AF]', '', input_string)

def remove_html_tags(input_string):
    """
    Removes HTML tags from the input string.
    """
    clean_text = re.sub(r'<[^>]+>', '', input_string)
    return unescape(clean_text)  # Unescape HTML entities like &amp;

def cleanup_markdown(input_string):
    """
    Converts Markdown to plain text by stripping formatting.
    """
    # Convert Markdown to HTML
    html = markdown(input_string)
    # Remove HTML tags
    return remove_html_tags(html)

def remove_extra_whitespace(input_string):
    """
    Removes extra whitespace, leaving only single spaces between words.
    """
    return re.sub(r'\s+', ' ', input_string).strip()

def remove_numbers(input_string):
    """
    Removes all numeric characters from the string.
    """
    return re.sub(r'\d+', '', input_string)

def remove_urls(input_string):
    """
    Removes URLs from the string.
    """
    return re.sub(r'https?://\S+|www\.\S+', '', input_string)

def remove_emails(input_string):
    """
    Removes email addresses from the string.
    """
    return re.sub(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', '', input_string)

def compress_text(input_string, compression_rate=0.5, reference_text_steering=None, target_token_count=None):
    """
    Compresses text using the Semantic Compressor.
    """
    try:
        return compress_text_semantic(
            input_string,
            compression_rate=compression_rate,
            reference_text_steering=reference_text_steering,
            target_token_count=target_token_count
        )
    except Exception:
        return input_string

class StringSimilarity(str, Enum):
    Ratio = "ratio"
    PartialRatio = "partial_ratio"
    TokenSortRatio = "token_sort_ratio"
    TokenSetRatio = "token_set_ratio"

def string_similarity(string1, string2, method: StringSimilarity = StringSimilarity.Ratio):
    """
    Calculates the similarity between two strings using fuzzy matching.
    """
    if method == StringSimilarity.Ratio:
        return fuzz.ratio(string1, string2)
    elif method == StringSimilarity.PartialRatio:
        return fuzz.partial_ratio(string1, string2)
    elif method == StringSimilarity.TokenSortRatio:
        return fuzz.token_sort_ratio(string1, string2)
    elif method == StringSimilarity.TokenSetRatio:
        return fuzz.token_set_ratio(string1, string2)
    else:
        raise ValueError("Invalid method.")

def string_similarity_from_list(reference_string: str, bag_of_strings: List[str], best_of: int = 1):
    """
    Calculates the similarity between a reference string and a bag of strings using fuzzy matching.
    """
    if best_of == 1:
        return process.extractOne(reference_string, bag_of_strings)
    else:
        return process.extract(reference_string, bag_of_strings, limit=best_of)

def find_needle_in_haystack(needle: str, haystack: List[str], best_of: int = 1):
    global textual_reranker, semantic_reranker
    if textual_reranker is None or semantic_reranker is None:
        initialize_reranker()
        
    textual_results = textual_reranker.rerank_documents(needle, haystack, top_k=50)
    semantic_results = semantic_reranker.rerank_documents(needle, haystack, top_k=50)
    merged_results = textual_results + semantic_results

    # Deduplicate the results
    return [result[0] for result in deduplicate_results(merged_results, top_k=best_of)]

def chunk_text(big_text: str, chunk_token_count: int = 500, overlap: int = 0):
    chunker = TokenChunker(
        tokenizer="gpt2",
        chunk_size=chunk_token_count,
        chunk_overlap=overlap
    )
    return [chunk.text for chunk in chunker(big_text)]
