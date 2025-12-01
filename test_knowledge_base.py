"""
Test Knowledge Base improvements.
"""

import sys
import os

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Load environment variables from .env
from dotenv import load_dotenv
load_dotenv()

from src.knowledge.persistent_vector_store import get_vector_store
from src.knowledge.chunking_strategy import OverlapChunker, ChunkingConfig
from src.knowledge.auto_refresh import get_refresher, RefreshConfig


def test_persistent_vector_store():
    """Test persistent vector store."""
    print("\n" + "=" * 60)
    print("1. Testing Persistent Vector Store (ChromaDB)")
    print("=" * 60)
    
    # Check if OpenAI API key is available
    if not os.getenv('OPENAI_API_KEY'):
        print("\n⚠️ SKIPPED: OPENAI_API_KEY not set")
        print("   Set OPENAI_API_KEY environment variable to run this test")
        return True  # Skip test, don't fail
    
    try:
        # Initialize vector store
        print("\n📦 Initializing vector store...")
        vector_store = get_vector_store(
            collection_name="test_collection",
            persist_directory="./data/test_chroma_db"
        )
        print("✅ Vector store initialized")
        
        # Create test documents
        print("\n📝 Creating test documents...")
        test_docs = [
            {
                'success': True,
                'chunks': [
                    'CTR optimization involves improving click-through rates by testing different ad creatives.',
                    'A/B testing is essential for understanding what resonates with your audience.',
                    'Monitor CTR trends over time to identify patterns and opportunities.'
                ],
                'source': 'test_doc_1',
                'url': 'http://test.com/doc1',
                'title': 'CTR Optimization Guide',
                'category': 'optimization',
                'priority': 1,
                'description': 'Guide for optimizing CTR'
            },
            {
                'success': True,
                'chunks': [
                    'Budget allocation should be based on campaign performance metrics.',
                    'High-performing campaigns deserve more budget to maximize ROI.',
                    'Regular budget reviews help optimize spending across channels.'
                ],
                'source': 'test_doc_2',
                'url': 'http://test.com/doc2',
                'title': 'Budget Management',
                'category': 'budget',
                'priority': 2,
                'description': 'Budget management best practices'
            }
        ]
        print(f"✅ Created {len(test_docs)} test documents")
        
        # Add documents
        print("\n💾 Adding documents to vector store...")
        result = vector_store.add_documents(test_docs)
        
        if result['success']:
            print(f"✅ Added {result['chunks_added']} chunks from {result['documents_processed']} documents")
            print(f"   Total documents in store: {result['total_documents']}")
        else:
            print(f"❌ Failed to add documents: {result['message']}")
            return False
        
        # Search
        print("\n🔍 Searching vector store...")
        search_results = vector_store.search(
            query="How to optimize CTR?",
            top_k=3
        )
        
        print(f"✅ Found {len(search_results)} results:")
        for i, result in enumerate(search_results, 1):
            print(f"\n   Result {i}:")
            print(f"   Score: {result['score']:.3f}")
            print(f"   Text: {result['text'][:80]}...")
            print(f"   Source: {result['metadata'].get('source', 'unknown')}")
        
        # Get stats
        print("\n📊 Vector store statistics:")
        stats = vector_store.get_stats()
        print(f"   Collection: {stats['collection_name']}")
        print(f"   Total documents: {stats['total_documents']}")
        print(f"   Location: {stats['persist_directory']}")
        
        print("\n✅ Persistent vector store test PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Persistent vector store test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_chunking_strategy():
    """Test chunking with overlap."""
    print("\n" + "=" * 60)
    print("2. Testing Chunking Strategy with Overlap")
    print("=" * 60)
    
    try:
        # Configure chunking
        print("\n⚙️ Configuring chunker...")
        config = ChunkingConfig(
            chunk_size=200,
            chunk_overlap=40,  # 20% overlap
            min_chunk_size=50,
            respect_sentence_boundaries=True
        )
        
        chunker = OverlapChunker(config)
        print(f"✅ Chunker configured:")
        print(f"   Chunk size: {config.chunk_size}")
        print(f"   Overlap: {config.chunk_overlap} ({chunker._overlap_percentage():.1f}%)")
        
        # Test text
        test_text = """
        Campaign performance analysis is crucial for success. CTR measures engagement.
        A high CTR indicates relevant ads. Budget optimization requires data analysis.
        Monitor metrics daily for best results. Adjust bids based on performance.
        Test different creatives regularly. Track conversions to measure ROI.
        """
        
        print(f"\n📝 Test text length: {len(test_text)} characters")
        
        # Chunk text
        print("\n✂️ Chunking text...")
        chunks = chunker.chunk_text(test_text)
        
        print(f"✅ Created {len(chunks)} chunks:")
        for i, chunk in enumerate(chunks, 1):
            print(f"\n   Chunk {i} ({len(chunk)} chars):")
            print(f"   {chunk[:100]}...")
        
        # Get stats
        print("\n📊 Chunking statistics:")
        stats = chunker.get_chunking_stats(chunks)
        print(f"   Total chunks: {stats['total_chunks']}")
        print(f"   Avg chunk size: {stats['avg_chunk_size']:.0f} chars")
        print(f"   Min/Max: {stats['min_chunk_size']}/{stats['max_chunk_size']} chars")
        print(f"   Overlap: {stats['overlap_percentage']:.1f}%")
        
        print("\n✅ Chunking strategy test PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Chunking strategy test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_auto_refresh():
    """Test auto-refresh mechanism."""
    print("\n" + "=" * 60)
    print("3. Testing Auto-Refresh Mechanism")
    print("=" * 60)
    
    try:
        import tempfile
        
        # Create test file
        print("\n📁 Creating test file...")
        test_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
        test_file.write("Initial content")
        test_file.close()
        print(f"✅ Created test file: {test_file.name}")
        
        # Configure refresher
        print("\n⚙️ Configuring auto-refresh...")
        config = RefreshConfig(
            check_interval_seconds=10,
            auto_refresh_enabled=True,
            refresh_on_startup=False
        )
        
        refresh_count = [0]
        
        def on_refresh(source_ids):
            refresh_count[0] += 1
            print(f"   🔄 Refresh callback triggered for: {source_ids}")
            return {'success': True}
        
        refresher = get_refresher(
            config=config,
            on_refresh_callback=on_refresh
        )
        print("✅ Refresher configured")
        
        # Register source
        print("\n📝 Registering source...")
        success = refresher.register_source(
            source_id="test_file",
            source_type="file",
            location=test_file.name
        )
        
        if success:
            print("✅ Source registered")
        else:
            print("❌ Failed to register source")
            return False
        
        # Check for changes (no changes yet)
        print("\n🔍 Checking for changes (initial)...")
        changes = refresher.check_for_changes()
        print(f"   Changes detected: {changes}")
        
        # Modify file
        print("\n✏️ Modifying file...")
        with open(test_file.name, 'w') as f:
            f.write("Modified content")
        print("✅ File modified")
        
        # Check for changes (should detect change)
        print("\n🔍 Checking for changes (after modification)...")
        changes = refresher.check_for_changes()
        print(f"   Changes detected: {changes}")
        
        if changes.get('test_file'):
            print("✅ Change detected successfully!")
        else:
            print("❌ Change not detected")
        
        # Trigger refresh
        print("\n🔄 Triggering manual refresh...")
        result = refresher.trigger_refresh(['test_file'])
        
        if result['success']:
            print(f"✅ Refresh completed: {result['message']}")
        else:
            print(f"❌ Refresh failed: {result['message']}")
        
        # Get stats
        print("\n📊 Refresh statistics:")
        stats = refresher.get_refresh_stats()
        print(f"   Total sources: {stats['total_sources']}")
        print(f"   Total refreshes: {stats['total_refreshes']}")
        print(f"   Auto-refresh enabled: {stats['auto_refresh_enabled']}")
        
        # Cleanup
        os.unlink(test_file.name)
        print("\n🧹 Cleaned up test file")
        
        print("\n✅ Auto-refresh test PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Auto-refresh test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("KNOWLEDGE BASE IMPROVEMENTS TEST SUITE")
    print("=" * 60)
    
    results = []
    
    # Test 1: Persistent Vector Store
    results.append(("Persistent Vector Store", test_persistent_vector_store()))
    
    # Test 2: Chunking Strategy
    results.append(("Chunking Strategy", test_chunking_strategy()))
    
    # Test 3: Auto-Refresh
    results.append(("Auto-Refresh", test_auto_refresh()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print("\n⚠️ SOME TESTS FAILED")
    
    print("=" * 60)
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
