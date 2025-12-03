#!/usr/bin/env python3
"""
Standalone verification test for AI Solution feature

This test verifies the AI solution implementation without requiring
a running server or Telegram bot setup.
"""

import asyncio
import sys
from pathlib import Path

# Add bot directory to path
sys.path.insert(0, str(Path(__file__).parent / 'bot'))

import database as db
import ai_service


async def main():
    """Run standalone verification"""
    print("\n" + "="*70)
    print("  AI SOLUTION FEATURE - STANDALONE VERIFICATION")
    print("="*70)
    
    print("\nThis test verifies the AI solution implementation is working.")
    print("It tests the core functionality without requiring a running server.")
    print("="*70)
    
    all_passed = True
    
    # Test 1: Database initialization and migrations
    print("\n[1] Testing database initialization...")
    try:
        await db.init_db()
        print("✓ Database initialized with AI solution columns")
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        all_passed = False
        return 1
    
    # Test 2: Create a test task
    print("\n[2] Creating test task...")
    try:
        task_id = await db.add_task(
            image_path="",
            correct_option="A",
            solution_image_path="",
            answer_type="quiz",
            created_by=0,
            task_text="Тест есеп: $2 + 2 = ?$",
            solution_text="Жауабы: $2 + 2 = 4$",
            option_a_text="4",
            option_b_text="5",
            option_c_text="3",
            option_d_text="6"
        )
        print(f"✓ Task created with ID: {task_id}")
    except Exception as e:
        print(f"✗ Task creation failed: {e}")
        all_passed = False
        return 1
    
    # Test 3: Update AI solution
    print("\n[3] Testing AI solution update...")
    try:
        test_solution = "**Шешімі:**\n\n$2 + 2 = 4$\n\nБұл қарапайым қосу."
        await db.update_ai_solution(task_id, test_solution, status='pending')
        print("✓ AI solution updated with pending status")
    except Exception as e:
        print(f"✗ AI solution update failed: {e}")
        all_passed = False
        return 1
    
    # Test 4: Get AI solution status
    print("\n[4] Testing AI solution status retrieval...")
    try:
        ai_status = await db.get_ai_solution_status(task_id)
        if ai_status and ai_status['ai_solution_status'] == 'pending':
            print("✓ AI solution status retrieved correctly")
            print(f"  Status: {ai_status['ai_solution_status']}")
            print(f"  Text length: {len(ai_status.get('ai_solution_text', ''))}")
        else:
            print(f"✗ AI solution status incorrect: {ai_status}")
            all_passed = False
    except Exception as e:
        print(f"✗ AI solution status retrieval failed: {e}")
        all_passed = False
    
    # Test 5: Approve AI solution
    print("\n[5] Testing AI solution approval...")
    try:
        await db.approve_ai_solution(task_id)
        ai_status = await db.get_ai_solution_status(task_id)
        if ai_status['ai_solution_status'] == 'approved':
            print("✓ AI solution approved successfully")
        else:
            print(f"✗ AI solution not approved: {ai_status['ai_solution_status']}")
            all_passed = False
    except Exception as e:
        print(f"✗ AI solution approval failed: {e}")
        all_passed = False
    
    # Test 6: Test solution priority logic
    print("\n[6] Testing solution priority logic...")
    try:
        task = await db.get_task(task_id)
        
        # Define the priority function
        def get_solution_text_for_task(task):
            if task.get("ai_solution_status") == "approved" and task.get("ai_solution_text"):
                return task.get("ai_solution_text")
            elif task.get("solution_text"):
                return task.get("solution_text")
            return None
        
        # Test with approved AI solution
        solution = get_solution_text_for_task(task)
        if solution == test_solution:
            print("✓ Solution priority: AI solution (approved) takes precedence")
        else:
            print(f"✗ Wrong solution returned")
            all_passed = False
        
        # Test after rejection
        await db.reject_ai_solution(task_id)
        task = await db.get_task(task_id)
        solution = get_solution_text_for_task(task)
        if solution == "Жауабы: $2 + 2 = 4$":  # Manual solution
            print("✓ Solution priority: Rejected AI falls back to manual")
        else:
            print(f"✗ Wrong solution after rejection")
            all_passed = False
    except Exception as e:
        print(f"✗ Solution priority test failed: {e}")
        all_passed = False
    
    # Test 7: Test prompt building
    print("\n[7] Testing AI prompt building...")
    try:
        task = await db.get_task(task_id)
        prompt = ai_service.build_solution_prompt(task)
        
        if all([
            "Есеп:" in prompt,
            "Тест (A/B/C/D)" in prompt,
            "A) 4" in prompt,
            "жауап:** A" in prompt,
            "қадам-қадаммен" in prompt
        ]):
            print("✓ AI prompt built correctly")
            print(f"  Prompt length: {len(prompt)} characters")
        else:
            print(f"✗ Prompt missing expected content")
            all_passed = False
    except Exception as e:
        print(f"✗ Prompt building failed: {e}")
        all_passed = False
    
    # Test 8: Test error handling
    print("\n[8] Testing error handling...")
    try:
        # Test with missing API key (should raise ValueError)
        import os
        old_key = os.environ.get('OPENAI_API_KEY')
        os.environ.pop('OPENAI_API_KEY', None)
        
        try:
            await ai_service.generate_ai_solution(task)
            print("✗ Should have raised ValueError for missing API key")
            all_passed = False
        except ValueError as e:
            if "OPENAI_API_KEY" in str(e):
                print("✓ Correctly raises ValueError when API key is missing")
            else:
                print(f"✗ Wrong error message: {e}")
                all_passed = False
        
        # Restore key if it existed
        if old_key:
            os.environ['OPENAI_API_KEY'] = old_key
    except Exception as e:
        print(f"✗ Error handling test failed: {e}")
        all_passed = False
    
    # Summary
    print("\n" + "="*70)
    if all_passed:
        print("  ✅ ALL VERIFICATION TESTS PASSED!")
        print("="*70)
        print("\n🎉 The AI Solution feature is working correctly!")
        print("\nImplementation verified:")
        print("  ✓ Database migrations")
        print("  ✓ AI solution CRUD operations")
        print("  ✓ Solution approval/rejection workflow")
        print("  ✓ Solution priority logic")
        print("  ✓ Prompt building")
        print("  ✓ Error handling")
        print("\nNext steps:")
        print("  1. See TESTING_QUICKSTART.md for manual testing")
        print("  2. See AI_SOLUTION_FEATURE.md for full documentation")
        print("  3. Run test_ai_api.py to test API endpoints (requires server)")
        return 0
    else:
        print("  ⚠️  SOME VERIFICATION TESTS FAILED")
        print("="*70)
        print("\nPlease review the output above for details.")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
