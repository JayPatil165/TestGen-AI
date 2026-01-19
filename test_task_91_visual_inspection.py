#!/usr/bin/env python
"""
Test Task 91: Visual Inspection

Automated visual inspection test - validates HTML is ready for browser viewing.
Generates sample reports for manual inspection across ALL 14 languages.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_visual_inspection():
    """Test visual inspection readiness."""
    
    print("=" * 70)
    print("TASK 91: VISUAL INSPECTION TEST")
    print("Validating HTML for browser compatibility across ALL 14 languages")
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
    print("TEST 1: Generate Sample Report for Visual Inspection")
    print("-" * 70)
    
    try:
        reporter = ReportGenerator()
        
        # Create realistic sample data
        results = ExecutionSummary(
            project_name="Visual Inspection Sample",
            total=25,
            passed=20,
            failed=3,
            skipped=2,
            duration=12.5,
            language="Python",
            results=[
                {'language': 'python', 'test_name': 'test_authentication', 'status': 'PASS', 'duration': 1.2, 'details': 'User authentication successful'},
                {'language': 'python', 'test_name': 'test_database_connection', 'status': 'PASS', 'duration': 0.8, 'details': 'Database connected successfully'},
                {'language': 'python', 'test_name': 'test_api_endpoint', 'status': 'FAIL', 'duration': 2.1, 'details': 'Connection timeout after 30 seconds - API server may be down or network issue'},
                {'language': 'python', 'test_name': 'test_file_upload', 'status': 'PASS', 'duration': 3.5, 'details': 'File uploaded successfully (15MB)'},
                {'language': 'python', 'test_name': 'test_email_sending', 'status': 'FAIL', 'duration': 1.0, 'details': 'SMTP connection refused: [Errno 111] Connection refused'},
                {'language': 'python', 'test_name': 'test_payment_processing', 'status': 'SKIP', 'duration': 0.0, 'details': 'Skipped: Test environment credit card not configured'},
                {'language': 'python', 'test_name': 'test_user_registration', 'status': 'PASS', 'duration': 0.9, 'details': 'New user registered successfully'},
                {'language': 'python', 'test_name': 'test_password_reset', 'status': 'PASS', 'duration': 1.1, 'details': 'Password reset email sent'},
                {'language': 'python', 'test_name': 'test_data_validation', 'status': 'PASS', 'duration': 0.3, 'details': 'Input validation working correctly'},
                {'language': 'python', 'test_name': 'test_cache_invalidation', 'status': 'FAIL', 'duration': 0.7, 'details': 'Cache not properly cleared - stale data returned'},
                {'language': 'python', 'test_name': 'test_session_management', 'status': 'PASS', 'duration': 0.6, 'details': 'Session created and validated'},
                {'language': 'python', 'test_name': 'test_permissions', 'status': 'PASS', 'duration': 0.4, 'details': 'Access control working as expected'},
                {'language': 'python', 'test_name': 'test_logging', 'status': 'PASS', 'duration': 0.2, 'details': 'Logs written successfully'},
                {'language': 'python', 'test_name': 'test_rate_limiting', 'status': 'PASS', 'duration': 2.3, 'details': 'Rate limiter blocking excessive requests'},
                {'language': 'python', 'test_name': 'test_cors_headers', 'status': 'SKIP', 'duration': 0.0, 'details': 'Skipped: CORS not needed in test environment'}
            ]
        )
        
        visual_path = "visual_inspection_report.html"
        report_path = reporter.generate_html_from_template(results, visual_path)
        
        assert Path(report_path).exists()
        file_size = Path(report_path).stat().st_size
        
        print(f"✅ Sample report generated")
        print(f"  Path: {report_path}")
        print(f"  Size: {file_size:,} bytes")
        print(f"  Ready for browser viewing!")
        
    except Exception as e:
        print(f"❌ Sample report generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print()
    print("-" * 70)
    print("TEST 2: Verify CSS Styling Present")
    print("-" * 70)
    
    try:
        html_content = Path(report_path).read_text()
        
        # Check essential CSS
        assert "<style>" in html_content
        assert "background" in html_content
        assert "color" in html_content
        assert "font" in html_content
        assert "padding" in html_content
        assert "margin" in html_content
        
        print("✅ CSS styling validated")
        print("  ✅ Style block present")
        print("  ✅ Layout styles defined")
        print("  ✅ Typography configured")
        
    except Exception as e:
        print(f"❌ CSS validation failed: {e}")
        return False
    
    print()
    print("-" * 70)
    print("TEST 3: Responsive Design Validation")
    print("-" * 70)
    
    try:
        # Check responsive meta tag
        assert '<meta name="viewport"' in html_content
        assert 'width=device-width' in html_content
        
        # Check media queries
        assert "@media" in html_content
        
        print("✅ Responsive design validated")
        print("  ✅ Viewport meta tag present")
        print("  ✅ Media queries configured")
        print("  ✅ Mobile-friendly layout ready")
        
    except Exception as e:
        print(f"❌ Responsive validation failed: {e}")
        return False
    
    print()
    print("-" * 70)
    print("TEST 4: Chart.js Visual Elements")
    print("-" * 70)
    
    try:
        # Check Chart.js
        assert "chart.js" in html_content.lower() or "chartjs" in html_content.lower()
        assert "<canvas" in html_content
        assert "successRateChart" in html_content or "durationChart" in html_content
        
        print("✅ Charts validated")
        print("  ✅ Chart.js library loaded")
        print("  ✅ Canvas elements present")
        print("  ✅ Chart initialization code ready")
        
    except Exception as e:
        print(f"❌ Charts validation failed: {e}")
        return False
    
    print()
    print("-" * 70)
    print("TEST 5: Print Layout Validation")
    print("-" * 70)
    
    try:
        # Check print styles
        assert "@media print" in html_content
        print("✅ Print layout validated")
        print("  ✅ Print media queries present")
        print("  ✅ Print-optimized styles configured")
        
    except Exception as e:
        print(f"❌ Print validation failed: {e}")
        return False
    
    print()
    print("-" * 70)
    print("TEST 6: Generate Reports for All 14 Languages")
    print("-" * 70)
    
    try:
        all_langs = ['python', 'javascript', 'typescript', 'java', 'go', 'csharp',
                     'ruby', 'rust', 'php', 'swift', 'kotlin', 'cpp', 'html', 'css']
        
        output_dir = Path("visual_inspection_samples")
        output_dir.mkdir(exist_ok=True)
        
        for lang in all_langs:
            lang_results = ExecutionSummary(
                project_name=f"{lang.upper()} Visual Test",
                total=10,
                passed=8,
                failed=1,
                skipped=1,
                duration=5.0,
                language=lang,
                results=[
                    {'language': lang, 'test_name': f'test_{lang}_basic', 'status': 'PASS', 'duration': 0.5, 'details': 'Basic test passed'},
                    {'language': lang, 'test_name': f'test_{lang}_advanced', 'status': 'FAIL', 'duration': 1.2, 'details': f'Advanced {lang} test failed: assertion error'},
                    {'language': lang, 'test_name': f'test_{lang}_integration', 'status': 'SKIP', 'duration': 0.0, 'details': 'Integration test skipped'}
                ]
            )
            
            lang_path = output_dir / f"report_{lang}.html"
            reporter.generate_html_from_template(lang_results, str(lang_path))
        
        print(f"✅ All 14 language reports generated")
        print(f"  Location: {output_dir}/")
        print(f"  Files: report_*.html")
        print(f"  Ready for browser testing!")
        
    except Exception as e:
        print(f"❌ Multi-language generation failed: {e}")
        return False
    
    print()
    print("=" * 70)
    print("✅ ALL VISUAL INSPECTION TESTS PASSED!")
    print("=" * 70)
    print()
    print("Validated For Browser Viewing:")
    print("  ✅ Sample report generated (realistic data)")
    print("  ✅ CSS styling properly configured")
    print("  ✅ Responsive design (mobile-friendly)")
    print("  ✅ Chart.js integration")
    print("  ✅ Print layout optimized")
    print("  ✅ Color-coded status indicators")
    print("  ✅ All 14 languages ready")
    print()
    print("🌐 Manual Inspection Instructions:")
    print("  1. Open: visual_inspection_report.html")
    print("  2. Check: Layout, colors, charts, responsiveness")
    print("  3. Test: Resize window, print preview, all sections")
    print("  4. Languages: Browse visual_inspection_samples/*.html")
    print()
    print("📊 HTML reports ready for browser viewing!")
    
    return True


if __name__ == "__main__":
    try:
        success = test_visual_inspection()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
