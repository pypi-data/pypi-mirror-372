from sklearn.feature_extraction.text import HashingVectorizer
from onnxruntime_extensions import get_library_path
import importlib.resources
import onnxruntime as ort
from os import cpu_count
from enum import Enum

onnx_model_path = str(importlib.resources.files('utility_pack').joinpath('resources/embedding-model/universal_sentence_encoder_quantized.onnx'))

_options = None
_providers = ["CPUExecutionProvider"]
onnx_model = None
cpu_core_count = None

class EmbeddingType(Enum):
    TEXTUAL = 1
    SEMANTIC = 2

def _initialize_onnx():
    global _options, onnx_model, cpu_core_count
    cpu_core_count = cpu_count()
    _options = ort.SessionOptions()
    _options.inter_op_num_threads, _options.intra_op_num_threads = cpu_core_count, cpu_core_count
    _options.register_custom_ops_library(get_library_path())
    onnx_model = ort.InferenceSession(
        path_or_bytes = onnx_model_path,
        sess_options=_options,
        providers=_providers
    )

def _get_textual_embeddings(texts, ngram_range=(2, 6), analyzer='char', n_features=512):
    vectorizer = HashingVectorizer(ngram_range=ngram_range, analyzer=analyzer, n_features=n_features)
    return vectorizer.transform(texts).toarray().tolist()

def _get_onnx_embeddings(texts):
    global onnx_model
    if onnx_model is None:
        _initialize_onnx()
    return onnx_model.run(output_names=["outputs"], input_feed={"inputs": texts})[0].tolist()

def extract_embeddings(texts, embedding_type=EmbeddingType.TEXTUAL):
    if embedding_type == EmbeddingType.TEXTUAL:
        return _get_textual_embeddings(texts)
    elif embedding_type == EmbeddingType.SEMANTIC:
        return _get_onnx_embeddings(texts)
    else:
        raise ValueError(f"Invalid embedding type: {embedding_type}")
