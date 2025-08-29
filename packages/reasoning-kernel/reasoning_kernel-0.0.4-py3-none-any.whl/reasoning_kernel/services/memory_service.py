# -*- coding: utf-8 -*-
"""
A simplified memory service that integrates with Semantic Kernel's modern memory management.
"""

import logging
from typing import List, Optional

from semantic_kernel.connectors.ai.open_ai import OpenAITextEmbedding
from semantic_kernel.connectors.in_memory import InMemoryStore
from semantic_kernel.memory.memory_record import MemoryRecord

logger = logging.getLogger(__name__)


class MemoryService:
    """
    A service for interacting with Semantic Kernel's memory.
    """

    def __init__(
        self,
        memory_store: InMemoryStore,
        embedding_service: OpenAITextEmbedding,
    ):
        self._memory_store = memory_store
        self._embedding_service = embedding_service

    async def save_information_async(
        self, collection: str, text: str, id: str, description: Optional[str] = None
    ):
        """
        Saves information to the memory store.

        Args:
            collection: The collection to save the information to.
            text: The text to save.
            id: The ID of the information.
            description: A description of the information.
        """
        try:
            await self._memory_store.upsert(
                collection_name=collection,
                record=MemoryRecord(
                    id=id,
                    text=text,
                    description=description,
                    embedding=await self._embedding_service.generate_embedding(text),
                ),
            )
            logger.info(f"Saved information with ID '{id}' to collection '{collection}'.")
        except Exception as e:
            logger.error(f"Error saving information to collection '{collection}': {e}")
            raise

    async def search_async(
        self, collection: str, query: str, limit: int = 1, min_relevance_score: float = 0.7
    ) -> List[MemoryRecord]:
        """
        Searches for information in the memory store.

        Args:
            collection: The collection to search in.
            query: The query to search for.
            limit: The maximum number of results to return.
            min_relevance_score: The minimum relevance score for a result to be returned.

        Returns:
            A list of memory records.
        """
        try:
            query_embedding = await self._embedding_service.generate_embedding(query)
            results = await self._memory_store.get_nearest_matches(
                collection_name=collection,
                embedding=query_embedding,
                limit=limit,
                min_relevance_score=min_relevance_score,
            )
            logger.info(f"Found {len(results)} results in collection '{collection}' for query '{query}'.")
            return results
        except Exception as e:
            logger.error(f"Error searching in collection '{collection}': {e}")
            raise