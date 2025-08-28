import asyncio
import os
import time
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image

from utility_pack.decorators import (
    custom_lru_cache,
    disk_lru_cache,
    make_hashable,
    retry,
    timed_lru_cache,
)


def test_make_hashable():
    assert isinstance(make_hashable([1, 2, 3]), tuple)
    assert isinstance(make_hashable({"a": 1, "b": 2}), tuple)
    assert isinstance(make_hashable({1, 2, 3}), tuple)

    img = Image.new("RGB", (60, 30), color="red")
    hashed_img = make_hashable(img)
    assert isinstance(hashed_img, tuple)
    assert hashed_img[0] == "PIL_Image"


def test_timed_lru_cache():
    @timed_lru_cache(max_size=2, minutes=0.01)
    def dummy_func(x):
        return x * 2

    assert dummy_func(2) == 4
    assert dummy_func(2) == 4
    dummy_func(3)
    dummy_func(4)
    dummy_func(5)
    time.sleep(0.61)
    assert dummy_func(2) == 4


@pytest.mark.asyncio
async def test_timed_lru_cache_async():
    @timed_lru_cache(max_size=2, minutes=0.01)
    async def dummy_async_func(x):
        await asyncio.sleep(0.01)
        return x * 2

    assert await dummy_async_func(2) == 4
    assert await dummy_async_func(2) == 4


def test_disk_lru_cache(tmpdir):
    cache_file = tmpdir.join("cache.pkl")

    @disk_lru_cache(max_size=2, cache_file=str(cache_file))
    def dummy_func(x):
        return x * 2

    assert dummy_func(2) == 4
    assert dummy_func(2) == 4
    assert os.path.exists(cache_file)


@pytest.mark.asyncio
async def test_disk_lru_cache_async(tmpdir):
    cache_file = tmpdir.join("cache.pkl")

    @disk_lru_cache(max_size=2, cache_file=str(cache_file))
    async def dummy_async_func(x):
        await asyncio.sleep(0.01)
        return x * 2

    assert await dummy_async_func(2) == 4
    assert await dummy_async_func(2) == 4
    assert os.path.exists(cache_file)


def test_retry():
    mock_func = MagicMock(side_effect=[Exception("fail"), 42])

    @retry(retry_count=1, delay=0.01)
    def dummy_func():
        return mock_func()

    assert dummy_func() == 42
    assert mock_func.call_count == 2


@pytest.mark.asyncio
async def test_retry_async():
    mock_func = MagicMock(side_effect=[Exception("fail"), 42])

    @retry(retry_count=1, delay=0.01)
    async def dummy_async_func():
        await asyncio.sleep(0.01)
        return mock_func()

    assert await dummy_async_func() == 42
    assert mock_func.call_count == 2


def test_custom_lru_cache():
    @custom_lru_cache(max_size=2)
    def dummy_func(x):
        return x * 2

    assert dummy_func(2) == 4
    assert dummy_func(2) == 4
    dummy_func(3)
    dummy_func(4)
    dummy_func(5)
    assert dummy_func(2) == 4


@pytest.mark.asyncio
async def test_custom_lru_cache_async():
    @custom_lru_cache(max_size=2)
    async def dummy_async_func(x):
        await asyncio.sleep(0.01)
        return x * 2

    assert await dummy_async_func(2) == 4
    assert await dummy_async_func(2) == 4
