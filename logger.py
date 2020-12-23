import sys
import json
import logging


class logJson():
    def format(self, log):
        return json.dumps({
            "severity": log.levelname,
            "message": log.msg,
        })


formatter = logJson()
stream = logging.StreamHandler(stream=sys.stdout)
stream.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(stream)
