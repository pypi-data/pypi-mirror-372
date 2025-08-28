# Anzar SDK Documentation

## Installation

```bash
pip install anzar
```

## Quick Start

```python
from anzar import AnzarAuth

# Initialize the SDK
auth = AnzarAuth

# Use the authenticated client
# (Add specific usage examples here)
```

## Configuration

### Environment Variables

Create a `.env` file in your project root:

```env
# Add your environment variables here
ANZAR_API_KEY=your_api_key
ANZAR_BASE_URL=https://api.anzar.com
```

## API Reference

### AnzarAuth

Authentication manager for user login, registration, and session management.

```python
from anzar import AnzarAuth
```

#### Methods

##### `login(email, password)`

Authenticate a user with credentials.

**Parameters:**
- `email` (str): User's email
- `password` (str): User's password

**Returns:**
- `User`: User object on success
- `Error`: Error object on failure

**Example:**
```python
result = AnzarAuth.login("user@example.com", "password123")
if isinstance(result, User):
    print(f"Logged in: {result.username}")
else:
    print(f"Login failed: {result.error}")
```

##### `register(username, email, password)`

Register a new user account.

**Parameters:**
- `username` (str): Desired username
- `email` (str): User's email address
- `password` (str): User's password

**Returns:**
- `User`: User object on success
- `Error`: Error object on failure

**Example:**
```python
result = AnzarAuth.register("newuser", "user@example.com", "password123")
```

##### `logout()`

Log out the current user.

**Returns:**
- `User`: Empty user object on success
- `Error`: Error object on failure

**Example:**
```python
result = AnzarAuth.logout()
```

##### `isLoggedIn()`

Check if a user is currently logged in.

**Returns:**
- `User`: Current user object if logged in
- `Error`: Error object if not logged in

**Example:**
```python
result = AnzarAuth.isLoggedIn()
if isinstance(result, User):
    print(f"Current user: {result.username}")
else:
    print("No user logged in")
```

## Error Handling

```python
from anzar.types import Error
try:
    result = AnzarAuth.login(email, password)
except Error as e:
    print(f"Error: {e}")
```

## Examples

### Basic Authentication Flow

```python
from anzar import AnzarAuth

# Register new user
result = AnzarAuth.register("johndoe", "john@example.com", "securepass123")
if isinstance(result, Error):
    print(f"Registration failed: {result.message}")
    return

# Login
result = AnzarAuth.login("john@example.com", "securepass123")
if isinstance(result, Error):
    print(f"Login failed: {result.message}")
    return

print(f"Welcome {result.username}")

# Check login status
user = AnzarAuth.isLoggedIn()
if not isinstance(user, Error):
    print(f"Current user: {user.username}")

# Logout
AnzarAuth.logout()
```

## Contributing

Instructions for contributing to the SDK.

## License

License information.
