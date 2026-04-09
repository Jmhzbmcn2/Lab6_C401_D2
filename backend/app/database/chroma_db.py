import os
import chromadb
from chromadb.utils import embedding_functions
from app.utils.logger import get_logger

logger = get_logger()

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
CHROMA_PATH = os.path.join(BASE_DIR, "database", "chroma_db")

client = chromadb.PersistentClient(path=CHROMA_PATH)
emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="paraphrase-multilingual-MiniLM-L12-v2"
)

try:
    collection = client.get_collection(name="medical_services", embedding_function=emb_fn)
except Exception as e:
    logger.error(f"Cannot get ChromaDB collection: {e}")
    collection = None

def search_services(query: str, n_results: int = 10, branch: str = None) -> list:
    logger.info("=== Chroma Search START ===")
    logger.debug(f"Input Query: {query} | Filter: {branch}")
    
    if collection is None:
        logger.error("ChromaDB Collection is NULL. Proceeding to failover.")
        return []
    
    where_filter = None
    if branch:
        if "smart" in branch.lower():
            where_filter = {"branch": "Smart City"}
        elif "time" in branch.lower():
            where_filter = {"branch": "Times City"}
            
    try:
        results = collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_filter,
            include=['distances', 'documents', 'metadatas']
        )
    except Exception as e:
        logger.error(f"ChromaDB search failed: {e}")
        return []
    
    ids = results['ids'][0] if results['ids'] else []
    docs = results['documents'][0] if results['documents'] else []
    metas = results['metadatas'][0] if results['metadatas'] else []
    distances = results['distances'][0] if 'distances' in results and results['distances'] else []
    
    output = []
    logger.debug(f"Retrieved {len(ids)} candidates.")
    for i in range(len(ids)):
        dist = distances[i] if i < len(distances) else 0.0
        logger.debug(f"Candidate {i} [ID: {ids[i]}] - Distance: {dist:.4f}")
        
        output.append({
            "id": ids[i],
            "document": docs[i] if i < len(docs) else "",
            "metadata": metas[i] if i < len(metas) else {},
            "distance": dist
        })
        
    logger.info("=== Chroma Search END ===")
    return output
