import logging
from empowernow_common.utils.logging_config import EmojiDowngradeFilter


def test_emoji_downgrades_to_debug(caplog):
    logger = logging.getLogger("empowernow.test")
    logger.setLevel(logging.DEBUG)
    logger.addFilter(EmojiDowngradeFilter())
    with caplog.at_level(logging.DEBUG):
        logger.info("🛡️ important info")
    # Record should be present at DEBUG, not INFO level after filter
    records = [r for r in caplog.records if "important info" in r.message]
    assert records and records[0].levelno == logging.DEBUG
