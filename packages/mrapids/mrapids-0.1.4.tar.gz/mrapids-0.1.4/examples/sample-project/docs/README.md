# API Documentation

## Overview
This REST API provides endpoints for managing users and related resources.

## Quick Start

### Install MicroRapid
```bash
npm install -g mrapids
```

### Run Operations
```bash
# List all users
mrapids run --operation listUsers

# Get specific user
mrapids run --operation getUser --param id=1

# Generate SDK
mrapids generate --language typescript

# Set up test scripts
mrapids setup-tests --format npm
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /users | List all users |
| POST | /users | Create new user |
| GET | /users/{id} | Get user by ID |
| PUT | /users/{id} | Update user |
| DELETE | /users/{id} | Delete user |

## Testing

Run all tests:
```bash
npm test
```

## Environment Configuration

Copy `.env.example` to `.env.local` and configure:
```bash
cp config/.env.example config/.env.local
```
