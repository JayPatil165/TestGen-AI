#!/usr/bin/env python
"""
Test Task 84: Jinja2 Template Rendering

Tests Jinja2 template rendering across ALL 14 languages in the venv.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_jinja2_rendering():
    """Test Jinja2 template rendering functionality."""
    
    print("=" * 70)
    print("TASK 84: JINJA2 TEMPLATE RENDERING TEST")
    print("Testing template rendering across ALL 14 languages")
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
    print("TEST 1: Load Template from File")
    print("-" * 70)
    
    try:
        reporter = ReportGenerator()
        
        # Check template exists
        template_path = Path("templates/report.html")
        assert template_path.exists(), "Template file not found"
        
        print(f"✅ Template file exists: {template_path}")
        print(f"  Size: {template_path.stat().st_size} bytes")
        
    except Exception as e:
        print(f"❌ Template loading failed: {e}")
        return False
    
    print()
    print("-" * 70)
    print("TEST 2: Prepare Template Context")
    print("-" * 70)
    
    try:
        results = ExecutionSummary(
            project_name="Context Test",
            total=10,
            passed=8,
            failed=2,
            skipped=0,
            duration=5.5,
            language="Python"
        )
        
        context = reporter._prepare_template_context(results)
        
        # Verify context keys
        assert 'project_name' in context
        assert 'language' in context
        assert 'timestamp' in context
        assert 'status_color' in context
        assert 'status_text' in context
        assert 'total' in context
        assert 'passed' in context
        assert 'failed' in context
        assert 'skipped' in context
        assert 'duration' in context
        assert 'success_rate' in context
        assert 'results' in context
        
        # Verify values
        assert context['project_name'] == "Context Test"
        assert context['language'] == "Python"
        assert context['total'] == 10
        assert context['status_text'] == "FAILED"  # Because failed > 0
        assert context['status_color'] == "#dc3545"  # Red
        
        print("✅ Template context prepared correctly")
        print(f"  ✅ All 12 context keys present")
        print(f"  ✅ Status: {context['status_text']} ({context['status_color']})")
        print(f"  ✅ Success rate: {context['success_rate']:.1f}%")
        
    except Exception as e:
        print(f"❌ Context preparation failed: {e}")
        return False
    
    print()
    print("-" * 70)
    print("TEST 3: Render Template to HTML String")
    print("-" * 70)
    
    try:
        html = reporter.render_template(results)
        
        # Verify HTML was generated
        assert len(html) > 0
        assert "<!DOCTYPE html>" in html
        assert "Context Test" in html
        assert "PYTHON" in html
        assert "FAILED" in html
        
        print("✅ Template rendered to HTML string")
        print(f"  HTML size: {len(html)} bytes")
        print(f"  Contains DOCTYPE: Yes")
        print(f"  Contains project name: Yes")
        
    except Exception as e:
        print(f"❌ Template rendering failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print()
    print("-" * 70)
    print("TEST 4: All 14 Languages Rendering")
    print("-" * 70)
    
    try:
        all_languages = [
            'python', 'javascript', 'typescript', 'java', 'go', 'csharp',
            'ruby', 'rust', 'php', 'swift', 'kotlin', 'cpp', 'html', 'css'
        ]
        
        results_all_langs = ExecutionSummary(
            project_name="All Languages Test",
            total=14,
            passed=14,
            failed=0,
            skipped=0,
            duration=12.0,
            results=[
                {
                    'language': lang,
                    'test_name': f'test_{lang}',
                    'status': 'PASS',
                    'duration': 0.8,
                    'details': f'Test passed for {lang}'
                }
                for lang in all_languages
            ]
        )
        
        html = reporter.render_template(results_all_langs)
        
        # Verify all languages present
        for lang in all_languages:
            assert lang.upper() in html, f"{lang.upper()} not found in rendered HTML"
        
        print("✅ All 14 languages rendered successfully")
        for lang in all_languages[:5]:
            print(f"  ✅ {lang.upper()} found")
        print(f"  ✅ ... and 9 more")
        
    except Exception as e:
        print(f"❌ Multi-language rendering failed: {e}")
        return False
    
    print()
    print("-" * 70)
    print("TEST 5: Generate HTML from Template (with File Save)")
    print("-" * 70)
    
    try:
        output_path = "test_task_84_output.html"
        result_path = reporter.generate_html_from_template(
            results_all_langs,
            output_path
        )
        
        # Verify file was created
        assert Path(result_path).exists()
        
        # Verify content
        content = Path(result_path).read_text()
        assert "All Languages Test" in content
        assert "PYTHON" in content
        
        file_size = Path(result_path).stat().st_size
        print(f"✅ HTML generated and saved to file")
        print(f"  Path: {result_path}")
        print(f"  Size: {file_size} bytes")
        
        # Cleanup
        Path(result_path).unlink()
        
    except Exception as e:
        print(f"❌ File generation failed: {e}")
        return False
    
    print()
    print("-" * 70)
    print("TEST 6: Different Status Colors")
    print("-" * 70)
    
    try:
        # Test PASSED status (green)
        passed_results = ExecutionSummary(total=5, passed=5, failed=0, skipped=0, duration=2.0)
        context = reporter._prepare_template_context(passed_results)
        assert context['status_color'] == "#28a745"  # Green
        assert context['status_text'] == "PASSED"
        print("  ✅ PASSED status: Green (#28a745)")
        
        # Test FAILED status (red)
        failed_results = ExecutionSummary(total=5, passed=3, failed=2, skipped=0, duration=2.0)
        context = reporter._prepare_template_context(failed_results)
        assert context['status_color'] == "#dc3545"  # Red
        assert context['status_text'] == "FAILED"
        print("  ✅ FAILED status: Red (#dc3545)")
        
        # Test PARTIAL status (yellow)
        partial_results = ExecutionSummary(total=5, passed=5, failed=0, skipped=0, duration=2.0)
        partial_results.skipped = 2
        partial_results.total = 7
        context = reporter._prepare_template_context(partial_results)
        assert context['status_color'] == "#ffc107"  # Yellow
        assert context['status_text'] == "PARTIAL"
        print("  ✅ PARTIAL status: Yellow (#ffc107)")
        
        print("✅ All status colors working correctly")
        
    except Exception as e:
        print(f"❌ Status colors test failed: {e}")
        return False
    
    print()
    print("-" * 70)
    print("TEST 7: Error Handling")
    print("-" * 70)
    
    try:
        # Test invalid results
        try:
            reporter.render_template("invalid")
            print("❌ Should have raised ValueError")
            return False
        except ValueError:
            print("  ✅ ValueError raised for invalid results")
        
        # Test missing template
        try:
            reporter.render_template(results, "nonexistent.html")
            print("❌ Should have raised FileNotFoundError")
            return False
        except FileNotFoundError:
            print("  ✅ FileNotFoundError raised for missing template")
        
        print("✅ Error handling working correctly")
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False
    
    print()
    print("=" * 70)
    print("✅ ALL JINJA2 RENDERING TESTS PASSED!")
    print("=" * 70)
    print()
    print("Verified Functionality:")
    print("  ✅ Load template from file (templates/report.html)")
    print("  ✅ Prepare template context (12 keys)")
    print("  ✅ Render template to HTML string")
    print("  ✅ Pass test results as context")
    print("  ✅ All 14 languages rendered")
    print("  ✅ Generate HTML and save to file")
    print("  ✅ Different status colors (PASS/FAIL/PARTIAL)")
    print("  ✅ Error handling (invalid inputs)")
    print()
    print("🎨 Jinja2 rendering works perfectly for ALL 14 languages!")
    
    return True


if __name__ == "__main__":
    try:
        success = test_jinja2_rendering()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
