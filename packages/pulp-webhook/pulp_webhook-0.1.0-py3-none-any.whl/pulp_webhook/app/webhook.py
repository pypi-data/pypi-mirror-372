import logging
import json
import requests

from typing import Dict, Any, Optional
from django.conf import settings

logger = logging.getLogger(__name__)

def send_webhook(payload: Dict[str, Any]) -> Optional[int]:
  url = getattr(settings, "WEBHOOK_URL", None)
  if not url:
    logger.debug("WEBHOOK_URL not set; skipping webhook.")
    return None

  secret = getattr(settings, "WEBHOOK_SECRET", None)
  body = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

  headers = {
    "Content-Type": "application/json",
    "User-Agent": "pulp-webhook/1.0",
  }
  if secret:
    headers['X-Pulp-Webhook-Token'] = secret

  try:
    r = requests.post(url, data=body, headers=headers)
    if 200 <= r.status_code < 300:
      return r.status_code
    logger.warning(f"Webhook HTTP {r.status_code}: {r.text[:500]}")
  except Exception as e:
    logger.warning(f"Webhook failed: {e}")

  return None
