from rori.models import Rori
from rori.watcher import HealthCheck


def test_lshift_now_healthy(rori: Rori):
    hc1 = HealthCheck(rori=rori, healthy=True, fails=0)
    hc2 = HealthCheck(rori=rori, healthy=False, fails=3)

    result = hc1 << hc2
    assert result.healthy is True
    assert result.fails == 0


def test_lshift_now_failing(rori: Rori):
    hc1 = HealthCheck(rori=rori, healthy=False, fails=0)
    hc2 = HealthCheck(rori=rori, healthy=False, fails=4)

    result = hc1 << hc2
    assert result.healthy is False
    assert result.fails == 5


def test_lshift_on_list(rori: Rori, rori_factory):
    hc = HealthCheck(rori=rori, healthy=False, fails=0)
    rori1 = rori_factory(name="ro-test-ri-1")
    rori2 = rori_factory(name="ro-test-ri-2")
    failed = [
        HealthCheck(rori=rori1, healthy=False, fails=1),
        HealthCheck(rori=rori, healthy=False, fails=3),
        HealthCheck(rori=rori2, healthy=False, fails=2),
    ]

    result = hc << failed
    assert result.healthy is False
    assert result.fails == 4
