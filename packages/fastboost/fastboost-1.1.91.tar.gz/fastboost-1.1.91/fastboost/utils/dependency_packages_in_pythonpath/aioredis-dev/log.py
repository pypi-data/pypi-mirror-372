import logging
import os
import sys

logger = logging.getLogger("aioredis3")
sentinel_logger = logger.getChild("sentinel")

if os.environ.get("aioredis3_DEBUG"):
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(stream=sys.stderr)
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
    )
    logger.addHandler(handler)
    os.environ["aioredis3_DEBUG"] = ""
