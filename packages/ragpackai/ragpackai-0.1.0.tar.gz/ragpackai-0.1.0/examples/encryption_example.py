"""
Encryption Example

This example demonstrates how to use RAGPack's encryption features
to protect sensitive data in .rag files.
"""

import os
import tempfile
import getpass
from pathlib import Path
from ragpack import RAGPack, EncryptionError

def create_sensitive_documents():
    """Create sample sensitive documents."""
    temp_dir = tempfile.mkdtemp()
    
    # Create sensitive document
    sensitive_doc = Path(temp_dir) / "confidential_data.txt"
    sensitive_doc.write_text("""
    CONFIDENTIAL COMPANY DATA
    
    Employee Information:
    - John Doe: Software Engineer, Salary: $95,000
    - Jane Smith: Product Manager, Salary: $110,000
    - Bob Johnson: Data Scientist, Salary: $105,000
    
    Financial Data:
    - Q4 Revenue: $2.5M
    - Operating Costs: $1.8M
    - Net Profit: $700K
    
    Strategic Plans:
    - Launch new AI product line in Q2
    - Expand to European markets
    - Acquire competitor XYZ Corp
    
    API Keys and Secrets:
    - Database Password: super_secret_123
    - API Key: sk-1234567890abcdef
    - Encryption Key: aes256_key_example
    """)
    
    # Create policy document
    policy_doc = Path(temp_dir) / "data_policy.txt"
    policy_doc.write_text("""
    Data Security Policy
    
    1. All sensitive data must be encrypted at rest
    2. Access to confidential information requires authorization
    3. Data must be classified as Public, Internal, or Confidential
    4. Confidential data requires additional security measures
    5. Regular security audits must be conducted
    
    Encryption Requirements:
    - Use AES-256 encryption for data at rest
    - Use strong passwords (minimum 12 characters)
    - Rotate encryption keys quarterly
    - Maintain secure key management practices
    """)
    
    return [str(sensitive_doc), str(policy_doc)]

def demonstrate_basic_encryption():
    """Demonstrate basic encryption and decryption."""
    print("🔒 Basic Encryption Example")
    print("-" * 30)
    
    # Create sensitive documents
    document_files = create_sensitive_documents()
    
    # Create RAG pack
    print("📦 Creating RAG pack with sensitive data...")
    try:
        pack = RAGPack.from_files(
            files=document_files,
            embed_model="openai:text-embedding-3-small",
            name="confidential_pack"
        )
        print("✅ Pack created successfully")
        
    except Exception as e:
        print(f"❌ Error creating pack: {e}")
        return None, None
    
    # Get encryption password
    print("\n🔑 Setting up encryption...")
    encryption_password = "demo_password_123"  # In real use, get from user input
    print(f"Using password: {encryption_password}")
    
    # Save with encryption
    encrypted_pack_path = "confidential_encrypted.rag"
    print(f"\n💾 Saving encrypted pack to {encrypted_pack_path}...")
    try:
        pack.save(encrypted_pack_path, encrypt_key=encryption_password)
        print("✅ Encrypted pack saved successfully")
        
        # Show file size
        file_size = os.path.getsize(encrypted_pack_path)
        print(f"📊 Encrypted file size: {file_size:,} bytes")
        
    except Exception as e:
        print(f"❌ Error saving encrypted pack: {e}")
        return None, None
    
    return encrypted_pack_path, encryption_password

def demonstrate_encrypted_loading():
    """Demonstrate loading encrypted packs."""
    print("\n🔓 Loading Encrypted Pack")
    print("-" * 30)
    
    encrypted_pack_path, correct_password = demonstrate_basic_encryption()
    if not encrypted_pack_path:
        return
    
    # Try loading without password (should fail)
    print("1️⃣ Attempting to load without password...")
    try:
        pack = RAGPack.load(encrypted_pack_path)
        print("❌ This should not succeed!")
        
    except EncryptionError as e:
        print(f"✅ Correctly failed: {e}")
    except Exception as e:
        print(f"✅ Failed as expected: {e}")
    
    # Try loading with wrong password (should fail)
    print("\n2️⃣ Attempting to load with wrong password...")
    try:
        pack = RAGPack.load(encrypted_pack_path, decrypt_key="wrong_password")
        print("❌ This should not succeed!")
        
    except Exception as e:
        print(f"✅ Correctly failed with wrong password: {e}")
    
    # Load with correct password (should succeed)
    print("\n3️⃣ Loading with correct password...")
    try:
        pack = RAGPack.load(encrypted_pack_path, decrypt_key=correct_password)
        print("✅ Successfully loaded encrypted pack!")
        
        # Test functionality
        stats = pack.get_stats()
        print(f"📊 Loaded {stats['document_count']} documents")
        
        # Test querying
        results = pack.query("What is the data security policy?", top_k=2)
        print(f"📊 Query returned {len(results)} results")
        
        # Test asking
        answer = pack.ask("What are the encryption requirements?")
        print(f"🤖 Answer: {answer[:100]}...")
        
        return pack
        
    except Exception as e:
        print(f"❌ Error loading with correct password: {e}")
        return None

def demonstrate_password_security():
    """Demonstrate secure password handling."""
    print("\n🛡️ Password Security Best Practices")
    print("-" * 40)
    
    print("1️⃣ Password strength requirements:")
    passwords = [
        ("weak", "123"),
        ("better", "password123"),
        ("good", "MySecurePass2024!"),
        ("excellent", "Tr0ub4dor&3_Complex_P@ssw0rd!")
    ]
    
    for strength, password in passwords:
        length = len(password)
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        
        score = sum([length >= 12, has_upper, has_lower, has_digit, has_special])
        
        print(f"   {strength.capitalize()}: '{password}' (Score: {score}/5)")
        print(f"      Length: {length}, Upper: {has_upper}, Lower: {has_lower}")
        print(f"      Digits: {has_digit}, Special: {has_special}")
    
    print("\n2️⃣ Secure password input (commented out for demo):")
    print("   # password = getpass.getpass('Enter encryption password: ')")
    print("   # This hides password input from terminal")
    
    print("\n3️⃣ Password storage recommendations:")
    print("   - Never hardcode passwords in source code")
    print("   - Use environment variables for automation")
    print("   - Consider using key management services")
    print("   - Implement password rotation policies")

def demonstrate_encryption_performance():
    """Show encryption performance considerations."""
    print("\n⚡ Encryption Performance")
    print("-" * 30)
    
    # Create packs of different sizes
    document_files = create_sensitive_documents()
    
    print("📊 Comparing encrypted vs unencrypted pack sizes...")
    
    try:
        # Create pack
        pack = RAGPack.from_files(
            files=document_files,
            embed_model="openai:text-embedding-3-small",
            name="performance_test"
        )
        
        # Save unencrypted
        unencrypted_path = "performance_unencrypted.rag"
        pack.save(unencrypted_path)
        unencrypted_size = os.path.getsize(unencrypted_path)
        
        # Save encrypted
        encrypted_path = "performance_encrypted.rag"
        pack.save(encrypted_path, encrypt_key="test_password")
        encrypted_size = os.path.getsize(encrypted_path)
        
        # Compare sizes
        overhead = encrypted_size - unencrypted_size
        overhead_percent = (overhead / unencrypted_size) * 100
        
        print(f"📊 Unencrypted size: {unencrypted_size:,} bytes")
        print(f"📊 Encrypted size: {encrypted_size:,} bytes")
        print(f"📊 Encryption overhead: {overhead:,} bytes ({overhead_percent:.1f}%)")
        
        # Cleanup
        for path in [unencrypted_path, encrypted_path]:
            if os.path.exists(path):
                os.remove(path)
        
    except Exception as e:
        print(f"❌ Performance test error: {e}")

def cleanup_example_files():
    """Clean up example files."""
    print("\n🧹 Cleaning up...")
    
    files_to_remove = [
        "confidential_encrypted.rag",
        "performance_unencrypted.rag",
        "performance_encrypted.rag"
    ]
    
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"✅ Removed {file_path}")

def main():
    """Main example function."""
    print("🔒 RAGPack Encryption Example")
    print("=" * 50)
    
    # Check if cryptography is available
    try:
        from cryptography.fernet import Fernet
        print("✅ Cryptography library available")
    except ImportError:
        print("❌ Cryptography library not available")
        print("💡 Install with: pip install cryptography")
        return
    
    try:
        # Demonstrate basic encryption
        demonstrate_encrypted_loading()
        
        # Show password security best practices
        demonstrate_password_security()
        
        # Show performance considerations
        demonstrate_encryption_performance()
        
    except KeyboardInterrupt:
        print("\n⏹️ Example interrupted by user")
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    
    finally:
        # Cleanup
        cleanup_example_files()
    
    print("\n🎉 Encryption example completed!")
    print("\n💡 Key security takeaways:")
    print("   - Always encrypt sensitive data")
    print("   - Use strong, unique passwords")
    print("   - Never hardcode passwords in source code")
    print("   - Consider encryption overhead in performance planning")
    print("   - Implement proper key management practices")

if __name__ == "__main__":
    main()
