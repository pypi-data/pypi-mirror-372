This is a collection of utility functions and decorators that can be used in various projects.

## 1\. Utility Decorators

This module provides a collection of useful decorators for caching, disk-based caching, and retrying function executions.

**How to Import:**

`from utility_pack.decorators import <DecoratorName>`

---

### `timed_lru_cache`

Caches function results in memory with a time-based expiration and LRU eviction policy.

```python
from utility_pack.decorators import timed_lru_cache
import time

@timed_lru_cache(max_size=2, minutes=5)  # Max 2 items, expire after 5 minutes
def expensive_operation(arg):
    print("Calculating...")
    time.sleep(1)  # Simulate a slow operation
    return arg * 2

print(expensive_operation(5))  # Calculates and prints 10
print(expensive_operation(5))  # Returns cached result (10) immediately
```

### `disk_lru_cache`

Caches function results to disk using a LRU eviction policy. This is useful for persisting results across multiple program invocations or in situations where in-memory caching is insufficient. Note that the function's return value MUST be pickleable.  
The disk caching implementation relies on `cloudpickle`, allowing for a wider range of Python objects (including lambdas, functions, and classes) to be serialized and cached, which the standard `pickle` module does not support.

```python
from utility_pack.decorators import disk_lru_cache
import os

@disk_lru_cache(max_size=2, cache_file="my_cache.pkl")
def another_expensive_operation(arg):
    print("Calculating from Disk...")
    return arg * 3

print(another_expensive_operation(4))  # Calculates and prints 12, saves to disk
print(another_expensive_operation(4))  # Retrieves from disk cache (12)
os.remove("my_cache.pkl") #cleanup
```

### `custom_lru_cache`

Same as python's native `lru_cache`, but with a custom implementation that allows to cache more complex data structures, via an interna hashing mechanism.

```python
from utility_pack.decorators import custom_lru_cache
import os

@custom_lru_cache(max_size=100)
def another_expensive_operation(arg):
    print("Calculating from Disk...")
    return arg * 3

print(another_expensive_operation(4))  # Calculates and prints 12, saves to cache
print(another_expensive_operation(4))  # Retrieves from cache
```

---

### `retry`

Retries a function execution a specified number of times if it raises an exception.

```python
from utility_pack.decorators import retry

@retry(retry_count=3, delay=0.5) # Retry thrice, delayed 0.5 seconds between attempts
def flaky_function():
    import random
    if random.random() < 0.5:
        raise ValueError("Something went wrong!")
    return "Success!"

print(flaky_function())
```

## 2\. Embeddings

### `utility_pack.embeddings` Module

This module provides functionalities for extracting text embeddings using different methods. It includes options for both textual (character-based n-grams) and semantic (ONNX transformer model based) embeddings.

To import the functionalities, use the following pattern: `from utility_pack.embeddings import <function_or_class_name>`

### `extract_embeddings` Function

This function is the main entry point for extracting embeddings. It takes a list of texts and an optional `embedding_type` argument to specify the desired embedding method.

```python
from utility_pack.embeddings import extract_embeddings, EmbeddingType

texts = ["This is a sample text.", "Another sample text."]

# Example: Extracting textual embeddings
textual_embeddings = extract_embeddings(texts, embedding_type=EmbeddingType.TEXTUAL)
print(f"Textual embeddings shape: {len(textual_embeddings), len(textual_embeddings[0])}")

# Example: Extracting semantic embeddings
semantic_embeddings = extract_embeddings(texts, embedding_type=EmbeddingType.SEMANTIC)
print(f"Semantic embeddings shape: {len(semantic_embeddings), len(semantic_embeddings[0])}")
```

**Parameters:**

*   `texts`: A list of strings to be embedded.
*   `embedding_type`: An `EmbeddingType` enum value specifying the desired embedding method (default: `EmbeddingType.TEXTUAL`).

**Returns:**

A list of embeddings represented as lists of floats. The format depends on the `embedding_type`.

## `Textual Embeddings` using HashingVectorizer

Implements character-based n-gram embeddings using scikit-learn's `HashingVectorizer`.

```python
from utility_pack.embeddings import extract_embeddings, EmbeddingType

texts = ["Simple and short text.", "Another short sample."]
textual_embeddings = extract_embeddings(texts, embedding_type=EmbeddingType.TEXTUAL)
print(f"Textual embeddings for short texts: {len(textual_embeddings), len(textual_embeddings[0])}")
```

## `Semantic Embeddings` using ONNX Transformer Model

Leverages a pre-trained ONNX transformer model to generate semantic embeddings. It uses a provided tokenizer to tokenize the input text and utilizes the ONNX runtime for inference. It first compresses the text (if longer than 500 tokens) with `compress_text` and then feeds to the transformer model.

```python
from utility_pack.embeddings import extract_embeddings, EmbeddingType

texts = ["A longer sentence for semantic analysis.", "Another example of a moderately long sentence."]
semantic_embeddings = extract_embeddings(texts, embedding_type=EmbeddingType.SEMANTIC)
print(f"Semantic embeddings for moderately long sentences {len(semantic_embeddings), len(semantic_embeddings[0])}")  #  len(semantic_embeddings) equal total texts.
```

## 3\. Interact with LLMs

### `utility_pack.llm`

This module provides functions to interact with LLMs from OpenRouter, Ollama, vLLM, and OpenAI. It supports chat and prompt formats, both streaming and non-streaming.

```python
# Functions that iteract with LLMs, based on environment variables

# PROVIDER: which provider to use, must be one of ['openrouter', 'ollama', 'vllm', 'openai']
# OPENROUTER_KEY
# OLLAMA_HOST, defaults to http://127.0.0.1:11434
# VLLM_URL, defaults to http://127.0.0.1:8000
# OPENAI_API_KEY

from utility_pack.llm import llm_chat, llm_prompt, llm_chat_async, llm_prompt_async, llm_prompt_stream, llm_chat_stream
```

### Classify Question (Generic or Directed)

Classifies a question as either "generic" or "directed" using a pre-trained ONNX model.

```python
from utility_pack.llm import classify_question_generic_or_directed
question = "What is the meaning of life?"
classification = classify_question_generic_or_directed(question)
print(f"The question is classified as: {classification}")
```

### Passage Re-ranking

Re-ranks a list of passages based on their relevance to a given question using a pre-trained ONNX model.

```python
from utility_pack.llm import rerank
question = "What are the benefits of exercise?"
passages = [
    "Exercise improves cardiovascular health.",
    "Eating a balanced diet is important for overall well-being.",
    "Regular exercise can help reduce stress and improve mood."
]
ranked_passages = rerank(question, passages)
for passage, score in ranked_passages:
    print(f"Passage: {passage}, Score: {score}")
```

## 4\. Logging

This module provides utility functions for logging exceptions with detailed information, including date/time in Brasilia time zone, filename, function name, line number, stack trace and parameters.

To import this module:

```python
from utility_pack.logger import get_datetime_brasilia, log_exception
```

### `get_datetime_brasilia()`

Returns the current date and time in the "America/Sao\_Paulo" timezone (Brasilia) formatted as a string.

**Example:**

```python
from utility_pack.logger import get_datetime_brasilia

current_time = get_datetime_brasilia()
print(current_time) # Output: e.g., 20/10/2023 - 15:30:45
```

### `log_exception()`

Logs an exception along with detailed context information - Brasilia datetime, filename, function name, line number, full stack trace and function arguments up to 100 characters. The error message is logged using the Python `logging` module at the ERROR level. This is intended to be called inside an `except` block.

**Example:**

```python
from utility_pack.logger import log_exception

def some_function(a, b):
    try:
        result = a / b
        return result
    except ZeroDivisionError:
        log_exception()

result = some_function(10, 0)
print(result) # Output (in console): None

# Will print out the exception in high detail automatically
```

## 5\. ML

### `timeseries_forecast`

Creates a time series forecast using the Prophet model.

**Parameters:**

*   `dates` (list): List of dates. Should be compatible with Prophet's date format.
*   `values` (list): List of corresponding numerical values.
*   `num_forecast_periods` (int, optional): Number of periods to forecast into the future. Defaults to 30.

**Returns:**

*   `list`: A list of forecasted values for the specified number of periods.

**Example:**

```python
from utility_pack.ml import timeseries_forecast
dates = ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05']
values = [10, 12, 15, 13, 17]
forecast = timeseries_forecast(dates, values, num_forecast_periods=7)
print(forecast)
```

---

### `find_high_correlation_features`

Identifies and returns a list of highly correlated features in a DataFrame.

**Parameters:**

*   `df` (pd.DataFrame): The input DataFrame.
*   `categorical_columns` (list): List of categorical column names.
*   `ignore_columns` (list): List of columns to ignore.
*   `threshold` (float, optional): The correlation threshold. Columns with correlation above this value are returned. Defaults to 0.9.

**Returns:**

*   `list`: A list of column names that are highly correlated with other columns.

**Example:**

```python
import pandas as pd
from utility_pack.ml import find_high_correlation_features

data = {'col1': [1, 2, 3, 4, 5], 'col2': [2, 4, 6, 8, 10], 'col3': ['A', 'B', 'A', 'C', 'B']}
df = pd.DataFrame(data)
categorical_cols = ['col3']
ignore_cols = []
high_corr_features = find_high_correlation_features(df, categorical_cols, ignore_cols, threshold=0.95)
print(high_corr_features)
```

---

### `prepare_dataframe_to_ml`

Prepares a DataFrame for machine learning by handling categorical and numerical features, missing values, high correlation, and dimensionality reduction using `prince`.

**Parameters:**

*   `df` (pd.DataFrame): The input DataFrame.

**Returns:**

*   `pd.DataFrame` or `np.ndarray`: A transformed DataFrame or numpy array ready for machine learning. The return type depends on which `prince` method is used (FAMD, MCA) or if it returns the numerical columns directly.

**Example:**

```python
import pandas as pd
from utility_pack.ml import prepare_dataframe_to_ml

data = {'col1': [1, 2, 3, 4, 5], 'col2': [2.0, 4.0, 6.0, 8.0, 10.0], 'col3': ['A', 'B', 'A', 'C', 'B']}
df = pd.DataFrame(data)
prepared_df = prepare_dataframe_to_ml(df)
print(prepared_df)
```

---

### `recommend_items_factorization`

Recommends items to sources using Alternating Least Squares (ALS) matrix factorization.

**Parameters:**

*   `df` (pd.DataFrame): Input DataFrame with 'source', 'item', and 'rating' columns.
*   `num_factors` (int, optional): Number of latent factors. Defaults to 20.
*   `num_iterations` (int, optional): Number of ALS iterations. Defaults to 5.
*   `reg` (float, optional): Regularization parameter. Defaults to 0.1.

**Returns:**

*   `pd.DataFrame`: DataFrame with columns 'source', 'recommended\_item', and 'recommendation\_score'.

**Example:**

```python
import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from utility_pack.ml import recommend_items_factorization

data = {'source': ['A', 'A', 'B', 'B', 'C'], 'item': ['X', 'Y', 'X', 'Z', 'Y'], 'rating': [5, 4, 3, 5, 2]}
df = pd.DataFrame(data)
recommendations = recommend_items_factorization(df, num_factors=10, num_iterations=3, reg=0.05)
print(recommendations)
```

---

### `recommendation_engine_co_occurrence`

Builds item recommendations based on co-occurrence or sequential transitions.

**Parameters:**

*   `df` (pd.DataFrame): Input DataFrame containing user-item interactions.
*   `user_col` (str): Column name representing user/customer ID.
*   `item_col` (str): Column name representing item ID.
*   `rating_col` (str, optional): Column name representing interaction strength. If None, interactions are weighted equally.
*   `date_col` (str, optional): Column name representing interaction timestamp. Required if `consider_order=True`.
*   `top_n` (int, optional): Number of top recommended items to return. Defaults to 5.
*   `consider_order` (bool, optional): Whether to consider the order of interactions. Defaults to False.
*   `generate_for_all_users` (bool, optional): Whether to generate recommendations for all users. Defaults to False.
*   `per_user_n` (int, optional): Number of recommendations per user when `generate_for_all_users=True`. Defaults to 5.

**Returns:**

*   `pd.DataFrame` or `function`:
    *   If `generate_for_all_users=False`: Returns a function that takes an item ID and returns top\_n recommended item IDs.
    *   If `generate_for_all_users=True`: Returns a DataFrame with columns `user_col`, `recommended_product`, and `score`.

**Example:**

```python
import pandas as pd
from utility_pack.ml import recommendation_engine_co_occurrence

data = {'customer_id': [1, 1, 1, 2, 2, 3], 'item_id': ['A', 'B', 'C', 'A', 'D', 'E']}
df = pd.DataFrame(data)
recommender = recommendation_engine_co_occurrence(df, 'customer_id', 'item_id')
print(recommender('A'))

user_recs = recommendation_engine_co_occurrence(df, 'customer_id', 'item_id', generate_for_all_users=True, per_user_n=2)
print(user_recs)
```

---

### `sequence_mining_analysis`

This script performs sequence mining analysis on transactional data to identify frequent patterns of events.

### Parameters:

*   `df` (pd.DataFrame): Input DataFrame containing transactional data.
*   `id_col` (str): Name of the column identifying unique sequences (e.g., customer ID).
*   `date_col` (str): Name of the column containing datetime values representing the order of events.
*   `analysis_col` (str): Name of the column containing the events to be analyzed.

### Returns:

*   `list`: A list of dictionaries, where each dictionary contains the 'target' event, its 'antecedents' (previous events), and 'consequents' (subsequent events), along with their probabilities.

### Usage Example:

```python
import pandas as pd
from utility_pack.ml import sequence_mining_analysis

# Sample DataFrame
data = {'customer_id': [1, 1, 1, 2, 2, 2],
        'date': ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-05', '2023-01-06', '2023-01-07'],
        'event': ['A', 'B', 'C', 'B', 'C', 'A']}
df = pd.DataFrame(data)
df['date'] = pd.to_datetime(df['date'])

# Perform sequence mining analysis
results = sequence_mining_analysis(df, 'customer_id', 'date', 'event')
```

---

### `TextClassifier`

A class for `robust` text classification using embeddings and a Multi-layer Perceptron classifier.

## Features

*   Text embedding using `extract_embeddings` with `both` **semantic** and **textual** types.
*   MLPClassifier for classification.
*   Label encoding using `LabelEncoder`.
*   Train/test split.
*   Prediction of single texts and batches.
*   Saving and loading the classifier.

## Usage

```python
from utility_pack.ml import TextClassifier

# Example data
texts = ["This is a positive example", "This is a negative example"]
labels = ["positive", "negative"]

# Initialize and train the classifier
classifier = TextClassifier()
classifier.train(texts, labels)

# Predict a single text
label, probability = classifier.predict("This is another example")
print(f"Predicted label: {label}, Probability: {probability}")

# Predict a batch of texts
predictions = classifier.predict_batch(["example 1", "example 2"])
print(f"Predictions: {predictions}")

# Save the classifier
classifier.save("classifier.pkl")

# Load the classifier
loaded_classifier = TextClassifier.load("classifier.pkl")
```

---

### `analyze_patterns`

Analyzes patterns in a dataset to identify association rules using a parallelized approach. It preprocesses the data by discretizing numerical columns, handling datetime columns, and then mines for frequent patterns and association rules.

**Parameters:**

* `file_path` (str): The path to the input CSV file.
* `discard_id` (bool, optional): If `True`, the `id_column` will be dropped from the DataFrame. Defaults to `True`.
* `id_column` (str, optional): The name of the ID column to be discarded if `discard_id` is `True`. Defaults to 'User\_ID'.
* `bins` (int, optional): The number of bins to use for discretizing numerical columns. Defaults to 3.
* `min_support` (float, optional): The minimum support threshold for a rule to be considered. Defaults to 0.05.
* `min_confidence` (float, optional): The minimum confidence threshold for a rule to be considered. Defaults to 0.6.

**Returns:**

* `pd.DataFrame`: A DataFrame containing the discovered association rules with 'antecedent', 'consequent', 'rule\_frequency' (support), and 'rule\_reliability' (confidence) columns.

**Example:**

```python
import pandas as pd
from utility_pack.ml import analyze_patterns

# Create a dummy CSV file for demonstration
data = {
    'User_ID': [1, 1, 2, 2, 3],
    'Age': [25, 30, 35, 40, 28],
    'City': ['New York', 'Los Angeles', 'New York', 'Chicago', 'Los Angeles'],
    'Purchase_Date': ['2023-01-01', '2023-01-05', '2023-01-02', '2023-01-06', '2023-01-03'],
    'Product': ['A', 'B', 'A', 'C', 'B']
}
df_sample = pd.DataFrame(data)
df_sample.to_csv('sample_data.csv', index=False)

# Analyze patterns
rules_df = analyze_patterns(
    file_path='sample_data.csv',
    discard_id=True,
    id_column='User_ID',
    bins=3,
    min_support=0.05,
    min_confidence=0.6
)
print(rules_df)
```

---

## 6\. Data Extraction with LLMs (Built-in RAG)

This utility extracts specific data from text using LLMs, with built-in RAG capabilities for large texts.  
Extracts data from a given text. If the text exceeds the token limit, it uses RAG (Retrieval-Augmented Generation) for efficient extraction.

**Parameters:**

*   `full_text` (str): The input text to extract data from.
*   `data_name` (str): The name of the data to extract.
*   `data_description` (str): A description of the data to extract.
*   `llm_provider` (LlmProvider): The LLM provider to use (e.g., "openrouter", "ollama", "vllm", "openai").
*   `llm_model` (str): The specific LLM model to use.
*   `max_input_tokens` (int, optional): The maximum number of tokens the LLM can process at once. Defaults to 8192.

**Returns:**

*   str: The extracted data in string format, or `None` if extraction fails.

**Example:**

```python
from utility_pack.extraction import get_data_from_text, LlmProvider

text = "..."  # large text
data_name = "email"
data_description = "The email address of the person"

email = get_data_from_text(
    full_text=text,
    data_name=data_name,
    data_description=data_description,
    llm_provider=LlmProvider.OPENROUTER,
    llm_model="mistralai/Mistral-7B-Instruct-v0.2"
)
```

---

## 7\. FastAPI Wrapper with Built-in Dashboard and bson\`s ObjectId fix

This is a fastapi wrapper that encapsulates frequently used functions, such as automatic ObjectId casting to string, telemetry collection, CORS and GZIP middleware as well.

```python
from utility_pack.fastapi_wrapper import FastAPIWrapper
from bson import ObjectId
import uvicorn

# You can provide your own `lifespan`
# The dashboard data and metrics endpoints are also basic-password protected
wrapper = FastAPIWrapper(lifespan=None, username="admin", password="password")
app = wrapper.app

@app.get("/test")
async def test():
    return {"objectid": ObjectId(), "nested": {"objectid": ObjectId()}} # Will cast automatically to str

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8005)

# Access http://0.0.0.0:8005/api/dashboard to view logged data
```

---

## 8\. OCR Utility Package

This package provides functions for performing OCR on images, with preprocessing steps for improved accuracy. It includes functionalities for binarization, deskewing, and raw OCR extraction.

To import this module:

```python
from utility_pack.ocr_util import ocr_image_pipeline, raw_ocr_with_topbottom_leftright
```

### `ocr_image_pipeline`

This function performs a complete OCR pipeline on a PIL image. It includes binarization using Sauvola's method, deskewing, resizing to tesseract's ideal size inference, and extracting text using Tesseract OCR. It prioritizes processing binarized and deskewed images, falling back on the original image if the initial attempt yields no text. It also performs post-processing to remove extra spaces and newline characters. This is the primary function you'll likely use.

```python
from PIL import Image
from utility_pack.ocr_util import ocr_image_pipeline

# Load the image
image_path = 'path/to/your/image.png'  # Replace with your image path
pil_image = Image.open(image_path)

# Perform OCR
text = ocr_image_pipeline(pil_image)

# Print the extracted text
print(text)
```

### `raw_ocr_with_topbottom_leftright`

This function performs raw OCR extraction on a PIL image or a processed image (like the output of `sauvola_binarization` or `rotate_image`), ordering the text by its position on the page (top to bottom, then left to right). It returns the extracted text as a single string, with each line separated by a newline character. It uses pytesseract's `image_to_data` function to obtain bounding box information and text.

```python
from PIL import Image
from utility_pack.ocr_util import raw_ocr_with_topbottom_leftright

# Load the image
image_path = 'path/to/your/image.png'  # Replace with your image path
pil_image = Image.open(image_path)

# Perform OCR
text = raw_ocr_with_topbottom_leftright(pil_image)

# Print the extracted text
print(text)
```

## 9\. Pandas Parallelization

This function allows you to parallelize a Pandas DataFrame's `apply` operation using multiple processes, significantly speeding up computations on large datasets. It leverages `cloudpickle` to serialize the function, enabling it to be passed between processes safely.

To import this module:

```python
from utility_pack.ocr_util import parallelize_apply
```

### Usage

`**parallelize_apply(df, func, n_jobs=-1)**`

Applies a function to a Pandas DataFrame in parallel.

*   `df`: The Pandas DataFrame to apply the function to.
*   `func`: The function to apply to each chunk of the DataFrame. The function will receive a Pandas DataFrame chunk as input.
*   `n_jobs`: The number of processes to use. `-1` uses all available CPU cores.

```python
import pandas as pd
from utility_pack.ocr_util import parallelize_apply

# Sample DataFrame
data = {'col1': range(100000), 'col2': range(100000, 200000)}
df = pd.DataFrame(data)

# Define a simple function to apply (e.g., square each value in column 'col1')
def square_col1(df_chunk):
    df_chunk['col1_squared'] = df_chunk['col1'] ** 2
    return df_chunk

# Parallelize the apply operation
result_df = parallelize_apply(df.copy(), square_col1, n_jobs=4) # Use 4 processes

# The 'result_df' now contains an additional column 'col1_squared'
print(result_df.head())
```

## 10\. JSON Parser Utility

This utility provides a function to extract and parse JSON data from strings, handling cases where the JSON is encapsulated within triple backticks or exists as a standalone string.

To import this module:

### Finding and Parsing JSON within Triple Backticks

````python
from utility_pack.parsers import find_and_parse_json_from_string

response_string = """
Some surrounding text.
```json
{
  "name": "example",
  "value": 123
}
```
More surrounding text.  
"""

parsed_json = find_and_parse_json_from_string(response_string)  
print(parsed_json)

## Expected Output: {'name': 'example', 'value': 123}
````

### Finding and Parsing Markdown within Triple Backticks

````python
from utility_pack.parsers import extract_markdown_content

response_string = """
Some surrounding text.
```
Hello World
```
More surrounding text.  
"""

parsed_json = extract_markdown_content(response_string)
print(parsed_json)

## Expected Output: Hello World
````

## 11\. PDF to Text Extraction with OCR Strategies

This module provides functionality to extract text from PDF files, with options to control OCR execution based on different strategies. It leverages the `fitz` (PyMuPDF) library for PDF processing and `PIL` for image manipulation and a custom `ocr_image_pipeline` for OCR.

To import this module:

```python
from utility_pack.pdfs import pdf_to_text, OcrStrategy, redact_pdf_and_convert_to_images
```

### Extract Text from PDF

The `pdf_to_text` function is the primary entry point for extracting text. It accepts a PDF file path and an OCR strategy to determine when to apply OCR.

```python
from utility_pack.pdfs import pdf_to_text, OcrStrategy

filepath = "path/to/your/pdf_file.pdf"  # Replace with the actual path to your PDF file
result = pdf_to_text(filepath, strategy_ocr=OcrStrategy.Auto)

print(result['full_text'])
```

### OCR Strategies

The `OcrStrategy` Enum defines the available strategies for handling OCR.

*   **Always:** OCR is performed on every page.
*   **Never:** OCR is never performed. Extracts only text that is already in the text layer of the PDF (if any).
*   **Auto:** OCR is performed on pages which have less then 10 words already extracted from their vectorized text, or detected as photos.

```python
from utility_pack.pdfs import pdf_to_text, OcrStrategy

filepath = "path/to/your/pdf_file.pdf"

# Example using the 'Always' strategy:
result = pdf_to_text(filepath, strategy_ocr=OcrStrategy.Always)
print(result['full_text'])
```

### Customize Zoom Factor

The `zoom_factor` parameter in `pdf_to_text` and `get_pdf_page_as_image` functions allows customization of the resolution of the converted image before OCR is performed. Higher values means more pixels and potentially better OCR results, at the cost of performance.

```python
from utility_pack.pdfs import pdf_to_text, OcrStrategy

filepath = "path/to/your/pdf_file.pdf"
result = pdf_to_text(filepath, strategy_ocr=OcrStrategy.Auto, zoom_factor=4.0) # Setting zoom to 4.0
print(result['full_text'])
```

### Get a PDF Page as an Image

The `get_pdf_page_as_image` function converts a specific page of a PDF into a PIL image object (via a PixMap object from pymupdf). This allows you to get image representations of specific pdf pages, which are used as inputs to the OCR process.

```python
from utility_pack.pdfs import get_pdf_page_as_image

filepath = "path/to/your/pdf_file.pdf"
page_number = 0 # first page

pix_image = get_pdf_page_as_image(filepath, page_number)
print(type(pix_image))
```

### Determine if a page is a photo

The `is_photo` function determines if a pix\_image contains a photo based on the amount of white pixels.

```python
from utility_pack.pdfs import get_pdf_page_as_image, is_photo

filepath = "path/to/your/pdf_file.pdf"
page_number = 0

pix_image = get_pdf_page_as_image(filepath, page_number)
is_it_a_photo = is_photo(pix_image)
print(is_it_a_photo)
```

### Redact PDF and Convert to Images

The `redact_pdf_and_convert_to_images` function processes a PDF by redacting specified text and optionally converting pages to images.

```python
from utility_pack.pdfs import redact_pdf_and_convert_to_images

pdf_path = "path/to/your/pdf_file.pdf"
search_strings = ["sensitive", "information"]
output_dir = "output"

result = redact_pdf_and_convert_to_images(pdf_path, search_strings, output_dir)

print(result)
```

**Parameters:**

*   `pdf_path` (str): The path to the input PDF file.
*   `search_strings` (list): A list of strings to search for and redact within the PDF.
*   `output_dir` (str): The directory where the output files (images or redacted PDF) will be saved. Defaults to "output".
*   `output_images` (bool): If `True`, the function outputs each page as an image. If `False`, the output is a redacted PDF. Defaults to `True`.

**Functionality:**

The function opens the PDF, searches for the specified strings on each page, and redacts them by removing the text from the text layer and drawing black rectangles over the identified areas.  It then either saves the redacted PDF or converts each page to an image, saving the images in the specified output directory.  The function returns either the paths to the generated images or the path to the redacted PDF.

## 12\. Text Utilities

This module provides a collection of text processing and utility functions for tasks such as cleaning, compressing, comparing, and chunking text.

### Usage

Import functions and classes as follows:

```python
from utility_pack.text import (
    get_uuid,
    remove_stopwords,
    remove_accents_replace,
    remove_accents_completely,
    remove_special_characters,
    remove_asian_characters,
    remove_html_tags,
    cleanup_markdown,
    remove_extra_whitespace,
    remove_numbers,
    remove_urls,
    remove_emails,
    compress_text,
    StringSimilarity,
    string_similarity,
    string_similarity_from_list,
    find_needle_in_haystack,
    chunk_text
)
```

Here separated single examples of each available module functionality

### `get_uuid`

Generates a short UUID.

```python
from utility_pack.text import get_uuid
unique_id = get_uuid()
print(unique_id)
```

### `remove_stopwords`

Removes common English (default) or Portuguese stopwords from a string.

```python
from utility_pack.text import remove_stopwords
text = "This is an example sentence with some stopwords."
cleaned_text = remove_stopwords(text)
print(cleaned_text)  # Output: example sentence stopwords.
```

### `remove_accents_replace`

Removes accents by replacing accented characters with their base characters.

```python
from utility_pack.text import remove_accents_replace
text = "Êxèmplo çøm áçêntøs."
cleaned_text = remove_accents_replace(text)
print(cleaned_text)  # Output: Exemplo com acentos.
```

### `remove_accents_completely`

Removes accents entirely, deleting accented characters.

```python
from utility_pack.text import remove_accents_completely
text = "Êxèmplo çøm áçêntøs."
cleaned_text = remove_accents_completely(text)
print(cleaned_text)  # Output: Exmplo cm cnts.
```

### `remove_special_characters`

Removes special characters, leaving only alphanumeric characters and spaces.

```python
from utility_pack.text import remove_special_characters
text = "Hello! This is a test@example.com."
cleaned_text = remove_special_characters(text)
print(cleaned_text)  # Output: Hello This is a testexamplecom
```

### `remove_asian_characters`

Removes Asian characters from the given string.

```python
from utility_pack.text import remove_asian_characters
text = "Hello こんにちは 世界"
cleaned_text = remove_asian_characters(text)
print(cleaned_text) # Output: Hello
```

### `remove_html_tags`

Removes HTML tags from a string.

```python
from utility_pack.text import remove_html_tags
text = "<p>This is <b>bold</b> text.</p>"
cleaned_text = remove_html_tags(text)
print(cleaned_text)  # Output: This is bold text.
```

### `cleanup_markdown`

Converts Markdown to plain text by removing Markdown formatting.

```python
from utility_pack.text import cleanup_markdown
text = "# This is a heading\n* This is a list item"
cleaned_text = cleanup_markdown(text)
print(cleaned_text)
# Output:
# This is a heading
# This is a list item
```

### `remove_extra_whitespace`

Removes extra whitespace, leaving only single spaces between words.

```python
from utility_pack.text import remove_extra_whitespace
text = "  This   has   extra    spaces.  "
cleaned_text = remove_extra_whitespace(text)
print(cleaned_text)  # Output: This has extra spaces.
```

### `remove_numbers`

Removes all numeric characters from the string.

```python
from utility_pack.text import remove_numbers
text = "This is a test string with 123 numbers."
cleaned_text = remove_numbers(text)
print(cleaned_text)  # Output: This is a test string with  numbers.
```

### `remove_urls`

Removes URLs from a string.

```python
from utility_pack.text import remove_urls
text = "Visit my website at https://www.example.com."
cleaned_text = remove_urls(text)
print(cleaned_text)  # Output: Visit my website at .
```

### `remove_emails`

Removes email addresses from a string.

```python
from utility_pack.text import remove_emails
text = "Contact me at test@example.com."
cleaned_text = remove_emails(text)
print(cleaned_text)  # Output: Contact me at .
```

### `compress_text`

Compresses text using semantic compression. Requires `compressor` package to be installed.

```python
from utility_pack.text import compress_text
text = "This is a long sentence that will be compressed."
compressed_text = compress_text(text, compression_rate=0.7)
print(compressed_text)
```

### `string_similarity`

Calculates the similarity between two strings using fuzzy matching based on Enum `StringSimilarity`.

```python
from utility_pack.text import string_similarity, StringSimilarity
string1 = "apple"
string2 = "aplle"
similarity = string_similarity(string1, string2, method=StringSimilarity.Ratio)
print(similarity)  # Output: e.g. 80
```

### `string_similarity_from_list`

Calculates the similarity between a reference string and a list of strings, and returns the most similar string (or top N most similar).

```python
from utility_pack.text import string_similarity_from_list
reference_string = "apple"
list_of_strings = ["aplle", "banana", "orange"]
result = string_similarity_from_list(reference_string, list_of_strings)
print(result)  # Output: ('aplle', 80) (example value)
```

### `find_needle_in_haystack`

Reranks documents to find the "needle" (best match) in a "haystack" (list of documents) using a combination of textual and semantic reranking.

```python
from utility_pack.text import find_needle_in_haystack
needle = "What is the capital of France?"
haystack = [
    "Paris is the capital of France.",
    "London is the capital of England.",
    "France is a country in Europe."
]
result = find_needle_in_haystack(needle, haystack)
print(result)
```

### `chunk_text`

Splits text into chunks of specified token count with optional overlap.

```python
from utility_pack.text import chunk_text
text = "This is a long piece of text that needs to be chunked."
chunks = chunk_text(text, chunk_token_count=10, overlap=2)
print(chunks)
```

## 13\. Vector Databases

This library provides two classes for vector storage and retrieval: `MiniVectorDB` for lightweight, in-memory storage with metadata filtering, and `VectorDB` for scalable, production-ready storage using MongoDB and LMDB.

### MiniVectorDB

`MiniVectorDB` offers a simple, file-based vector database with metadata filtering capabilities. It uses pickle for storage and Faiss for indexing.

```python
from utility_pack.vector_storage import MiniVectorDB
import numpy as np

# Initialize a MiniVectorDB instance
db = MiniVectorDB(storage_file='my_vector_db.pkl')
```

#### Store a single embedding

```python
unique_id = "doc1"
embedding = np.array([0.1, 0.2, 0.3], dtype=np.float32)
metadata = {"category": "science", "author": "John Doe"}

db.store_embedding(unique_id, embedding, metadata)
```

#### Store a batch of embeddings

```python
unique_ids = ["doc2", "doc3"]
embeddings = [
    np.array([0.4, 0.5, 0.6], dtype=np.float32),
    np.array([0.7, 0.8, 0.9], dtype=np.float32)
]
metadata_dicts = [
    {"category": "history", "author": "Jane Smith"},
    {"category": "technology", "author": "Peter Jones"}
]

db.store_embeddings_batch(unique_ids, embeddings, metadata_dicts)
```

#### Get a vector by its unique ID

```python
unique_id = "doc1"
vector = db.get_vector(unique_id)
print(vector)
```

#### Delete an embedding

```python
unique_id = "doc1"
db.delete_embedding(unique_id)
```

#### Find the most similar embeddings (Semantic Search)

```python
query_embedding = np.array([0.2, 0.3, 0.4], dtype=np.float32)
metadata_filter = {"category": "science"}
exclude_filter = {"author": "John Doe"}
or_filters = [{"category": "science"}, {"author": "Jane Smith"}]

ids, distances, metadatas = db.find_most_similar(query_embedding, metadata_filter=metadata_filter, exclude_filter=exclude_filter, or_filters=or_filters, k=3)

print(f"IDs: {ids}")
print(f"Distances: {distances}")
print(f"Metadatas: {metadatas}")
```

#### Persist the database to disk

```python
db.persist_to_disk()
```

### VectorDB

`VectorDB` is designed for production environments, integrating MongoDB for metadata storage and LMDB for efficient vector storage. It depends on the `ShardedLmdbStorage` helper class for LMDB management.

```python
from utility_pack.vector_storage_helper import ShardedLmdbStorage
from utility_pack.vector_storage import VectorDB

# Initialize ShardedLmdbStorage. Ensure to provide lmdb_dir at init
vector_storage = ShardedLmdbStorage(base_path="shards/vectors", num_shards=5)
text_storage = ShardedLmdbStorage(base_path="shards/texts", num_shards=5)

db = VectorDB(mongo_uri="mongodb://localhost:27017/", mongo_database="my_db", mongo_collection="my_collection", vector_storage=vector_storage, text_storage=text_storage)
```

#### Store a batch of embeddings with metadata and text

```python
unique_ids = ["doc1", "doc2"]
embeddings = [
    np.array([0.1, 0.2, 0.3], dtype=np.float32),
    np.array([0.4, 0.5, 0.6], dtype=np.float32)
]
metadata_dicts = [
    {"category": "science", "author": "John Doe", "text_content": "This is a science document."},
    {"category": "history", "author": "Jane Smith", "text_content": "This is a history document."}
]

db.store_embeddings_batch(unique_ids, embeddings, metadata_dicts=metadata_dicts, text_field="text_content")
```

#### Delete embeddings by unique IDs

```python
unique_ids = ["doc1", "doc2"]
db.delete_embeddings_batch(unique_ids)
```

#### Delete embeddings based on metadata

```python
metadata_filters = {"category": "science"}
db.delete_embeddings_by_metadata(metadata_filters)
```

#### Find the most similar embeddings (basic usage)

```python
query_embedding = np.array([0.2, 0.3, 0.4], dtype=np.float32)
filters = {"category": "science"}
output_fields = ["author"]

ids, distances, metadatas = db.find_most_similar(query_embedding, filters=filters, output_fields=output_fields, k=3)

print(f"IDs: {ids}")
print(f"Distances: {distances}")
print(f"Metadatas: {metadatas}")
```

#### Find the most similar embeddings with batch processing

```python
query_embedding = np.array([0.2, 0.3, 0.4], dtype=np.float32)
filters = {"category": "science"}
output_fields = ["author"]

ids, distances, metadatas = db.find_most_similar_in_batches(query_embedding, filters=filters, output_fields=output_fields, k=3, max_ram_usage_gb=1)

print(f"IDs: {ids}")
print(f"Distances: {distances}")
print(f"Metadatas: {metadatas}")
```

#### Check the count for each of the storages

```python
db.check_counts()
```

```python
total_count = db.get_total_count()
print(f"Total count of documents: {total_count}")
```

### HybridVectorDB

`HybridVectorDB` is designed for production environments, integrating MongoDB for metadata storage and LMDB for efficient vector storage, as well as supporting Hybrid search with Reciprocal Rank Fusion (RRF), using both semantic dense vectors and sparse vectors (SPLADE models, for example). It depends on the `ShardedLmdbStorage` helper class for LMDB management.

```python
from utility_pack.vector_storage_helper import ShardedLmdbStorage
from utility_pack.vector_storage import HybridVectorDB

# Initialize ShardedLmdbStorage. Ensure to provide lmdb_dir at init
dense_storage = ShardedLmdbStorage(base_path="shards/dense_vectors", num_shards=5)
sparse_storage = ShardedLmdbStorage(base_path="shards/sparse_vectors", num_shards=5)
text_storage = ShardedLmdbStorage(base_path="shards/texts", num_shards=5)

db = HybridVectorDB(
    mongo_uri="mongodb://localhost:27017/",
    mongo_database="my_db",
    mongo_collection="my_collection",
    dense_vector_storage = dense_storage,
    sparse_vector_storage = sparse_storage,
    text_storage = text_storage
)
```

#### Store a batch of embeddings with metadata and text

```python
from sentence_transformers import SentenceTransformer
from sentence_transformers import SparseEncoder

sparse_model = SparseEncoder("naver/splade-cocondenser-ensembledistil")
dense_model = SentenceTransformer("nomic-ai/nomic-embed-text-v2-moe", trust_remote_code=True)

unique_ids = ["doc1", "doc2"]
metadata_dicts = [
    {"category": "science", "author": "John Doe", "text_content": "This is a science document."},
    {"category": "history", "author": "Jane Smith", "text_content": "This is a history document."}
]
dense_embeddings = dense_model.encode([ m['text_content'] for m in metadata_dicts ], prompt_name='passage')
sparse_embeddings = sparse_model.encode([ m['text_content'] for m in metadata_dicts ])

db.store_embeddings_batch(
    unique_ids = unique_ids,
    sparse_embeddings = sparse_embeddings,
    dense_embeddings = dense_embeddings,
    metadata_dicts = metadata_dicts,
    text_field = "text_content"
)
```

#### Delete embeddings by unique IDs

```python
unique_ids = ["doc1", "doc2"]
db.delete_embeddings_batch(unique_ids)
```

#### Delete embeddings based on metadata

```python
metadata_filters = {"category": "science"}
db.delete_embeddings_by_metadata(metadata_filters)
```

#### Find the most similar embeddings (basic usage)

```python
query = "What is XYZ?"
dense_query_embedding = dense_model.encode([query], prompt_name='query')
sparse_query_embedding = sparse_model.encode([query])
filters = {"category": "science"}
output_fields = ["author"]

ids, distances, metadatas = db.find_most_similar(
    sparse_embedding = sparse_query_embedding,
    dense_embedding = dense_query_embedding
    filters = filters,
    output_fields=  output_fields,
    k = 3,
    k_rrf = 480 # Reciprocal Rank Fusion (RRF) K
)

print(f"IDs: {ids}")
print(f"Distances: {distances}")
print(f"Metadatas: {metadatas}")
```

#### Find the most similar embeddings with batch processing

```python
# This ensures
ids, distances, metadatas = db.find_most_similar_in_batches(
    sparse_embedding = sparse_query_embedding,
    dense_embedding = dense_query_embedding
    filters = filters,
    output_fields=  output_fields,
    k = 3,
    k_rrf = 480, # Reciprocal Rank Fusion (RRF) K
    max_ram_usage_gb = 2 # While using the batching approach, we can ensure we won't exceed this ram while searching
)
```

#### Check the count for each of the storages

```python
db.check_counts()
```

```python
total_count = db.get_total_count()
print(f"Total count of documents: {total_count}")
```