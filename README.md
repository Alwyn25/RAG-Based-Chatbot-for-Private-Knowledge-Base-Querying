<p align="center"> <h1>RAG-Based-Chatbot-for-Private-Knowledge-Base-Querying</h1></p>

<p align="center"> The RAG-Based Chatbot for Private Knowledge Base Querying is a system designed to efficiently retrieve relevant information from a private knowledge base in response to user queries. RAG, short for Retrieve and Generate, is a framework that combines retrieval-based and generation-based methods for natural language processing tasks. This chatbot utilizes the RAG framework to provide accurate and contextually relevant answers to user questions within a private knowledge base.</p>

<details open>
  <summary><h2>Operation steps:</h2></summary>

- Text Corpus Chunking: The entire knowledge base is divided into manageable chunks, each representing a distinct piece of context available for querying. These chunks may comprise various data sources, such as documentation in Confluence and PDF reports.

- Chunk Embedding: Each chunk of text is transformed into a vector embedding using an embedding model. This process converts the textual information into a numerical representation suitable for computational operations.

- Vector Database Storage: All vector embeddings generated from the text chunks are stored in a vector database for efficient retrieval during query processing.

- Embedding Text Mapping: The system saves the original text corresponding to each vector embedding, along with a pointer to the embedding. This mapping facilitates the reconstruction of context when presenting answers to user queries.

- Query Embedding: When a user submits a question or query, it is embedded into a vector representation using the same embedding model employed for the text corpus chunks.

- Vector Database Query: The vector representation of the query is used to perform a query against the index in the vector database. The system retrieves a predetermined number of context vectors that are most similar to the query vector through an approximate nearest neighbor search.

- Approximate Nearest Neighbor Search: The vector database employs an approximate nearest neighbor search algorithm to efficiently find context vectors that closely match the query vector in the embedding/latent space.

- Embedding-Text Mapping: The retrieved context vectors are mapped back to their corresponding text chunks in the knowledge base. This mapping links the numerical representations to the original textual context.

- Contextual Query to LLM: The question, along with the retrieved context text chunks, is passed to a Large Language Model (LLM) via prompt. The LLM is instructed to use only the provided context to generate an answer to the given question. Prompt engineering techniques are employed to ensure that the answers generated by the LLM are relevant and accurate based on the provided context.

</details>

<details open>
  <summary><h2><img width="32" height="32" src="https://img.icons8.com/windows/32/product-architecture.png" alt="product-architecture"/>  Rag Architecture:</h2></summary>
  <p align="center">
    <img src="https://github.com/Alwyn25/RAG-Based-Chatbot-for-Private-Knowledge-Base-Querying/assets/99828232/ce4299fd-6b71-4b1b-b50a-b360d1386c0d" alt="Image">
</p>
</details>


