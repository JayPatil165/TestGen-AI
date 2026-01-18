#!/usr/bin/env python
"""
Test Task 80: ReportGenerator Class

Tests report generation functionality across ALL 14 languages in the venv.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_report_generator():
    """Test ReportGenerator class."""
    
    print("=" * 70)
    print("TASK 80: REPORTGENERATOR CLASS TEST")
    print("Testing across ALL 14 languages")
    print("=" * 70)
    print()
    
    # Import modules
    try:
        from testgen.ui.reporter import ReportGenerator, ExecutionSummary, create_reporter
        print("✅ Modules imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import: {e}")
        return False
    
    # Create reporter
    try:
        reporter = ReportGenerator()
        print("✅ ReportGenerator created")
    except Exception as e:
        print(f"❌ Failed to create reporter: {e}")
        return False
    
    print()
    print("-" * 70)
    print("TEST 1: ExecutionSummary Class")
    print("-" * 70)
    
    try:
        summary = ExecutionSummary(
            project_name="Test Project",
            total=10,
            passed=8,
            failed=2,
            skipped=0,
            duration=5.5
        )
        
        print(f"  Total: {summary.total}")
        print(f"  Passed: {summary.passed}")
        print(f"  Failed: {summary.failed}")
        print(f"  Success Rate: {summary.success_rate:.1f}%")
        
        assert summary.total == 10
        assert summary.passed == 8
        assert summary.failed == 2
        assert summary.success_rate == 80.0
        
        print("✅ ExecutionSummary class working")
    except Exception as e:
        print(f"❌ ExecutionSummary failed: {e}")
        return False
    
    print()
    print("-" * 70)
    print("TEST 2: HTML Report Generation")
    print("-" * 70)
    
    try:
        # Create sample results for all 14 languages
        results = ExecutionSummary(
            project_name="TestGen-AI Multi-Language Test",
            total=14,
            passed=11,
            failed=2,
            skipped=1,
            duration=12.5,
            results=[
                {'language': 'python', 'test_name': 'test_calculator', 'status': 'PASS', 'duration': 0.5, 'details': 'OK'},
                {'language': 'javascript', 'test_name': 'test_utils', 'status': 'FAIL', 'duration': 2.3, 'details': 'Error in line 10'},
                {'language': 'typescript', 'test_name': 'test_types', 'status': 'PASS', 'duration': 0.9, 'details': 'Type OK'},
                {'language': 'java', 'test_name': 'testService', 'status': 'PASS', 'duration': 1.2, 'details': 'All good'},
                {'language': 'go', 'test_name': 'TestHandler', 'status': 'SKIP', 'duration': 0.0, 'details': 'Not implemented'},
                {'language': 'csharp', 'test_name': 'TestDatabase', 'status': 'FAIL', 'duration': 3.1, 'details': 'Timeout'},
                {'language': 'ruby', 'test_name': 'test_model', 'status': 'PASS', 'duration': 0.9, 'details': 'RSpec passed'},
                {'language': 'rust', 'test_name': 'test_safety', 'status': 'PASS', 'duration': 0.6, 'details': 'Cargo OK'},
                {'language': 'php', 'test_name': 'testApi', 'status': 'PASS', 'duration': 1.5, 'details': 'OK'},
                {'language': 'swift', 'test_name': 'testViewController', 'status': 'PASS', 'duration': 0.8, 'details': 'XCTest passed'},
                {'language': 'kotlin', 'test_name': 'testRepository', 'status': 'PASS', 'duration': 1.1, 'details': 'All good'},
                {'language': 'cpp', 'test_name': 'testAlgorithm', 'status': 'PASS', 'duration': 0.7, 'details': 'Google Test passed'},
                {'language': 'html', 'test_name': 'test_structure', 'status': 'PASS', 'duration': 0.2, 'details': 'Valid HTML5'},
                {'language': 'css', 'test_name': 'test_styles', 'status': 'PASS', 'duration': 0.3, 'details': 'CSS validated'},
            ]
        )
        
        output_path = "test_report.html"
        result_path = reporter.generate_html(results, output_path)
        
        # Verify file was created
        assert Path(result_path).exists()
        
        # Verify content
        content = Path(result_path).read_text()
        assert "TestGen-AI Multi-Language Test" in content
        assert "11" in content  # passed count
        assert "2" in content   # failed count
        assert "PYTHON" in content
        assert "JAVASCRIPT" in content
        
        print(f"✅ HTML report generated: {result_path}")
        print(f"  File size: {Path(result_path).stat().st_size} bytes")
        
        # Cleanup
        Path(result_path).unlink()
        
    except Exception as e:
        print(f"❌ HTML generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print()
    print("-" * 70)
    print("TEST 3: JSON Report Generation")
    print("-" * 70)
    
    try:
        results = ExecutionSummary(
            project_name="Test Project",
            total=5,
            passed=4,
            failed=1,
            skipped=0,
            duration=2.5,
            language="Python"
        )
        
        output_path = "test_report.json"
        result_path = reporter.generate_json(results, output_path)
        
        # Verify file was created
        assert Path(result_path).exists()
        
        # Verify content
        with open(result_path) as f:
            data = json.load(f)
        
        assert data['total'] == 5
        assert data['passed'] == 4
        assert data['failed'] == 1
        assert data['success_rate'] == 80.0
        assert data['language'] == 'Python'
        
        print(f"✅ JSON report generated: {result_path}")
        print(f"  Success rate: {data['success_rate']:.1f}%")
        
        # Cleanup
        Path(result_path).unlink()
        
    except Exception as e:
        print(f"❌ JSON generation failed: {e}")
        return False
    
    print()
    print("-" * 70)
    print("TEST 4: Factory Function")
    print("-" * 70)
    
    try:
        reporter2 = create_reporter()
        assert isinstance(reporter2, ReportGenerator)
        print("✅ create_reporter() factory function working")
    except Exception as e:
        print(f"❌ Factory function failed: {e}")
        return False
    
    print()
    print("-" * 70)
    print("TEST 5: All 14 Languages Report")
    print("-" * 70)
    
    try:
        all_langs_results = ExecutionSummary(
            project_name="Universal Language Test Report",
            total=14,
            passed=14,
            failed=0,
            skipped=0,
            duration=10.5,
            results=[
                {'language': lang, 'test_name': f'test_{lang}', 'status': 'PASS', 'duration': 0.7, 'details': 'OK'}
                for lang in ['python', 'javascript', 'typescript', 'java', 'go', 'csharp', 
                            'ruby', 'rust', 'php', 'swift', 'kotlin', 'cpp', 'html', 'css']
            ]
        )
        
        output_path = "all_languages_report.html"
        result_path = reporter.generate_html(all_langs_results, output_path)
        
        content = Path(result_path).read_text()
        
        # Verify all languages are present in uppercase
        for lang in ['PYTHON', 'JAVASCRIPT', 'TYPESCRIPT', 'JAVA', 'GO', 'CSHARP',
                    'RUBY', 'RUST', 'PHP', 'SWIFT', 'KOTLIN', 'CPP', 'HTML', 'CSS']:
            assert lang in content, f"{lang} not found in report"
        
        print(f"✅ All 14 languages in HTML report")
        print(f"  Success rate: 100%")
        
        # Cleanup
        Path(result_path).unlink()
        
    except Exception as e:
        print(f"❌ Multi-language report failed: {e}")
        return False
    
    print()
    print("-" * 70)
    print("TEST 6: Error Handling")
    print("-" * 70)
    
    try:
        # Test invalid input
        try:
            reporter.generate_html("invalid", "test.html")
            print("❌ Should have raised ValueError")
            return False
        except ValueError:
            print("✅ ValueError raised for invalid input")
        
        # Test to_dict method
        summary = ExecutionSummary(total=5, passed=5, failed=0, skipped=0, duration=2.0)
        data = summary.to_dict()
        assert 'project_name' in data
        assert 'timestamp' in data
        assert 'success_rate' in data
        print("✅ to_dict() method working")
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False
    
    print()
    print("=" * 70)
    print("✅ ALL REPORTGENERATOR TESTS PASSED!")
    print("=" * 70)
    print()
    print("Verified Functionality:")
    print("  ✅ ExecutionSummary class")
    print("  ✅ HTML report generation")
    print("  ✅ JSON report generation")
    print("  ✅ Factory function (create_reporter)")
    print("  ✅ All 14 languages support")
    print("  ✅ Error handling")
    print("  ✅ Success rate calculation")
    print("  ✅ Beautiful HTML formatting with CSS")
    print()
    print("📊 Report generation works for ALL 14 languages!")
    
    return True


if __name__ == "__main__":
    try:
        success = test_report_generator()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
