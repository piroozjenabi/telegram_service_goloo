# System Architecture Diagram

## High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     TELEGRAM BOT MAKER SYSTEM                    │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│   Telegram   │         │   Admin UI   │         │  REST API    │
│   Platform   │         │   (Unfold)   │         │ (Django Ninja)│
└──────┬───────┘         └──────┬───────┘         └──────┬───────┘
       │                        │                        │
       │ Webhooks               │ Management             │ HTTP
       │                        │                        │
       ▼                        ▼                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                        DJANGO APPLICATION                        │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                      Bot Application                        │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │ │
│  │  │   Models     │  │    Views     │  │    Admin     │    │ │
│  │  │              │  │              │  │              │    │ │
│  │  │ TelegramBot  │  │ API Endpoints│  │ Bot Admin    │    │ │
│  │  │ BotUser      │  │ Webhook      │  │ User Admin   │    │ │
│  │  │ BotFlow      │  │ Handler      │  │ Flow Admin   │    │ │
│  │  │ BotMessage   │  │ Flow Proc.   │  │ Message Admin│    │ │
│  │  └──────┬───────┘  └──────┬───────┘  └──────────────┘    │ │
│  │         │                 │                               │ │
│  └─────────┼─────────────────┼───────────────────────────────┘ │
│            │                 │                                  │
│            ▼                 ▼                                  │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                    Database Layer                        │  │
│  │              (SQLite / PostgreSQL)                       │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Bot Creation Flow
```
Admin/API Request
       │
       ▼
Create TelegramBot
       │
       ├─> Generate UUID
       ├─> Store Token
       ├─> Fetch Bot Info from Telegram
       └─> Save to Database
```

### 2. Webhook Setup Flow
```
Setup Request
       │
       ▼
Construct Webhook URL
  (BASE_URL/api/webhook/{UUID})
       │
       ▼
Call Telegram API
  (setWebhook)
       │
       ▼
Update Bot Record
  (is_webhook_set = True)
```

### 3. Message Processing Flow
```
Telegram → Webhook → Django
                        │
                        ▼
                  Parse Update
                        │
                        ├─> Extract User Data
                        │   └─> Get/Create BotUser
                        │       └─> Update User Count
                        │
                        ├─> Extract Message Data
                        │   └─> Save BotMessage
                        │       └─> Increment Request Count
                        │
                        └─> Process Flow
                            ├─> Match Command/Default
                            ├─> Execute Flow Logic
                            └─> Send Response
                                └─> Save Outgoing Message
```

## Database Schema

```
┌─────────────────────────────────────────────────────────────┐
│                      TelegramBot                             │
├─────────────────────────────────────────────────────────────┤
│ id (UUID, PK)                                               │
│ name (str)                                                  │
│ token (str, unique)                                         │
│ username (str)                                              │
│ user_count (int)                                            │
│ request_count (int)                                         │
│ is_webhook_set (bool)                                       │
│ webhook_url (url)                                           │
│ is_active (bool)                                            │
│ created_at, updated_at                                      │
└────────────┬────────────────────────────────────────────────┘
             │
             │ 1:N
             │
    ┌────────┴────────┬────────────────┬──────────────┐
    │                 │                │              │
    ▼                 ▼                ▼              ▼
┌─────────┐    ┌──────────┐    ┌──────────┐   ┌──────────┐
│ BotUser │    │ BotFlow  │    │BotMessage│   │BotMessage│
├─────────┤    ├──────────┤    ├──────────┤   ├──────────┤
│ bot_id  │    │ bot_id   │    │ bot_id   │   │ bot_id   │
│ chat_id │    │ name     │    │ user_id  │   │ user_id  │
│username │    │flow_data │    │ type     │   │ type     │
│first_   │    │trigger_  │    │direction │   │direction │
│ name    │    │ command  │    │ text     │   │ text     │
│last_    │    │is_default│    │file_url  │   │file_url  │
│ name    │    │is_active │    │flow_id   │   │flow_id   │
│language │    │created_at│    │created_at│   │created_at│
│phone    │    │updated_at│    └──────────┘   └──────────┘
│bio      │    └──────────┘         ▲              ▲
│profile_ │                          │              │
│ photo   │                          └──────┬───────┘
│is_      │                                 │
│ blocked │                            Incoming  Outgoing
│is_active│                            Messages  Messages
│first_   │
│interact │
│last_    │
│interact │
└─────────┘
```

## API Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      API Endpoints                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Bot Management                                              │
│  ├─ POST   /api/bots              Create Bot                │
│  ├─ GET    /api/bots              List Bots                 │
│  ├─ GET    /api/bots/{id}         Get Bot                   │
│  ├─ POST   /api/bots/{id}/webhook Setup Webhook             │
│  ├─ DELETE /api/bots/{id}/webhook Remove Webhook            │
│  └─ GET    /api/bots/{id}/stats   Get Statistics            │
│                                                              │
│  Webhook Handler                                             │
│  └─ POST   /api/webhook/{bot_id}  Receive Updates           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Flow Processing Engine

```
┌─────────────────────────────────────────────────────────────┐
│                   Flow Processing Logic                      │
└─────────────────────────────────────────────────────────────┘

Incoming Message
       │
       ▼
┌──────────────┐
│ Extract Text │
└──────┬───────┘
       │
       ▼
┌──────────────────┐      Yes    ┌─────────────────┐
│ Is Command?      │─────────────>│ Match Command   │
│ (starts with /)  │              │ Trigger         │
└──────┬───────────┘              └────────┬────────┘
       │ No                                │
       │                                   │
       ▼                                   ▼
┌──────────────────┐              ┌─────────────────┐
│ Get Default Flow │              │ Get Flow by     │
│                  │              │ Command         │
└──────┬───────────┘              └────────┬────────┘
       │                                   │
       └───────────────┬───────────────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Execute Flow    │
              │                 │
              │ Parse flow_data │
              │ Generate Response│
              │ Send to User    │
              │ Save Message    │
              └─────────────────┘
```

## Flow Types

```
┌─────────────────────────────────────────────────────────────┐
│                      Flow Types                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Simple Response                                          │
│     {                                                        │
│       "response": "Hello World"                              │
│     }                                                        │
│                                                              │
│  2. Multi-Step Flow                                          │
│     {                                                        │
│       "steps": [                                             │
│         {"id": "step1", "type": "message", ...},            │
│         {"id": "step2", "type": "question", ...}            │
│       ],                                                     │
│       "initial_step": "step1"                                │
│     }                                                        │
│                                                              │
│  3. Menu Flow                                                │
│     {                                                        │
│       "type": "menu",                                        │
│       "text": "Choose option",                               │
│       "buttons": [...]                                       │
│     }                                                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Production Setup                          │
└─────────────────────────────────────────────────────────────┘

Internet
   │
   ▼
┌──────────────┐
│ Load Balancer│
│   (HTTPS)    │
└──────┬───────┘
       │
       ├─────────────┬─────────────┐
       │             │             │
       ▼             ▼             ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│ Django   │  │ Django   │  │ Django   │
│ Instance │  │ Instance │  │ Instance │
│    1     │  │    2     │  │    3     │
└────┬─────┘  └────┬─────┘  └────┬─────┘
     │             │             │
     └─────────────┼─────────────┘
                   │
                   ▼
          ┌────────────────┐
          │   PostgreSQL   │
          │    Database    │
          └────────────────┘
                   │
                   ▼
          ┌────────────────┐
          │  Redis Cache   │
          │   (Optional)   │
          └────────────────┘
```

## Security Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    Security Features                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. UUID-Based Webhook URLs                                  │
│     └─> Hard to guess, unique per bot                       │
│                                                              │
│  2. Token Security                                           │
│     └─> Stored securely, never exposed in API               │
│                                                              │
│  3. CSRF Protection                                          │
│     └─> Django built-in protection                          │
│                                                              │
│  4. Admin Authentication                                     │
│     └─> Required for all admin operations                   │
│                                                              │
│  5. HTTPS Required                                           │
│     └─> Telegram webhooks require HTTPS                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Performance Optimizations

```
┌─────────────────────────────────────────────────────────────┐
│                  Performance Features                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ✓ Async/Await for Telegram API calls                       │
│  ✓ Webhook-based (no polling overhead)                      │
│  ✓ Database indexing on frequently queried fields           │
│  ✓ Efficient ORM queries with select_related                │
│  ✓ Request counting without extra queries                   │
│  ✓ JSON field for flexible flow storage                     │
│  ✓ Unique constraints to prevent duplicates                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```
