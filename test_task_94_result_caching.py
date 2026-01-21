#!/usr/bin/env python
"""
Test Task 94: Result Caching Implementation

Tests result caching functionality across ALL 14 languages.
"""

import sys
from pathlib import Path
import time
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_result_caching():
    """Test result caching functionality."""
    
    print("=" * 70)
    print("TASK 94: RESULT CACHING TEST")
    print("Testing cache functionality across ALL 14 languages")
    print("=" * 70)
    print()
    
    # Import modules
    try:
        from testgen.manager import WorkflowManager
        print("✅ Modules imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import: {e}")
        return False
    
    print()
    print("-" * 70)
    print("TEST 1: Cache Directory Initialization")
    print("-" * 70)
    
    try:
        manager = WorkflowManager(config={
            'language': 'python',
            'cache_dir': 'test_cache'
        })
        
        assert manager.cache_dir == Path('test_cache')
        assert manager.cache_dir.exists()
        
        print("✅ Cache directory initialized")
        print(f"  Cache dir: {manager.cache_dir}")
        print(f"  Directory exists: {manager.cache_dir.exists()}")
        
    except Exception as e:
        print(f"❌ Cache directory init failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print()
    print("-" * 70)
    print("TEST 2: Cache Scan Results")
    print("-" * 70)
    
    try:
        test_files = ['file1.py', 'file2.py', 'file3.py']
        manager.cache_scan_results(test_files, 'python')
        
        # Verify cache file was created
        cache_file = manager.cache_dir / "scan_python.json"
        assert cache_file.exists()
        
        # Load and verify content
        cache_data = json.loads(cache_file.read_text())
        assert cache_data['language'] == 'python'
        assert cache_data['files'] == test_files
        assert 'timestamp' in cache_data
        
        print("✅ Scan results cached")
        print(f"  Files cached: {len(test_files)}")
        print(f"  Cache file: {cache_file.name}")
        
    except Exception as e:
        print(f"❌ Cache scan test failed: {e}")
        return False
    
    print()
    print("-" * 70)
    print("TEST 3: Load Scan Cache (Valid)")
    print("-" * 70)
    
    try:
        cached_files = manager.load_scan_cache('python', max_age_seconds=3600)
        
        assert cached_files is not None
        assert cached_files == test_files
        
        print("✅ Scan cache loaded successfully")
        print(f"  Loaded {len(cached_files)} files")
        print(f"  Cache valid: Yes")
        
    except Exception as e:
        print(f"❌ Load scan cache failed: {e}")
        return False
    
    print()
    print("-" * 70)
    print("TEST 4: Load Scan Cache (Expired)")
    print("-" * 70)
    
    try:
        # Try to load with 0 second max age (should be expired)
        expired_cache = manager.load_scan_cache('python', max_age_seconds=0)
        
        assert expired_cache is None
        
        print("✅ Cache expiration working")
        print(f"  Expired cache returned: None")
        
    except Exception as e:
        print(f"❌ Cache expiration test failed: {e}")
        return False
    
    print()
    print("-" * 70)
    print("TEST 5: Cache Test Results")
    print("-" * 70)
    
    try:
        test_results = {
            'total': 10,
            'passed': 8,
            'failed': 2,
            'skipped': 0,
            'duration': 5.5
        }
        
        manager.cache_test_results(test_results, 'python')
        
        # Verify cache file
        cache_file = manager.cache_dir / "test_results_python.json"
        assert cache_file.exists()
        
        # Load and verify
        cache_data = json.loads(cache_file.read_text())
        assert cache_data['language'] == 'python'
        assert cache_data['results'] == test_results
        
        print("✅ Test results cached")
        print(f"  Results: {test_results['total']} tests")
        print(f"  Cache file: {cache_file.name}")
        
    except Exception as e:
        print(f"❌ Cache test results failed: {e}")
        return False
    
    print()
    print("-" * 70)
    print("TEST 6: Load Test Cache")
    print("-" * 70)
    
    try:
        cached_results = manager.load_test_cache('python', max_age_seconds=1800)
        
        assert cached_results is not None
        assert cached_results == test_results
        
        print("✅ Test cache loaded successfully")
        print(f"  Total tests: {cached_results['total']}")
        print(f"  Passed: {cached_results['passed']}")
        
    except Exception as e:
        print(f"❌ Load test cache failed: {e}")
        return False
    
    print()
    print("-" * 70)
    print("TEST 7: Invalidate Specific Cache")
    print("-" * 70)
    
    try:
        # Invalidate scan cache for python
        manager.invalidate_cache('scan', 'python')
        
        # Should not exist after invalidation
        cache_file = manager.cache_dir / "scan_python.json"
        assert not cache_file.exists()
        
        # Try to load - should return None
        result = manager.load_scan_cache('python')
        assert result is None
        
        print("✅ Cache invalidation working")
        print(f"  Invalidated: scan_python.json")
        print(f"  File removed: Yes")
        
    except Exception as e:
        print(f"❌ Cache invalidation failed: {e}")
        return False
    
    print()
    print("-" * 70)
    print("TEST 8: Clear All Caches")
    print("-" * 70)
    
    try:
        # Add some more caches
        manager.cache_scan_results(['a.js'], 'javascript')
        manager.cache_test_results({'total': 5}, 'javascript')
        
        # Clear all
        manager.clear_all_caches()
        
        # Verify all cleared
        scan_files = list(manager.cache_dir.glob("scan_*.json"))
        test_files = list(manager.cache_dir.glob("test_results_*.json"))
        
        assert len(scan_files) == 0
        assert len(test_files) == 0
        
        print("✅ All caches cleared")
        print(f"  Scan caches: {len(scan_files)}")
        print(f"  Test caches: {len(test_files)}")
        
    except Exception as e:
        print(f"❌ Clear all caches failed: {e}")
        return False
    
    print()
    print("-" * 70)
    print("TEST 9: All 14 Languages Caching")
    print("-" * 70)
    
    try:
        all_langs = ['python', 'javascript', 'typescript', 'java', 'go', 'csharp',
                     'ruby', 'rust', 'php', 'swift', 'kotlin', 'cpp', 'html', 'css']
        
        # Cache for each language
        for lang in all_langs:
            manager.cache_scan_results([f'file.{lang}'], lang)
        
        # Verify all caches exist
        for lang in all_langs:
            cache_file = manager.cache_dir / f"scan_{lang}.json"
            assert cache_file.exists()
        
        print("✅ All 14 languages caching works")
        print(f"  Languages cached: {len(all_langs)}")
        print(f"  Cache files created: {len(all_langs)}")
        
        # Cleanup
        manager.clear_all_caches()
        
    except Exception as e:
        print(f"❌ Multi-language caching failed: {e}")
        return False
    
    # Cleanup test cache directory
    try:
        import shutil
        if manager.cache_dir.exists():
            shutil.rmtree(manager.cache_dir)
    except:
        pass
    
    print()
    print("=" * 70)
    print("✅ ALL RESULT CACHING TESTS PASSED!")
    print("=" * 70)
    print()
    print("Verified Functionality:")
    print("  ✅ Cache directory initialization")
    print("  ✅ Cache scan results to .testgen-cache/")
    print("  ✅ Cache test execution results")
    print("  ✅ Load cached results")
    print("  ✅ Cache expiration (age-based)")
    print("  ✅ Invalidate specific caches")
    print("  ✅ Clear all caches")
    print("  ✅ All 14 languages supported")
    print()
    print("💾 Result caching system ready!")
    
    return True


if __name__ == "__main__":
    try:
        success = test_result_caching()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
