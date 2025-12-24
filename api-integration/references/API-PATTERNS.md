# API Integration Design Patterns

## Client Architecture Patterns

### 1. Resource-Based Client

Organize API methods around resources:

```python
class APIClient:
    def __init__(self, base_url, auth):
        self.base_url = base_url
        self.auth = auth
        self.users = UserResource(self)
        self.posts = PostResource(self)
        self.comments = CommentResource(self)

class UserResource:
    def __init__(self, client):
        self.client = client
    
    def list(self, **params):
        return self.client._request('GET', '/users', params=params)
    
    def get(self, user_id):
        return self.client._request('GET', f'/users/{user_id}')
    
    def create(self, data):
        return self.client._request('POST', '/users', json=data)
    
    def update(self, user_id, data):
        return self.client._request('PUT', f'/users/{user_id}', json=data)
    
    def delete(self, user_id):
        return self.client._request('DELETE', f'/users/{user_id}')

# Usage
client = APIClient('https://api.example.com', auth_token)
user = client.users.get(123)
```

### 2. Fluent Interface Pattern

Chain methods for readability:

```python
class APIQuery:
    def __init__(self, client, resource):
        self.client = client
        self.resource = resource
        self.filters = {}
        self.sort_by = None
        self.page_size = 20
    
    def filter(self, **kwargs):
        self.filters.update(kwargs)
        return self
    
    def sort(self, field):
        self.sort_by = field
        return self
    
    def limit(self, count):
        self.page_size = count
        return self
    
    def execute(self):
        params = {
            **self.filters,
            'sort': self.sort_by,
            'limit': self.page_size
        }
        return self.client._request('GET', f'/{self.resource}', params=params)

# Usage
users = (client.query('users')
    .filter(status='active', role='admin')
    .sort('created_at')
    .limit(50)
    .execute())
```

### 3. Builder Pattern

For complex API requests:

```python
class RequestBuilder:
    def __init__(self, client):
        self.client = client
        self.method = 'GET'
        self.endpoint = ''
        self.headers = {}
        self.params = {}
        self.data = None
    
    def get(self, endpoint):
        self.method = 'GET'
        self.endpoint = endpoint
        return self
    
    def post(self, endpoint):
        self.method = 'POST'
        self.endpoint = endpoint
        return self
    
    def with_headers(self, headers):
        self.headers.update(headers)
        return self
    
    def with_params(self, params):
        self.params.update(params)
        return self
    
    def with_body(self, data):
        self.data = data
        return self
    
    def execute(self):
        return self.client._request(
            self.method,
            self.endpoint,
            headers=self.headers,
            params=self.params,
            json=self.data
        )

# Usage
response = (RequestBuilder(client)
    .post('/users')
    .with_headers({'X-Custom-Header': 'value'})
    .with_body({'name': 'John', 'email': 'john@example.com'})
    .execute())
```

## Error Handling Patterns

### 1. Circuit Breaker

Prevent cascading failures:

```python
from enum import Enum
from datetime import datetime, timedelta

class CircuitState(Enum):
    CLOSED = 1  # Normal operation
    OPEN = 2    # Failing, reject requests
    HALF_OPEN = 3  # Testing recovery

class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    def call(self, func, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise CircuitBreakerOpenError("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _should_attempt_reset(self):
        return (datetime.now() - self.last_failure_time).seconds >= self.timeout
    
    def _on_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
```

### 2. Retry with Exponential Backoff

```python
import time
from typing import Callable, Type

def exponential_backoff_retry(
    max_retries: int = 3,
    base_delay: float = 1,
    max_delay: float = 60,
    exceptions: tuple = (Exception,)
):
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            delay = base_delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries:
                        raise
                    
                    # Add jitter to prevent thundering herd
                    jitter = random.uniform(0, 0.1 * delay)
                    sleep_time = min(delay + jitter, max_delay)
                    
                    logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {sleep_time:.2f}s")
                    time.sleep(sleep_time)
                    
                    delay *= 2  # Exponential increase
            
        return wrapper
    return decorator
```

## Authentication Patterns

### 1. Token Refresh

```python
from datetime import datetime, timedelta
from threading import Lock

class TokenManager:
    def __init__(self, auth_url, client_id, client_secret):
        self.auth_url = auth_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.refresh_token = None
        self.expires_at = None
        self.lock = Lock()
    
    def get_access_token(self):
        with self.lock:
            if self._is_token_expired():
                self._refresh_access_token()
            return self.access_token
    
    def _is_token_expired(self):
        if not self.expires_at:
            return True
        # Refresh 5 minutes before actual expiry
        return datetime.now() >= self.expires_at - timedelta(minutes=5)
    
    def _refresh_access_token(self):
        response = requests.post(
            self.auth_url,
            data={
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }
        )
        data = response.json()
        
        self.access_token = data['access_token']
        self.refresh_token = data.get('refresh_token')
        expires_in = data.get('expires_in', 3600)
        self.expires_at = datetime.now() + timedelta(seconds=expires_in)
```

### 2. API Key Rotation

```python
class RotatingKeyAuth:
    def __init__(self, keys: list):
        self.keys = keys
        self.current_index = 0
        self.failure_counts = {key: 0 for key in keys}
    
    def get_key(self):
        return self.keys[self.current_index]
    
    def rotate(self):
        self.current_index = (self.current_index + 1) % len(self.keys)
    
    def mark_failed(self, key):
        self.failure_counts[key] += 1
        if self.failure_counts[key] >= 3:
            # Remove bad key
            self.keys.remove(key)
```

## Rate Limiting Patterns

### 1. Token Bucket

```python
import time

class TokenBucket:
    def __init__(self, capacity, refill_rate):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_refill = time.time()
    
    def consume(self, tokens=1):
        self._refill()
        
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False
    
    def _refill(self):
        now = time.time()
        elapsed = now - self.last_refill
        new_tokens = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + new_tokens)
        self.last_refill = now
```

### 2. Sliding Window

```python
from collections import deque
import time

class SlidingWindowRateLimiter:
    def __init__(self, max_requests, window_seconds):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = deque()
    
    def allow_request(self):
        now = time.time()
        
        # Remove old requests outside window
        while self.requests and self.requests[0] <= now - self.window_seconds:
            self.requests.popleft()
        
        if len(self.requests) < self.max_requests:
            self.requests.append(now)
            return True
        
        return False
```

## Response Handling Patterns

### 1. Response Wrapper

```python
from typing import Optional, Any
from dataclasses import dataclass

@dataclass
class APIResponse:
    status_code: int
    data: Optional[Any]
    error: Optional[str]
    headers: dict
    
    @property
    def success(self) -> bool:
        return 200 <= self.status_code < 300
    
    @property
    def rate_limit_remaining(self) -> Optional[int]:
        value = self.headers.get('X-RateLimit-Remaining')
        return int(value) if value else None
    
    def raise_for_error(self):
        if not self.success:
            raise APIError(f"HTTP {self.status_code}: {self.error}")

class APIClient:
    def _request(self, method, endpoint, **kwargs) -> APIResponse:
        response = self.session.request(method, url, **kwargs)
        
        try:
            data = response.json()
        except:
            data = response.text
        
        return APIResponse(
            status_code=response.status_code,
            data=data if response.ok else None,
            error=None if response.ok else str(data),
            headers=dict(response.headers)
        )
```

### 2. Data Transformation

```python
from typing import TypeVar, Generic, Callable

T = TypeVar('T')

class APIClient:
    def _request_typed(
        self,
        method: str,
        endpoint: str,
        response_type: Callable[[dict], T],
        **kwargs
    ) -> T:
        """Make request and transform response to typed object."""
        response = self._request(method, endpoint, **kwargs)
        return response_type(response.data)

# Usage with dataclasses
from dataclasses import dataclass

@dataclass
class User:
    id: int
    name: str
    email: str
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data['id'],
            name=data['name'],
            email=data['email']
        )

user = client._request_typed('GET', '/users/1', User.from_dict)
```

## Testing Patterns

### 1. Mock API Server

```python
from unittest.mock import Mock
import pytest

@pytest.fixture
def mock_api():
    mock = Mock()
    mock.base_url = 'https://api.test.com'
    
    def side_effect(*args, **kwargs):
        endpoint = args[1]
        if endpoint == '/users/1':
            return {'id': 1, 'name': 'Test User'}
        raise ValueError(f"Unexpected endpoint: {endpoint}")
    
    mock._request.side_effect = side_effect
    return mock
```

### 2. Request Recording

```python
class RecordingAPIClient(APIClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.recorded_requests = []
    
    def _request(self, method, endpoint, **kwargs):
        self.recorded_requests.append({
            'method': method,
            'endpoint': endpoint,
            'kwargs': kwargs,
            'timestamp': time.time()
        })
        return super()._request(method, endpoint, **kwargs)
```
