""" """

# import
from typing import List, Dict, Optional
import os
import logging
from pathlib import Path
from .store import Store
from .registry import Registry, ModelWeights
from .search import Search

logger = logging.getLogger(__name__)


class RAGService:
    """RAG service for retrieving relevant context from the knowledge base."""

    def __init__(
        self,
        embeddings_path: Path,
        config_path: Path,
        weights_path: Path,
        use_dual_embedding: Optional[bool] = None,
    ):
        """
        Initialize the RAG service.

        Args:
            embeddings_path: Path to the txtai embeddings index
            config_path: Path to the repositories configuration file
            weights_path: Path to the model weights file
            use_dual_embedding: Whether to use dual embedding models (general + code).
                               If None, reads from USE_DUAL_EMBEDDING environment variable.
        """
        # Read dual embedding setting from environment if not explicitly set
        if use_dual_embedding is None:
            use_dual_embedding = os.environ.get("USE_DUAL_EMBEDDING", "true").lower() == "true"

        # Initialize core components
        self.registry = Registry(config_path, use_dual_embedding=use_dual_embedding)
        self.store = Store(embeddings_path.parent)
        self.search = Search(
            embeddings_path,
            dual=use_dual_embedding,
            code_model=os.environ.get("CODE_EMBEDDING_MODEL", "microsoft/codebert-base"),
        )
        self.weights = ModelWeights(weights_path)

        # Store paths
        self.embeddings_path = embeddings_path
        self.config_path = config_path
        self.weights_path = weights_path
        self.use_dual_embedding = use_dual_embedding

        self._weights = {}  # runtime weights set via API

    """
    def search(self, query, limit):
        hits = self.search.run(query, limit)
        # apply weights via self.weights then return
    def retrieve(self, doc_id, start, end):
        meta = self.registry.get_meta(doc_id)
        text = self.store.read_lines(doc_id, start, end)
        return Passage(doc_id, text, meta.github_url, meta.content_sha256)
    # list_tree, set_weight, version() similarly thin"""

    def get_context_for_query(self, query: str, max_chars: int = 4000) -> str:
        """
        Get formatted context for a query, suitable for LLM prompts.

        Args:
            query: Search query
            max_chars: Maximum characters to include in context

        Returns:
            Formatted context string
        """
        results = self.search(query, limit=5)

        if not results:
            return "No relevant information found."

        context_parts = []
        current_length = 0

        for result in results:
            # Get GitHub URL for this document
            github_url = self._get_github_url(result["id"])

            # Truncate text if needed (allow more content per document)
            text = result["text"]

            # Add document info with both source path and GitHub link
            if github_url:
                # Extract filename for link text
                filename = result["id"].split("/")[-1]
                doc_info = f"Source: {result['id']}\nGitHub URL: <{github_url}|{filename}>\n"
            else:
                doc_info = f"Source: {result['id']}\n"

            content = f"{text}\n\n"

            # Check if adding this would exceed max_chars
            if current_length + len(doc_info) + len(content) > max_chars:
                break

            context_parts.append(doc_info + content)
            current_length += len(doc_info) + len(content)

        if not context_parts:
            return "No relevant information found."

        return "".join(context_parts).strip()

    def get_raw_results_for_ai(self, query: str, limit: int = 5) -> List[Dict[str, str]]:
        """
        Get raw RAG results with GitHub URLs for AI processing.

        Args:
            query: Search query
            limit: Maximum number of results to return

        Returns:
            List of dictionaries with 'id', 'text', 'score', and 'github_url' keys
        """
        results = self.search(query, limit)

        enhanced_results = []
        for result in results:
            github_url = self._get_github_url(result["id"])
            enhanced_results.append(
                {
                    "id": result["id"],
                    "text": result["text"],
                    "score": result["score"],
                    "github_url": github_url,
                    "model_score": result.get("model_score", 1.0),
                    "extension_weight": result.get("extension_weight", 1.0),
                    "adjusted_score": result.get("adjusted_score", result["score"]),
                }
            )

        return enhanced_results

    def get_detailed_context(self, query: str, max_chars: int = 6000) -> str:
        """
        Get detailed context with more content per document.

        Args:
            query: Search query
            max_chars: Maximum characters to include in context

        Returns:
            Formatted context string with more detailed content
        """
        results = self.search(query, limit=2)  # Fewer results, more content each

        if not results:
            return "No relevant information found."

        context_parts = []
        current_length = 0

        for result in results:
            # Get GitHub URL for this document
            github_url = self._get_github_url(result["id"])

            # Allow much more content per document
            text = result["text"]

            # Add document info with both source path and GitHub link
            if github_url:
                # Extract filename for link text
                filename = result["id"].split("/")[-1]
                doc_info = f"Source: {result['id']}\nGitHub URL: <{github_url}|{filename}>\n"
            else:
                doc_info = f"Source: {result['id']}\n"

            content = f"{text}\n\n"

            # Check if adding this would exceed max_chars
            if current_length + len(doc_info) + len(content) > max_chars:
                break

            context_parts.append(doc_info + content)
            current_length += len(doc_info) + len(content)

        if not context_parts:
            return "No relevant information found."

        return "".join(context_parts).strip()

    def is_available(self) -> bool:
        """Check if the RAG service is available and ready."""
        return self.general_embeddings is not None

    async def search_docs(
        self,
        query: str,
        limit: int = 6,
        toolkit: str = None,
        doctype: str = None,
        threshold: float = 0.0,
    ) -> List[Dict]:
        """Search for documents with optional filtering."""
        # Before searching, push runtime weights into search.model_weights (backwards compatibility)
        if self._weights:
            # Merge without losing existing file-based model weights
            self.search.model_weights.update(self._weights)

        # Get initial search results
        results = self.search.search(query, limit * 2)  # Get more to allow for filtering

        # Apply filters if specified
        if toolkit or doctype:
            filtered_results = []
            for result in results:
                doc_id = result["id"]
                meta = self.registry.get_meta(doc_id)

                # Check toolkit filter
                if toolkit and meta.toolkit != toolkit:
                    continue

                # Check doctype filter
                if doctype and meta.doctype != doctype:
                    continue

                filtered_results.append(result)
            results = filtered_results

        # Apply threshold filter
        if threshold > 0.0:
            results = [r for r in results if r["score"] >= threshold]

        # Return top results up to limit
        return results[:limit]

    async def retrieve(self, doc_id: str, start: int = None, end: int = None) -> Dict:
        """Retrieve a span of text from a document."""
        # Default full document if no range provided
        if start is None or end is None:
            text = self.store.read_lines(doc_id)
        else:
            text = self.store.read_lines(doc_id, start, end)
        meta = self.registry.get_meta(doc_id)
        return {
            "doc_id": doc_id,
            "text": text,
            "github_url": meta.github_url,
            "content_sha256": meta.content_sha256,
        }

    async def retrieve_batch(self, items: List[Dict]) -> List[Dict]:
        """Retrieve multiple text spans in batch."""
        results = []
        for item in items:
            doc_id = item["doc_id"]
            start = item.get("start")
            end = item.get("end")
            try:
                result = await self.retrieve(doc_id, start, end)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to retrieve {doc_id}: {e}")
                # Add placeholder with error info
                results.append(
                    {
                        "doc_id": doc_id,
                        "text": f"Error retrieving document: {str(e)}",
                        "github_url": "",
                        "content_sha256": "",
                        "error": str(e),
                    }
                )
        return results

    async def list_tree(self, prefix: str = "", depth: int = 2, max_entries: int = 500) -> List[Dict]:
        """List document IDs under a prefix as a tree structure."""
        # Get document IDs from the actual search index, not the registry config
        if not self.search.general_embeddings:
            return []

        try:
            # Get all document IDs from the search index by doing a broad search
            # txtai doesn't have a direct "list all IDs" method, so we search for common terms
            all_results = []

            # Try several broad searches to get as many document IDs as possible
            search_terms = ["the", "and", "a", "import", "def", "class", "README", "docs"]
            seen_ids = set()

            for term in search_terms:
                try:
                    results = self.search.general_embeddings.search(term, limit=2000)
                    for result in results:
                        doc_id = result.get("id", "")
                        if doc_id and doc_id not in seen_ids:
                            if not prefix or doc_id.startswith(prefix):
                                all_results.append(doc_id)
                                seen_ids.add(doc_id)
                except Exception:
                    # Skip documents that can't be parsed
                    continue

                # Stop if we have enough diverse results
                if len(seen_ids) > 1000:
                    break

            # Filter by prefix
            if prefix:
                doc_ids = [doc_id for doc_id in all_results if doc_id.startswith(prefix)]
            else:
                doc_ids = all_results

        except Exception:
            # Fallback to registry-based approach if search fails
            doc_ids = self.registry.list_ids(prefix)

        # Convert flat list to tree structure
        tree_entries = []
        seen_paths = set()

        # First pass: collect ALL paths (not limited by max_entries) to properly detect directories
        all_paths = set()
        for doc_id in doc_ids:
            parts = doc_id.split("/")
            for i in range(1, min(len(parts), depth + 1) + 1):  # Go one level deeper to detect directories
                path = "/".join(parts[:i])
                all_paths.add(path)

        # Second pass: build tree entries (limited by max_entries for display)
        entries_added = 0
        for doc_id in doc_ids:
            if entries_added >= max_entries:
                break

            parts = doc_id.split("/")
            for i in range(1, min(len(parts), depth) + 1):
                path = "/".join(parts[:i])
                if path not in seen_paths:
                    seen_paths.add(path)

                    # Check if this path has any children (making it a directory)
                    is_directory = any(other_path.startswith(path + "/") for other_path in all_paths)

                    tree_entries.append(
                        {
                            "path": path,
                            "type": "directory" if is_directory else "file",
                            "doc_id": doc_id if i == len(parts) else None,
                        }
                    )
                    entries_added += 1

                    if entries_added >= max_entries:
                        break

        return tree_entries

    async def set_weight(
        self,
        doc_id: str,
        multiplier: float,
        namespace: str = "global",
        ttl_days: int = None,
    ) -> None:
        """Set model weight for a document (runtime only). Extra parameters ignored for backward compatibility."""
        if not hasattr(self, "_weights"):
            self._weights = {}
        try:
            m = float(multiplier)
        except Exception:
            m = 1.0
        # Clamp similar to search logic expectations
        m = max(0.1, min(m, 10.0))
        self._weights[doc_id] = m
        # Immediately reflect in search (so next call sees it)
        self.search.model_weights[doc_id] = m
        logger.info(f"Runtime weight set for {doc_id}: {m}")

    async def version(self) -> Dict:
        """Return index and build version info, with robust error handling for build info and extra environment details."""
        import sys
        import platform
        from nancy_brain import __version__

        __build_sha__ = "unknown"
        __built_at__ = "unknown"
        try:
            from nancy_brain import _build_info

            __build_sha__ = getattr(_build_info, "__build_sha__", "unknown")
            __built_at__ = getattr(_build_info, "__built_at__", "unknown")
        except (ImportError, AttributeError, Exception):
            pass

        # Gather environment info
        python_version = platform.python_version()
        implementation = platform.python_implementation()
        environment = os.environ.get("CONDA_DEFAULT_ENV") or os.environ.get("VIRTUAL_ENV") or "unknown"

        # Try to get key dependency versions
        def get_version(pkg):
            try:
                return __import__(pkg).__version__
            except Exception:
                return "unknown"

        dependencies = {
            "fastapi": get_version("fastapi"),
            "pydantic": get_version("pydantic"),
            "txtai": get_version("txtai"),
            "faiss": get_version("faiss") if get_version("faiss") != "unknown" else get_version("faiss_cpu"),
            "torch": get_version("torch"),
            "transformers": get_version("transformers"),
        }

        return {
            "index_version": __version__,
            "build_sha": __build_sha__,
            "built_at": __built_at__,
            "python_version": python_version,
            "python_implementation": implementation,
            "environment": environment,
            "dependencies": dependencies,
        }

    async def health(self) -> Dict:
        """Return service health status."""
        try:
            # Basic health checks
            is_ready = self.registry is not None and self.store is not None and self.search is not None

            status = "ok" if is_ready else "degraded"

            return {
                "status": status,
                "registry_loaded": self.registry is not None,
                "store_loaded": self.store is not None,
                "search_loaded": self.search is not None,
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "error", "error": str(e)}
