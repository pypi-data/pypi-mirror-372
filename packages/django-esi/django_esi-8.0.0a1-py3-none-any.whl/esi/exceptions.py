class ESIErrorLimitException(Exception):
    """ESI Global Error Limit Exceeded
    https://developers.eveonline.com/docs/services/esi/best-practices/#error-limit
    """
    def __init__(self, reset=None, *args, **kwargs) -> None:
        self.reset = reset
        msg = kwargs.get("message") or (
            f"ESI Error limited. Reset in {reset} seconds." if reset else "ESI Error limited."
        )
        super().__init__(msg, *args)


class ESIBucketLimitException(Exception):
    """Endpoint (Bucket) Specific Rate Limit Exceeded"""
    def __init__(self, bucket, *args, **kwargs) -> None:
        self.bucket = bucket
        msg = kwargs.get("message") or f"ESI bucket limit reached for {bucket}."
        super().__init__(msg, *args)
