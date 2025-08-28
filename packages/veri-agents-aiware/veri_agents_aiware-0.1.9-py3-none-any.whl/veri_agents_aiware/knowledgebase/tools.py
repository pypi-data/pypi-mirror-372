import logging
import re
from typing import TYPE_CHECKING, Optional, Tuple

from langchain.callbacks.manager import (
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool
from langchain_core.runnables.config import RunnableConfig
from langchain_core.messages.utils import count_tokens_approximately
from pydantic import BaseModel, Field
from veri_agents_knowledgebase.knowledgebase import KnowledgeFilter
from veri_agents_aiware.knowledgebase.knowledgebase import AiwareKnowledgebase
from veri_agents_knowledgebase.types import Document, DocumentReference, ScoredDocumentChunks
import yaml

log = logging.getLogger(__name__)

def _escape_tool_name(name: str) -> str:
    return "".join(re.findall('[a-zA-Z0-9_-]', name.replace("-", "_").replace(" ", "_")))

class AiwareKnowledgebaseSearchInput(BaseModel):
    query: str = Field(
        description="query to search for documents in the knowledgebase."
    )
    documents: Optional[list[str] | str] = Field(
        default=None,
        description="Documents are selected only if they match the document IDs in the list. Useful if you only want to search inside specific documents.",
    )


class AiwareKnowledgebaseSearch(BaseTool):
    """Search for documents in an aiware knowledgebase (that can not be selected by the agent)."""

    name: str = "aiware_kb_search"
    description: str = ""
    args_schema = AiwareKnowledgebaseSearchInput
    response_format: str = "content_and_artifact"  # type: ignore
    handle_tool_errors: bool = True
    num_results: int = 10
    knowledgebase: AiwareKnowledgebase
    """ The knowledgebase to list documents from. This is passed in when the tool is created. """

    name_suffix: str | None = None
    """ You can pass in a suffix to the name of the tool. This is useful if you want to have multiple instances of this tool. """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.name_suffix:
            self.name += self.name_suffix

        self.name = _escape_tool_name(self.name)

        self.description = f"Searches for documents in the \"{self.knowledgebase.name}\" knowledgebase."
        if self.knowledgebase.description:
            self.description += f"Use this tool if you're interested in documents about {self.knowledgebase.description}."

    def _create_filter(
        self,
        documents: Optional[list[str] | str] = None,
    ) -> KnowledgeFilter:
        """Create a filter for the knowledgebase from inputs and runnable config

        Args:
            documents: If the document ID is in this list, it will be selected.
        """
        return KnowledgeFilter(
            docs=documents,
        )

    def _run(
        self,
        query: str,
        config: RunnableConfig,
        documents: Optional[list[str] | str] = None,
    ) -> Tuple[str, list[ScoredDocumentChunks]]:
        return_text = ""

        filter = self._create_filter(documents=documents)

        log.info(
            f"[AiwareKnowledgebaseSearch] Searching in knowledgebase \"{self.knowledgebase.name}\" for {query} using user filter {filter}"
        )
        docs_chunks = list(self.knowledgebase.search(
            query, limit=self.num_results, filter=filter
        ))
        log.debug(f"[AiwareKnowledgebaseSearch] Retrieved {len(docs_chunks or [])} search results")
        if not docs_chunks:
            return_text = f"No results found in the knowledgebase for query '{query}'."
        else:
            return_text = yaml.dump([doc_chunks.model_dump() for doc_chunks in docs_chunks], sort_keys=False)

            # # truncate return prompt and documents if they exceed the total token limit
            # if (
            #     return_text
            #     and count_tokens_approximately(return_text) > self.retrieve_total_tokens
            # ):
            #     return_text = return_text[: self.retrieve_total_tokens]

        return return_text, docs_chunks

    async def _arun(
        self,
        query: str,
        config: RunnableConfig,
        documents: Optional[list[str] | str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Tuple[str, list[ScoredDocumentChunks]]:
        return_text = ""

        filter = self._create_filter(documents=documents)

        log.info(
            f"[AiwareKnowledgebaseSearch] Searching in knowledgebase \"{self.knowledgebase.name}\" for {query} using user filter {filter}"
        )
        try:
            docs_chunks = [item async for item in self.knowledgebase.asearch(
                query, limit=self.num_results, filter=filter
            )]
        except NotImplementedError:
            docs_chunks = list(self.knowledgebase.search(
                query, limit=self.num_results, filter=filter
            ))
        # log.debug(f"[AiwareKnowledgebaseQuery] Retrieved {len(ret_docs)} documents.")
        log.debug(f"[AiwareKnowledgebaseSearch] Retrieved {len(docs_chunks or [])} search results")

        if not docs_chunks:
            return_text = f"No results found in the knowledgebase for query '{query}'."
        else:
            return_text = yaml.dump([doc_chunks.model_dump() for doc_chunks in docs_chunks], sort_keys=False)

            # # truncate return prompt and documents if they exceed the total token limit
            # if (
            #     return_text
            #     and count_tokens_approximately(return_text) > self.retrieve_total_tokens
            # ):
            #     return_text = return_text[: self.retrieve_total_tokens]

        return return_text, docs_chunks

class AiwareKnowledgebaseListDocumentsInput(BaseModel):
    pass

class AiwareKnowledgebaseListDocuments(BaseTool):
    """List documents in an aiware knowledgebase that is not selected by the agent."""

    name: str = "aiware_kb_list_documents"
    description: str = ""
    args_schema = AiwareKnowledgebaseListDocumentsInput
    response_format: str = "content_and_artifact"  # type: ignore
    handle_tool_errors: bool = True
    knowledgebase: AiwareKnowledgebase
    """ The knowledgebase to list documents from. This is passed in when the tool is created. """

    name_suffix: str | None = None
    """ You can pass in a suffix to the name of the tool. This is useful if you want to have multiple instances of this tool. """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.name_suffix:
            self.name += self.name_suffix

        self.name = _escape_tool_name(self.name)

        self.description = (
            f"Lists the documents in the \"{self.knowledgebase.name}\" knowledgebase. Does not return document content."
        )
        if self.knowledgebase.description:
            self.description += f"Use this tool if you're interested in documents about {self.knowledgebase.description}."

    def _create_filter(
        self,
    ) -> KnowledgeFilter:
        """Create a filter for the knowledgebase from inputs"""
        return KnowledgeFilter()

    def _run(
        self,
        config: RunnableConfig,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Tuple[str, list[DocumentReference]]:
        log.debug("[AiwareKnowledgebaseListDocuments] Listing documents")

        # filter set by the agent
        filter = self._create_filter()

        docs = list(self.knowledgebase.list_documents(filter))
        log.debug(f"[AiwareKnowledgebaseListDocuments] Retrieved {len(docs or [])} documents.")
        return yaml.dump([doc.model_dump() for doc in docs], sort_keys=False), docs
    
    async def _arun(
        self,
        config: RunnableConfig,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Tuple[str, list[DocumentReference]]:
        log.debug("[AiwareKnowledgebaseListDocuments] Listing documents")

        # filter set by the agent
        filter = self._create_filter()

        docs = [doc async for doc in self.knowledgebase.alist_documents(filter)]
        log.debug(f"[AiwareKnowledgebaseListDocuments] Retrieved {len(docs or [])} documents.")
        return yaml.dump([doc.model_dump() for doc in docs], sort_keys=False), docs
    
class AiwareKnowledgebaseRetrieveDocumentsInput(BaseModel):
    documents: list[str] | str = Field(
        description="Documents are selected only if they match the document IDs in the list.",
    )

class AiwareKnowledgebaseRetrieveDocuments(BaseTool):
    """Retrieve documents in an aiware knowledgebase (that can not be selected by the agent)."""

    name: str = "aiware_kb_retrieve_documents"
    description: str = ""
    args_schema = AiwareKnowledgebaseRetrieveDocumentsInput
    response_format: str = "content_and_artifact"  # type: ignore
    handle_tool_errors: bool = True
    num_results: int = 10
    knowledgebase: AiwareKnowledgebase
    """ The knowledgebase to retrieve documents from. This is passed in when the tool is created. """

    name_suffix: str | None = None
    """ You can pass in a suffix to the name of the tool. This is useful if you want to have multiple instances of this tool. """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.name_suffix:
            self.name += self.name_suffix

        self.name = _escape_tool_name(self.name)

        self.description = f"Retrieves specific documents' content in the \"{self.knowledgebase.name}\" knowledgebase."
        if self.knowledgebase.description:
            self.description += f"Use this tool if you're interested in documents about {self.knowledgebase.description}."

    def _create_filter(
        self,
        documents: list[str] | str,
    ) -> KnowledgeFilter:
        """Create a filter for the knowledgebase from inputs and runnable config

        Args:
            documents: If the document ID is in this list, it will be selected.
        """
        return KnowledgeFilter(
            docs=documents,
        )

    def _run(
        self,
        config: RunnableConfig,
        documents: list[str] | str,
    ) -> Tuple[str, list[Document]]:
        # We tell the LLM if the user has specified any filters
        return_text = ""

        filter = self._create_filter(documents=documents)

        log.info(
            f"[AiwareKnowledgebaseRetrieveDocuments] Retrieving documents in knowledgebase \"{self.knowledgebase.name}\" using user filter {filter}"
        )
        docs = list(self.knowledgebase.get_documents(
            filter=filter
        ))

        log.debug(f"[AiwareKnowledgebaseRetrieveDocuments] Retrieved {len(docs or [])} documents.")
        if not docs:
            return_text = f"Unable to retrieve documents in the knowledgebase with ids: {documents}."
        else:
            return_text = yaml.dump([doc.model_dump() for doc in docs])

        return return_text, docs

    async def _arun(
        self,
        config: RunnableConfig,
        documents: list[str] | str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Tuple[str, list[Document]]:
        # We tell the LLM if the user has specified any filters
        return_text = ""

        filter = self._create_filter(documents=documents)

        log.info(
            f"[AiwareKnowledgebaseRetrieveDocuments] Retrieving documents in knowledgebase \"{self.knowledgebase.name}\" using user filter {filter}"
        )
        try:
            docs = [item async for item in self.knowledgebase.aget_documents(
                filter=filter
            )]
        except NotImplementedError:
            docs = list(self.knowledgebase.get_documents(
                filter=filter
            ))

        log.debug(f"[AiwareKnowledgebaseRetrieveDocuments] Retrieved {len(docs or [])} documents.")
        if not docs:
            return_text = f"Unable to retrieve documents in the knowledgebase with ids: {documents}."
        else:
            return_text = yaml.dump([doc.model_dump() for doc in docs])
        
        return return_text, docs
