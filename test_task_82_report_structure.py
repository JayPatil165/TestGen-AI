#!/usr/bin/env python
"""
Test Task 82: HTML Report Structure Design

Verifies the HTML report structure has all required components
for all 14 languages in the venv.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_report_structure():
    """Test HTML report structure has all required components."""
    
    print("=" * 70)
    print("TASK 82: HTML REPORT STRUCTURE DESIGN TEST")
    print("Verifying structure across ALL 14 languages")
    print("=" * 70)
    print()
    
    # Import modules
    try:
        from testgen.ui.reporter import ReportGenerator, ExecutionSummary
        print("✅ Modules imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import: {e}")
        return False
    
    print()
    print("-" * 70)
    print("TEST 1: Header Components")
    print("-" * 70)
    
    try:
        reporter = ReportGenerator()
        results = ExecutionSummary(
            project_name="Structure Test Project",
            total=10,
            passed=8,
            failed=2,
            skipped=0,
            duration=5.5
        )
        
        html = reporter._generate_html_content(results)
        
        # Verify header components
        assert "Structure Test Project" in html
        assert "Generated:" in html  # Timestamp
        assert "status-badge" in html  # Status badge
        
        print("✅ Header structure verified")
        print("  ✅ Project name present")
        print("  ✅ Timestamp present")
        print("  ✅ Status badge present")
        
    except Exception as e:
        print(f"❌ Header test failed: {e}")
        return False
    
    print()
    print("-" * 70)
    print("TEST 2: Summary Stats Cards")
    print("-" * 70)
    
    try:
        # Verify summary stats
        assert "Total Tests" in html
        assert "Passed" in html
        assert "Failed" in html
        assert "Skipped" in html
        assert "Duration" in html
        assert "Success Rate" in html
        
        # Verify card classes
        assert "summary-card total" in html
        assert "summary-card passed" in html
        assert "summary-card failed" in html
        assert "summary-card skipped" in html
        assert "summary-card duration" in html
        assert "summary-card rate" in html
        
        print("✅ Summary stats structure verified")
        print("  ✅ 6 summary cards present")
        print("  ✅ All metrics displayed")
        
    except Exception as e:
        print(f"❌ Summary stats test failed: {e}")
        return False
    
    print()
    print("-" * 70)
    print("TEST 3: Test Results Table")
    print("-" * 70)
    
    try:
        results_with_data = ExecutionSummary(
            project_name="Table Test",
            total=3,
            passed=2,
            failed=1,
            skipped=0,
            duration=3.0,
            results=[
                {'language': 'python', 'test_name': 'test_1', 'status': 'PASS', 'duration': 1.0, 'details': 'OK'},
                {'language': 'javascript', 'test_name': 'test_2', 'status': 'FAIL', 'duration': 1.5, 'details': 'Error'},
                {'language': 'java', 'test_name': 'test_3', 'status': 'PASS', 'duration': 0.5, 'details': 'Good'},
            ]
        )
        
        html = reporter._generate_html_content(results_with_data)
        
        # Verify table structure
        assert "<table>" in html
        assert "<thead>" in html
        assert "<tbody>" in html
        
        # Verify table headers
        assert "<th>#</th>" in html
        assert "<th>Language</th>" in html
        assert "<th>Test Name</th>" in html
        assert "<th>Status</th>" in html
        assert "<th>Duration</th>" in html
        assert "<th>Details</th>" in html
        
        # Verify table has data rows
        assert "PYTHON" in html
        assert "JAVASCRIPT" in html
        assert "JAVA" in html
        
        print("✅ Table structure verified")
        print("  ✅ Table headers present")
        print("  ✅ Table body with data")
        print("  ✅ 6 columns (# Language, Test, Status, Duration, Details)")
        
    except Exception as e:
        print(f"❌ Table test failed: {e}")
        return False
    
    print()
    print("-" * 70)
    print("TEST 4: Footer with Environment Info")
    print("-" * 70)
    
    try:
        # Verify footer
        assert "footer" in html
        assert "TestGen-AI" in html
        assert "Universal Multi-Language Testing Framework" in html
        assert "Python, JavaScript, TypeScript, Java, Go, C#, Ruby, Rust, PHP, Swift, Kotlin, C++, HTML, CSS" in html
        
        print("✅ Footer structure verified")
        print("  ✅ Generator info present")
        print("  ✅ Framework description")
        print("  ✅ All 14 languages listed")
        
    except Exception as e:
        print(f"❌ Footer test failed: {e}")
        return False
    
    print()
    print("-" * 70)
    print("TEST 5: Embedded CSS Styling")
    print("-" * 70)
    
    try:
        # Verify CSS is embedded
        assert "<style>" in html
        assert "</style>" in html
        
        # Verify key styles
        assert ".container" in html
        assert ".header" in html
        assert ".summary" in html
        assert ".summary-card" in html
        assert "table" in html
        assert ".footer" in html
        
        # Verify gradient backgrounds
        assert "linear-gradient" in html
        
        print("✅ CSS styling verified")
        print("  ✅ Embedded <style> tag")
        print("  ✅ Container, header, summary, table, footer styles")
        print("  ✅ Gradient backgrounds")
        
    except Exception as e:
        print(f"❌ CSS test failed: {e}")
        return False
    
    print()
    print("-" * 70)
    print("TEST 6: Complete HTML Document Structure")
    print("-" * 70)
    
    try:
        # Verify complete HTML document
        assert "<!DOCTYPE html>" in html
        assert "<html lang=\"en\">" in html
        assert "<head>" in html
        assert "<meta charset=\"UTF-8\">" in html
        assert "<title>" in html
        assert "<body>" in html
        assert "</html>" in html
        
        print("✅ HTML document structure verified")
        print("  ✅ DOCTYPE declaration")
        print("  ✅ Complete HTML5 structure")
        print("  ✅ Meta tags present")
        
    except Exception as e:
        print(f"❌ HTML document test failed: {e}")
        return False
    
    print()
    print("-" * 70)
    print("TEST 7: All 14 Languages in Report")
    print("-" * 70)
    
    try:
        all_langs_results = ExecutionSummary(
            project_name="All Languages Test",
            total=14,
            passed=14,
            failed=0,
            skipped=0,
            duration=10.0,
            results=[
                {'language': lang, 'test_name': f'test_{lang}', 'status': 'PASS', 'duration': 0.7, 'details': 'OK'}
                for lang in ['python', 'javascript', 'typescript', 'java', 'go', 'csharp',
                            'ruby', 'rust', 'php', 'swift', 'kotlin', 'cpp', 'html', 'css']
            ]
        )
        
        html = reporter._generate_html_content(all_langs_results)
        
        # Verify all 14 languages
        for lang in ['PYTHON', 'JAVASCRIPT', 'TYPESCRIPT', 'JAVA', 'GO', 'CSHARP',
                    'RUBY', 'RUST', 'PHP', 'SWIFT', 'KOTLIN', 'CPP', 'HTML', 'CSS']:
            assert lang in html, f"{lang} not found in report"
        
        print("✅ All 14 languages in report structure")
        
    except Exception as e:
        print(f"❌ Multi-language test failed: {e}")
        return False
    
    print()
    print("=" * 70)
    print("✅ ALL REPORT STRUCTURE TESTS PASSED!")
    print("=" * 70)
    print()
    print("Verified Structure Components:")
    print("  ✅ Header: Project name, timestamp, status badge")
    print("  ✅ Summary: 6 stat cards (total, passed, failed, skipped, duration, rate)")
    print("  ✅ Body: Detailed test results table (6 columns)")
    print("  ✅ Footer: Generator info + 14 languages listed")
    print("  ✅ CSS: Embedded styling with gradients")
    print("  ✅ HTML5: Complete valid document structure")
    print()
    print("📋 HTML report structure designed for ALL 14 languages!")
    
    return True


if __name__ == "__main__":
    try:
        success = test_report_structure()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
