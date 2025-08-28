from utility_pack.llm import openrouter_prompt, ollama_prompt, vllm_prompt, openai_prompt
from utility_pack.text import chunk_text, find_needle_in_haystack, detect_language
from utility_pack.embeddings import extract_embeddings, EmbeddingType
from utility_pack.parsers import find_and_parse_json_from_string
from utility_pack.vector_storage import MiniVectorDB
from compressor.semantic import count_tokens
from utility_pack.decorators import retry
import uuid, traceback
from enum import Enum

class LlmProvider(str, Enum):
    OPENROUTER = "openrouter"
    OLLAMA = "ollama"
    VLLM = "vllm"
    OPENAI = "openai"

@retry(retry_count=5, delay=0.3)
def prompt_for_data(context, data_name, data_description, llm_provider, llm_model):
    lang = detect_language(context)
    if lang == 'pt':
        prompt = f"Sua tarefa é extrair o \"{data_name}\" do seguinte texto:\n\n<text_start>\n{context}\n<text_end>. A descrição para \"{data_name}\" é:\n{data_description}.\n\nSua resposta deve estar no formato JSON, usando este formato estritamente:\n\n```json\n{{\n \"data\": \"dado extraído\"\n}}\n```\n\nSe o \"{data_name}\" não estiver presente no texto, retorne o valor de \"data\" como null."
    else:
        prompt = f"Your task is to extract the \"{data_name}\" from the following text:\n\n<text_start>\n{context}\n<text_end>. The description for \"{data_name}\" is:\n{data_description}.\n\nYour answer should be in JSON format, using this format strictly:\n\n```json\n{{\n    \"data\": \"extracted data\"\n}}\n```\n\nIf the \"{data_name}\" is not present in the text, return the \"data\" value as null."

    if llm_provider == LlmProvider.OPENROUTER:
        response = openrouter_prompt(prompt, model=llm_model)
    elif llm_provider == LlmProvider.OLLAMA:
        response = ollama_prompt(prompt, model=llm_model)
    elif llm_provider == LlmProvider.VLLM:
        response = vllm_prompt(prompt, model=llm_model)
    elif llm_provider == LlmProvider.OPENAI:
        response = openai_prompt(prompt, model=llm_model)
    else:
        raise ValueError(f"Invalid LLM provider: {llm_provider}")

    return find_and_parse_json_from_string(response)["data"]

def get_data_from_text(full_text, data_name, data_description, llm_provider, llm_model, max_input_tokens=8192):
    try:
        token_count = count_tokens(full_text)
        
        # Check if the chunk count exceeds the max tokens
        if token_count > max_input_tokens:

            # Use RAG
            chunks = chunk_text(full_text, chunk_token_count=500)
            db = MiniVectorDB()

            unique_ids = []
            embeddings = []
            metadata_dicts = []
            
            # Each chunk must be embedded with its neighbors
            for i, chunk in enumerate(chunks):
                chunk_before = chunks[i-1] if i > 0 else ""
                current_chunk = chunk
                chunk_after = chunks[i+1] if i < len(chunks)-1 else ""

                text_to_embed = f"{chunk_before} {current_chunk} {chunk_after}"
                
                unique_ids.append(str(uuid.uuid4()))
                embeddings.append(extract_embeddings([text_to_embed], EmbeddingType.SEMANTIC)[0])
                metadata_dicts.append({"text": current_chunk, "index": i})

            # 1 - Index
            db.store_embeddings_batch(
                unique_ids=unique_ids,
                embeddings=embeddings,
                metadata_dicts=metadata_dicts
            )

            # 2 - Retrieve
            _, _, results = db.find_most_similar(
                embedding=extract_embeddings([data_description], EmbeddingType.SEMANTIC)[0],
                k=max_input_tokens // 500,
                autocut=True
            )
            results = list(results)

            # Sort by key "index", ascending
            results.sort(key=lambda x: x["index"])
            retrieved_text_context = ' '.join([r["text"] for r in results])

            found_text = find_needle_in_haystack(
                needle = f"{data_name} - {data_description}",
                haystack = chunks,
                best_of = 2
            )

            retrieved_text_context = f"{retrieved_text_context}\n{found_text}"

            # 3 - Extract data
            result = prompt_for_data(
                context=retrieved_text_context,
                data_name=data_name,
                data_description=data_description,
                llm_provider=llm_provider,
                llm_model=llm_model
            )

            # Delete all variables to free ram
            del retrieved_text_context, found_text, full_text, results, unique_ids, embeddings, metadata_dicts, chunks, db

            return result

        else:
            # Send full text to LLM
            result = prompt_for_data(
                context=full_text,
                data_name=data_name,
                data_description=data_description,
                llm_provider=llm_provider,
                llm_model=llm_model
            )

            return result
    except Exception as e:
        traceback.print_exc()
    
    return None
