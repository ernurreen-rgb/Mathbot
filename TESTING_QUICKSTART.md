# Quick Start Guide - Testing AI Solution Feature

This guide shows you how to quickly test the AI solution feature.

## Prerequisites

- Python 3.11+
- Dependencies installed (`pip install -r bot/requirements.txt`)
- Optional: OpenAI API key for real AI generation

## Option 1: Automated Tests (Recommended)

### Step 1: Run Unit Tests

```bash
cd bot
python test_ai_solution.py
```

Expected output:
```
✅ ALL TESTS PASSED!
The AI Solution feature is working correctly!
```

This tests:
- Database AI solution functions
- Solution priority logic
- Prompt building
- Error handling

### Step 2: Run API Tests (Optional)

**Terminal 1 - Start the server:**
```bash
cd bot
export BOT_TOKEN=dummy_token_for_testing
python main.py
```

Wait for: `Application startup complete.`

**Terminal 2 - Run API tests:**
```bash
cd bot
python test_ai_api.py
```

This tests all admin API endpoints end-to-end.

## Option 2: Manual Testing with cURL

### Step 1: Start the Server

```bash
cd bot
export BOT_TOKEN=your_telegram_bot_token
export OPENAI_API_KEY=your_openai_api_key  # Optional
python main.py
```

### Step 2: Create a Test Task

```bash
curl -X POST http://localhost:8000/api/admin/tasks \
  -H "X-Admin-Email: ernurreen@gmail.com" \
  -F "correct_option=A" \
  -F "answer_type=quiz" \
  -F "task_text=Тест: \$2 + 2 = ?\$" \
  -F "option_a_text=4" \
  -F "option_b_text=5"
```

Note the task `id` from the response (e.g., `"id": 1`).

### Step 3: Request AI Solution

```bash
curl -X POST http://localhost:8000/api/admin/tasks/1/ai-solution \
  -H "X-Admin-Email: ernurreen@gmail.com"
```

**If you don't have OPENAI_API_KEY**, you'll get an error. That's OK - it means the error handling works!

**If you have OPENAI_API_KEY**, you'll see the generated solution.

### Step 4: Check AI Solution Status

```bash
curl http://localhost:8000/api/admin/tasks/1/ai-solution \
  -H "X-Admin-Email: ernurreen@gmail.com"
```

### Step 5: Approve AI Solution

```bash
curl -X POST http://localhost:8000/api/admin/tasks/1/ai-solution/approve \
  -H "X-Admin-Email: ernurreen@gmail.com"
```

### Step 6: Verify Solution Priority

```bash
curl http://localhost:8000/api/admin/tasks/1 \
  -H "X-Admin-Email: ernurreen@gmail.com"
```

Check that `ai_solution_status` is `"approved"`.

## Option 3: Test with Database Directly

```bash
cd bot
python3 << 'EOF'
import asyncio
import database as db

async def test():
    await db.init_db()
    
    # Create task
    task_id = await db.add_task(
        image_path="",
        correct_option="A",
        solution_image_path="",
        answer_type="quiz",
        created_by=0,
        task_text="Test: $2 + 2 = ?$",
        solution_text="Answer: $2 + 2 = 4$",
        option_a_text="4",
        option_b_text="5",
        option_c_text="3",
        option_d_text="6"
    )
    print(f"Created task: {task_id}")
    
    # Add AI solution
    await db.update_ai_solution(
        task_id, 
        "**Шешімі:**\n\n$2 + 2 = 4$",
        status='pending'
    )
    print("AI solution added (pending)")
    
    # Approve it
    await db.approve_ai_solution(task_id)
    print("AI solution approved")
    
    # Verify
    status = await db.get_ai_solution_status(task_id)
    print(f"Status: {status['ai_solution_status']}")
    print("✓ Test completed successfully!")

asyncio.run(test())
EOF
```

## What Gets Tested?

### ✅ Database Operations
- Creating tasks with AI solution fields
- Updating AI solutions
- Approving/rejecting AI solutions
- Retrieving AI solution status

### ✅ API Integration
- Admin authentication
- AI solution request endpoint
- Approval/rejection workflow
- Status retrieval

### ✅ Solution Priority
- AI solution (approved) > Manual text > Image
- Pending/rejected AI solutions are ignored

### ✅ Error Handling
- Missing OPENAI_API_KEY
- Invalid admin email
- Missing task
- API failures

## Common Issues

### "OPENAI_API_KEY environment variable is not set"

**This is expected** if you don't have an OpenAI API key. The feature still works with:
- Manual AI solutions (set via database)
- Testing the approval/rejection workflow
- Testing solution priority logic

### "Admin access required"

Make sure you're using the correct admin email:
- Default: `ernurreen@gmail.com`
- Or set via: `export ADMIN_EMAILS=your@email.com`

### "Could not connect to server"

Make sure the server is running:
```bash
cd bot
export BOT_TOKEN=dummy
python main.py
```

## Success Criteria

The AI solution feature is working if:

1. ✅ Unit tests pass (`python test_ai_solution.py`)
2. ✅ Database functions work (create/update/approve/reject)
3. ✅ Solution priority logic works correctly
4. ✅ Admin API endpoints are accessible with correct email
5. ✅ Non-admin access is blocked (403)
6. ✅ Error handling works when API key is missing

## Next Steps

After verifying the feature works:

1. **Production Setup:**
   - Set real `OPENAI_API_KEY` in environment
   - Configure `ADMIN_EMAILS` with your admin emails
   - Test with real math problems

2. **Web Admin Panel:**
   - Access `/admin` route in web interface
   - Test "Request AI Solution" button
   - Test approve/reject workflow in UI

3. **Monitoring:**
   - Monitor OpenAI API usage
   - Review AI-generated solutions
   - Track approval/rejection rates

---

**For questions or issues, refer to:**
- `AI_SOLUTION_FEATURE.md` - Full feature documentation
- `AI_SOLUTION_TESTING.md` - Detailed testing report
- `README.md` - General project documentation
