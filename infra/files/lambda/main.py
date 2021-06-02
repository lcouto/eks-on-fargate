import json
import logging
import os
import ssl
import urllib.parse
import urllib.request
import urllib.response
from datetime import datetime
from typing import Dict

# configure logging parameters
debug = os.environ.get("DEBUG")
logging_level = logging.DEBUG if debug else logging.INFO
request_debug_level = 5 if debug else 0

# configure logger
logger = logging.getLogger()
logger.setLevel(logging_level)

# configure request handler
request_context = ssl._create_unverified_context()
request_handler = urllib.request.HTTPSHandler(
    context=request_context, debuglevel=request_debug_level
)


def build_patch_body(annotations: Dict) -> Dict:
    return json.dumps(
        {"spec": {"template": {"metadata": {"annotations": annotations}}}}
    )


def patch_coredns_service(url: str, headers: Dict[str, str], data: str) -> None:
    request = urllib.request.Request(
        method="PATCH", url=url, headers=headers, data=bytes(data.encode("utf-8"))
    )
    opener = urllib.request.build_opener(request_handler)
    with opener.open(request) as response:
        return response.read().decode()


def handler(event, _):
    logger.info(event)

    token = event.get("token")
    endpoint = event.get("endpoint")

    url = f"{endpoint}/apis/apps/v1/namespaces/kube-system/deployments/coredns"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/strategic-merge-patch+json",
    }

    try:
        # delete ec2 compute type label
        body = build_patch_body(
            {"$patch": "delete", "eks.amazonaws.com/compute-type": "ec2"}
        )
        logging.info("Patch Request: %s", body)
        response = patch_coredns_service(url, headers, body)
        logging.info("Patch Response: %s", response)
        reload_body = build_patch_body(
            {"kubectl.kubrnetes.io/restartedAt":"'+date+'"}
        )
        logging.info("Reload Request: %s", reload_body)
        response = patch_coredns_service(url, headers, reload_body)
        logging.info("Reload Response: %s", response)        
    except urllib.error.HTTPError as e:
        logger.error("Request Error: %s", e)
