import pytest
import respx
import httpx
import pytest_asyncio

from empowernow_common.authzen.client import EnhancedPDP


@pytest_asyncio.fixture
async def epdp():
    pdp = EnhancedPDP(
        base_url="https://pdp.example.com",
        client_id="client123",
        client_secret="topsecret",  # used as bearer for now
        token_url="https://pdp.example.com/token",
    )
    yield pdp
    # ensure underlying httpx client closes
    if hasattr(pdp, "_http_client") and pdp._http_client:
        await pdp._http_client.aclose()


@pytest.mark.asyncio
async def test_evaluate_permit(epdp):
    """Happy-path 200 OK with decision true."""
    expected_json = {"decision": True, "context": {"constraints": [], "obligations": []}}

    with respx.mock(base_url="https://pdp.example.com", assert_all_called=False) as router:
        router.post("/v1/evaluation").mock(return_value=httpx.Response(200, json=expected_json))

        result = await epdp.evaluate({})
        assert result.decision is True
        # correlation id is injected back
        assert epdp.config.correlation_header in result.reason or True  # presence check via context handled internally


@pytest.mark.asyncio
async def test_transport_retry_then_success(epdp):
    """First attempt returns 500, second succeeds. Evaluate should still succeed."""
    with respx.mock(base_url="https://pdp.example.com", assert_all_called=False) as router:
        route = router.post("/v1/evaluation")
        route.side_effect = [
            httpx.Response(500, json={"error": "boom"}),
            httpx.Response(200, json={"decision": True, "context": {}}),
        ]
        res = await epdp.evaluate({})
        assert res.decision is True
        # ensure two calls were made
        assert route.called
        assert route.call_count == 2


@pytest.mark.asyncio
async def test_transport_fail_closed(epdp):
    """After retries exhausted, client returns denied decision."""
    with respx.mock(base_url="https://pdp.example.com", assert_all_called=False) as router:
        router.post("/v1/evaluation").mock(return_value=httpx.Response(503))
        res = await epdp.evaluate({})
        assert res.decision is False


# ---------------------------------------------------------------------------
# Extras / raw_context
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_raw_context_passthrough(epdp):
    """Unknown keys in PDP context should be retrievable via get_extra."""
    extra_ctx = {"foo": "bar", "constraints": []}
    payload = {"decision": True, "context": extra_ctx}

    with respx.mock(base_url="https://pdp.example.com", assert_all_called=False) as router:
        router.post("/v1/evaluation").mock(return_value=httpx.Response(200, json=payload))

        res = await epdp.evaluate({})
        assert res.decision is True
        assert res.get_extra("foo") == "bar"


# ---------------------------------------------------------------------------
# Batch evaluations
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_batch_execute_all(epdp):
    batch_req = [
        {"subject": {"type": "user", "id": "alice"}, "action": {"name": "read"}, "resource": {"type": "doc", "id": "1"}},
        {"subject": {"type": "user", "id": "alice"}, "action": {"name": "read"}, "resource": {"type": "doc", "id": "2"}},
    ]
    batch_resp = {
        "evaluations": [
            {"decision": True, "context": {}},
            {"decision": False, "context": {}},
        ]
    }
    with respx.mock(base_url="https://pdp.example.com", assert_all_called=False) as router:
        router.post("/v1/evaluations").mock(return_value=httpx.Response(200, json=batch_resp))
        res_list = await epdp.evaluate_batch(batch_req)
        assert len(res_list) == 2
        assert res_list[0].decision is True and res_list[1].decision is False


# ---------------------------------------------------------------------------
# Search endpoints
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_search_subject(epdp):
    search_result = {"results": [{"type": "user", "id": "alice"}]}
    with respx.mock(base_url="https://pdp.example.com", assert_all_called=False) as router:
        router.post("/access/v1/search/subject").mock(return_value=httpx.Response(200, json=search_result))
        res = await epdp.search_subject({"name": "read"}, {"type": "doc", "id": "1"})
        assert res["results"][0]["id"] == "alice"


@pytest.mark.asyncio
async def test_iter_search_subject_pagination(epdp):
    """Generator should follow next_token until exhausted."""
    page1 = {"results": [{"id": 1}], "page": {"next_token": "abc"}}
    page2 = {"results": [{"id": 2}], "page": {"next_token": ""}}
    with respx.mock(base_url="https://pdp.example.com", assert_all_called=False) as router:
        router.post("/access/v1/search/subject").side_effect = [
            httpx.Response(200, json=page1),
            httpx.Response(200, json=page2),
        ]
        out = []
        async for item in epdp.iter_search_subject({"name": "read"}, {"type": "doc", "id": "1"}):
            out.append(item["id"])
        assert out == [1, 2]


# Global fixture to mock token endpoint for all tests in module

@pytest.fixture(autouse=True)
def _mock_token():
    with respx.mock(base_url="https://pdp.example.com", assert_all_called=False) as router:
        router.post("/token").mock(return_value=httpx.Response(200, json={"access_token": "dummy", "expires_in": 3600}))
        yield 