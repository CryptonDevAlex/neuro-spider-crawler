from app.crawler.policy import CrawlPolicy


def test_policy_defaults() -> None:
    policy = CrawlPolicy()
    assert policy.max_depth == 2
    assert policy.max_pages == 30
    assert policy.respect_robots is True
