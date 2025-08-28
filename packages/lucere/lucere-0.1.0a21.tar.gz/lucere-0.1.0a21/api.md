# Models

Methods:

- <code title="get /models">client.models.<a href="./src/lucere/resources/models.py">list</a>() -> object</code>

# Chat

## Completions

Methods:

- <code title="post /chat/completions">client.chat.completions.<a href="./src/lucere/resources/chat/completions.py">create</a>(\*\*<a href="src/lucere/types/chat/completion_create_params.py">params</a>) -> object</code>
- <code title="post /chat/completions/test">client.chat.completions.<a href="./src/lucere/resources/chat/completions.py">test</a>() -> object</code>

# Token

Types:

```python
from lucere.types import TokenResponse, VerifyResponse
```

Methods:

- <code title="post /generate-token">client.token.<a href="./src/lucere/resources/token.py">generate</a>(\*\*<a href="src/lucere/types/token_generate_params.py">params</a>) -> <a href="./src/lucere/types/token_response.py">TokenResponse</a></code>
- <code title="get /verify-token">client.token.<a href="./src/lucere/resources/token.py">verify</a>() -> <a href="./src/lucere/types/verify_response.py">VerifyResponse</a></code>
