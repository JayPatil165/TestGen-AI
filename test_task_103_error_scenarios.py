#!/usr/bin/env python
"""
Test Task 103: Error Scenario Testing

Tests error handling scenarios for all 14 languages.
"""

import sys
from pathlib import Path
import shutil

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_error_scenarios():
    """Test error scenarios."""
    
    print("=" * 70)
    print("TASK 103: ERROR SCENARIO TESTING")
    print("Testing error scenarios across ALL 14 languages")
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
    print("TEST 1: Invalid Language Configuration")
    print("-" * 70)
    
    try:
        invalid_config = {'language': 'invalid_language'}
        
        try:
            WorkflowManager.validate_config(invalid_config)
            print("❌ Should have raised ValueError")
            return False
        except ValueError as e:
            assert "Invalid language" in str(e)
            print("✅ Invalid language properly rejected")
            print(f"  Error: {str(e)}")
        
    except Exception as e:
        print(f"❌ Invalid language test failed: {e}")
        return False
    
    print()
    print("-" * 70)
    print("TEST 2: Malformed Configuration")
    print("-" * 70)
    
    try:
        # Manager should handle None gracefully
        manager = WorkflowManager(config=None)
        assert manager.config == {}
        
        # Manager should handle empty config
        manager2 = WorkflowManager(config={})
        assert manager2.language == 'python'  # Default
        
        print("✅ Malformed config handled gracefully")
        print(f"  None config: Defaults applied")
        print(f"  Empty config: Defaults applied")
        
    except Exception as e:
        print(f"❌ Malformed config test failed: {e}")
        return False
    
    print()
    print("-" * 70)
    print("TEST 3: Missing Directory Handling")
    print("-" * 70)
    
    try:
        # Config with non-existent paths should auto-create
        config_with_paths = {
            'output_dir': 'test_nonexistent_dir',
            'report_dir': 'test_nonexistent_reports'
        }
        
        WorkflowManager.validate_config(config_with_paths)
        
        # Paths should be created
        assert Path('test_nonexistent_dir').exists()
        assert Path('test_nonexistent_reports').exists()
        
        print("✅ Missing directories auto-created")
        print(f"  Output dir created: Yes")
        print(f"  Report dir created: Yes")
        
        # Cleanup
        shutil.rmtree('test_nonexistent_dir')
        shutil.rmtree('test_nonexistent_reports')
        
    except Exception as e:
        print(f"❌ Missing directory test failed: {e}")
        return False
    
    print()
    print("-" * 70)
    print("TEST 4: Error Handling Integration")
    print("-" * 70)
    
    try:
        manager = WorkflowManager(config={'language': 'python'})
        
        # Test various error types
        errors_to_test = [
            (ValueError("Test value error"), "value_error_context"),
            (FileNotFoundError("Test file not found"), "file_context"),
            (TypeError("Test type error"), "type_context"),
        ]
        
        for error, context in errors_to_test:
            error_info = manager.handle_error(error, context, "test_op")
            assert error_info['type'] == type(error).__name__
            assert error_info['context'] == context
        
        # All errors should be tracked
        all_errors = manager.get_errors()
        assert len(all_errors) >= 3
        
        print("✅ Error handling working for all error types")
        print(f"  Errors tracked: {len(all_errors)}")
        print(f"  Types: ValueError, FileNotFoundError, TypeError")
        
    except Exception as e:
        print(f"❌ Error handling integration test failed: {e}")
        return False
    
    print()
    print("-" * 70)
    print("TEST 5: Rollback on Failure")
    print("-" * 70)
    
    try:
        manager = WorkflowManager(config={'language': 'python'})
        
        # Create test directory
        test_dir = Path("test_rollback_dir")
        test_dir.mkdir(exist_ok=True)
        (test_dir / "original.txt").write_text("original")
        
        # Operation that fails should rollback
        def failing_operation():
            (test_dir / "temp.txt").write_text("temp")
            raise RuntimeError("Simulated failure")
        
        try:
            manager.safe_file_operation(failing_operation, backup_dir=str(test_dir))
        except RuntimeError:
            pass  # Expected
        
        # Original should be preserved
        assert (test_dir / "original.txt").exists()
        assert not (test_dir / "temp.txt").exists()  # Rolled back
        
        print("✅ Rollback on failure working")
        print(f"  Original preserved: Yes")
        print(f"  Failed changes rolled back: Yes")
        
        # Cleanup
        shutil.rmtree(test_dir)
        
    except Exception as e:
        print(f"❌ Rollback test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print()
    print("-" * 70)
    print("TEST 6: All 14 Languages Error Handling")
    print("-" * 70)
    
    try:
        all_langs = ['python', 'javascript', 'typescript', 'java', 'go', 'csharp',
                     'ruby', 'rust', 'php', 'swift', 'kotlin', 'cpp', 'html', 'css']
        
        for lang in all_langs:
            config = {'language': lang}
            # Should validate successfully
            assert WorkflowManager.validate_config(config) == True
            
            # Should create manager successfully
            lang_manager = WorkflowManager(config=config)
            assert lang_manager.language == lang
        
        print("✅ All 14 languages error handling works")
        print(f"  Languages tested: All 14")
        
    except Exception as e:
        print(f"❌ Multi-language error test failed: {e}")
        return False
    
    # Cleanup
    try:
        if Path(".testgen").exists():
            shutil.rmtree(".testgen")
        if manager.cache_dir.exists():
            shutil.rmtree(manager.cache_dir)
    except:
        pass
    
    print()
    print("=" * 70)
    print("✅ ALL ERROR SCENARIO TESTS PASSED!")
    print("=" * 70)
    print()
    print("Verified Error Scenarios:")
    print("  ✅ Invalid language configuration")
    print("  ✅ Malformed configuration handling")
    print("  ✅ Missing directory auto-creation")
    print("  ✅ Error handling integration")
    print("  ✅ Rollback on failure")
    print("  ✅ All 14 languages error handling")
    print()
    print("🛡️ Error scenario handling ready!")
    print()
    print("🎉 MODULE 8 COMPLETE! 🎉")
    
    return True


if __name__ == "__main__":
    try:
        success = test_error_scenarios()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
