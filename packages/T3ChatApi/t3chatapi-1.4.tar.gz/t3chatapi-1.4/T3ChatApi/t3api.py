import json
import uuid
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple

import requests


class T3ChatError(Exception):
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_text: Optional[str] = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text


def _new_message_id() -> str:
    return str(uuid.uuid4())


def build_message(
    role: str,
    text: str,
    msg_id: Optional[str] = None,
    attachments: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Build a single T3 message dict from role + text.
    role: 'user' or 'assistant'
    """
    if role not in ("user", "assistant"):
        raise ValueError("role must be 'user' or 'assistant'")
    return {
        "id": msg_id or _new_message_id(),
        "parts": [{"text": text, "type": "text"}],
        "role": role,
        "attachments": attachments or [],
    }


def normalize_history(history: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Accepts a list of message-like dicts and converts them to T3 format:
    - If 'parts' missing, use 'text' or 'content' to build parts.
    - Ensures 'id' and 'attachments' exist.
    - Keeps only roles 'user' or 'assistant'.
    """
    out: List[Dict[str, Any]] = []
    for m in history:
        role = m.get("role")
        if role not in ("user", "assistant"):
            raise ValueError("history message role must be 'user' or 'assistant'")
        parts = m.get("parts")
        if not parts:
            text = m.get("text") or m.get("content")
            if text is None:
                raise ValueError("history message missing 'text'/'content'/'parts'")
            parts = [{"text": str(text), "type": "text"}]
        out.append(
            {
                "id": m.get("id") or _new_message_id(),
                "parts": parts,
                "role": role,
                "attachments": m.get("attachments") or [],
            }
        )
    return out


class T3ChatClient:
    """
    Minimal T3 Chat API client.

    Requirements (based on reduction tests):
    - Only 'access_token' cookie and 'convexSessionId' are required.
    - Minimal headers: just 'content-type: application/json' and a UA.
    - Required payload fields: messages, threadMetadata, responseMessageId,
      model, convexSessionId.

    Usage:
      client = T3ChatClient(access_token, convex_session_id)
      full_text, thread_id, new_history = client.chat(
          message="Hello",
          history=[build_message("user", "Hi"), build_message("assistant", "Hello!")],
          model="gemini-2.5-flash"
      )
    """

    def __init__(
        self,
        access_token: str,
        convex_session_id: str,
        base_url: str = "https://t3.chat",
        user_agent: str = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/139.0.0.0 Safari/537.36"
        ),
        timeout: float = 60.0,
    ):
        if not access_token:
            raise ValueError("access_token is required")
        if not convex_session_id:
            raise ValueError("convex_session_id is required")

        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.convex_session_id = convex_session_id  # plain UUID string

        s = requests.Session()
        s.headers.update(
            {
                "content-type": "application/json",
                "user-agent": user_agent,
            }
        )
        s.cookies.set("access_token", access_token.strip().rstrip(";"))
        self.session = s

    def chat(
        self,
        message: Optional[str] = None,
        history: Optional[Iterable[Dict[str, Any]]] = None,
        model: str = "gemini-2.5-flash",
        thread_id: Optional[str] = None,
        on_token: Optional[Callable[[str], None]] = None,
    ) -> Tuple[str, str, List[Dict[str, Any]]]:
        """
        Send a chat request.

        Parameters:
          - message: optional current user message (str). If None, you must
            provide a history that already contains a trailing user message.
          - history: iterable of messages (dicts). Each entry can be:
              { role: 'user'|'assistant', text|content: str, id?: str }
            or already T3-shaped with 'parts': [{text,type}].
          - model: model name (e.g., 'gemini-2.5-flash')
          - thread_id: optional thread UUID; if omitted, a new one is created
          - on_token: optional callback(token_str) for streaming tokens

        Returns:
          (full_text, thread_id, new_history) where new_history is the
          normalized history including the assistant response.
        """
        messages: List[Dict[str, Any]] = []
        if history:
            messages = normalize_history(history)

        if message is not None:
            # Append the current user message at the end
            messages.append(build_message("user", message))

        if not messages:
            raise ValueError("No messages to send. Provide 'message' or 'history'.")

        used_thread_id = thread_id or str(uuid.uuid4())
        response_message_id = _new_message_id()

        payload = {
            "messages": messages,
            "threadMetadata": {"id": used_thread_id},
            "responseMessageId": response_message_id,
            "model": model,
            # convexSessionId must be present; plain UUID string works
            "convexSessionId": self.convex_session_id,
        }

        url = f"{self.base_url}/api/chat"
        try:
            with self.session.post(
                url, json=payload, stream=True, timeout=self.timeout
            ) as resp:
                if not resp.ok:
                    body = None
                    try:
                        body = resp.text
                    except Exception:
                        pass
                    raise T3ChatError(
                        f"Chat HTTP error: {resp.status_code}",
                        status_code=resp.status_code,
                        response_text=body,
                    )

                full_text_chunks: List[str] = []

                for raw_line in resp.iter_lines(decode_unicode=True):
                    if not raw_line:
                        continue
                    if not raw_line.startswith("0:"):
                        # ignore metadata lines (e:, d:, f:, etc.)
                        continue

                    body = raw_line[2:]
                    # Two formats observed:
                    # 1) 0:"token"
                    # 2) 0:{"result":{"data":{"type":"text","content":"..."}}}
                    try:
                        parsed = json.loads(body)
                    except json.JSONDecodeError:
                        # non-JSON token; ignore in strict mode
                        continue

                    if isinstance(parsed, str):
                        full_text_chunks.append(parsed)
                        if on_token:
                            on_token(parsed)
                        continue

                    if (
                        isinstance(parsed, dict)
                        and "result" in parsed
                        and isinstance(parsed["result"], dict)
                        and "data" in parsed["result"]
                        and isinstance(parsed["result"]["data"], dict)
                    ):
                        d = parsed["result"]["data"]
                        if d.get("type") == "text" and "content" in d:
                            token = str(d["content"])
                            full_text_chunks.append(token)
                            if on_token:
                                on_token(token)

                full_text = "".join(full_text_chunks)

        except requests.exceptions.RequestException as e:
            raise T3ChatError(f"Network error: {e}") from e

        # Build updated history with assistant reply appended
        new_history = list(messages)
        new_history.append(
            build_message("assistant", full_text, msg_id=response_message_id)
        )
        return full_text, used_thread_id, new_history


# Simple convenience function (one-shot call without managing history)
def chat_once(
    access_token: str,
    convex_session_id: str,
    message: str,
    model: str = "gemini-2.5-flash",
    on_token: Optional[Callable[[str], None]] = None,
) -> str:
    client = T3ChatClient(access_token, convex_session_id)
    text, _thread, _hist = client.chat(
        message=message, history=None, model=model, on_token=on_token
    )
    return text