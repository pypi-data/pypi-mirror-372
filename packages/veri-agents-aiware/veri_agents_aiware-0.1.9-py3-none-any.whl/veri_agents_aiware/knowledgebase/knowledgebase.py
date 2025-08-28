import logging
from typing import Any, AsyncGenerator, Iterator, Optional, TypedDict, cast
from pydantic import Field
from veri_agents_aiware.aiware_client.client import AgentsAiware
from veri_agents_aiware.aiware_client.graphql.client_generated.fragments import TDOMeta
from aiware.search.models import (
    VectorSearchRequest,
    VectorSearchRequestFilter,
    VectorSearchRequestFilterOperator,
    VectorSearchRequestSemanticSearch,
    VectorSearchRequestSemanticSearchVectorSimilarity,
    VectorSearchResultsResultVector,
)
from veri_agents_aiware.utils import not_none
from veri_agents_knowledgebase import Knowledgebase, KnowledgeFilter
from langchain_core.documents.base import BaseMedia
from langchain_core.embeddings import Embeddings
from langchain_core.tools import BaseTool
from langchain_core.messages.utils import count_tokens_approximately
import cachetools.func
from veri_agents_knowledgebase.knowledgebase import and_filters
from veri_agents_knowledgebase.types import Document, DocumentChunk, DocumentChunks, DocumentReference, ScoredDocumentChunk, ScoredDocumentChunks
import yaml

log = logging.getLogger(__name__)


class TDODocumentReferenceMetadata(TypedDict):
    name: str
    created_date_time: str | None
    modified_date_time: str | None


class VectorResultDocumentChunkMetadata(TypedDict):
    relevancy_score: float


Default_AiwareKnowledgebase_Name = "Aiware"


class AiwareKnowledgebase(Knowledgebase):
    def __init__(
        self,
        aiware: AgentsAiware,
        embedding_model_name: str,
        embedding_model: Embeddings,
        filter: KnowledgeFilter | None = None,
        # retrieve_summaries: bool = True,
        # retrieve_parents: bool = True,
        # retrieve_parents_max_tokens: int = 10000,
        # retrieve_parents_num: int = 3,
        # retrieve_total_tokens: int = 70000,
        name: str = Default_AiwareKnowledgebase_Name,
        **kwargs,
    ):
        """Initialize the Aiware knowledge base.

        Args:
            aiware (Aiware): The Aiware client (with auth)
            embedding_model_name (str): The name of the embedding model - used for DB slicing.
            embedding_model (Embeddings): The embedding model to use for vectorization.
            filter (KnowledgeFilter | None): Optional filter to apply to the knowledge base.
        """
        super().__init__(name=name, **kwargs)

        self.aiware = aiware

        self.filter = filter
        # self.retrieve_summaries = retrieve_summaries
        # self.retrieve_parents = retrieve_parents
        # self.retrieve_parents_max_tokens = retrieve_parents_max_tokens
        # self.retrieve_parents_num = retrieve_parents_num
        # self.retrieve_total_tokens = retrieve_total_tokens

        self.embedding_model_name = embedding_model_name
        self.embedding_model = embedding_model

    @cachetools.func.ttl_cache(maxsize=1, ttl=360)
    def _load_tags(self) -> dict[str, str]:
        """Load tags from the documents in the knowledge base."""
        tags = self.metadata.tags
        # TODO
        return tags

    @property
    def tags(self):
        """Get the tags for the workflow."""
        return self._load_tags()

    @staticmethod
    def _to_aiware_filter(filter: KnowledgeFilter) -> VectorSearchRequestFilter:
        and_conditions: list[VectorSearchRequestFilter] = []

        if filter.docs is not None:
            docs = filter.docs if isinstance(filter.docs, list) else [filter.docs]
            docs_conditions: list[VectorSearchRequestFilter] = []
            for doc in docs:
                docs_conditions.append(
                    VectorSearchRequestFilter(
                        operator=VectorSearchRequestFilterOperator.term,
                        field="recordingId",
                        value=doc,
                    )
                )
            and_conditions.append(
                VectorSearchRequestFilter(
                    operator=VectorSearchRequestFilterOperator.or_,
                    conditions=cast(
                        Any,
                        docs_conditions,
                    ),
                )
            )

        if filter.pre_tags_any_of is not None:
            log.warning(
                "AiwareKnowledgebase.retrieve does not support filter.pre_tags_any_of parameter"
            )
        if filter.pre_tags_all_of is not None:
            log.warning(
                "AiwareKnowledgebase.retrieve does not support filter.pre_tags_all_of parameter"
            )
        if filter.tags_any_of is not None:
            log.warning(
                "AiwareKnowledgebase.retrieve does not support filter.tags_any_of parameter"
            )
        if filter.tags_all_of is not None:
            log.warning(
                "AiwareKnowledgebase.retrieve does not support filter.tags_all_of parameter"
            )

        return VectorSearchRequestFilter(
            operator=VectorSearchRequestFilterOperator.and_,
            conditions=cast(
                Any,
                and_conditions,
            ),
        )

    def _resolve_filter(self, filter: KnowledgeFilter | None = None) -> KnowledgeFilter:
        resolved_filter = and_filters(self.filter, filter)

        if resolved_filter is None or not resolved_filter.docs:
            raise RuntimeError("filter.docs is required")

        return resolved_filter

    def _get_aiware_filter(
        self, filter: KnowledgeFilter | None = None
    ) -> VectorSearchRequestFilter:
        aiware_filters: list[VectorSearchRequestFilter] = [
            VectorSearchRequestFilter(
                operator=VectorSearchRequestFilterOperator.term,
                field="tags.key",
                value="embedding-model",
            ),
            VectorSearchRequestFilter(
                operator=VectorSearchRequestFilterOperator.term,
                field="tags.value",
                value=self.embedding_model_name,
            ),
        ]

        resolved_user_filter = self._resolve_filter(filter=filter)

        aiware_filters.append(
            AiwareKnowledgebase._to_aiware_filter(resolved_user_filter)
        )

        return VectorSearchRequestFilter(
            operator=VectorSearchRequestFilterOperator.and_,
            conditions=cast(
                Any,
                aiware_filters,
            ),
        )
    
    def _doc_meta_from_tdo(self, tdo: TDOMeta) -> TDODocumentReferenceMetadata:
        return {
            "name": tdo.name or "Unknown",
            "created_date_time": tdo.createdDateTime.__str__(),
            "modified_date_time": tdo.modifiedDateTime.__str__(),
        }

    def _doc_ref_from_tdo(self, tdo: TDOMeta) -> DocumentReference:
        return DocumentReference(id=tdo.id, metadata=self._doc_meta_from_tdo(tdo))
    
    def _doc_content_from_tdo(self, tdo: TDOMeta) -> str:
        raise NotImplementedError

    def _doc_from_tdo(self, tdo: TDOMeta) -> Document:
        return Document(id=tdo.id, page_content=self._doc_content_from_tdo(tdo), metadata=self._doc_meta_from_tdo(tdo))

    def _doc_chunk_from_result(
        self, tdo_ref: DocumentReference, result: VectorSearchResultsResultVector
    ) -> ScoredDocumentChunk:
        chunk_content: Optional[str] = None
        chunk_meta: VectorResultDocumentChunkMetadata = {
            "relevancy_score": result.score
        }

        if result.model_extra and (tags := result.model_extra.get("tags")):
            for tag in cast(list, tags):
                if tag["key"] == "input":
                    chunk_content = cast(str, tag["value"])
                    break

        if chunk_content is None:
            raise Exception("tags.input not present")

        return ScoredDocumentChunk(id=tdo_ref.id, score=result.score, chunk_content=chunk_content, metadata=cast(dict, chunk_meta))

    def search(
        self,
        query: str,
        limit: int,
        filter: KnowledgeFilter | None = None,
        **kwargs,
    ) -> Iterator[ScoredDocumentChunks]:
        aiware_filter = self._get_aiware_filter(filter)

        query_embeddings = self.embedding_model.embed_query(query)

        vector_search_res = self.aiware.search.vector_search(
            VectorSearchRequest(
                limit=limit,
                semanticSearch=VectorSearchRequestSemanticSearch(
                    vectorSimilarity=VectorSearchRequestSemanticSearchVectorSimilarity(
                        rawData=query_embeddings
                    ),
                ),
                select=["tags"],
                filters=[aiware_filter],
            )
        )

        results = vector_search_res.results
        if not results:
            return

        results_per_tdo: dict[
            str, tuple[list[VectorSearchResultsResultVector], float]
        ] = {
            not_none(result.recordingId): (result.vectors, result.score)
            for result in results
        }

        # # Get all scores and select the top n tdos
        # top_tdos = sorted(
        #     chunks_per_tdo.items(),
        #     key=lambda item: sum(chunk_ref.score for chunk_ref in item[1]),
        #     reverse=True,
        # )[: self.retrieve_parents_num]
        # top_tdo_ids = [tdo_id for tdo_id, _ in top_tdos]

        tdo_ids = [tdo_id for tdo_id in results_per_tdo.keys()]
        tdos_res = self.aiware.graphql.rag_get_td_os_meta(
            ids=tdo_ids, idsCount=len(tdo_ids)
        )

        if (
            tdos_res.temporalDataObjects is None
            or tdos_res.temporalDataObjects.records is None
        ):
            return

        tdos: dict[str, TDOMeta] = {}
        for tdo_res in tdos_res.temporalDataObjects.records:
            if tdo_res is None:
                continue
            tdos[tdo_res.id] = tdo_res

        for tdo_id, (tdo_results, _) in results_per_tdo.items():
            tdo = tdos.get(tdo_id, None)
            if tdo is None:
                continue

            tdo_ref = self._doc_ref_from_tdo(tdo)

            # tdo_ret_chunks: list[DocumentChunk] = []
            # tdo_ret: DocumentReference = {"parent_doc": tdo_ref.metadata, "chunks": []}
            tdo_chunks: ScoredDocumentChunks = ScoredDocumentChunks(id=tdo_ref.id, metadata=tdo_ref.metadata, chunks=[])

            for tdo_result in tdo_results:
                doc_chunk = self._doc_chunk_from_result(tdo_ref, tdo_result)
                tdo_chunks.chunks.append(doc_chunk)

            yield tdo_chunks

    async def asearch(
        self,
        query: str,
        limit: int,
        filter: KnowledgeFilter | None = None,
    ) -> AsyncGenerator[ScoredDocumentChunks, None]:
        # TODO: optimize
        for doc_chunks in self.search(query=query, limit=limit, filter=filter):
            yield doc_chunks

    def list_documents(
        self,
        filter: KnowledgeFilter | None = None,
    ) -> Iterator[DocumentReference]:
        """List all documents from the knowledge base."""
        resolved_user_filter = self._resolve_filter(filter=filter)

        if not resolved_user_filter.docs_list:
            raise RuntimeError(
                "filter (in constructor or as arg) is required for list_documents"
            )

        tdo_ids = resolved_user_filter.docs_list
        tdos_res = self.aiware.graphql.rag_get_td_os_meta(
            ids=tdo_ids, idsCount=len(tdo_ids)
        )

        if (
            tdos_res.temporalDataObjects is None
            or tdos_res.temporalDataObjects.records is None
        ):
            return iter([])

        docs: list[DocumentReference] = []

        for tdo_res in tdos_res.temporalDataObjects.records:
            if tdo_res is None:
                continue

            tdo = tdo_res

            tdo_doc = self._doc_ref_from_tdo(tdo)
            docs.append(tdo_doc)

        return iter(docs)

    async def alist_documents(
        self,
        filter: KnowledgeFilter | None = None,
    ) -> AsyncGenerator[DocumentReference, None]:
        """List all documents from the knowledge base."""
        for doc in self.list_documents(filter=filter):
            yield doc

    def get_documents(
        self,
        filter: KnowledgeFilter | None = None,
    ) -> Iterator[Document]:
        """Get all documents from the knowledge base."""
        resolved_user_filter = self._resolve_filter(filter=filter)

        if not resolved_user_filter.docs_list:
            raise RuntimeError(
                "filter (in constructor or as arg) is required for get_documents"
            )

        tdo_ids = resolved_user_filter.docs_list
        tdos_res = self.aiware.graphql.rag_get_td_os_meta(
            ids=tdo_ids, idsCount=len(tdo_ids)
        )

        if (
            tdos_res.temporalDataObjects is None
            or tdos_res.temporalDataObjects.records is None
        ):
            return iter([])

        docs: list[Document] = []

        for tdo_res in tdos_res.temporalDataObjects.records:
            if tdo_res is None:
                continue

            tdo = tdo_res

            tdo_doc = self._doc_from_tdo(tdo)
            docs.append(tdo_doc)

        return iter(docs)

    async def aget_documents(
        self,
        filter: KnowledgeFilter | None = None,
    ) -> AsyncGenerator[Document, None]:
        """Get all documents from the knowledge base."""
        for doc in self.get_documents(filter=filter):
            yield doc

    def get_tools(
        self,
        search_tools: bool = True,
        list_tools: bool = True,
        retrieve_tools: bool = True,
        write_tools: bool = False,
        name_suffix: str | None = None,
        runnable_config_filter_prefix: str | None = None,
        **kwargs: Any,
    ) -> list[BaseTool]:
        """Get agent tools to access this knowledgebase.

        Args:
            search_tools (bool): Whether to include tools for searching documents.
            list_docs_tools (bool): Whether to include tools for listing documents.
            get_docs_tools (bool): Whether to include tools for retrieving documents.
            write_tools (bool): Whether to include tools for writing documents.
        Returns:
            list[BaseTool]: List of tools for the knowledge base.
        """
        from veri_agents_aiware.knowledgebase.tools import (
            AiwareKnowledgebaseListDocuments,
            AiwareKnowledgebaseSearch,
            # AiwareKnowledgebaseRetrieveDocuments
        )

        tools = []

        resolved_name_suffix = (
            self.metadata.collection
            or (
                self.metadata.name
                if self.metadata.name != Default_AiwareKnowledgebase_Name
                else None
            )
            if name_suffix is None
            else name_suffix
        )

        if search_tools:
            tools.append(
                AiwareKnowledgebaseSearch(
                    knowledgebase=self,
                    num_results=kwargs.get("num_results", 10),
                    name_suffix=f"_{resolved_name_suffix}" if resolved_name_suffix else None,
                )
            )
        if list_tools:
            tools.append(
                AiwareKnowledgebaseListDocuments(
                    knowledgebase=self,
                    name_suffix=f"_{resolved_name_suffix}" if resolved_name_suffix else None,
                )
            )
        # if retrieve_tools:
        #     tools.append(
        #         AiwareKnowledgebaseRetrieveDocuments(
        #             knowledgebase=self,
        #             name_suffix=f"_{resolved_name_suffix}" if resolved_name_suffix else None,
        #         )
        #     )

        return tools
