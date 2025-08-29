"""
Basic ragpackai Usage Example

This example demonstrates the fundamental operations of ragpackai:
- Creating a pack from documents
- Saving and loading packs
- Querying and asking questions
"""

import os
import tempfile
from pathlib import Path
from ragpackai import ragpackai

def create_sample_documents():
    """Create sample documents for demonstration."""
    temp_dir = tempfile.mkdtemp()
    
    # Create sample documents
    doc1_path = Path(temp_dir) / "ai_overview.txt"
    doc1_path.write_text("""
    Artificial Intelligence Overview
    
    Artificial Intelligence (AI) is a branch of computer science that aims to create 
    intelligent machines that can perform tasks that typically require human intelligence.
    These tasks include learning, reasoning, problem-solving, perception, and language understanding.
    
    Key areas of AI include:
    - Machine Learning: Algorithms that improve through experience
    - Natural Language Processing: Understanding and generating human language
    - Computer Vision: Interpreting and understanding visual information
    - Robotics: Creating intelligent physical agents
    
    AI has applications in healthcare, finance, transportation, entertainment, and many other fields.
    """)
    
    doc2_path = Path(temp_dir) / "machine_learning.txt"
    doc2_path.write_text("""
    Machine Learning Fundamentals
    
    Machine Learning (ML) is a subset of artificial intelligence that focuses on the 
    development of algorithms that can learn and make decisions from data without being 
    explicitly programmed for every scenario.
    
    Types of Machine Learning:
    1. Supervised Learning: Learning from labeled training data
    2. Unsupervised Learning: Finding patterns in data without labels
    3. Reinforcement Learning: Learning through interaction with an environment
    
    Common algorithms include:
    - Linear Regression
    - Decision Trees
    - Neural Networks
    - Support Vector Machines
    - Random Forest
    
    ML is used in recommendation systems, image recognition, fraud detection, and more.
    """)
    
    doc3_path = Path(temp_dir) / "installation_guide.txt"
    doc3_path.write_text("""
    ragpackai Installation Guide
    
    To install ragpackai, follow these steps:
    
    1. Basic Installation:
       pip install ragpackai
    
    2. With Optional Providers:
       pip install ragpackai[google]     # For Google Vertex AI
       pip install ragpackai[groq]       # For Groq
       pip install ragpackai[all]        # All providers
    
    3. Set up API Keys:
       export OPENAI_API_KEY="your-openai-key"
       export GOOGLE_CLOUD_PROJECT="your-project"
       export GROQ_API_KEY="your-groq-key"
    
    4. Verify Installation:
       python -c "import ragpackai; print(ragpackai.get_version())"
    
    Requirements:
    - Python 3.9 or higher
    - At least 4GB RAM recommended
    - Internet connection for cloud providers
    """)
    
    return [str(doc1_path), str(doc2_path), str(doc3_path)]

def main():
    """Main example function."""
    print("🚀 ragpackai Basic Usage Example")
    print("=" * 50)
    
    # Step 1: Create sample documents
    print("\n📄 Creating sample documents...")
    document_files = create_sample_documents()
    print(f"Created {len(document_files)} sample documents")
    
    # Step 2: Create a RAG pack
    print("\n📦 Creating RAG pack...")
    try:
        pack = ragpackai.from_files(
            files=document_files,
            embed_model="openai:text-embedding-3-small",  # Default embedding model
            chunk_size=512,
            chunk_overlap=50,
            name="ai_knowledge_base"
        )
        print("✅ RAG pack created successfully!")
        
        # Show pack statistics
        stats = pack.get_stats()
        print(f"   📊 Documents: {stats['document_count']}")
        print(f"   📊 Name: {stats['name']}")
        
    except Exception as e:
        print(f"❌ Error creating pack: {e}")
        print("💡 Make sure you have set OPENAI_API_KEY environment variable")
        return
    
    # Step 3: Save the pack
    print("\n💾 Saving RAG pack...")
    pack_path = "ai_knowledge_base.rag"
    try:
        pack.save(pack_path)
        print(f"✅ Pack saved to: {pack_path}")
        
        # Show file size
        file_size = os.path.getsize(pack_path)
        print(f"   📊 File size: {file_size:,} bytes")
        
    except Exception as e:
        print(f"❌ Error saving pack: {e}")
        return
    
    # Step 4: Load the pack
    print("\n📂 Loading RAG pack...")
    try:
        loaded_pack = ragpackai.load(pack_path)
        print("✅ Pack loaded successfully!")
        
        stats = loaded_pack.get_stats()
        print(f"   📊 Loaded documents: {stats['document_count']}")
        
    except Exception as e:
        print(f"❌ Error loading pack: {e}")
        return
    
    # Step 5: Query the pack (retrieval only)
    print("\n🔍 Querying the pack...")
    try:
        query_results = loaded_pack.query(
            "What is machine learning?", 
            top_k=3
        )
        
        print(f"Found {len(query_results)} relevant chunks:")
        for i, result in enumerate(query_results, 1):
            source = result.get('source', 'unknown')
            score = result.get('score', 0.0)
            chunk = result.get('chunk', '')[:200] + "..."
            
            print(f"\n   [{i}] Source: {Path(source).name}")
            print(f"       Score: {score:.3f}")
            print(f"       Content: {chunk}")
            
    except Exception as e:
        print(f"❌ Error querying pack: {e}")
    
    # Step 6: Ask questions (retrieval + LLM)
    print("\n🤖 Asking questions...")
    questions = [
        "What is artificial intelligence?",
        "How do I install ragpackai?",
        "What are the types of machine learning?"
    ]
    
    for question in questions:
        print(f"\n❓ Question: {question}")
        try:
            answer = loaded_pack.ask(question, top_k=3, temperature=0.1)
            print(f"🤖 Answer: {answer}")
            
        except Exception as e:
            print(f"❌ Error asking question: {e}")
            print("💡 Make sure you have set OPENAI_API_KEY environment variable")
    
    # Step 7: Cleanup
    print("\n🧹 Cleaning up...")
    try:
        # Remove the pack file
        if os.path.exists(pack_path):
            os.remove(pack_path)
            print(f"✅ Removed {pack_path}")
        
        # Remove sample documents
        for doc_path in document_files:
            if os.path.exists(doc_path):
                os.remove(doc_path)
        
        # Remove temp directory
        temp_dir = Path(document_files[0]).parent
        if temp_dir.exists():
            import shutil
            shutil.rmtree(temp_dir)
        
        print("✅ Cleanup completed")
        
    except Exception as e:
        print(f"⚠️  Cleanup warning: {e}")
    
    print("\n🎉 Example completed successfully!")
    print("\n💡 Next steps:")
    print("   - Try different embedding models")
    print("   - Experiment with provider overrides")
    print("   - Use encryption for sensitive data")
    print("   - Explore the CLI interface")

if __name__ == "__main__":
    main()
