# Threads

Types:

```python
from aiinbx.types import ThreadRetrieveResponse, ThreadForwardResponse, ThreadSearchResponse
```

Methods:

- <code title="get /threads/{threadId}">client.threads.<a href="./src/aiinbx/resources/threads.py">retrieve</a>(thread_id) -> <a href="./src/aiinbx/types/thread_retrieve_response.py">ThreadRetrieveResponse</a></code>
- <code title="post /threads/{threadId}/forward">client.threads.<a href="./src/aiinbx/resources/threads.py">forward</a>(thread_id, \*\*<a href="src/aiinbx/types/thread_forward_params.py">params</a>) -> <a href="./src/aiinbx/types/thread_forward_response.py">ThreadForwardResponse</a></code>
- <code title="post /threads/search">client.threads.<a href="./src/aiinbx/resources/threads.py">search</a>(\*\*<a href="src/aiinbx/types/thread_search_params.py">params</a>) -> <a href="./src/aiinbx/types/thread_search_response.py">ThreadSearchResponse</a></code>

# Emails

Types:

```python
from aiinbx.types import EmailRetrieveResponse, EmailReplyResponse, EmailSendResponse
```

Methods:

- <code title="get /emails/{emailId}">client.emails.<a href="./src/aiinbx/resources/emails.py">retrieve</a>(email_id) -> <a href="./src/aiinbx/types/email_retrieve_response.py">EmailRetrieveResponse</a></code>
- <code title="post /emails/{emailId}/reply">client.emails.<a href="./src/aiinbx/resources/emails.py">reply</a>(email_id, \*\*<a href="src/aiinbx/types/email_reply_params.py">params</a>) -> <a href="./src/aiinbx/types/email_reply_response.py">EmailReplyResponse</a></code>
- <code title="post /emails/send">client.emails.<a href="./src/aiinbx/resources/emails.py">send</a>(\*\*<a href="src/aiinbx/types/email_send_params.py">params</a>) -> <a href="./src/aiinbx/types/email_send_response.py">EmailSendResponse</a></code>
