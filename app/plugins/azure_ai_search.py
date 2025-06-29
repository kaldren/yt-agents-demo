from semantic_kernel.functions import kernel_function
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.aio import SearchClient
from semantic_kernel.connectors.ai.open_ai import AzureTextEmbedding
from azure.search.documents.models import VectorizedQuery
import os
from dotenv import load_dotenv
load_dotenv()

class AzureAISearch:
    """Azure AI Search plugin for Semantic Kernel."""

    def __init__(self):

        embedding_settings = {
            "endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
            "api_key": os.getenv("AZURE_OPENAI_API_KEY"),
            "deployment_name": os.getenv("AZURE_OPENAI_EMBEDDING_MODEL_ID")
        }

        self.azure_embedding = AzureTextEmbedding.from_dict(embedding_settings)
        

    async def embed_query(self, query: str):
        result = await self.azure_embedding.generate_embeddings([query])
        return result[0]

    @kernel_function(description="Execute this function every time you have questions about Ryanair policies, procedures, or other information.", name="search_ryanair_docs")
    async def search_ryanair_docs(self, query: str) -> str:
        """Search Ryanair docs via Azure AI Search using a vector query."""
        print(f"Searching Ryanair documents for query: {query}…")

        service_endpoint = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
        index_name = os.getenv("AZURE_SEARCH_INDEX_NAME")
        key = os.getenv("AZURE_SEARCH_API_KEY")

        # 1) get embedding
        raw_vec = await self.embed_query(query)
        vec = raw_vec.tolist()

        # 2) build the vector query
        vq = VectorizedQuery(vector=vec, k_nearest_neighbors=3, fields="text_vector")

        # 3) await the async search call to get an AsyncItemPaged

        async with SearchClient(service_endpoint, index_name, AzureKeyCredential(key)) as search_client:
            paged = await search_client.search(
                search_text=query,
                vector_queries=[vq],
                select=["chunk"],
                top=3,
            )

            # 4) now you can `async for` over it
            chunks = []
            async for doc in paged:
                chunks.append(doc["chunk"])

            # 5) return the big string
            return "\n".join(chunks)

