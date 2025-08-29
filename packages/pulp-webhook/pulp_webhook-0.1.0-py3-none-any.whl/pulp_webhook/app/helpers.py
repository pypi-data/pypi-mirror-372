import logging

from typing import List, Dict, Any
from django.conf import settings

from pulpcore.app.models import (
  ContentArtifact,
  RemoteArtifact,
  RepositoryVersion,
)
from pulp_rpm.app.models import Package as RpmPackage, RpmDistribution
from pulp_file.app.models import FileContent, FileDistribution

log = logging.getLogger(__name__)

CONTENT_ORIGIN = (getattr(settings, "CONTENT_ORIGIN", "") or "").rstrip("/")

def is_synced(content_pk: int) -> bool:
  ca_pks = list(ContentArtifact.objects.filter(content_id=content_pk).values_list("pk", flat=True))
  return bool(ca_pks and RemoteArtifact.objects.filter(content_artifact_id__in=ca_pks).exists())

def file_relpath(fc: FileContent) -> str:
  return (fc.relative_path or "").lstrip("/")

def file_dist_urls(fc: FileContent, repo) -> List[str]:
  if not CONTENT_ORIGIN:
    return []

  rel = file_relpath(fc)
  urls = []
  for dist in FileDistribution.objects.filter(repository=repo):
    base = (dist.base_path or "").strip("/")
    urls.append(f"{CONTENT_ORIGIN}/pulp/content/{base}/{rel}")

  return urls

def published_relpath_rpm(pkg: RpmPackage) -> str:
  loc = (getattr(pkg, "location_href", "") or "").lstrip("/")
  if loc.startswith("Packages/") or "/" in loc:
    return loc
  fname = loc or f"{pkg.name}-{pkg.version}-{pkg.release}.{pkg.arch}.rpm"
  first = (fname[0].lower() if fname else "_")

  return f"Packages/{first}/{fname}"

def rpm_dist_urls(pkg: RpmPackage, repo) -> List[str]:
  if not CONTENT_ORIGIN:
    return []

  rel = published_relpath_rpm(pkg)
  urls = []

  for dist in RpmDistribution.objects.filter(repository=repo):
    base = (dist.base_path or "").strip("/")
    urls.append(f"{CONTENT_ORIGIN}/pulp/content/{base}/{rel}")

  return urls

def compile_payload(event_name: str, repo: RepositoryVersion, content: List[Any]) -> Dict[str, Any]:
  payload = {
    "event": event_name,
    "repository": repo.name,
    "content": content,
  }

  log.info(f"Payload: {payload}")

  return payload
