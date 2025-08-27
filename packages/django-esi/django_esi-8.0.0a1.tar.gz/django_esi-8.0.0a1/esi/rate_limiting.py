import time
from django.core.cache import cache
from esi.exceptions import ESIBucketLimitException


class ESIRateLimitBucket:
    MARKET_DATA_HISTORY = ("market_data_history", 300, 60)
    CHARACTER_CORPORATION_HISTORY = ("character_corporation_history", 300, 60)

    def __init__(self, slug, limit, window):
        self.slug = slug
        self.limit = limit
        self.window = window

    @classmethod
    def choices(cls):
        return [(bucket.slug, bucket.slug.replace("_", " ").title()) for bucket in cls]


class ESIRateLimiter:
    def __init__(self) -> None:
        pass

    def _slug_to_key(self, slug) -> str:
        return f"esi:bucket:{slug}"

    def init_bucket(self, bucket: ESIRateLimitBucket) -> None:
        # Set our bucket up if it doesn't already exist
        cache.set(
            self._slug_to_key(bucket.slug),
            bucket.limit,
            timeout=bucket.window,
            nx=True  # Don't re-create if it does exist
        )

    def get_bucket(self, bucket: ESIRateLimitBucket) -> int:
        # get the value from the bucket
        return cache.get(
            self._slug_to_key(bucket.slug),
            1  # When not found return 1
        )

    def get_timeout(self, bucket: ESIRateLimitBucket, raise_on_limit: bool = True) -> int:
        curent_bucket = self.get_bucket(bucket)
        if curent_bucket <= 0:
            timeout = cache.ttl(self._slug_to_key(bucket.slug)) + 1
            msg = (
                f"Rate limit for bucket '{bucket.slug}' exceeded: "
                f"{curent_bucket}/{bucket.limit} in last {bucket.window}s. "
                f"Wait {timeout}s."
            )
            if raise_on_limit:
                raise ESIBucketLimitException(msg)  # Throw error
            else:
                return timeout  # return the time left till reset
        else:
            return 0  # we are good.

    def decr_bucket(self, bucket: ESIRateLimitBucket) -> int:
        # decrease the bucket value by 1 from the bucket
        return cache.decr(
            self._slug_to_key(bucket.slug)
        )

    def check_bucket(self, bucket: ESIRateLimitBucket, raise_on_limit: bool = True):
        ESIRateLimits.init_bucket(bucket)
        # get the value
        bucket_val = ESIRateLimits.get_bucket(bucket)
        if bucket_val <= 0:
            timeout = ESIRateLimits.get_timeout(bucket, raise_on_limit=raise_on_limit)
            if timeout > 0:
                time.sleep(timeout)
            return
        # reduce our bucket by 1
        ESIRateLimits.decr_bucket(bucket)


ESIRateLimits = ESIRateLimiter()
