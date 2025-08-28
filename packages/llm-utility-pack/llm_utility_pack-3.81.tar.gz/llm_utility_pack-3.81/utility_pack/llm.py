import os, requests, json, aiohttp, asyncio, importlib
from utility_pack.logger import log_exception
from compressor.semantic import count_tokens
from utility_pack.text import compress_text
from tokenizers import Tokenizer
import onnxruntime as ort
import numpy as np

from ollama import AsyncClient
from ollama import Client

from openai import OpenAI
from openai import AsyncOpenAI

question_classifier_tokenizer = None
question_classifier_session = None
reranker_tokenizer = None
reranker_session = None

OPENROUTER_KEY = os.environ.get("OPENROUTER_KEY")
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
VLLM_URL = os.environ.get("VLLM_URL", "http://127.0.0.1:8000")
if VLLM_URL.endswith("/"):
    VLLM_URL = VLLM_URL[:-1]
VLLM_KEY = os.environ.get("VLLM_KEY", "EMPTY")

OLLAMA_SYNC_CLIENT = Client(host=OLLAMA_HOST)
OLLAMA_ASYNC_CLIENT = AsyncClient(host=OLLAMA_HOST)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if OPENAI_API_KEY:
    OPENAI_SYNC_CLIENT = OpenAI(
        api_key=OPENAI_API_KEY
    )
    OPENAI_ASYNC_CLIENT = AsyncOpenAI(
        api_key=OPENAI_API_KEY
    )
else:
    OPENAI_SYNC_CLIENT = None
    OPENAI_ASYNC_CLIENT = None

PROVIDER = os.environ.get("LLM_PROVIDER", "openrouter")

def openrouter_chat(messages: list, model: str = "google/gemini-flash-1.5-8b", max_tokens=None):
    """
    Needs the OPENROUTER_KEY environment variable set.

    Expects an array of messages, where each message is an object with a role and content.
    The role can be "user" or "assistant".

    Example:
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how are you?"},
        {"role": "assistant", "content": "I'm doing well, thank you for asking!"}
    ]
    """
    payload = {
        "model": model,
        "messages": messages
    }
    if max_tokens:
        payload["max_tokens"] = max_tokens
    response = requests.post(
        url=OPENROUTER_URL,
        headers={
            "Authorization": f"Bearer {OPENROUTER_KEY}"
        },
        data=json.dumps(payload)
    )
    json_response = response.json()
    return json_response["choices"][0]["message"]["content"].strip()

def openrouter_prompt(message: str, model: str = "google/gemini-flash-1.5-8b", max_tokens=None):
    """
    Needs the OPENROUTER_KEY environment variable set.
    """
    return openrouter_chat([{"role": "user", "content": message}], model, max_tokens)

async def openrouter_chat_stream(messages: list, model: str = "google/gemini-flash-1.5-8b", max_tokens=None):
    """
    Needs the OPENROUTER_KEY environment variable set.

    Expects an array of messages, where each message is an object with a role and content.
    The role can be "user" or "assistant".

    Example:
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how are you?"},
        {"role": "assistant", "content": "I'm doing well, thank you for asking!"}
    ]
    """
    payload = {
        "stream": True,
        "model": model,
        "messages": messages
    }
    if max_tokens:
        payload['max_tokens'] = max_tokens
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
                OPENROUTER_URL,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {OPENROUTER_KEY}"
                },
                json=payload
            ) as response:
            
            buffer = ""
            async for chunk in response.content.iter_any():
                buffer += chunk.decode()
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)

                    if line.startswith("data: "):
                        event_data = line[len("data: "):]
                        if event_data != '[DONE]':
                            try:
                                current_text = json.loads(event_data)['choices'][0]['delta']['content']
                                yield current_text
                                await asyncio.sleep(0.01)
                            except Exception:
                                try:
                                    current_text = json.loads(event_data)['choices'][0]['text']
                                    yield current_text
                                    await asyncio.sleep(0.01)
                                except Exception:
                                    log_exception()

async def openrouter_prompt_stream(message: str, model: str = "google/gemini-flash-1.5-8b", max_tokens=None):
    """
    Needs the OPENROUTER_KEY environment variable set.
    """
    async for chunk in openrouter_chat_stream([{"role": "user", "content": message}], model, max_tokens):
        yield chunk

async def openrouter_chat_async(messages: list, model: str = "google/gemini-flash-1.5-8b", max_tokens=None):
    payload = {
        "stream": False,
        "model": model,
        "messages": messages
    }
    if max_tokens:
        payload['max_tokens'] = max_tokens
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
                OPENROUTER_URL,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {OPENROUTER_KEY}"
                },
                json=payload
            ) as response:
            json_response = await response.json()
            return json_response["choices"][0]["message"]["content"].strip()

async def openrouter_prompt_async(message: str, model: str = "google/gemini-flash-1.5-8b", max_tokens=None):
    return openrouter_chat([{"role": "user", "content": message}], model, max_tokens)

def ollama_chat(messages: list, model: str = "qwen2.5:0.5b", max_tokens=None):
    """
    Needs the OLLAMA_HOST environment variable set.

    Expects an array of messages, where each message is an object with a role and content.
    The role can be "user" or "assistant".

    Example:
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how are you?"},
        {"role": "assistant", "content": "I'm doing well, thank you for asking!"}
    ]
    """
    options = {}
    if max_tokens:
        options['num_predict'] = max_tokens

    response = OLLAMA_SYNC_CLIENT.chat(
        model=model,
        messages=messages,
        options=options
    )
    return response.message.content

def ollama_prompt(message: str, model: str = "qwen2.5:0.5b", max_tokens=None):
    """
    Needs the OLLAMA_HOST environment variable set.
    """
    return ollama_chat([{'role': 'user', 'content': message}], model, max_tokens)

async def ollama_chat_stream(messages: list, model: str = "qwen2.5:0.5b", max_tokens=None):
    """
    Needs the OLLAMA_HOST environment variable set.

    Expects an array of messages, where each message is an object with a role and content.
    The role can be "user" or "assistant".

    Example:
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how are you?"},
        {"role": "assistant", "content": "I'm doing well, thank you for asking!"}
    ]
    """
    options = {}
    if max_tokens:
        options['num_predict'] = max_tokens

    async for chunk in await OLLAMA_ASYNC_CLIENT.chat(
        model=model,
        messages=messages,
        options=options,
        stream=True
    ):
        yield chunk.message.content

async def ollama_prompt_stream(message: str, model: str = "qwen2.5:0.5b", max_tokens=None):
    """
    Needs the OLLAMA_HOST environment variable set.
    """
    async for chunk in ollama_chat_stream([{"role": "user", "content": message}], model, max_tokens):
        yield chunk

async def ollama_chat_async(messages: list, model: str = "qwen2.5:0.5b", max_tokens=None):
    options = {}
    if max_tokens:
        options['num_predict'] = max_tokens

    async with AsyncClient(host=OLLAMA_HOST) as client:
        response = await client.chat(
            model=model,
            messages=messages,
            options=options
        )
        return response.message.content

async def ollama_prompt_async(message: str, model: str = "qwen2.5:0.5b", max_tokens=None):
    return ollama_chat([{'role': 'user', 'content': message}], model, max_tokens)

def vllm_chat(messages: list, model: str = "Qwen/Qwen2.5-0.5B-Instruct", max_tokens=None):
    payload = {
        "messages": messages,
        "model": model,
        "stream": False
    }
    if max_tokens:
        payload["max_completion_tokens"] = max_tokens
    response = requests.post(
        url=f"{VLLM_URL}/v1/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer EMPTY"
        },
        json=payload
    )
    return response.json()['choices'][0]['message']['content'].strip()

def vllm_prompt(message: str, model: str = "Qwen/Qwen2.5-0.5B-Instruct", max_tokens=None):
    return vllm_chat([{"role": "user", "content": message}], model, max_tokens)

async def vllm_chat_stream(messages: list, model: str = "Qwen/Qwen2.5-0.5B-Instruct", max_tokens=None):
    payload = {
        "messages": messages,
        "model": model,
        "stream": True
    }
    if max_tokens:
        payload["max_completion_tokens"] = max_tokens
    async with aiohttp.ClientSession() as session:
        async with session.post(
                VLLM_URL,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {VLLM_KEY}"
                },
                json=payload
            ) as response:
            
            buffer = ""
            async for chunk in response.content.iter_any():
                buffer += chunk.decode()
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if line.startswith("data: "):
                        event_data = line[len("data: "):]
                        if event_data != '[DONE]':
                            try:
                                current_text = json.loads(event_data)['choices'][0]['delta']['content']
                                yield current_text
                                await asyncio.sleep(0.01)
                            except Exception:
                                try:
                                    current_text = json.loads(event_data)['choices'][0]['text']
                                    yield current_text
                                    await asyncio.sleep(0.01)
                                except Exception:
                                    log_exception()

async def vllm_prompt_stream(message: str, model: str = "Qwen/Qwen2.5-0.5B-Instruct", max_tokens=None):
    async for chunk in vllm_chat_stream([{"role": "user", "content": message}], model, max_tokens):
        yield chunk

async def vllm_chat_async(messages: list, model: str = "Qwen/Qwen2.5-0.5B-Instruct", max_tokens=None):
    payload = {
        "messages": messages,
        "model": model,
        "stream": False
    }
    if max_tokens:
        payload["max_completion_tokens"] = max_tokens
    async with aiohttp.ClientSession() as session:
        async with session.post(
                VLLM_URL,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer EMPTY"
                },
                json=payload
            ) as response:
            json_response = await response.json()
            return json_response['choices'][0]['message']['content'].strip()

async def vllm_prompt_async(message: str, model: str = "Qwen/Qwen2.5-0.5B-Instruct", max_tokens=None):
    return vllm_chat([{"role": "user", "content": message}], model, max_tokens)

def openai_chat(messages: list, model: str = "gpt-4o-mini", max_tokens=None):
    payload = {
        "model": model,
        "messages": messages
    }
    if max_tokens:
        payload["max_tokens"] = max_tokens
    response = OPENAI_SYNC_CLIENT.chat.completions.create(**payload)
    return response.choices[0].message.content.strip()

def openai_prompt(message: str, model: str = "gpt-4o-mini", max_tokens=None):
    return openai_chat([{"role": "user", "content": message}], model, max_tokens)

async def openai_chat_stream(messages: list, model: str = "gpt-4o-mini", max_tokens=None):
    async for resp in await OPENAI_ASYNC_CLIENT.chat.completions.create(
            model = model,
            stream = True,
            messages = messages,
            max_tokens = max_tokens
        ):
        if resp.choices[0].delta.content is not None:
            current_text = resp.choices[0].delta.content
            yield current_text

async def openai_prompt_stream(message: str, model: str = "gpt-4o-mini", max_tokens=None):
    async for chunk in openai_chat_stream([{"role": "user", "content": message}], model, max_tokens):
        yield chunk

async def openai_chat_async(messages: list, model: str = "gpt-4o-mini", max_tokens=None):
    async with AsyncOpenAI(api_key=OPENAI_API_KEY) as openai_client:
        resp = await openai_client.chat.completions.create(
            model = model,
            stream = False,
            messages = messages,
            max_tokens = max_tokens
        )

        return resp.choices[0].message.content.strip()

async def openai_prompt_async(message: str, model: str = "gpt-4o-mini", max_tokens=None):
    return openai_chat([{"role": "user", "content": message}], model, max_tokens)

def _initialize_question_classifier():
    global question_classifier_tokenizer, question_classifier_session
    question_classifier_tokenizer = Tokenizer.from_file(str(importlib.resources.files('utility_pack').joinpath('resources/question-classifier/tokenizer.json')))
    question_classifier_session = ort.InferenceSession(str(importlib.resources.files('utility_pack').joinpath('resources/question-classifier/model.onnx')))

def _initialize_reranker():
    global reranker_tokenizer, reranker_session
    reranker_tokenizer = Tokenizer.from_file(str(importlib.resources.files('utility_pack').joinpath('resources/reranker/tokenizer.json')))
    reranker_session = ort.InferenceSession(str(importlib.resources.files('utility_pack').joinpath('resources/reranker/model.onnx')))

def classify_question_generic_or_directed(question):
    global question_classifier_session, question_classifier_tokenizer
    
    if question_classifier_session is None or question_classifier_tokenizer is None:
        _initialize_question_classifier()

    # Encode and truncate to 512 tokens
    encoding = question_classifier_tokenizer.encode(question.lower())
    ids = encoding.ids[:512]
    input_ids = np.array([ids], dtype=np.int64)
    attention_mask = np.array([[1] * len(ids)], dtype=np.int64)
    token_type_ids = np.zeros_like(input_ids, dtype=np.int64)

    # Pad if needed
    pad_len = 512 - len(ids)
    if pad_len > 0:
        input_ids = np.pad(input_ids, ((0, 0), (0, pad_len)), constant_values=0)
        attention_mask = np.pad(attention_mask, ((0, 0), (0, pad_len)), constant_values=0)
        token_type_ids = np.pad(token_type_ids, ((0, 0), (0, pad_len)), constant_values=0)

    # Run inference
    ort_inputs = {
        "input_ids": input_ids,
        "attention_mask": attention_mask,
        "token_type_ids": token_type_ids
    }
    logits = question_classifier_session.run(None, ort_inputs)[0]
    predicted_class = int(np.argmax(logits, axis=1)[0])
    return "generic" if predicted_class == 0 else "directed"

def rerank(question, passages, normalize_scores=True):
    global reranker_session, reranker_tokenizer
    if reranker_session is None or reranker_tokenizer is None:
        _initialize_reranker()

    templates = [f"Query: {question}\nSentence: {passage}" for passage in passages]
    encoded_inputs = reranker_tokenizer.encode_batch(templates)

    input_ids = [enc.ids[:512] for enc in encoded_inputs]
    attention_mask = [[1] * len(ids) for ids in input_ids]
    token_type_ids = [[0] * len(ids) for ids in input_ids]

    batch_max_length = max(len(ids) for ids in input_ids)

    def pad_sequence(seq, pad_value=0):
        return seq + [pad_value] * (batch_max_length - len(seq))

    input_ids = np.array([pad_sequence(ids) for ids in input_ids], dtype=np.int64)
    attention_mask = np.array([pad_sequence(mask, pad_value=0) for mask in attention_mask], dtype=np.int64)
    token_type_ids = np.array([pad_sequence(types, pad_value=0) for types in token_type_ids], dtype=np.int64)

    inputs_onnx = {
        "input_ids": input_ids,
        "attention_mask": attention_mask,
        "token_type_ids": token_type_ids
    }

    outputs = reranker_session.run(None, inputs_onnx)
    logits = outputs[0]

    probabilities = np.exp(logits) / np.sum(np.exp(logits), axis=1, keepdims=True)

    predicted_classes = np.argmax(probabilities, axis=1).tolist()
    confidences = np.max(probabilities, axis=1).tolist()

    results = [
        {"passage": passage, "prediction": pred, "confidence": conf}
        for passage, pred, conf in zip(passages, predicted_classes, confidences)
    ]

    final_results = []
    for document, result in zip(passages, results):
        if result['prediction'] == 0:
            result['confidence'] = 1 - result['confidence']
        final_results.append((document, result['confidence']))
    
    sorted_results = sorted(final_results, key=lambda x: x[1], reverse=True)

    if normalize_scores:
        total_score = sum(result[1] for result in sorted_results)
        if total_score > 0:
            sorted_results = [(result[0], result[1] / total_score) for result in sorted_results]

    return sorted_results

def llm_chat(messages: list, max_tokens=None, model_tag="google/gemini-2.0-flash-lite-001"):
    if PROVIDER == "openrouter":
        return openrouter_chat(messages, model_tag, max_tokens)
    elif PROVIDER == "ollama":
        return ollama_chat(messages, model_tag, max_tokens)
    elif PROVIDER == "vllm":
        return vllm_chat(messages, model_tag, max_tokens)
    elif PROVIDER == "openai":
        return openai_chat(messages, model_tag, max_tokens)
    else:
        raise Exception(f"Unknown LLM provider: {PROVIDER}")

async def llm_chat_async(messages: list, max_tokens=None, model_tag="google/gemini-2.0-flash-lite-001"):
    if PROVIDER == "openrouter":
        return await openrouter_chat_async(messages, model_tag, max_tokens)
    elif PROVIDER == "ollama":
        return await ollama_chat_async(messages, model_tag, max_tokens)
    elif PROVIDER == "vllm":
        return await vllm_chat_async(messages, model_tag, max_tokens)
    elif PROVIDER == "openai":
        return await openai_chat_async(messages, model_tag, max_tokens)
    else:
        raise Exception(f"Unknown LLM provider: {PROVIDER}")

def llm_prompt(message: str, max_tokens=None, model_tag="google/gemini-2.0-flash-lite-001"):
    if PROVIDER == "openrouter":
        return openrouter_prompt(message, model_tag, max_tokens)
    elif PROVIDER == "ollama":
        return ollama_prompt(message, model_tag, max_tokens)
    elif PROVIDER == "vllm":
        return vllm_prompt(message, model_tag, max_tokens)
    elif PROVIDER == "openai":
        return openai_prompt(message, model_tag, max_tokens)
    else:
        raise Exception(f"Unknown LLM provider: {PROVIDER}")

async def llm_prompt_async(message: str, max_tokens=None, model_tag="google/gemini-2.0-flash-lite-001"):
    if PROVIDER == "openrouter":
        return await openrouter_prompt_async(message, model_tag, max_tokens)
    elif PROVIDER == "ollama":
        return await ollama_prompt_async(message, model_tag, max_tokens)
    elif PROVIDER == "vllm":
        return await vllm_prompt_async(message, model_tag, max_tokens)
    elif PROVIDER == "openai":
        return await openai_prompt_async(message, model_tag, max_tokens)
    else:
        raise Exception(f"Unknown LLM provider: {PROVIDER}")

async def llm_chat_stream(messages: list, max_tokens=None, model_tag="google/gemini-2.0-flash-lite-001", model=None):
    model_to_use = model_tag
    if model:
        model_to_use = model
    if PROVIDER == "openrouter":
        async for chunk in openrouter_chat_stream(messages, model_to_use, max_tokens):
            yield chunk
            await asyncio.sleep(0.01)
    elif PROVIDER == "ollama":
        async for chunk in ollama_chat_stream(messages, model_to_use, max_tokens):
            yield chunk
            await asyncio.sleep(0.01)
    elif PROVIDER == "vllm":
        async for chunk in vllm_chat_stream(messages, model_to_use, max_tokens):
            yield chunk
            await asyncio.sleep(0.01)
    elif PROVIDER == "openai":
        async for chunk in openai_chat_stream(messages, model_to_use, max_tokens):
            yield chunk
            await asyncio.sleep(0.01)
    else:
        raise Exception(f"Unknown LLM provider: {PROVIDER}")

async def llm_prompt_stream(message: str, max_tokens=None, model_tag="google/gemini-2.0-flash-lite-001"):
    if PROVIDER == "openrouter":
        async for chunk in openrouter_prompt_stream(message, model_tag, max_tokens):
            yield chunk
            await asyncio.sleep(0.01)
    elif PROVIDER == "ollama":
        async for chunk in ollama_prompt_stream(message, model_tag, max_tokens):
            yield chunk
            await asyncio.sleep(0.01)
    elif PROVIDER == "vllm":
        async for chunk in vllm_prompt_stream(message, model_tag, max_tokens):
            yield chunk
            await asyncio.sleep(0.01)
    elif PROVIDER == "openai":
        async for chunk in openai_prompt_stream(message, model_tag, max_tokens):
            yield chunk
            await asyncio.sleep(0.01)
    else:
        raise Exception(f"Unknown LLM provider: {PROVIDER}")
