import time, os
from empowernow_common.fips.validator import (
    start_continuous_validation,
    _VALIDATOR_THREAD,
)


def test_background_validation(monkeypatch):
    calls = []

    def fake_ensure():
        calls.append(time.time())
        if len(calls) == 2:
            raise RuntimeError("fail once")

    monkeypatch.setattr(
        "empowernow_common.fips.validator.FIPSValidator.ensure_compliance", fake_ensure
    )
    start_continuous_validation(interval=0.1, strict=False)
    time.sleep(0.35)
    # ensure thread ran at least twice
    assert len(calls) >= 3
