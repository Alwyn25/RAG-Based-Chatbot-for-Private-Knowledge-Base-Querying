import os
import asyncio
from typing import List, Dict, Any
from datetime import datetime
import hashlib
import json

# Document processing libraries
import PyPDF2
import docx
import pandas as pd
from bs4 import BeautifulSoup
import markdown

from .embeddings import EmbeddingGenerator

class DocumentProcessor:
    def __init__(self):
        self.embedding_generator = EmbeddingGenerator()
        
        # Simple file tracking without MongoDB
        self.processed_docs_file = "processed_documents.json"
        self.docs_indexed = self._load_processed_docs()
        
        # Supported file types
        self.supported_extensions = {'.pdf', '.docx', '.csv', '.md', '.html', '.txt'}

    def _load_processed_docs(self):
        """Load processed documents from JSON file"""
        if os.path.exists(self.processed_docs_file):
            try:
                with open(self.processed_docs_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def _save_processed_docs(self):
        """Save processed documents to JSON file"""
        try:
            with open(self.processed_docs_file, 'w') as f:
                json.dump(self.docs_indexed, f, indent=2)
        except Exception as e:
            print(f"Error saving processed docs: {e}")
    
    def _doc_exists(self, file_hash):
        """Check if document was already processed"""
        return file_hash in self.docs_indexed
    
    def _add_processed_doc(self, file_hash, metadata):
        """Add document to processed list"""
        self.docs_indexed[file_hash] = metadata
        self._save_processed_docs()

    async def process_folder(self, folder_path: str, vector_store) -> None:
        """Process all documents in a folder"""
        if not os.path.exists(folder_path):
            print(f"Folder {folder_path} does not exist")
            return
        
        print(f"Processing documents in {folder_path}...")
        
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            
            if os.path.isfile(file_path):
                file_ext = os.path.splitext(filename)[1].lower()
                
                if file_ext in self.supported_extensions:
                    await self.process_document(file_path, vector_store)
                else:
                    print(f"Skipping unsupported file: {filename}")

    async def process_document(self, file_path: str, vector_store) -> None:
        """Process a single document"""
        try:
            filename = os.path.basename(file_path)
            file_ext = os.path.splitext(filename)[1].lower()
            file_size = os.path.getsize(file_path)
            
            # Generate file hash for duplicate detection
            file_hash = self._generate_file_hash(file_path)
            
            # Check if already processed
            if self._doc_exists(file_hash):
                print(f"Document {filename} already processed, skipping...")
                return
            
            print(f"Processing {filename}...")
            
            # Extract text based on file type
            if file_ext == '.pdf':
                text_content = self._extract_pdf_text(file_path)
            elif file_ext == '.docx':
                text_content = self._extract_docx_text(file_path)
            elif file_ext == '.csv':
                text_content = self._extract_csv_text(file_path)
            elif file_ext == '.md':
                text_content = self._extract_markdown_text(file_path)
            elif file_ext == '.html':
                text_content = self._extract_html_text(file_path)
            elif file_ext == '.txt':
                text_content = self._extract_txt_text(file_path)
            else:
                print(f"Unsupported file type: {file_ext}")
                return
            
            if not text_content:
                print(f"No text extracted from {filename}")
                return
            
            # Chunk the text
            chunks = self._chunk_text(text_content)
            
            # Generate embeddings and store in vector database
            for i, chunk in enumerate(chunks):
                chunk_id = f"{filename}_chunk_{i}"
                
                # Generate embedding
                embedding = await self.embedding_generator.generate_embedding(chunk)
                
                # Store in vector database
                metadata = {
                    "filename": filename,
                    "chunk_id": chunk_id,
                    "chunk_index": i,
                    "file_type": file_ext,
                    "text": chunk
                }
                
                await vector_store.add_document(chunk_id, embedding, metadata)
            
            # Record processed document
            doc_metadata = {
                "filename": filename,
                "file_path": file_path,
                "file_hash": file_hash,
                "file_type": file_ext,
                "file_size": file_size,
                "chunk_count": len(chunks),
                "indexed_at": datetime.utcnow().isoformat(),
                "status": "indexed"
            }
            
            self._add_processed_doc(file_hash, doc_metadata)
            print(f"Successfully processed {filename} with {len(chunks)} chunks")
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            
            # Record error
            error_metadata = {
                "filename": os.path.basename(file_path),
                "file_path": file_path,
                "file_type": os.path.splitext(file_path)[1].lower(),
                "indexed_at": datetime.utcnow().isoformat(),
                "status": "error",
                "error_message": str(e)
            }
            
            self._add_processed_doc(self._generate_file_hash(file_path), error_metadata)

    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            print(f"Error extracting PDF text: {e}")
            return ""

    def _extract_docx_text(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            print(f"Error extracting DOCX text: {e}")
            return ""

    def _extract_csv_text(self, file_path: str) -> str:
        """Extract text from CSV file"""
        try:
            df = pd.read_csv(file_path)
            # Convert DataFrame to text representation
            text = df.to_string(index=False)
            return text
        except Exception as e:
            print(f"Error extracting CSV text: {e}")
            return ""

    def _extract_markdown_text(self, file_path: str) -> str:
        """Extract text from Markdown file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                md_content = file.read()
                # Convert markdown to HTML, then extract text
                html = markdown.markdown(md_content)
                soup = BeautifulSoup(html, 'html.parser')
                return soup.get_text()
        except Exception as e:
            print(f"Error extracting Markdown text: {e}")
            return ""

    def _extract_html_text(self, file_path: str) -> str:
        """Extract text from HTML file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                html_content = file.read()
                soup = BeautifulSoup(html_content, 'html.parser')
                return soup.get_text()
        except Exception as e:
            print(f"Error extracting HTML text: {e}")
            return ""

    def _extract_txt_text(self, file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error extracting TXT text: {e}")
            return ""

    def _chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence ending
                sentence_end = text.rfind('.', start, end)
                if sentence_end > start:
                    end = sentence_end + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
            
            if start >= len(text):
                break
        
        return chunks

    def _generate_file_hash(self, file_path: str) -> str:
        """Generate MD5 hash of file for duplicate detection"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
