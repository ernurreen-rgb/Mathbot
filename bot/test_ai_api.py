#!/usr/bin/env python3
"""
Test script for AI Solution API endpoints

This script tests the HTTP API endpoints for the AI solution feature.
It should be run while the server (main.py) is running.
"""

import asyncio
import aiohttp
import sys
import os
from pathlib import Path

# Add bot directory to path for database import
sys.path.insert(0, str(Path(__file__).parent))
import database as db

# Base URL for the API
BASE_URL = "http://localhost:8000"

# Admin email for authentication (configurable via environment variable)
ADMIN_EMAIL = os.getenv("TEST_ADMIN_EMAIL", "ernurreen@gmail.com")


async def test_ai_solution_api():
    """Test AI solution API endpoints"""
    print("\n" + "="*70)
    print("  AI SOLUTION API ENDPOINTS TEST")
    print("="*70)
    
    print("\nPrerequisites:")
    print("  • Server must be running (python main.py)")
    print("  • Set BOT_TOKEN environment variable (can be dummy for API testing)")
    print("  • Optionally set OPENAI_API_KEY to test AI generation")
    print("="*70)
    
    async with aiohttp.ClientSession() as session:
        # Test 1: Create a test task via admin API
        print("\n[1] Creating a test task...")
        task_data = aiohttp.FormData()
        task_data.add_field('correct_option', 'A')
        task_data.add_field('answer_type', 'quiz')
        task_data.add_field('task_text', 'Тест есеп: $2 + 2 = ?$')
        task_data.add_field('solution_text', 'Жауабы: $2 + 2 = 4$')
        task_data.add_field('option_a_text', '4')
        task_data.add_field('option_b_text', '5')
        task_data.add_field('option_c_text', '3')
        task_data.add_field('option_d_text', '6')
        
        headers = {"X-Admin-Email": ADMIN_EMAIL}
        
        try:
            async with session.post(
                f"{BASE_URL}/api/admin/tasks",
                data=task_data,
                headers=headers
            ) as resp:
                if resp.status == 200:
                    task = await resp.json()
                    task_id = task.get('id')
                    print(f"✓ Task created successfully (ID: {task_id})")
                else:
                    error = await resp.text()
                    print(f"✗ Failed to create task: {resp.status} - {error}")
                    return False
        except aiohttp.ClientConnectorError:
            print("✗ Could not connect to server. Is it running?")
            print("  Run: cd bot && export BOT_TOKEN=dummy && python main.py")
            return False
        
        # Test 2: Request AI solution
        print("\n[2] Requesting AI solution...")
        try:
            async with session.post(
                f"{BASE_URL}/api/admin/tasks/{task_id}/ai-solution",
                headers=headers
            ) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    print(f"✓ AI solution requested")
                    if 'ai_solution_text' in result:
                        print(f"  Status: {result.get('ai_solution_status')}")
                        print(f"  Length: {len(result.get('ai_solution_text', ''))} characters")
                    else:
                        print(f"  Response: {result}")
                else:
                    error = await resp.text()
                    if "OPENAI_API_KEY" in error:
                        print(f"⚠️  OPENAI_API_KEY not set - skipping AI generation test")
                        print(f"  (This is expected if you don't have an API key)")
                        # Continue with manual AI solution for testing
                        print("\n  Setting AI solution manually for testing...")
                        await db.update_ai_solution(
                            task_id,
                            "**Шешімі:**\n\n$2 + 2 = 4$\n\nБұл қарапайым қосу.",
                            status='pending'
                        )
                        print("  ✓ Manual AI solution set")
                    else:
                        print(f"✗ Failed: {resp.status} - {error}")
                        return False
        except Exception as e:
            print(f"✗ Exception: {e}")
            return False
        
        # Test 3: Get AI solution status
        print("\n[3] Getting AI solution status...")
        try:
            async with session.get(
                f"{BASE_URL}/api/admin/tasks/{task_id}/ai-solution",
                headers=headers
            ) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    print(f"✓ AI solution status retrieved")
                    print(f"  Status: {result.get('ai_solution_status')}")
                    print(f"  Has text: {bool(result.get('ai_solution_text'))}")
                else:
                    error = await resp.text()
                    print(f"✗ Failed: {resp.status} - {error}")
                    return False
        except Exception as e:
            print(f"✗ Exception: {e}")
            return False
        
        # Test 4: Approve AI solution
        print("\n[4] Approving AI solution...")
        try:
            async with session.post(
                f"{BASE_URL}/api/admin/tasks/{task_id}/ai-solution/approve",
                headers=headers
            ) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    print(f"✓ AI solution approved")
                    print(f"  Status: {result.get('ai_solution_status')}")
                else:
                    error = await resp.text()
                    print(f"✗ Failed: {resp.status} - {error}")
                    return False
        except Exception as e:
            print(f"✗ Exception: {e}")
            return False
        
        # Test 5: Verify task returns AI solution
        print("\n[5] Verifying task returns AI solution...")
        try:
            async with session.get(
                f"{BASE_URL}/api/admin/tasks/{task_id}",
                headers=headers
            ) as resp:
                if resp.status == 200:
                    task = await resp.json()
                    if task.get('ai_solution_status') == 'approved':
                        print(f"✓ Task has approved AI solution")
                        print(f"  AI text length: {len(task.get('ai_solution_text', ''))}")
                    else:
                        print(f"✗ AI solution not approved in task data")
                        return False
                else:
                    error = await resp.text()
                    print(f"✗ Failed: {resp.status} - {error}")
                    return False
        except Exception as e:
            print(f"✗ Exception: {e}")
            return False
        
        # Test 6: Test retry functionality
        print("\n[6] Testing AI solution retry...")
        try:
            # First, let's check if we can retry
            async with session.post(
                f"{BASE_URL}/api/admin/tasks/{task_id}/ai-solution/retry",
                headers=headers
            ) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    print(f"✓ AI solution retry works")
                    print(f"  Status: {result.get('ai_solution_status')}")
                elif "OPENAI_API_KEY" in await resp.text():
                    print(f"⚠️  Retry skipped (no API key)")
                else:
                    error = await resp.text()
                    print(f"✗ Failed: {resp.status} - {error}")
                    return False
        except Exception as e:
            print(f"✗ Exception: {e}")
            return False
        
        # Test 7: Test reject functionality
        print("\n[7] Testing AI solution reject...")
        try:
            async with session.post(
                f"{BASE_URL}/api/admin/tasks/{task_id}/ai-solution/reject",
                headers=headers
            ) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    print(f"✓ AI solution rejected")
                    print(f"  Status: {result.get('ai_solution_status')}")
                else:
                    error = await resp.text()
                    print(f"✗ Failed: {resp.status} - {error}")
                    return False
        except Exception as e:
            print(f"✗ Exception: {e}")
            return False
        
        # Test 8: Verify non-admin cannot access
        print("\n[8] Testing admin authentication...")
        try:
            headers_non_admin = {"X-Admin-Email": "notadmin@example.com"}
            async with session.post(
                f"{BASE_URL}/api/admin/tasks/{task_id}/ai-solution/approve",
                headers=headers_non_admin
            ) as resp:
                if resp.status == 403:
                    print(f"✓ Non-admin correctly denied access (403)")
                else:
                    print(f"✗ Non-admin should get 403, got {resp.status}")
                    return False
        except Exception as e:
            print(f"✗ Exception: {e}")
            return False
        
        # Cleanup
        print("\n[9] Cleaning up test task...")
        try:
            async with session.delete(
                f"{BASE_URL}/api/admin/tasks/{task_id}",
                headers=headers
            ) as resp:
                if resp.status == 200:
                    print(f"✓ Test task deleted")
                else:
                    print(f"⚠️  Could not delete task (status {resp.status})")
        except Exception as e:
            print(f"⚠️  Exception during cleanup: {e}")
        
        print("\n" + "="*70)
        print("  ✅ ALL API TESTS PASSED!")
        print("="*70)
        print("\nThe AI Solution API endpoints are working correctly!")
        return True


async def main():
    """Main test runner"""
    try:
        success = await test_ai_solution_api()
        return 0 if success else 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
