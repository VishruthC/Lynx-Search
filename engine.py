import os
import chromadb
from chromadb.utils import embedding_functions

# 1. Initialize the Chroma client (persists data locally in a folder)
chroma_client = chromadb.PersistentClient(path="./search_index")

# 2. Define a local embedding function using a lightweight open-source model
# This model will run locally on your machine and convert sentences into 384-dimensional vectors.
embedding_model = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

# 3. Create or get our search collection
collection = chroma_client.get_or_create_collection(
    name="my_documents", 
    embedding_function=embedding_model
)

def index_documents(docs_folder):
    """Reads text files from a folder and indexes them into the vector DB."""
    if not os.path.exists(docs_folder):
        print(f"Error: Folder '{docs_folder}' not found.")
        return

    documents = []
    metadatas = []
    ids = []

    for filename in os.listdir(docs_folder):
        if filename.endswith(".txt"):
            file_path = os.path.join(docs_folder, filename)
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                documents.append(content)
                metadatas.append({"source": filename})
                ids.append(filename) # Using filename as a unique ID

    if documents:
        # Upsert adds new documents or updates them if the ID already exists
        collection.upsert(documents=documents, metadatas=metadatas, ids=ids)
        print(f" Successfully indexed {len(documents)} documents!")
    else:
        print("No .txt files found to index.")

def search(query_text, max_results=2):
    """Queries the vector database for the most semantically similar documents."""
    results = collection.query(
        query_texts=[query_text],
        n_results=max_results
    )
    
    print(f"\n Search Results for: '{query_text}'")
    print("-" * 50)
    
    # Iterate through the results and display them cleanly
    for i in range(len(results['ids'][0])):
        doc_id = results['ids'][0][i]
        document = results['documents'][0][i]
        distance = results['distances'][0][i] # Lower distance = closer match
        
        print(f"Match #{i+1} | Source: {doc_id} | Similarity Distance: {distance:.4f}")
        print(f"Content: {document}\n")

if __name__ == "__main__":
    # Index our local files
    print("Indexing documents...")
    index_documents("./documents")
    
    # Test queries
    search("Who controls the financial and commercial rights of Grand Prix racing")
    search("How fast does an f1 car go on the straights?")