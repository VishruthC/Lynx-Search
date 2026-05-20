from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import chromadb
from chromadb.utils import embedding_functions

app = FastAPI(title="Semantic Search Engine API")

# Allow your frontend UI to talk to this backend server safely
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ChromaDB client connections
chroma_client = chromadb.PersistentClient(path="./search_index")
embedding_model = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)
collection = chroma_client.get_or_create_collection(
    name="my_documents", 
    embedding_function=embedding_model
)

@app.get("/search")
def search_api(q: str = Query(..., description="The search query text"), limit: int = 3):
    """API endpoint to query the vector database and return formatted JSON."""
    if not q.strip():
        return {"query": q, "results": []}

    results = collection.query(
        query_texts=[q],
        n_results=limit
    )
    
    formatted_results = []
    
    # Safely unpack database results
    if results and 'ids' in results and len(results['ids'][0]) > 0:
        for i in range(len(results['ids'][0])):
            formatted_results.append({
                "id": results['ids'][0][i],
                "content": results['documents'][0][i],
                "source": results['metadatas'][0][i].get("source", "Unknown"),
                "chunk_index": results['metadatas'][0][i].get("chunk_index", 0),
                "distance": float(results['distances'][0][i]),
                # Invert distance into a readable confidence percentage
                "confidence_score": round((1.0 - results['distances'][0][i]) * 100, 1)
            })
            
    return {
        "query": q,
        "total_matches": len(formatted_results),
        "results": formatted_results
    }

if __name__ == "__main__":
    import uvicorn
    print("Launching Local Search Engine API on http://127.0.0.1:8000")
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)