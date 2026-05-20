# Discord Bot Setup Guide

## 🤖 Overview

This Discord bot connects to your AI backend API and provides instant AI chat functionality in Discord!

## ✨ Features

- **!ask** - Quick AI responses without memory
- **!chat** - Conversation with memory (per user)
- **!stream** - Real-time streaming responses
- **!memory** - View your conversation history
- **!clear** - Clear your saved conversations
- **!health** - Check if API is online
- **!help** - Show all commands

## 🚀 Setup Steps

### Step 1: Create Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click **New Application**
3. Name it (e.g., "AI Bot")
4. Go to **Bot** section
5. Click **Add Bot**
6. Under **TOKEN**, click **Copy**
7. Save this token safely! ⚠️

### Step 2: Configure Bot Permissions

1. In Developer Portal, go to **OAuth2** → **URL Generator**
2. Select scopes:
   - ✅ `bot`
3. Select permissions:
   - ✅ `Send Messages`
   - ✅ `Read Messages/View Channels`
   - ✅ `Read Message History`
4. Copy the generated URL
5. Open it in browser and authorize the bot to your server

### Step 3: Deploy on Railway

1. Create new Railway project
2. Add this `discord_bot.py` file
3. Add environment variables:
   ```
   DISCORD_TOKEN = your_token_here
   AI_API_URL = https://bbytota87.duckdns.org
   ```
4. Update `requirements.txt` with discord.py
5. Start command: `python discord_bot.py`
6. Deploy ✅

## 📱 Usage Examples

### Quick Question
```
!ask What is Python?
```
Response: Instant answer without saving history

### Chat with Memory
```
!chat Tell me about AI
!chat What did we just talk about?
```
Response: Bot remembers previous messages

### View History
```
!memory
```
Response: Shows your last 10 messages

### Real-time Response
```
!stream Write a poem about coding
```
Response: Streams response word-by-word

## 🔧 Configuration

### Environment Variables

| Variable | Required | Value |
|----------|----------|-------|
| `DISCORD_TOKEN` | ✅ Yes | Your bot token |
| `AI_API_URL` | ✅ Yes | `https://bbytota87.duckdns.org` |

### .env File (Local Testing)

```
DISCORD_TOKEN=your_token_here
AI_API_URL=https://bbytota87.duckdns.org
```

## 🧪 Testing Locally

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create `.env` file with your token

3. Run bot:
   ```bash
   python discord_bot.py
   ```

4. In Discord, test commands:
   ```
   !health
   !ask Hello
   !help
   ```

## 🐛 Troubleshooting

### Bot doesn't show up in Discord
- Check you authorized it with correct permissions
- Ensure token is correct

### "Cannot reach API" error
- Check `AI_API_URL` is correct
- Verify your AI backend is running on Railway
- Check API key is set in Railway variables

### Bot is offline
- Check Railway logs
- Verify `DISCORD_TOKEN` is set in Railway variables
- Make sure bot process is running

### Commands not working
- Use `!help` to see all commands
- Check Discord server permissions
- Verify bot has message permissions

## 📊 Command Details

### !ask `<prompt>`
- Quick one-off questions
- No conversation history saved
- Best for simple queries

### !chat `<prompt>`
- Maintains conversation per user
- Bot remembers context
- Best for multi-turn conversations

### !stream `<prompt>`
- Real-time token streaming
- Faster perceived response
- Best for long responses

### !memory
- Shows your last 10 messages
- Displays conversation ID
- Helps debug conversation state

### !clear
- Deletes your conversation history
- Starts fresh next time
- Only clears your data

### !health
- Checks if API is responding
- Shows API version
- Shows last update time

## 🔒 Security

- ⚠️ Never share your `DISCORD_TOKEN`
- Use Railway Variables (never commit to GitHub)
- Bot only stores conversation in memory
- Conversations cleared when bot restarts

## 📈 Advanced Usage

### Multiple Servers
Bot works on multiple Discord servers simultaneously

### User Isolation
Each user has separate conversation memory

### Error Handling
Bot gracefully handles API errors and timeouts

## 🆘 Support

- Check logs in Railway dashboard
- Verify API is running: `https://bbytota87.duckdns.org/health`
- Review [discord.py docs](https://discordpy.readthedocs.io)
- Check [OpenAI docs](https://platform.openai.com/docs)

---

**Your Discord bot is ready!** 🎉
