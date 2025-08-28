from FluencyLogisticsOperations import FLO

class DummySession:
    def __init__(self):
        self.last = None
    def post(self, url, data=None, headers=None, timeout=None):
        self.last = {"url": url, "data": data, "headers": headers, "timeout": timeout}
        class R:
            status_code = 200
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            text = "payload={\"data\":[{\"id\":\"abc123\"}]}"
        return R()

def test_positional_identifier_unquoted():
    flo = FLO(base_url="https://example.com", token_provider=lambda: "TOKEN", session=DummySession())
    df = flo.client.resource("abc123").get()
    assert flo.session.last["data"]["method"] == "client.resource(abc123).get()"
    assert not df.empty

def test_kwargs_are_quoted():
    flo = FLO(base_url="https://example.com", token_provider=lambda: "TOKEN", session=DummySession())
    df = flo.client.resource.collect(limit=100, created_after="2025-08-01")
    assert flo.session.last["data"]["method"] == "client.resource.collect(limit=100, created_after=\"2025-08-01\")"
    assert not df.empty
