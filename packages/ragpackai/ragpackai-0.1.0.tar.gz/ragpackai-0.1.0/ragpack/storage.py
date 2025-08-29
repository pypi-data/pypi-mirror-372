"""
Storage module for RAGPack.

Handles saving and loading .rag files with optional AES-GCM encryption.
A .rag file is a structured zip archive containing documents, vectorstore,
metadata, and configuration.
"""

import json
import os
import shutil
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import base64

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    ENCRYPTION_AVAILABLE = True
except ImportError:
    ENCRYPTION_AVAILABLE = False


class StorageError(Exception):
    """Raised when storage operations fail."""
    pass


class EncryptionError(StorageError):
    """Raised when encryption/decryption operations fail."""
    pass


def _derive_key_from_password(password: str, salt: bytes) -> bytes:
    """Derive encryption key from password using PBKDF2."""
    if not ENCRYPTION_AVAILABLE:
        raise EncryptionError(
            "Encryption not available. Install cryptography: pip install cryptography"
        )
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


def _encrypt_data(data: bytes, password: str) -> bytes:
    """Encrypt data using AES-GCM with password-derived key."""
    salt = os.urandom(16)
    key = _derive_key_from_password(password, salt)
    fernet = Fernet(key)
    encrypted_data = fernet.encrypt(data)
    return salt + encrypted_data


def _decrypt_data(encrypted_data: bytes, password: str) -> bytes:
    """Decrypt data using AES-GCM with password-derived key."""
    salt = encrypted_data[:16]
    encrypted_content = encrypted_data[16:]
    key = _derive_key_from_password(password, salt)
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_content)


def save_rag_pack(
    pack_path: str,
    metadata: Dict[str, Any],
    config: Dict[str, Any],
    documents: List[Dict[str, Any]],
    vectorstore_path: str,
    encrypt_key: Optional[str] = None
) -> None:
    """
    Save a RAG pack to a .rag file.
    
    Args:
        pack_path: Path to save the .rag file
        metadata: Pack metadata dictionary
        config: Configuration dictionary
        documents: List of document dictionaries with content and metadata
        vectorstore_path: Path to the vectorstore directory
        encrypt_key: Optional encryption password
        
    Raises:
        StorageError: If saving fails
        EncryptionError: If encryption fails
    """
    pack_path = Path(pack_path)
    
    # Ensure .rag extension
    if pack_path.suffix != '.rag':
        pack_path = pack_path.with_suffix('.rag')
    
    # Create parent directory if it doesn't exist
    pack_path.parent.mkdir(parents=True, exist_ok=True)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        try:
            # Save metadata
            metadata_path = temp_path / "metadata.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            # Save config
            config_path = temp_path / "config.json"
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            # Save documents
            documents_dir = temp_path / "documents"
            documents_dir.mkdir()
            
            for i, doc in enumerate(documents):
                doc_filename = doc.get('filename', f'document_{i}.txt')
                doc_path = documents_dir / doc_filename
                
                content = doc.get('content', '')
                if isinstance(content, bytes):
                    with open(doc_path, 'wb') as f:
                        f.write(content)
                else:
                    with open(doc_path, 'w', encoding='utf-8') as f:
                        f.write(str(content))
            
            # Copy vectorstore
            if os.path.exists(vectorstore_path):
                vectorstore_dest = temp_path / "vectorstore"
                shutil.copytree(vectorstore_path, vectorstore_dest)
            
            # Create zip archive
            with zipfile.ZipFile(pack_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(temp_path):
                    for file in files:
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(temp_path)
                        
                        if encrypt_key:
                            # Read and encrypt file content
                            with open(file_path, 'rb') as f:
                                file_data = f.read()
                            
                            encrypted_data = _encrypt_data(file_data, encrypt_key)
                            
                            # Write encrypted data to zip
                            zipf.writestr(str(arcname) + '.enc', encrypted_data)
                        else:
                            zipf.write(file_path, arcname)
                
                # Add encryption marker if encrypted
                if encrypt_key:
                    zipf.writestr('.encrypted', b'1')
        
        except Exception as e:
            raise StorageError(f"Failed to save RAG pack: {e}") from e


def load_rag_pack(
    pack_path: str,
    extract_to: Optional[str] = None,
    decrypt_key: Optional[str] = None
) -> tuple[Dict[str, Any], Dict[str, Any], List[Dict[str, Any]], str]:
    """
    Load a RAG pack from a .rag file.
    
    Args:
        pack_path: Path to the .rag file
        extract_to: Directory to extract to (optional, uses temp dir if None)
        decrypt_key: Decryption password if pack is encrypted
        
    Returns:
        Tuple of (metadata, config, documents, vectorstore_path)
        
    Raises:
        StorageError: If loading fails
        EncryptionError: If decryption fails
    """
    pack_path = Path(pack_path)
    
    if not pack_path.exists():
        raise StorageError(f"RAG pack not found: {pack_path}")
    
    if not pack_path.suffix == '.rag':
        raise StorageError(f"Invalid file extension. Expected .rag, got {pack_path.suffix}")
    
    # Determine extraction directory
    if extract_to:
        extract_dir = Path(extract_to)
        extract_dir.mkdir(parents=True, exist_ok=True)
        cleanup_extract_dir = False
    else:
        extract_dir = Path(tempfile.mkdtemp())
        cleanup_extract_dir = True
    
    try:
        with zipfile.ZipFile(pack_path, 'r') as zipf:
            # Check if encrypted
            is_encrypted = '.encrypted' in zipf.namelist()
            
            if is_encrypted and not decrypt_key:
                raise EncryptionError("RAG pack is encrypted but no decryption key provided")
            
            if is_encrypted:
                # Extract and decrypt files
                for file_info in zipf.filelist:
                    if file_info.filename == '.encrypted':
                        continue
                    
                    if file_info.filename.endswith('.enc'):
                        # Decrypt file
                        encrypted_data = zipf.read(file_info.filename)
                        decrypted_data = _decrypt_data(encrypted_data, decrypt_key)
                        
                        # Write decrypted file
                        original_name = file_info.filename[:-4]  # Remove .enc
                        output_path = extract_dir / original_name
                        output_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        with open(output_path, 'wb') as f:
                            f.write(decrypted_data)
            else:
                # Extract normally
                zipf.extractall(extract_dir)
        
        # Load metadata
        metadata_path = extract_dir / "metadata.json"
        if not metadata_path.exists():
            raise StorageError("metadata.json not found in RAG pack")
        
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        # Load config
        config_path = extract_dir / "config.json"
        if not config_path.exists():
            raise StorageError("config.json not found in RAG pack")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Load documents
        documents = []
        documents_dir = extract_dir / "documents"
        if documents_dir.exists():
            for doc_file in documents_dir.iterdir():
                if doc_file.is_file():
                    try:
                        # Try to read as text first
                        with open(doc_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                    except UnicodeDecodeError:
                        # Read as binary if text fails
                        with open(doc_file, 'rb') as f:
                            content = f.read()
                    
                    documents.append({
                        'filename': doc_file.name,
                        'content': content,
                        'path': str(doc_file)
                    })
        
        # Get vectorstore path
        vectorstore_path = str(extract_dir / "vectorstore")
        
        return metadata, config, documents, vectorstore_path
    
    except Exception as e:
        if cleanup_extract_dir and extract_dir.exists():
            shutil.rmtree(extract_dir)
        
        if isinstance(e, (StorageError, EncryptionError)):
            raise
        else:
            raise StorageError(f"Failed to load RAG pack: {e}") from e


def validate_rag_pack(pack_path: str) -> Dict[str, Any]:
    """
    Validate a .rag file and return basic information.
    
    Args:
        pack_path: Path to the .rag file
        
    Returns:
        Dictionary with pack information
        
    Raises:
        StorageError: If validation fails
    """
    pack_path = Path(pack_path)
    
    if not pack_path.exists():
        raise StorageError(f"RAG pack not found: {pack_path}")
    
    if not pack_path.suffix == '.rag':
        raise StorageError(f"Invalid file extension. Expected .rag, got {pack_path.suffix}")
    
    try:
        with zipfile.ZipFile(pack_path, 'r') as zipf:
            files = zipf.namelist()
            
            # Check required files
            required_files = ['metadata.json', 'config.json']
            is_encrypted = '.encrypted' in files
            
            if is_encrypted:
                required_files = [f + '.enc' for f in required_files]
            
            missing_files = [f for f in required_files if f not in files]
            if missing_files:
                raise StorageError(f"Missing required files: {missing_files}")
            
            # Get basic info
            info = {
                'path': str(pack_path),
                'size_bytes': pack_path.stat().st_size,
                'encrypted': is_encrypted,
                'files': len(files),
                'created': datetime.fromtimestamp(pack_path.stat().st_ctime).isoformat()
            }
            
            return info
    
    except zipfile.BadZipFile as e:
        raise StorageError(f"Invalid zip file: {e}") from e
    except Exception as e:
        raise StorageError(f"Failed to validate RAG pack: {e}") from e
