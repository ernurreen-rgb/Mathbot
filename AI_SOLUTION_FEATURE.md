# AI Solution Feature - Documentation

## Overview

Mathbot now supports AI-powered solution explanations for math problems. Admins can request AI to generate detailed step-by-step solutions, review them, and approve/reject before showing to users.

## Features

- 🤖 **AI-Generated Solutions**: Uses OpenAI API to generate detailed explanations in Kazakh
- ✅ **Admin Approval Workflow**: Admins review and approve solutions before users see them
- 🔄 **Retry Mechanism**: Admins can regenerate solutions if not satisfied
- 💾 **Cached Solutions**: Approved solutions are saved in database for fast access
- 📝 **LaTeX Support**: Solutions are formatted with LaTeX mathematical notation
- 🌐 **Multi-Language**: Supports both Telegram bot and web interface

## How It Works

### 1. Admin Workflow

1. **Request AI Solution**:
   - Admin opens a task in the admin panel
   - Clicks "Request AI Solution" button
   - System sends task to OpenAI API for explanation
   - AI generates step-by-step solution in Kazakh with LaTeX formulas

2. **Review Solution**:
   - Admin reviews the generated solution
   - Can choose to:
     - **Approve**: Solution becomes visible to all users
     - **Reject**: Solution is marked as rejected
     - **Retry**: Generate a new solution

3. **Approved Solution**:
   - Once approved, solution is cached in database
   - Users see AI solution immediately (no API calls needed)
   - Solution appears both in Telegram bot and web interface

### 2. User Experience

- When solving a problem, users can view the solution
- System prioritizes AI solution (if approved) over manual solutions
- Fallback to manual solution_text or solution_image if no AI solution

### 3. Priority Order for Solution Display

1. **AI Solution** (if approved) - Highest priority
2. **Manual Text Solution** (solution_text field)
3. **Manual Image Solution** (solution_image_path)

## API Endpoints

### Admin Endpoints (Require X-Admin-Email header)

#### Request AI Solution
```http
POST /api/admin/tasks/{task_id}/ai-solution
X-Admin-Email: admin@example.com

Response:
{
  "task_id": 1,
  "ai_solution_text": "**Шешімі:**\n\n...",
  "ai_solution_status": "pending",
  "message": "AI solution generated successfully. Please review and approve/reject."
}
```

#### Retry AI Solution
```http
POST /api/admin/tasks/{task_id}/ai-solution/retry
X-Admin-Email: admin@example.com

Response:
{
  "task_id": 1,
  "ai_solution_text": "**Шешімі:**\n\n...",
  "ai_solution_status": "pending",
  "message": "AI solution regenerated successfully. Please review and approve/reject."
}
```

#### Approve AI Solution
```http
POST /api/admin/tasks/{task_id}/ai-solution/approve
X-Admin-Email: admin@example.com

Response:
{
  "task_id": 1,
  "ai_solution_status": "approved",
  "message": "AI solution approved successfully"
}
```

#### Reject AI Solution
```http
POST /api/admin/tasks/{task_id}/ai-solution/reject
X-Admin-Email: admin@example.com

Response:
{
  "task_id": 1,
  "ai_solution_status": "rejected",
  "message": "AI solution rejected"
}
```

#### Get AI Solution Status
```http
GET /api/admin/tasks/{task_id}/ai-solution
X-Admin-Email: admin@example.com

Response:
{
  "task_id": 1,
  "ai_solution_text": "**Шешімі:**\n\n...",
  "ai_solution_status": "approved",
  "ai_solution_requested_at": "2024-01-15T10:30:00"
}
```

## Database Schema

### New Columns in `tasks` Table

| Column                    | Type      | Description                                    |
|---------------------------|-----------|------------------------------------------------|
| ai_solution_text          | TEXT      | AI-generated solution content (Markdown/LaTeX) |
| ai_solution_status        | TEXT      | Status: 'none', 'pending', 'approved', 'rejected' |
| ai_solution_requested_at  | TIMESTAMP | When AI solution was requested                 |

## Environment Variables

### Required for AI Feature

```env
OPENAI_API_KEY=sk-...  # Your OpenAI API key
```

### Optional Configuration

```env
OPENAI_MODEL=gpt-4o-mini  # Default model (can use gpt-4, gpt-3.5-turbo, etc.)
```

## AI Prompt Template

The system generates prompts in Kazakh with:
- Task text (with LaTeX formulas)
- Answer type (quiz/text)
- Quiz options (if applicable)
- Correct answer
- Instructions for step-by-step explanation

Example prompt:
```
**Есеп:**
Егер $x + y = 10$ және $x - y = 2$ болса, $x$ және $y$ табыңыз.

**Түрі:** Қолмен енгізу

**Дұрыс жауап:** x=6, y=4

Бұл есептің толық шешімін қадам-қадаммен түсіндіріп беріңіз. 
Шешім қазақ тілінде, математикалық формулалар LaTeX форматында болуы керек.
```

## Example AI Response

```markdown
**Шешімі:**

Бізде екі теңдеу бар:
1. $x + y = 10$
2. $x - y = 2$

**Қадам 1:** Екі теңдеуді қосамыз
$(x + y) + (x - y) = 10 + 2$
$2x = 12$
$x = 6$

**Қадам 2:** $x = 6$ мәнін бірінші теңдеуге қойып, $y$ табамыз
$6 + y = 10$
$y = 4$

**Жауабы:** $x = 6$, $y = 4$
```

## Implementation Details

### Files Modified/Created

1. **bot/database.py**
   - Added migration for AI solution columns
   - Added functions: `update_ai_solution()`, `approve_ai_solution()`, `reject_ai_solution()`, `get_ai_solution_status()`

2. **bot/ai_service.py** (NEW)
   - OpenAI API integration
   - Prompt building logic
   - Error handling for API failures

3. **bot/main.py**
   - Added AI solution admin endpoints
   - Updated solution display logic (Telegram bot and API)
   - Prioritized AI solutions in response

4. **bot/requirements.txt**
   - No additional dependencies needed (aiohttp already included via aiogram)

## Testing

### Manual Testing Steps

1. **Setup**:
   ```bash
   export OPENAI_API_KEY=sk-...
   cd bot
   python main.py
   ```

2. **Request AI Solution**:
   ```bash
   curl -X POST http://localhost:8000/api/admin/tasks/1/ai-solution \
     -H "X-Admin-Email: admin@example.com"
   ```

3. **Approve Solution**:
   ```bash
   curl -X POST http://localhost:8000/api/admin/tasks/1/ai-solution/approve \
     -H "X-Admin-Email: admin@example.com"
   ```

4. **View in API**:
   ```bash
   curl http://localhost:8000/api/task/random?email=user@example.com
   ```

### Automated Tests

Database workflow test included in implementation (see commit).

## Security Considerations

- ✅ Admin-only endpoints protected by email verification
- ✅ OpenAI API key stored in environment variable (not in code)
- ✅ Input validation on all endpoints
- ✅ Error handling for API failures
- ✅ No sensitive data in AI prompts (only task content)

## Cost Optimization

- ✅ Solutions cached after approval (no repeated API calls)
- ✅ Uses cost-effective model by default (gpt-4o-mini)
- ✅ Admin reviews prevent showing poor-quality solutions
- ✅ Retry mechanism minimizes wasted generations

## Future Enhancements

- [ ] Add support for multiple languages
- [ ] Track AI solution quality metrics
- [ ] A/B testing for AI vs manual solutions
- [ ] Batch generation for multiple tasks
- [ ] Solution improvement suggestions
- [ ] Integration with other AI providers (Claude, Gemini)

## Troubleshooting

### Error: "OPENAI_API_KEY environment variable is not set"
**Solution**: Set the environment variable:
```bash
export OPENAI_API_KEY=sk-...
```

### Error: "OpenAI API error (status 429)"
**Solution**: Rate limit exceeded. Wait a few minutes or upgrade OpenAI plan.

### Error: "No solution generated by AI"
**Solution**: Check API response in logs. May need to adjust prompt or model.

### AI generates solution in wrong language
**Solution**: The system prompt forces Kazakh. Check if using correct model version.

## Support

For issues or questions:
- Open an issue in the GitHub repository
- Check OpenAI API status: https://status.openai.com/
- Review server logs for detailed error messages
