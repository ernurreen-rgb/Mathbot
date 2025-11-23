# Telegram Login Configuration

## Requirements for Telegram Login to Work

The Telegram Login Widget has specific requirements that must be met for it to function correctly:

### 1. Bot Domain Registration
You **must** register your domain with the Telegram bot using BotFather:

1. Open Telegram and start a chat with [@BotFather](https://t.me/BotFather)
2. Send the command `/setdomain`
3. Select your bot (`@yeramathbot`)
4. Enter your domain (e.g., `yourdomain.com` or `subdomain.yourdomain.com`)

**Important**: 
- Do NOT include `https://` or `http://` in the domain
- Do NOT include paths (like `/login`)
- Only the domain itself (e.g., `example.com`)

### 2. Public Domain Required
The Telegram Login Widget **does not work on localhost**. You need:
- A publicly accessible domain
- The domain must match what you registered with BotFather

For development testing:
- Use a tunneling service like [ngrok](https://ngrok.com/) or [localhost.run](https://localhost.run/)
- Register the tunnel domain with BotFather
- Remember to update the domain in BotFather when your tunnel URL changes

### 3. HTTPS in Production
In production, your site should be served over HTTPS. Most hosting providers (Vercel, Netlify, etc.) provide this automatically.

### 4. Environment Variables
Make sure the `BOT_TOKEN` environment variable is set:

**Development (.env.local)**:
```
BOT_TOKEN=your_bot_token_here
```

**Production (Vercel/hosting provider)**:
Set the `BOT_TOKEN` environment variable in your hosting provider's dashboard.

## Debugging

If login still doesn't work:

1. **Check Browser Console**: Open browser DevTools (F12) and check the Console tab for error messages. Look for messages starting with `[Telegram Widget]` or `[Telegram Auth]`.

2. **Verify Bot Configuration**:
   - Ensure the bot token is correct
   - Confirm the domain is registered with BotFather
   - Check that you're using the correct bot username in the code (`yeramathbot`)

3. **Check Network Tab**: In browser DevTools, check the Network tab to see:
   - Is the Telegram widget script loading? (telegram-widget.js)
   - Are there any CORS errors?
   - Does the POST request to `/login/telegram` succeed?

4. **Test on Production Domain**: Remember that the widget doesn't work on localhost. Test on your actual deployed site.

## Common Issues

### "Widget doesn't appear"
- Check if the telegram-widget.js script loaded successfully
- Verify the container div with id "tg-login" exists
- Check browser console for errors

### "Widget appears but clicking does nothing"
- Domain not registered with BotFather
- Testing on localhost instead of public domain
- Check browser console for callback errors

### "Authentication succeeds but backend returns error"
- BOT_TOKEN environment variable not set
- BOT_TOKEN is incorrect
- Hash verification failing (check server logs)

## Testing Checklist

- [ ] Bot domain registered with BotFather (`/setdomain`)
- [ ] Testing on public domain (not localhost)
- [ ] BOT_TOKEN environment variable set correctly
- [ ] Site accessible over HTTPS (in production)
- [ ] Browser console shows no errors
- [ ] Telegram widget appears on the page
