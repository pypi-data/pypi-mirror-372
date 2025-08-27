# tests/test_a2a_client.py
import pytest
import httpx
from typing import Any, AsyncIterator, List, Dict

from a2a_cli.a2a_client import A2AClient
from a2a_json_rpc.transport import JSONRPCTransport
from a2a_json_rpc.spec import (
    Task, TaskSendParams, TaskQueryParams, TaskIdParams,
    TaskPushNotificationConfig, TaskStatusUpdateEvent, TaskArtifactUpdateEvent,
    TaskState,
)
from a2a_json_rpc.json_rpc_errors import JSONRPCError
from pydantic import ValidationError


class FakeTransport(JSONRPCTransport):
    def __init__(self, call_return: Any = None, stream_msgs: List[Dict] = None):
        self.calls: List[Any] = []
        self.call_return = call_return
        self.stream_msgs = stream_msgs or []
        self.notified: List[Any] = []

    async def call(self, method: str, params: Any) -> Any:
        self.calls.append((method, params))
        if isinstance(self.call_return, Exception):
            raise self.call_return
        return self.call_return

    async def notify(self, method: str, params: Any) -> None:
        self.notified.append((method, params))

    def stream(self) -> AsyncIterator[Dict]:
        async def gen():
            for msg in self.stream_msgs:
                yield msg
        return gen()


@pytest.mark.asyncio
async def test_send_and_get_and_cancel_task():
    raw_task = {"id": "t1", "status": {"state": "completed"}}
    transport = FakeTransport(call_return=raw_task)
    client = A2AClient(transport)

    params = TaskSendParams(id="t1", session_id="test-session", message={"role": "user", "parts": []})
    task = await client.send_task(params)
    assert isinstance(task, Task)
    assert task.id == "t1"
    assert task.status.state == TaskState.completed
    assert transport.calls[-1][0] == "tasks/send"

    query = TaskQueryParams(id="t1", historyLength=5)
    task2 = await client.get_task(query)
    assert task2.id == "t1"
    assert transport.calls[-1][0] == "tasks/get"

    cancel = TaskIdParams(id="t1")
    result = await client.cancel_task(cancel)
    assert transport.calls[-1][0] == "tasks/cancel"
    assert result is None


@pytest.mark.asyncio
async def test_push_notification_config():
    raw_conf = {"id": "t2", "pushNotificationConfig": {"url": "u"}}
    transport = FakeTransport(call_return=raw_conf)
    client = A2AClient(transport)

    params = TaskPushNotificationConfig(id="t2", pushNotificationConfig={"url": "u"})
    conf = await client.set_push_notification(params)
    assert conf.id == "t2"
    assert conf.pushNotificationConfig.url == "u"
    assert transport.calls[-1][0] == "tasks/pushNotification/set"

    transport = FakeTransport(call_return=raw_conf)
    client = A2AClient(transport)
    cid = TaskIdParams(id="t2")
    conf2 = await client.get_push_notification(cid)
    assert conf2.id == "t2"
    assert transport.calls[-1][0] == "tasks/pushNotification/get"


@pytest.mark.asyncio
async def test_send_subscribe_and_resubscribe_streams():
    # Change the structure to match what's actually returned by the client
    status_msg = {"id": "t3", "status": {"state": "working"}}
    artifact_msg = {"id": "t3", "artifact": {"parts": [], "index": 0}}
    transport = FakeTransport(call_return=None, stream_msgs=[status_msg, artifact_msg])
    client = A2AClient(transport)

    params = TaskSendParams(id="t3", session_id="test-session", message={"role": "user", "parts": []})
    events = []
    async for ev in client.send_subscribe(params):
        events.append(ev)
        if len(events) == 2:
            break
    
    # Updated to check for model objects instead of dictionaries
    assert isinstance(events[0], TaskStatusUpdateEvent)
    assert events[0].id == "t3"
    assert events[0].status.state == TaskState.working
    
    assert isinstance(events[1], TaskArtifactUpdateEvent)
    assert events[1].id == "t3"
    assert transport.calls[0][0] == "tasks/sendSubscribe"

    transport = FakeTransport(call_return=None, stream_msgs=[status_msg])
    client = A2AClient(transport)
    q = TaskQueryParams(id="t3")
    events2 = []
    async for ev in client.resubscribe(q):
        events2.append(ev)
        break
    
    # Updated to check for model objects
    assert isinstance(events2[0], TaskStatusUpdateEvent)
    assert events2[0].id == "t3"
    assert transport.calls[0][0] == "tasks/resubscribe"


@pytest.mark.asyncio
async def test_error_propagation():
    err = JSONRPCError(message="fail")
    transport = FakeTransport(call_return=err)
    client = A2AClient(transport)
    with pytest.raises(JSONRPCError):
        await client.get_task(TaskQueryParams(id="x"))


# Edge case tests
@pytest.mark.asyncio
async def test_factory_methods():
    http_client = A2AClient.over_http("http://test")
    ws_client = A2AClient.over_ws("ws://test")
    sse_client = A2AClient.over_sse("http://test", "http://test/stream")
    from a2a_cli.transport.http import JSONRPCHTTPClient
    from a2a_cli.transport.websocket import JSONRPCWebSocketClient
    from a2a_cli.transport.sse import JSONRPCSSEClient
    assert isinstance(http_client.transport, JSONRPCHTTPClient)
    assert isinstance(ws_client.transport, JSONRPCWebSocketClient)
    assert isinstance(sse_client.transport, JSONRPCSSEClient)


@pytest.mark.asyncio
async def test_send_subscribe_with_http_not_supported():
    # Create client with mocked transport
    client = A2AClient.over_http("http://localhost:8000")
    
    # Mock the HTTP client to prevent real network requests
    def handler(request: httpx.Request):
        return httpx.Response(
            status_code=200,
            json={"jsonrpc": "2.0", "result": {"ok": True}, "id": None},
        )
    
    mock_transport = httpx.MockTransport(handler)
    client.transport._client = httpx.AsyncClient(transport=mock_transport)
    
    params = TaskSendParams(id="t4", session_id="test-session", message={"role": "user", "parts": []})
    with pytest.raises(NotImplementedError):
        # send_subscribe will call stream(), which HTTP transport does not support
        async for _ in client.send_subscribe(params):
            pass


@pytest.mark.asyncio
async def test_validation_error_on_bad_response():
    # Transport returns invalid shape, causing Pydantic ValidationError
    transport = FakeTransport(call_return={"foo": "bar"})
    client = A2AClient(transport)
    with pytest.raises(ValidationError):
        await client.get_task(TaskQueryParams(id="t5"))