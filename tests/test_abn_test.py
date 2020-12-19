import pytest

from redis_cooker.abn_test import ABNTest, Choice
from redis_cooker.clients import current_redis_client, set_connection_url

set_connection_url('redis://:@127.0.0.1:6379/15')
client = current_redis_client()


class TestABNTest:
    def test_fetch(self):
        topic = "lead comment"
        choices = [Choice(name="A", value=5), Choice(name="B", value=5)]
        abn_test = ABNTest(topic, choices)
        choice_names = [i.name for i in choices]
        for i in range(10):
            choice = abn_test.fetch()
            assert choice in choice_names
        assert sum(int(i) for i in client.mget(abn_test.keys.keys())) == 0

    def test_value_nonzero(self):
        topic = "lead comment"
        choices = [Choice(name="A", value=5), Choice(name="C", value=0)]
        with pytest.raises(AssertionError):
            _ = ABNTest(topic, choices)
