"""
Christofy - Enhanced RAG Pipeline with Ollama Integration

A robust RAG (Retrieval-Augmented Generation) system that supports multiple file formats
and integrates with any Ollama models for embeddings and text generation.
"""

import os
import platform
import chromadb
import requests
import json
from pathlib import Path
from typing import Union, List, Optional, Dict, Any
import logging
import time
import hashlib

__version__ = "1.0.2"
__author__ = "Aswin Christo"

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Optional imports with graceful fallbacks
try:
    import PyPDF2
    PDF_AVAILABLE = True
    USE_PYPDF2 = True
except ImportError:
    try:
        import pdfplumber
        PDF_AVAILABLE = True
        USE_PYPDF2 = False
    except ImportError:
        PDF_AVAILABLE = False
        USE_PYPDF2 = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False


class CustomOllamaEmbeddingFunction:
    """Custom Ollama embedding function with correct ChromaDB signature."""
    
    def __init__(self, model_name: str, url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.url = url.rstrip('/')
        self.api_url = f"{self.url}/api/embeddings"
        self.session = requests.Session()
        self.session.timeout = 30
    
    def __call__(self, input: Union[str, List[str]]) -> List[List[float]]:
        """Generate embeddings for input texts."""
        if isinstance(input, str):
            input_texts = [input]
        else:
            input_texts = input
        
        embeddings = []
        for text in input_texts:
            try:
                response = self.session.post(
                    self.api_url,
                    json={"model": self.model_name, "prompt": text},
                    timeout=30
                )
                
                if response.status_code != 200:
                    logger.error(f"Embedding API error: {response.status_code}")
                    raise Exception(f"Embedding API error: {response.status_code}")
                
                result = response.json()
                if 'embedding' not in result:
                    raise Exception("No embedding found in response")
                
                embeddings.append(result['embedding'])
                
            except Exception as e:
                logger.error(f"Error generating embedding: {str(e)}")
                raise e
        
        return embeddings


def get_ollama_base_url() -> str:
    """Get the appropriate Ollama base URL."""
    return os.getenv('OLLAMA_HOST', "http://localhost:11434")


def get_available_models() -> List[str]:
    """Get list of available Ollama models."""
    ollama_url = get_ollama_base_url()
    try:
        response = requests.get(f"{ollama_url}/api/tags", timeout=10)
        if response.status_code == 200:
            models = response.json()
            return [model['name'] for model in models.get('models', [])]
        return []
    except:
        return []


def validate_model(model_name: str) -> bool:
    """Validate if a model is available in Ollama."""
    available_models = get_available_models()
    
    if not available_models:
        logger.warning("Could not verify model availability. Proceeding anyway...")
        return True
    
    if model_name in available_models:
        return True
    
    # Check model variants
    base_model = model_name.split(':')[0]
    for model in available_models:
        if model.startswith(base_model):
            logger.info(f"Found model variant: {model}")
            return True
    
    logger.error(f"Model '{model_name}' not found.")
    logger.info(f"Available: {', '.join(available_models[:5])}")
    logger.info(f"Install with: ollama pull {model_name}")
    return False


def extract_text_from_pdf(file_path: Path) -> str:
    """Extract text from PDF files."""
    if not PDF_AVAILABLE:
        raise ImportError("PDF support not available. Install: pip install PyPDF2 or pdfplumber")
    
    text = ""
    try:
        if USE_PYPDF2:
            import PyPDF2
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
        else:
            import pdfplumber
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
    except Exception as e:
        logger.error(f"Error reading PDF: {e}")
        raise
    
    return text.strip()


def extract_text_from_docx(file_path: Path) -> str:
    """Extract text from DOCX files."""
    if not DOCX_AVAILABLE:
        raise ImportError("DOCX support not available. Install: pip install python-docx")
    
    try:
        doc = docx.Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()
    except Exception as e:
        logger.error(f"Error reading DOCX: {e}")
        raise


def extract_text_from_csv(file_path: Path) -> List[str]:
    """Extract text from CSV files."""
    if not PANDAS_AVAILABLE:
        raise ImportError("CSV support not available. Install: pip install pandas")
    
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
        logger.info(f"CSV loaded: {df.shape[0]} rows, {df.shape[1]} columns")
        
        texts = []
        
        # Add header information
        column_info = f"Dataset: {file_path.name}\nColumns: {', '.join(df.columns)}\nTotal rows: {df.shape[0]}\n"
        texts.append(column_info)
        
        # Convert rows to text
        for idx, row in df.iterrows():
            row_text = f"Row {idx + 1}:\n"
            for col in df.columns:
                value = row[col]
                if pd.notna(value):
                    row_text += f"{col}: {value}\n"
            texts.append(row_text.strip())
            
            if idx >= 500:  # Limit for performance
                logger.info("Limited to first 500 rows")
                break
        
        return texts
        
    except Exception as e:
        logger.error(f"Error reading CSV: {e}")
        raise


def extract_text_from_excel(file_path: Path) -> List[str]:
    """Extract text from Excel files."""
    if not PANDAS_AVAILABLE:
        raise ImportError("Excel support not available. Install: pip install pandas openpyxl")
    
    try:
        excel_file = pd.ExcelFile(file_path)
        all_texts = []
        
        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            sheet_info = f"Sheet: {sheet_name}\nColumns: {', '.join(df.columns)}\nRows: {df.shape[0]}\n"
            all_texts.append(sheet_info)
            
            for idx, row in df.iterrows():
                row_text = f"Sheet {sheet_name}, Row {idx + 1}:\n"
                for col in df.columns:
                    value = row[col]
                    if pd.notna(value):
                        row_text += f"{col}: {value}\n"
                all_texts.append(row_text.strip())
                
                if idx >= 200:
                    break
        
        return all_texts
        
    except Exception as e:
        logger.error(f"Error reading Excel: {e}")
        raise


def extract_text_from_file(file_path: Path) -> List[str]:
    """Extract text from various file formats."""
    file_extension = file_path.suffix.lower()
    
    try:
        if file_extension == '.csv':
            return extract_text_from_csv(file_path)
        
        elif file_extension in ['.xlsx', '.xls']:
            return extract_text_from_excel(file_path)
        
        elif file_extension == '.pdf':
            content = extract_text_from_pdf(file_path)
            if len(content) > 2000:
                paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
                return paragraphs if paragraphs else [content]
            return [content]
        
        elif file_extension == '.docx':
            content = extract_text_from_docx(file_path)
            if len(content) > 2000:
                paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
                return paragraphs if paragraphs else [content]
            return [content]
        
        elif file_extension == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if len(content) > 2000:
                    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
                    return paragraphs if paragraphs else [content]
                return [content]
        
        elif file_extension == '.json':
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [json.dumps(data, indent=2)]
        
        else:
            # Fallback for unknown file types
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                return [content]
    
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        raise


def load_documents(input_data: Union[str, List[str]]) -> List[str]:
    """Load documents from various sources."""
    texts = []
    
    if isinstance(input_data, str):
        path = Path(input_data)
        
        if path.is_dir():
            supported_extensions = {'.txt', '.pdf', '.docx', '.csv', '.xlsx', '.xls', '.json'}
            
            for file_path in path.rglob('*'):
                if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                    try:
                        logger.info(f"Processing: {file_path.name}")
                        file_texts = extract_text_from_file(file_path)
                        texts.extend(file_texts)
                    except Exception as e:
                        logger.error(f"Failed to process {file_path}: {e}")
                        continue
        
        elif path.is_file():
            file_texts = extract_text_from_file(path)
            texts.extend(file_texts)
        
        else:
            texts.append(input_data)
    
    elif isinstance(input_data, list):
        for item in input_data:
            texts.extend(load_documents(item))
    
    if not texts:
        raise ValueError("No valid content found")
    
    logger.info(f"Loaded {len(texts)} document chunks")
    return texts


def initialize_database(
    persist_directory: str = "rag_db", 
    collection_name: str = "documents", 
    embedding_model: str = "nomic-embed-text",
    reset: bool = False
):
    """Initialize ChromaDB with persistence."""
    try:
        persist_path = Path(persist_directory).resolve()
        persist_path.mkdir(exist_ok=True)
        
        client = chromadb.PersistentClient(path=str(persist_path))
        
        ollama_url = get_ollama_base_url()
        logger.info(f"Using Ollama at: {ollama_url}")
        
        if not validate_model(embedding_model):
            raise ValueError(f"Embedding model '{embedding_model}' not available")
        
        embedding_function = CustomOllamaEmbeddingFunction(
            model_name=embedding_model,
            url=ollama_url
        )
        
        existing_collections = [col.name for col in client.list_collections()]
        
        if collection_name in existing_collections and not reset:
            logger.info(f"Using existing collection: {collection_name}")
            collection = client.get_collection(
                name=collection_name,
                embedding_function=embedding_function
            )
            logger.info(f"Collection contains {collection.count()} documents")
        else:
            if collection_name in existing_collections:
                client.delete_collection(name=collection_name)
                logger.info(f"Deleted existing collection: {collection_name}")
            
            logger.info(f"Creating new collection: {collection_name}")
            collection = client.create_collection(
                name=collection_name,
                embedding_function=embedding_function
            )
        
        return client, collection
    
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


def store_documents(collection, texts: List[str], source: str = "unknown"):
    """Store documents in the database."""
    content_hash = hashlib.md5("".join(texts).encode()).hexdigest()[:8]
    
    try:
        existing = collection.get(where={"content_hash": content_hash})
        if existing['ids']:
            logger.info("Content already exists, skipping storage")
            return
    except:
        pass
    
    doc_id = int(time.time() * 1000)
    stored_count = 0
    
    for idx, text in enumerate(texts):
        if text.strip():
            try:
                collection.add(
                    documents=[text],
                    ids=[f"{content_hash}_{doc_id}_{idx}"],
                    metadatas=[{
                        "source": source, 
                        "chunk_index": idx,
                        "content_hash": content_hash,
                        "timestamp": int(time.time())
                    }]
                )
                stored_count += 1
            except Exception as e:
                logger.error(f"Error storing chunk {idx}: {e}")
                continue
    
    logger.info(f"Stored {stored_count} document chunks")


def retrieve_context(collection, query: str, top_k: int = 5) -> List[str]:
    """Retrieve relevant context from the database."""
    try:
        results = collection.query(query_texts=[query], n_results=min(top_k, collection.count()))
        return results['documents'][0] if results['documents'] else []
    except Exception as e:
        logger.error(f"Error retrieving context: {e}")
        return []


def query_ollama(
    prompt: str, 
    model: str = "llama3.2", 
    temperature: float = 0.7
) -> str:
    """Query Ollama for text generation."""
    ollama_url = get_ollama_base_url()
    
    try:
        # Test connection
        health_response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        if health_response.status_code != 200:
            raise ConnectionError("Ollama server not responding")
        
        if not validate_model(model):
            raise ValueError(f"Model '{model}' not available")
        
        response = requests.post(
            f"{ollama_url}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "temperature": temperature
            },
            timeout=120
        )
        
        if response.status_code == 200:
            return response.json().get('response', 'No response generated')
        else:
            raise Exception(f"Ollama API error: {response.status_code}")
    
    except requests.exceptions.ConnectionError:
        raise ConnectionError(f"Cannot connect to Ollama at {ollama_url}")
    except requests.exceptions.Timeout:
        raise TimeoutError("Request timed out")
    except Exception as e:
        raise Exception(f"Error querying Ollama: {e}")


def run_rag_pipeline(
    data: Union[str, List[str]], 
    query: str, 
    model: str = "llama3.2",
    embedding_model: str = "nomic-embed-text", 
    temperature: float = 0.7,
    top_k: int = 10,
    persist_directory: str = "rag_db",
    collection_name: str = "documents",
    reset: bool = False
) -> str:
    """
    Main function to ask questions about your data using RAG.
    
    Args:
        data: Path to file/directory or text content
        query: Your question about the data
        model: Ollama model for generation (default: "llama3.2")
        embedding_model: Ollama model for embeddings (default: "nomic-embed-text")
        temperature: Generation temperature (0.0-1.0)
        top_k: Number of relevant chunks to retrieve
        persist_directory: Database directory
        collection_name: Database collection name
        reset: Whether to recreate the database
    
    Returns:
        Generated answer based on your data
    """
    try:
        logger.info("🚀 Starting Christofy RAG Pipeline...")
        
        # Show available models
        available = get_available_models()
        if available:
            logger.info(f"Available models: {', '.join(available[:3])}...")

        # Initialize database
        client, collection = initialize_database(
            persist_directory=persist_directory,
            collection_name=collection_name,
            embedding_model=embedding_model,
            reset=reset
        )

        # Load and store documents if needed
        if collection.count() == 0 or reset:
            logger.info("📁 Processing documents...")
            texts = load_documents(data)
            source_info = str(data) if isinstance(data, (str, Path)) else "direct_input"
            store_documents(collection, texts, source_info)

        # Retrieve relevant context
        logger.info(f"🔍 Finding relevant information for: '{query}'")
        contexts = retrieve_context(collection, query, top_k)

        if not contexts:
            context_text = "No relevant context found."
        else:
            context_text = "\n\n---\n\n".join(contexts)
            logger.info(f"✅ Found {len(contexts)} relevant chunks")

        # Generate response
        prompt = f"""Based on the following context, answer the question thoroughly and specifically.

CONTEXT:
{context_text}

QUESTION: {query}

INSTRUCTIONS:
- Use only the information provided in the context
- Be specific and include relevant details from the data
- If the context doesn't contain enough information, say so clearly

ANSWER:"""

        logger.info(f"🤖 Generating response with {model}...")
        answer = query_ollama(prompt, model=model, temperature=temperature)

        logger.info("✅ Done!")
        return answer

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise


def get_system_info() -> Dict[str, Any]:
    """Get system information for debugging."""
    return {
        "platform": platform.system(),
        "python_version": platform.python_version(),
        "ollama_url": get_ollama_base_url(),
        "available_models": get_available_models(),
        "features": {
            "PDF support": PDF_AVAILABLE,
            "CSV/Excel support": PANDAS_AVAILABLE,
            "DOCX support": DOCX_AVAILABLE
        }
    }


# Convenience aliases
rag = run_rag_pipeline  # Alias for the main function
query_data = run_rag_pipeline  # Another alias