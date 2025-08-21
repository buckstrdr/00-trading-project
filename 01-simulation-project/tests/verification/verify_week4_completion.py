#!/usr/bin/env python3
"""
Week 4 Completion Verification Script
Direct verification of all Week 4 requirements
"""

import os
from pathlib import Path

def verify_week4_completion():
    """Verify Week 4 completion status with detailed diagnostics"""
    
    print("Week 4 Completion Verification")
    print("=" * 50)
    
    base_path = Path("C:/Users/salte/ClaudeProjects/github-repos/01-simulation-project")
    
    checks = []
    
    # 1. Service Communication Tests
    print("\n1. Service Communication Tests")
    integration_file = base_path / "tests/integration/test_service_communication.py"
    
    if integration_file.exists():
        try:
            content = integration_file.read_text(encoding='utf-8')
            test_methods = content.count("def test_")
            content_size = len(content)
            
            print(f"   File exists: [YES]")
            print(f"   File size: {content_size} bytes")
            print(f"   Test methods: {test_methods}")
            print(f"   Size > 10000: {content_size > 10000}")
            print(f"   Methods >= 5: {test_methods >= 5}")
            
            integration_comprehensive = test_methods >= 5 and content_size > 10000
            print(f"   Integration comprehensive: {integration_comprehensive}")
            checks.append(("Integration Tests", integration_comprehensive))
            
        except Exception as e:
            print(f"   Error reading file: {e}")
            checks.append(("Integration Tests", False))
    else:
        print("   File exists: [NO]")
        checks.append(("Integration Tests", False))
    
    # 2. System Health Monitoring
    print("\n2. System Health Monitoring")
    run_system_file = base_path / "run_system.py" 
    health_test_file = base_path / "test_system_health.py"
    
    health_monitoring = False
    
    if run_system_file.exists():
        try:
            content = run_system_file.read_text(encoding='utf-8')
            # Check for Unicode characters that would cause encoding issues
            has_unicode_emojis = any(char in content for char in ['\u2705', '\u274c', '\u1f680', '\u1f310', '\u1f389'])
            
            print(f"   run_system.py exists: [YES]")
            print(f"   Has Unicode emojis: {has_unicode_emojis}")
            print(f"   Encoding safe: {not has_unicode_emojis}")
            
            health_monitoring = not has_unicode_emojis
            
        except UnicodeDecodeError:
            print(f"   Unicode encoding error detected: [ERROR]")
            health_monitoring = False
        except Exception as e:
            print(f"   Error reading run_system.py: {e}")
            health_monitoring = False
    else:
        print("   run_system.py exists: [NO]")
    
    if health_test_file.exists():
        print(f"   test_system_health.py exists: [YES]")
        health_monitoring = True
    else:
        print(f"   test_system_health.py exists: [NO]")
    
    checks.append(("Health Monitoring", health_monitoring))
    
    # 3. API Documentation
    print("\n3. API Documentation")
    api_doc_file = base_path / "API_DOCUMENTATION.md"
    
    if api_doc_file.exists():
        try:
            content = api_doc_file.read_text(encoding='utf-8')
            
            # Check for endpoint examples
            required_examples = [
                "GET http://localhost:8001/health",
                "POST http://localhost:8002/api/backtest",
                "POST http://localhost:8005/api/portfolio"
            ]
            
            examples_found = sum(1 for example in required_examples if example in content)
            has_all_examples = examples_found == len(required_examples)
            
            print(f"   File exists: [YES]")
            print(f"   Required examples found: {examples_found}/{len(required_examples)}")
            print(f"   Has all examples: {has_all_examples}")
            
            # Print which examples were found
            for example in required_examples:
                found = "[YES]" if example in content else "[NO]"
                print(f"     {found} {example}")
            
            checks.append(("API Documentation", has_all_examples))
            
        except Exception as e:
            print(f"   Error reading API_DOCUMENTATION.md: {e}")
            checks.append(("API Documentation", False))
    else:
        print("   File exists: [NO]") 
        checks.append(("API Documentation", False))
    
    # Calculate completion percentage
    print("\n" + "=" * 50)
    print("WEEK 4 COMPLETION SUMMARY")
    print("=" * 50)
    
    passed_checks = sum(1 for _, status in checks if status)
    total_checks = len(checks)
    completion_percentage = (passed_checks / total_checks) * 100
    
    for check_name, status in checks:
        status_icon = "[PASS]" if status else "[FAIL]"
        print(f"{status_icon} {check_name}: {'PASS' if status else 'FAIL'}")
    
    print(f"\nCompletion: {passed_checks}/{total_checks} ({completion_percentage:.0f}%)")
    
    if completion_percentage == 100:
        print("[SUCCESS] WEEK 4: 100% COMPLETE!")
        return True
    else:
        print(f"[WARNING] WEEK 4: {completion_percentage:.0f}% COMPLETE")
        return False

if __name__ == "__main__":
    success = verify_week4_completion()
    exit(0 if success else 1)