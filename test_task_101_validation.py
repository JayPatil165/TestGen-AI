#!/usr/bin/env python
"""
Test Task 101: Configuration Validation

Tests configuration validation for all 14 languages.
"""

import sys
from pathlib import Path
import shutil

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_configuration_validation():
    """Test configuration validation functionality."""
    
    print("=" * 70)
    print("TASK 101: CONFIGURATION VALIDATION TEST")
    print("Testing config validation across ALL 14 languages")
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
    print("TEST 1: Valid Language Validation")
    print("-" * 70)
    
    try:
        valid_config = {'language': 'python', 'output_dir': 'test_output'}
        assert WorkflowManager.validate_config(valid_config) == True
        
        print("✅ Valid language passes validation")
        
    except Exception as e:
        print(f"❌ Valid language test failed: {e}")
        return False
    
    print()
    print("-" * 70)
    print("TEST 2: Invalid Language Validation")
    print("-" * 70)
    
    try:
        invalid_config = {'language': 'invalid_lang'}
        
        try:
            WorkflowManager.validate_config(invalid_config)
            print("❌ Should have raised ValueError for invalid language")
            return False
        except ValueError as e:
            assert "Invalid language" in str(e)
            print("✅ Invalid language raises ValueError")
        
    except Exception as e:
        print(f"❌ Invalid language test failed: {e}")
        return False
    
    print()
    print("-" * 70)
    print("TEST 3: Path Auto-Creation")
    print("-" * 70)
    
    try:
        config_with_paths = {
            'output_dir': 'test_auto_dir',
            'report_dir': 'test_auto_reports'
        }
        
        WorkflowManager.validate_config(config_with_paths)
        
        # Check paths were created
        assert Path('test_auto_dir').exists()
        assert Path('test_auto_reports').exists()
        
        print("✅ Paths auto-created during validation")
        
        # Cleanup
        shutil.rmtree('test_auto_dir')
        shutil.rmtree('test_auto_reports')
        
    except Exception as e:
        print(f"❌ Path auto-creation test failed: {e}")
        return False
    
    print()
    print("-" * 70)
    print("TEST 4: All 14 Languages Validation")
    print("-" * 70)
    
    try:
        all_langs = ['python', 'javascript', 'typescript', 'java', 'go', 'csharp',
                     'ruby', 'rust', 'php', 'swift', 'kotlin', 'cpp', 'html', 'css']
        
        for lang in all_langs:
            config = {'language': lang}
            assert WorkflowManager.validate_config(config) == True
        
        print("✅ All 14 languages pass validation")
        print(f"  Validated: {', '.join(all_langs[:5])}...")
        
    except Exception as e:
        print(f"❌ Multi-language validation failed: {e}")
        return False
    
    # Cleanup
    try:
        if Path("test_output").exists():
            shutil.rmtree("test_output")
    except:
        pass
    
    print()
    print("=" * 70)
    print("✅ ALL CONFIGURATION VALIDATION TESTS PASSED!")
    print("=" * 70)
    print()
    print("Verified Functionality:")
    print("  ✅ Valid language validation")
    print("  ✅ Invalid language detection")
    print("  ✅ Path auto-creation")
    print("  ✅ All 14 languages validated")
    print()
    print("✓ Validation system ready!")
    
    return True


if __name__ == "__main__":
    try:
        success = test_configuration_validation()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
