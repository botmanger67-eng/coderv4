import pytest
from datetime import datetime, timedelta
from src.utils.rate_limiter import RateLimiter


class TestRateLimiter:
    """Test suite for RateLimiter utility."""

    def test_initialization_default_values(self):
        """Test RateLimiter initializes with default values."""
        limiter = RateLimiter()
        assert limiter.max_requests == 10
        assert limiter.window_seconds == 60

    def test_initialization_custom_values(self):
        """Test RateLimiter initializes with custom values."""
        limiter = RateLimiter(max_requests=5, window_seconds=30)
        assert limiter.max_requests == 5
        assert limiter.window_seconds == 30

    def test_initialization_invalid_values(self):
        """Test RateLimiter raises error for invalid values."""
        with pytest.raises(ValueError, match="max_requests must be positive"):
            RateLimiter(max_requests=0)
        with pytest.raises(ValueError, match="max_requests must be positive"):
            RateLimiter(max_requests=-1)
        with pytest.raises(ValueError, match="window_seconds must be positive"):
            RateLimiter(window_seconds=0)
        with pytest.raises(ValueError, match="window_seconds must be positive"):
            RateLimiter(window_seconds=-10)

    def test_allow_request_under_limit(self):
        """Test allow_request returns True when under limit."""
        limiter = RateLimiter(max_requests=3, window_seconds=60)
        assert limiter.allow_request() is True
        assert limiter.allow_request() is True
        assert limiter.allow_request() is True

    def test_allow_request_at_limit(self):
        """Test allow_request returns False when at limit."""
        limiter = RateLimiter(max_requests=2, window_seconds=60)
        assert limiter.allow_request() is True
        assert limiter.allow_request() is True
        assert limiter.allow_request() is False

    def test_allow_request_after_window_expiry(self):
        """Test allow_request returns True after window expires."""
        limiter = RateLimiter(max_requests=1, window_seconds=1)
        assert limiter.allow_request() is True
        assert limiter.allow_request() is False

        # Simulate time passing
        limiter._window_start = datetime.utcnow() - timedelta(seconds=2)
        limiter._request_count = 0

        assert limiter.allow_request() is True

    def test_reset(self):
        """Test reset clears rate limiter state."""
        limiter = RateLimiter(max_requests=1, window_seconds=60)
        limiter.allow_request()
        assert limiter._request_count == 1

        limiter.reset()
        assert limiter._request_count == 0
        assert limiter._window_start is not None

    def test_remaining_requests(self):
        """Test remaining_requests property."""
        limiter = RateLimiter(max_requests=5, window_seconds=60)
        assert limiter.remaining_requests == 5

        limiter.allow_request()
        assert limiter.remaining_requests == 4

        limiter.allow_request()
        assert limiter.remaining_requests == 3

    def test_remaining_requests_after_window_expiry(self):
        """Test remaining_requests resets after window expiry."""
        limiter = RateLimiter(max_requests=2, window_seconds=1)
        limiter.allow_request()
        limiter.allow_request()
        assert limiter.remaining_requests == 0

        # Simulate window expiry
        limiter._window_start = datetime.utcnow() - timedelta(seconds=2)
        limiter._request_count = 0

        assert limiter.remaining_requests == 2

    def test_time_until_reset(self):
        """Test time_until_reset property."""
        limiter = RateLimiter(max_requests=5, window_seconds=60)
        assert 0 < limiter.time_until_reset <= 60

        # After some time
        limiter._window_start = datetime.utcnow() - timedelta(seconds=30)
        assert 25 <= limiter.time_until_reset <= 35

    def test_time_until_reset_expired_window(self):
        """Test time_until_reset returns 0 for expired window."""
        limiter = RateLimiter(max_requests=5, window_seconds=1)
        limiter._window_start = datetime.utcnow() - timedelta(seconds=2)
        assert limiter.time_until_reset == 0

    def test_concurrent_requests(self):
        """Test rate limiter handles multiple requests correctly."""
        limiter = RateLimiter(max_requests=3, window_seconds=60)
        results = [limiter.allow_request() for _ in range(5)]
        assert results == [True, True, True, False, False]

    def test_window_auto_reset(self):
        """Test rate limiter auto-resets window when expired."""
        limiter = RateLimiter(max_requests=2, window_seconds=1)
        limiter.allow_request()
        limiter.allow_request()
        assert limiter.allow_request() is False

        # Simulate time passing
        limiter._window_start = datetime.utcnow() - timedelta(seconds=2)
        limiter._request_count = 0

        assert limiter.allow_request() is True
        assert limiter.remaining_requests == 1

    def test_str_representation(self):
        """Test string representation of RateLimiter."""
        limiter = RateLimiter(max_requests=10, window_seconds=60)
        expected = f"RateLimiter(max_requests=10, window_seconds=60, remaining=10, time_until_reset={limiter.time_until_reset:.1f}s)"
        assert str(limiter) == expected

    def test_repr_representation(self):
        """Test repr representation of RateLimiter."""
        limiter = RateLimiter(max_requests=10, window_seconds=60)
        expected = f"RateLimiter(max_requests=10, window_seconds=60)"
        assert repr(limiter) == expected

    def test_edge_case_single_request(self):
        """Test rate limiter with single request limit."""
        limiter = RateLimiter(max_requests=1, window_seconds=60)
        assert limiter.allow_request() is True
        assert limiter.allow_request() is False
        assert limiter.remaining_requests == 0

    def test_edge_case_large_window(self):
        """Test rate limiter with large window."""
        limiter = RateLimiter(max_requests=1000, window_seconds=3600)
        for _ in range(1000):
            assert limiter.allow_request() is True
        assert limiter.allow_request() is False
        assert limiter.remaining_requests == 0

    def test_edge_case_zero_window(self):
        """Test rate limiter with zero window raises error."""
        with pytest.raises(ValueError):
            RateLimiter(max_requests=5, window_seconds=0)

    def test_edge_case_negative_values(self):
        """Test rate limiter with negative values raises error."""
        with pytest.raises(ValueError):
            RateLimiter(max_requests=-5, window_seconds=60)
        with pytest.raises(ValueError):
            RateLimiter(max_requests=5, window_seconds=-60)

    def test_is_rate_limited(self):
        """Test is_rate_limited property."""
        limiter = RateLimiter(max_requests=2, window_seconds=60)
        assert limiter.is_rate_limited is False

        limiter.allow_request()
        limiter.allow_request()
        assert limiter.is_rate_limited is True

        limiter.reset()
        assert limiter.is_rate_limited is False

    def test_wait_time(self):
        """Test wait_time property returns correct value."""
        limiter = RateLimiter(max_requests=1, window_seconds=60)
        assert limiter.wait_time == 0

        limiter.allow_request()
        assert limiter.wait_time > 0
        assert limiter.wait_time <= 60

    def test_wait_time_no_limit(self):
        """Test wait_time returns 0 when not rate limited."""
        limiter = RateLimiter(max_requests=10, window_seconds=60)
        assert limiter.wait_time == 0

    def test_multiple_resets(self):
        """Test multiple resets work correctly."""
        limiter = RateLimiter(max_requests=3, window_seconds=60)
        for _ in range(3):
            limiter.allow_request()
        assert limiter.remaining_requests == 0

        limiter.reset()
        assert limiter.remaining_requests == 3

        for _ in range(3):
            limiter.allow_request()
        assert limiter.remaining_requests == 0

        limiter.reset()
        assert limiter.remaining_requests == 3

    def test_allow_request_with_timestamp(self):
        """Test allow_request with custom timestamp."""
        limiter = RateLimiter(max_requests=2, window_seconds=60)
        now = datetime.utcnow()

        assert limiter.allow_request(timestamp=now) is True
        assert limiter.allow_request(timestamp=now + timedelta(seconds=1)) is True
        assert limiter.allow_request(timestamp=now + timedelta(seconds=2)) is False

        # After window expires
        future = now + timedelta(seconds=61)
        assert limiter.allow_request(timestamp=future) is True

    def test_remaining_requests_with_timestamp(self):
        """Test remaining_requests with custom timestamp."""
        limiter = RateLimiter(max_requests=3, window_seconds=60)
        now = datetime.utcnow()

        assert limiter.remaining_requests(timestamp=now) == 3
        limiter.allow_request(timestamp=now)
        assert limiter.remaining_requests(timestamp=now) == 2

        # After window expires
        future = now + timedelta(seconds=61)
        assert limiter.remaining_requests(timestamp=future) == 3

    def test_time_until_reset_with_timestamp(self):
        """Test time_until_reset with custom timestamp."""
        limiter = RateLimiter(max_requests=5, window_seconds=60)
        now = datetime.utcnow()

        time_left = limiter.time_until_reset(timestamp=now)
        assert 0 < time_left <= 60

        # After some time
        later = now + timedelta(seconds=30)
        time_left = limiter.time_until_reset(timestamp=later)
        assert 25 <= time_left <= 35

        # After window expires
        future = now + timedelta(seconds=61)
        assert limiter.time_until_reset(timestamp=future) == 0