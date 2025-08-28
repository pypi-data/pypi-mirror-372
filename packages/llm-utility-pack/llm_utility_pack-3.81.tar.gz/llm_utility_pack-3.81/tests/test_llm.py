import os
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import numpy as np

from utility_pack.llm import (
    classify_question_generic_or_directed,
    llm_chat,
    llm_chat_async,
    llm_chat_stream,
    llm_prompt,
    llm_prompt_async,
    llm_prompt_stream,
    openai_chat,
    openai_chat_async,
    openai_chat_stream,
    openai_prompt,
    openai_prompt_async,
    openai_prompt_stream,
    openrouter_chat,
    openrouter_chat_async,
    openrouter_chat_stream,
    openrouter_prompt,
    openrouter_prompt_async,
    openrouter_prompt_stream,
    rerank,
)


@patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}, clear=True)
class TestLLM(unittest.TestCase):
    @patch.dict(os.environ, {"OPENROUTER_KEY": "test_key"})
    @patch("requests.post")
    def test_openrouter_chat(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"choices": [{"message": {"content": "response"}}]}
        mock_post.return_value = mock_response

        response = openrouter_chat([{"role": "user", "content": "test"}])
        self.assertEqual(response, "response")

    @patch.dict(os.environ, {"OPENROUTER_KEY": "test_key"})
    @patch("requests.post")
    def test_openrouter_prompt(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"choices": [{"message": {"content": "response"}}]}
        mock_post.return_value = mock_response

        response = openrouter_prompt("test")
        self.assertEqual(response, "response")

    @patch.dict(os.environ, {"OPENROUTER_KEY": "test_key"})
    @patch("aiohttp.ClientSession.post")
    async def test_openrouter_chat_stream(self, mock_post):
        async def mock_response_context_manager(*args, **kwargs):
            mock_response = MagicMock()
            mock_response.content.iter_any = AsyncMock(
                return_value=[b'data: {"choices": [{"delta": {"content": "response"}}]}\n']
            )
            mock_response.__aenter__.return_value = mock_response
            return mock_response

        mock_post.return_value = await mock_response_context_manager()

        chunks = [chunk async for chunk in openrouter_chat_stream([{"role": "user", "content": "test"}])]
        self.assertEqual(chunks, ["response"])

    @patch.dict(os.environ, {"OPENROUTER_KEY": "test_key"})
    @patch("utility_pack.llm.openrouter_chat_stream")
    async def test_openrouter_prompt_stream(self, mock_chat_stream):
        async def mock_stream_gen():
            yield "response"

        mock_chat_stream.return_value = mock_stream_gen()

        chunks = [chunk async for chunk in openrouter_prompt_stream("test")]
        self.assertEqual(chunks, ["response"])

    @patch.dict(os.environ, {"OPENROUTER_KEY": "test_key"})
    @patch("aiohttp.ClientSession.post")
    async def test_openrouter_chat_async(self, mock_post):
        async def mock_response_context_manager(*args, **kwargs):
            mock_response = MagicMock()
            mock_response.json = AsyncMock(return_value={"choices": [{"message": {"content": "response"}}]})
            mock_response.__aenter__.return_value = mock_response
            return mock_response

        mock_post.return_value = await mock_response_context_manager()

        response = await openrouter_chat_async([{"role": "user", "content": "test"}])
        self.assertEqual(response, "response")

    @patch.dict(os.environ, {"OPENROUTER_KEY": "test_key"})
    @patch("utility_pack.llm.openrouter_chat")
    async def test_openrouter_prompt_async(self, mock_chat):
        mock_chat.return_value = "response"
        response = await openrouter_prompt_async("test")
        self.assertEqual(response, "response")

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"})
    @patch("utility_pack.llm.OPENAI_SYNC_CLIENT")
    def test_openai_chat(self, mock_client):
        mock_response = MagicMock(choices=[MagicMock(message=MagicMock(content="response"))])
        mock_client.chat.completions.create.return_value = mock_response
        response = openai_chat([{"role": "user", "content": "test"}])
        self.assertEqual(response, "response")

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"})
    @patch("utility_pack.llm.openai_chat")
    def test_openai_prompt(self, mock_chat):
        mock_chat.return_value = "response"
        response = openai_prompt("test")
        self.assertEqual(response, "response")

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"})
    @patch("openai.resources.chat.completions.AsyncCompletions.create")
    async def test_openai_chat_stream(self, mock_create):
        async def mock_stream_gen():
            yield MagicMock(choices=[MagicMock(delta=MagicMock(content="response"))])

        mock_create.return_value = mock_stream_gen()
        chunks = [chunk async for chunk in openai_chat_stream([{"role": "user", "content": "test"}])]
        self.assertEqual(chunks, ["response"])

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"})
    @patch("utility_pack.llm.openai_chat_stream")
    async def test_openai_prompt_stream(self, mock_chat_stream):
        async def mock_stream_gen():
            yield "response"

        mock_chat_stream.return_value = mock_stream_gen()
        chunks = [chunk async for chunk in openai_prompt_stream("test")]
        self.assertEqual(chunks, ["response"])

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"})
    @patch("openai.resources.chat.completions.AsyncCompletions.create")
    async def test_openai_chat_async(self, mock_create):
        mock_response = MagicMock(choices=[MagicMock(message=MagicMock(content="response"))])
        mock_create.return_value = mock_response
        response = await openai_chat_async([{"role": "user", "content": "test"}])
        self.assertEqual(response, "response")

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"})
    @patch("utility_pack.llm.openai_chat")
    async def test_openai_prompt_async(self, mock_chat):
        mock_chat.return_value = "response"
        response = await openai_prompt_async("test")
        self.assertEqual(response, "response")

    @patch("utility_pack.llm.question_classifier_tokenizer")
    @patch("utility_pack.llm.question_classifier_session")
    def test_classify_question_generic_or_directed(self, mock_session, mock_tokenizer):
        mock_tokenizer.encode.return_value.ids = [0] * 10
        mock_session.run.return_value = [np.array([[0.9, 0.1]])]

        with patch("utility_pack.llm._initialize_question_classifier") as mock_init:
            result = classify_question_generic_or_directed("test question")
            mock_init.assert_not_called()  # Should not be called if already initialized

        self.assertEqual(result, "generic")

    @patch("utility_pack.llm.reranker_tokenizer")
    @patch("utility_pack.llm.reranker_session")
    def test_rerank(self, mock_session, mock_tokenizer):
        mock_tokenizer.encode_batch.return_value = [MagicMock(ids=[0] * 10)]
        mock_session.run.return_value = [np.array([[0.1, 0.9]])]

        with patch("utility_pack.llm._initialize_reranker") as mock_init:
            results = rerank("question", ["passage"])
            mock_init.assert_not_called()  # Should not be called if already initialized

        self.assertEqual(len(results), 1)

    @patch.dict(os.environ, {"LLM_PROVIDER": "openrouter"})
    @patch("utility_pack.llm.openrouter_chat")
    def test_llm_chat(self, mock_chat):
        mock_chat.return_value = "response"
        response = llm_chat([{"role": "user", "content": "test"}])
        self.assertEqual(response, "response")

    @patch.dict(os.environ, {"LLM_PROVIDER": "openrouter"})
    @patch("utility_pack.llm.openrouter_chat_async")
    async def test_llm_chat_async(self, mock_chat_async):
        mock_chat_async.return_value = "response"
        response = await llm_chat_async([{"role": "user", "content": "test"}])
        self.assertEqual(response, "response")

    @patch.dict(os.environ, {"LLM_PROVIDER": "openrouter"})
    @patch("utility_pack.llm.openrouter_prompt")
    def test_llm_prompt(self, mock_prompt):
        mock_prompt.return_value = "response"
        response = llm_prompt("test")
        self.assertEqual(response, "response")

    @patch.dict(os.environ, {"LLM_PROVIDER": "openrouter"})
    @patch("utility_pack.llm.openrouter_prompt_async")
    async def test_llm_prompt_async(self, mock_prompt_async):
        mock_prompt_async.return_value = "response"
        response = await llm_prompt_async("test")
        self.assertEqual(response, "response")

    @patch.dict(os.environ, {"LLM_PROVIDER": "openrouter"})
    @patch("utility_pack.llm.openrouter_chat_stream")
    async def test_llm_chat_stream(self, mock_chat_stream):
        async def mock_stream_gen():
            yield "response"

        mock_chat_stream.return_value = mock_stream_gen()
        chunks = [chunk async for chunk in llm_chat_stream([{"role": "user", "content": "test"}])]
        self.assertEqual(chunks, ["response"])

    @patch.dict(os.environ, {"LLM_PROVIDER": "openrouter"})
    @patch("utility_pack.llm.openrouter_prompt_stream")
    async def test_llm_prompt_stream(self, mock_prompt_stream):
        async def mock_stream_gen():
            yield "response"

        mock_prompt_stream.return_value = mock_stream_gen()
        chunks = [chunk async for chunk in llm_prompt_stream("test")]
        self.assertEqual(chunks, ["response"])


if __name__ == "__main__":
    unittest.main()
