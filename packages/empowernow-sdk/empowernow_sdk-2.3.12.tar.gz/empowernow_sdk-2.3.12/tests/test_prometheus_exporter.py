from empowernow_common.utils.metrics import export_metrics


def test_export_metrics_format():
    sample = {"total_requests": 5, "cache_hits": 3}
    data = export_metrics(sample)
    text = data.decode()
    assert "empowernow_total_requests" in text
    assert "empowernow_cache_hits" in text
