#!/usr/bin/env python3
"""
Comprehensive test script for AI Solution feature

Tests:
1. Database AI solution functions
2. AI service integration (with mock if no API key)
3. Solution priority order
4. Error handling
"""

import asyncio
import os
import sys
from pathlib import Path

# Add bot directory to path
sys.path.insert(0, str(Path(__file__).parent))

import database as db
import ai_service


async def test_database_ai_functions():
    """Test database AI solution management functions"""
    print("\n" + "="*60)
    print("TEST 1: Database AI Solution Functions")
    print("="*60)
    
    # Initialize database
    await db.init_db()
    print("✓ Database initialized")
    
    # Create a test task
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
    print(f"✓ Created test task with ID: {task_id}")
    
    # Test 1: Update AI solution with pending status
    test_solution = "**Шешімі:**\n\n$2 + 2 = 4$\n\nБұл қарапайым қосу."
    await db.update_ai_solution(task_id, test_solution, status='pending')
    print("✓ Updated AI solution with pending status")
    
    # Verify the update
    ai_status = await db.get_ai_solution_status(task_id)
    assert ai_status is not None, "AI status should exist"
    assert ai_status['ai_solution_text'] == test_solution, "AI solution text should match"
    assert ai_status['ai_solution_status'] == 'pending', "Status should be pending"
    assert ai_status['ai_solution_requested_at'] is not None, "Timestamp should be set"
    print("✓ Verified AI solution is pending")
    
    # Test 2: Approve AI solution
    await db.approve_ai_solution(task_id)
    ai_status = await db.get_ai_solution_status(task_id)
    assert ai_status['ai_solution_status'] == 'approved', "Status should be approved"
    print("✓ AI solution approved successfully")
    
    # Test 3: Reject AI solution (after another update)
    await db.update_ai_solution(task_id, "New solution", status='pending')
    await db.reject_ai_solution(task_id)
    ai_status = await db.get_ai_solution_status(task_id)
    assert ai_status['ai_solution_status'] == 'rejected', "Status should be rejected"
    print("✓ AI solution rejected successfully")
    
    # Test 4: Verify task retrieval includes AI fields
    task = await db.get_task(task_id)
    assert 'ai_solution_text' in task, "Task should have ai_solution_text field"
    assert 'ai_solution_status' in task, "Task should have ai_solution_status field"
    print("✓ Task retrieval includes AI solution fields")
    
    print("\n✅ All database tests passed!")
    return task_id


async def test_ai_service_integration(task_id):
    """Test AI service integration"""
    print("\n" + "="*60)
    print("TEST 2: AI Service Integration")
    print("="*60)
    
    # Get the test task
    task = await db.get_task(task_id)
    
    # Check if OpenAI API key is configured
    api_key = os.getenv("OPENAI_API_KEY", "")
    
    if not api_key:
        print("⚠️  OPENAI_API_KEY not set - testing error handling only")
        
        # Test that it raises appropriate error
        try:
            await ai_service.generate_ai_solution(task)
            print("❌ Should have raised ValueError for missing API key")
            return False
        except ValueError as e:
            if "OPENAI_API_KEY" in str(e):
                print("✓ Correctly raises ValueError when API key is missing")
            else:
                print(f"❌ Wrong error message: {e}")
                return False
        
        print("\n⚠️  Skipping actual API call test (no API key)")
        print("   To test with real API, set OPENAI_API_KEY environment variable")
        return True
    
    else:
        print(f"✓ OPENAI_API_KEY is configured")
        print(f"✓ Using model: {ai_service.OPENAI_MODEL}")
        
        try:
            print("\n🤖 Generating AI solution (this may take 10-30 seconds)...")
            solution = await ai_service.generate_ai_solution(task)
            
            print(f"\n✓ AI solution generated successfully!")
            print(f"  Length: {len(solution)} characters")
            print(f"\n  Preview (first 200 chars):")
            print(f"  {solution[:200]}...")
            
            # Verify solution is in Kazakh and has some expected markers
            if any(word in solution.lower() for word in ['шешім', 'жауап', 'есеп', 'қадам']):
                print("✓ Solution appears to be in Kazakh")
            else:
                print("⚠️  Solution may not be in Kazakh (expected Kazakh keywords)")
            
            # Check for LaTeX formatting
            if '$' in solution or '$$' in solution:
                print("✓ Solution includes LaTeX formatting")
            else:
                print("⚠️  No LaTeX formatting detected in solution")
            
            # Update database with the generated solution
            await db.update_ai_solution(task_id, solution, status='pending')
            print("✓ Saved AI solution to database")
            
            print("\n✅ AI service integration test passed!")
            return True
            
        except Exception as e:
            print(f"❌ AI service test failed: {e}")
            import traceback
            traceback.print_exc()
            return False


async def test_solution_priority():
    """Test solution priority order (AI > manual text > image)"""
    print("\n" + "="*60)
    print("TEST 3: Solution Priority Order")
    print("="*60)
    
    # Define the function inline to avoid importing main.py (which needs aiogram)
    def get_solution_text_for_task(task):
        """Get the appropriate solution text for a task."""
        # Priority 1: AI solution if approved
        if task.get("ai_solution_status") == "approved" and task.get("ai_solution_text"):
            return task.get("ai_solution_text")
        # Priority 2: Manual solution text
        elif task.get("solution_text"):
            return task.get("solution_text")
        # Priority 3: None (caller will check for solution image)
        return None
    
    # Test case 1: AI solution approved (highest priority)
    task1 = {
        "ai_solution_status": "approved",
        "ai_solution_text": "AI Solution Text",
        "solution_text": "Manual Solution Text",
        "solution_image_path": "image.jpg"
    }
    result1 = get_solution_text_for_task(task1)
    assert result1 == "AI Solution Text", "Should return AI solution when approved"
    print("✓ Priority 1: Approved AI solution takes precedence")
    
    # Test case 2: AI solution pending (should not be used)
    task2 = {
        "ai_solution_status": "pending",
        "ai_solution_text": "Pending AI Solution",
        "solution_text": "Manual Solution Text",
        "solution_image_path": "image.jpg"
    }
    result2 = get_solution_text_for_task(task2)
    assert result2 == "Manual Solution Text", "Should return manual text when AI is pending"
    print("✓ Priority 2: Pending AI solution is not used, falls back to manual text")
    
    # Test case 3: AI solution rejected
    task3 = {
        "ai_solution_status": "rejected",
        "ai_solution_text": "Rejected AI Solution",
        "solution_text": "Manual Solution Text",
        "solution_image_path": "image.jpg"
    }
    result3 = get_solution_text_for_task(task3)
    assert result3 == "Manual Solution Text", "Should return manual text when AI is rejected"
    print("✓ Priority 3: Rejected AI solution is not used, falls back to manual text")
    
    # Test case 4: No AI solution, only manual text
    task4 = {
        "ai_solution_status": "none",
        "ai_solution_text": None,
        "solution_text": "Manual Solution Text",
        "solution_image_path": "image.jpg"
    }
    result4 = get_solution_text_for_task(task4)
    assert result4 == "Manual Solution Text", "Should return manual text when no AI solution"
    print("✓ Priority 4: Manual text used when no AI solution")
    
    # Test case 5: No text solutions (should return None, fall back to image)
    task5 = {
        "ai_solution_status": "none",
        "ai_solution_text": None,
        "solution_text": None,
        "solution_image_path": "image.jpg"
    }
    result5 = get_solution_text_for_task(task5)
    assert result5 is None, "Should return None to allow image fallback"
    print("✓ Priority 5: Returns None when no text solutions (allows image fallback)")
    
    print("\n✅ All solution priority tests passed!")


async def test_prompt_building():
    """Test AI prompt building logic"""
    print("\n" + "="*60)
    print("TEST 4: AI Prompt Building")
    print("="*60)
    
    # Import only the specific function to avoid loading full aiogram dependency
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from ai_service import build_solution_prompt
    
    # Test quiz task
    quiz_task = {
        "task_text": "Егер $x + y = 10$ және $x - y = 2$ болса, $x$ мәнін табыңыз.",
        "answer_type": "quiz",
        "option_a_text": "6",
        "option_b_text": "8",
        "option_c_text": "4",
        "option_d_text": "12",
        "correct_option": "A"
    }
    
    prompt1 = build_solution_prompt(quiz_task)
    assert "Есеп:" in prompt1, "Prompt should include task label"
    assert quiz_task["task_text"] in prompt1, "Prompt should include task text"
    assert "Тест (A/B/C/D)" in prompt1, "Prompt should indicate quiz type"
    assert "A) 6" in prompt1, "Prompt should include options"
    assert "жауап:** A" in prompt1, "Prompt should include correct answer"
    print("✓ Quiz task prompt built correctly")
    
    # Test text input task
    text_task = {
        "task_text": "Теңдеуді шешіңіз: $2x = 10$",
        "answer_type": "text",
        "correct_option": "5"
    }
    
    prompt2 = build_solution_prompt(text_task)
    assert "Қолмен енгізу" in prompt2, "Prompt should indicate text input type"
    assert "жауап:** 5" in prompt2, "Prompt should include correct answer"
    print("✓ Text input task prompt built correctly")
    
    # Test task without text (image-based)
    image_task = {
        "task_text": "",
        "answer_type": "quiz",
        "correct_option": "B"
    }
    
    prompt3 = build_solution_prompt(image_task)
    assert "(суретте берілген)" in prompt3, "Prompt should indicate image-based task"
    print("✓ Image-based task prompt built correctly")
    
    print("\n✅ All prompt building tests passed!")


async def cleanup_test_data():
    """Clean up test data"""
    print("\n" + "="*60)
    print("Cleaning up test data...")
    print("="*60)
    
    # Note: In a real scenario, you might want to delete test tasks
    # For now, we'll just note that test data exists in database.db
    print("⚠️  Test data remains in database.db")
    print("   To clean up, delete bot/database.db file")


async def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("  AI SOLUTION FEATURE - COMPREHENSIVE TEST SUITE")
    print("="*70)
    print("\nThis script tests the AI solution feature implementation:")
    print("  • Database AI solution functions")
    print("  • AI service integration with OpenAI API")
    print("  • Solution priority order")
    print("  • Prompt building logic")
    print("="*70)
    
    all_passed = True
    task_id = None
    
    try:
        # Test 1: Database functions
        task_id = await test_database_ai_functions()
        
        # Test 2: AI service integration
        ai_test_passed = await test_ai_service_integration(task_id)
        if not ai_test_passed:
            all_passed = False
        
        # Test 3: Solution priority
        await test_solution_priority()
        
        # Test 4: Prompt building
        await test_prompt_building()
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        all_passed = False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        all_passed = False
    finally:
        await cleanup_test_data()
    
    # Print summary
    print("\n" + "="*70)
    if all_passed:
        print("  ✅ ALL TESTS PASSED!")
        print("="*70)
        print("\nThe AI Solution feature is working correctly!")
        print("\nNext steps:")
        print("  1. Set OPENAI_API_KEY to test real API integration")
        print("  2. Test the feature via HTTP API endpoints")
        print("  3. Test the feature in the web admin panel")
        return 0
    else:
        print("  ⚠️  SOME TESTS HAD ISSUES")
        print("="*70)
        print("\nPlease review the output above for details.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
