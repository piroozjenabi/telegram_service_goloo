# API Usage Examples

Complete examples for interacting with the Dynamic Telegram Bot Maker API.

## Base URL

```
Development: http://localhost:8000
Production: https://yourdomain.com
```

## Authentication

Currently, the API is open. For production, consider adding authentication:
- API Keys
- JWT Tokens
- OAuth2

## API Endpoints

### 1. Create a Bot

**Endpoint:** `POST /api/bots`

**Request:**
```bash
curl -X POST http://localhost:8000/api/bots \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Awesome Bot",
    "token": "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
  }'
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "My Awesome Bot",
  "username": "my_awesome_bot",
  "user_count": 0,
  "request_count": 0,
  "is_webhook_set": false,
  "webhook_url": null,
  "is_active": true
}
```

**Python Example:**
```python
import requests

response = requests.post(
    'http://localhost:8000/api/bots',
    json={
        'name': 'My Awesome Bot',
        'token': '1234567890:ABCdefGHIjklMNOpqrsTUVwxyz'
    }
)

bot = response.json()
print(f"Bot created with ID: {bot['id']}")
```

**JavaScript Example:**
```javascript
fetch('http://localhost:8000/api/bots', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    name: 'My Awesome Bot',
    token: '1234567890:ABCdefGHIjklMNOpqrsTUVwxyz'
  })
})
.then(response => response.json())
.then(bot => console.log('Bot created:', bot.id));
```

---

### 2. List All Bots

**Endpoint:** `GET /api/bots`

**Request:**
```bash
curl http://localhost:8000/api/bots
```

**Response:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "My Awesome Bot",
    "username": "my_awesome_bot",
    "user_count": 42,
    "request_count": 1337,
    "is_webhook_set": true,
    "webhook_url": "https://yourdomain.com/api/webhook/550e8400-e29b-41d4-a716-446655440000",
    "is_active": true
  },
  {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "name": "Another Bot",
    "username": "another_bot",
    "user_count": 15,
    "request_count": 234,
    "is_webhook_set": true,
    "webhook_url": "https://yourdomain.com/api/webhook/660e8400-e29b-41d4-a716-446655440001",
    "is_active": true
  }
]
```

**Python Example:**
```python
import requests

response = requests.get('http://localhost:8000/api/bots')
bots = response.json()

for bot in bots:
    print(f"{bot['name']}: {bot['user_count']} users, {bot['request_count']} requests")
```

---

### 3. Get Bot Details

**Endpoint:** `GET /api/bots/{bot_id}`

**Request:**
```bash
curl http://localhost:8000/api/bots/550e8400-e29b-41d4-a716-446655440000
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "My Awesome Bot",
  "username": "my_awesome_bot",
  "user_count": 42,
  "request_count": 1337,
  "is_webhook_set": true,
  "webhook_url": "https://yourdomain.com/api/webhook/550e8400-e29b-41d4-a716-446655440000",
  "is_active": true
}
```

---

### 4. Setup Webhook

**Endpoint:** `POST /api/bots/{bot_id}/webhook`

**Request:**
```bash
curl -X POST http://localhost:8000/api/bots/550e8400-e29b-41d4-a716-446655440000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "webhook_url": "https://yourdomain.com"
  }'
```

**Response:**
```json
{
  "success": true,
  "webhook_url": "https://yourdomain.com/api/webhook/550e8400-e29b-41d4-a716-446655440000"
}
```

**Python Example:**
```python
import requests

bot_id = "550e8400-e29b-41d4-a716-446655440000"
response = requests.post(
    f'http://localhost:8000/api/bots/{bot_id}/webhook',
    json={'webhook_url': 'https://yourdomain.com'}
)

result = response.json()
if result['success']:
    print(f"Webhook set: {result['webhook_url']}")
```

**With ngrok (Local Testing):**
```bash
# Terminal 1: Start ngrok
ngrok http 8000

# Terminal 2: Setup webhook with ngrok URL
BOT_ID="550e8400-e29b-41d4-a716-446655440000"
NGROK_URL="https://abc123.ngrok.io"

curl -X POST http://localhost:8000/api/bots/$BOT_ID/webhook \
  -H "Content-Type: application/json" \
  -d "{\"webhook_url\": \"$NGROK_URL\"}"
```

---

### 5. Delete Webhook

**Endpoint:** `DELETE /api/bots/{bot_id}/webhook`

**Request:**
```bash
curl -X DELETE http://localhost:8000/api/bots/550e8400-e29b-41d4-a716-446655440000/webhook
```

**Response:**
```json
{
  "success": true
}
```

**Python Example:**
```python
import requests

bot_id = "550e8400-e29b-41d4-a716-446655440000"
response = requests.delete(
    f'http://localhost:8000/api/bots/{bot_id}/webhook'
)

result = response.json()
if result['success']:
    print("Webhook removed successfully")
```

---

### 6. Get Bot Statistics

**Endpoint:** `GET /api/bots/{bot_id}/stats`

**Request:**
```bash
curl http://localhost:8000/api/bots/550e8400-e29b-41d4-a716-446655440000/stats
```

**Response:**
```json
{
  "bot_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_count": 42,
  "request_count": 1337,
  "total_messages": 2500,
  "incoming_messages": 1337,
  "outgoing_messages": 1163
}
```

**Python Example:**
```python
import requests

bot_id = "550e8400-e29b-41d4-a716-446655440000"
response = requests.get(
    f'http://localhost:8000/api/bots/{bot_id}/stats'
)

stats = response.json()
print(f"Bot Statistics:")
print(f"  Users: {stats['user_count']}")
print(f"  Requests: {stats['request_count']}")
print(f"  Messages: {stats['total_messages']}")
print(f"  Incoming: {stats['incoming_messages']}")
print(f"  Outgoing: {stats['outgoing_messages']}")
```

---

## Complete Python Script Example

```python
#!/usr/bin/env python3
"""
Complete example of using the Telegram Bot Maker API
"""
import requests
import time

BASE_URL = "http://localhost:8000"

def create_bot(name, token):
    """Create a new bot"""
    response = requests.post(
        f"{BASE_URL}/api/bots",
        json={"name": name, "token": token}
    )
    return response.json()

def list_bots():
    """List all bots"""
    response = requests.get(f"{BASE_URL}/api/bots")
    return response.json()

def get_bot(bot_id):
    """Get bot details"""
    response = requests.get(f"{BASE_URL}/api/bots/{bot_id}")
    return response.json()

def setup_webhook(bot_id, webhook_url):
    """Setup webhook for a bot"""
    response = requests.post(
        f"{BASE_URL}/api/bots/{bot_id}/webhook",
        json={"webhook_url": webhook_url}
    )
    return response.json()

def delete_webhook(bot_id):
    """Delete webhook for a bot"""
    response = requests.delete(f"{BASE_URL}/api/bots/{bot_id}/webhook")
    return response.json()

def get_stats(bot_id):
    """Get bot statistics"""
    response = requests.get(f"{BASE_URL}/api/bots/{bot_id}/stats")
    return response.json()

def main():
    # Create a bot
    print("Creating bot...")
    bot = create_bot(
        name="Test Bot",
        token="YOUR_BOT_TOKEN_HERE"
    )
    print(f"✓ Bot created: {bot['id']}")
    
    bot_id = bot['id']
    
    # List all bots
    print("\nListing all bots...")
    bots = list_bots()
    print(f"✓ Found {len(bots)} bot(s)")
    
    # Get bot details
    print("\nGetting bot details...")
    bot_details = get_bot(bot_id)
    print(f"✓ Bot: {bot_details['name']} (@{bot_details['username']})")
    
    # Setup webhook
    print("\nSetting up webhook...")
    webhook_result = setup_webhook(bot_id, "https://yourdomain.com")
    if webhook_result['success']:
        print(f"✓ Webhook set: {webhook_result['webhook_url']}")
    
    # Wait a bit
    time.sleep(2)
    
    # Get statistics
    print("\nGetting statistics...")
    stats = get_stats(bot_id)
    print(f"✓ Users: {stats['user_count']}")
    print(f"✓ Requests: {stats['request_count']}")
    print(f"✓ Messages: {stats['total_messages']}")
    
    # Delete webhook
    print("\nDeleting webhook...")
    delete_result = delete_webhook(bot_id)
    if delete_result['success']:
        print("✓ Webhook deleted")
    
    print("\n✅ All operations completed successfully!")

if __name__ == "__main__":
    main()
```

---

## Complete JavaScript Example

```javascript
// Complete example using fetch API
const BASE_URL = 'http://localhost:8000';

// Create a bot
async function createBot(name, token) {
  const response = await fetch(`${BASE_URL}/api/bots`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, token })
  });
  return response.json();
}

// List all bots
async function listBots() {
  const response = await fetch(`${BASE_URL}/api/bots`);
  return response.json();
}

// Get bot details
async function getBot(botId) {
  const response = await fetch(`${BASE_URL}/api/bots/${botId}`);
  return response.json();
}

// Setup webhook
async function setupWebhook(botId, webhookUrl) {
  const response = await fetch(`${BASE_URL}/api/bots/${botId}/webhook`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ webhook_url: webhookUrl })
  });
  return response.json();
}

// Delete webhook
async function deleteWebhook(botId) {
  const response = await fetch(`${BASE_URL}/api/bots/${botId}/webhook`, {
    method: 'DELETE'
  });
  return response.json();
}

// Get statistics
async function getStats(botId) {
  const response = await fetch(`${BASE_URL}/api/bots/${botId}/stats`);
  return response.json();
}

// Main function
async function main() {
  try {
    // Create bot
    console.log('Creating bot...');
    const bot = await createBot('Test Bot', 'YOUR_BOT_TOKEN_HERE');
    console.log('✓ Bot created:', bot.id);
    
    const botId = bot.id;
    
    // List bots
    console.log('\nListing all bots...');
    const bots = await listBots();
    console.log(`✓ Found ${bots.length} bot(s)`);
    
    // Get bot details
    console.log('\nGetting bot details...');
    const botDetails = await getBot(botId);
    console.log(`✓ Bot: ${botDetails.name} (@${botDetails.username})`);
    
    // Setup webhook
    console.log('\nSetting up webhook...');
    const webhookResult = await setupWebhook(botId, 'https://yourdomain.com');
    if (webhookResult.success) {
      console.log(`✓ Webhook set: ${webhookResult.webhook_url}`);
    }
    
    // Get statistics
    console.log('\nGetting statistics...');
    const stats = await getStats(botId);
    console.log(`✓ Users: ${stats.user_count}`);
    console.log(`✓ Requests: ${stats.request_count}`);
    console.log(`✓ Messages: ${stats.total_messages}`);
    
    // Delete webhook
    console.log('\nDeleting webhook...');
    const deleteResult = await deleteWebhook(botId);
    if (deleteResult.success) {
      console.log('✓ Webhook deleted');
    }
    
    console.log('\n✅ All operations completed successfully!');
    
  } catch (error) {
    console.error('Error:', error);
  }
}

// Run
main();
```

---

## Error Handling

### Common Error Responses

**Invalid Bot Token:**
```json
{
  "error": "Invalid bot token"
}
```

**Bot Not Found:**
```json
{
  "detail": "Not found"
}
```

**Webhook Setup Failed:**
```json
{
  "error": "Failed to set webhook: URL must be HTTPS"
}
```

### Python Error Handling Example:
```python
import requests

try:
    response = requests.post(
        'http://localhost:8000/api/bots',
        json={'name': 'Test', 'token': 'invalid_token'}
    )
    response.raise_for_status()
    bot = response.json()
except requests.exceptions.HTTPError as e:
    print(f"HTTP Error: {e}")
    print(f"Response: {e.response.json()}")
except requests.exceptions.RequestException as e:
    print(f"Request Error: {e}")
```

---

## Rate Limiting (Future)

Consider implementing rate limiting in production:

```python
# Example rate limit headers (to be implemented)
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640000000
```

---

## Webhook Payload Example

When Telegram sends updates to your webhook:

**Incoming Webhook Payload:**
```json
{
  "update_id": 123456789,
  "message": {
    "message_id": 1,
    "from": {
      "id": 987654321,
      "is_bot": false,
      "first_name": "John",
      "last_name": "Doe",
      "username": "johndoe",
      "language_code": "en"
    },
    "chat": {
      "id": 987654321,
      "first_name": "John",
      "last_name": "Doe",
      "username": "johndoe",
      "type": "private"
    },
    "date": 1640000000,
    "text": "/start"
  }
}
```

This payload is automatically processed by the system and:
1. User is created/updated in database
2. Message is saved
3. Flow is matched and executed
4. Response is sent back to user

---

## Testing with curl

### Complete Test Sequence:
```bash
# 1. Create bot
BOT_RESPONSE=$(curl -s -X POST http://localhost:8000/api/bots \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Bot", "token": "YOUR_TOKEN"}')

BOT_ID=$(echo $BOT_RESPONSE | jq -r '.id')
echo "Bot ID: $BOT_ID"

# 2. List bots
curl -s http://localhost:8000/api/bots | jq

# 3. Get bot details
curl -s http://localhost:8000/api/bots/$BOT_ID | jq

# 4. Setup webhook
curl -s -X POST http://localhost:8000/api/bots/$BOT_ID/webhook \
  -H "Content-Type: application/json" \
  -d '{"webhook_url": "https://yourdomain.com"}' | jq

# 5. Get stats
curl -s http://localhost:8000/api/bots/$BOT_ID/stats | jq

# 6. Delete webhook
curl -s -X DELETE http://localhost:8000/api/bots/$BOT_ID/webhook | jq
```
