import logging

from django.db import transaction, connection
from django.db.models.signals import post_save
from django.dispatch import receiver

from pulp_webhook.app.webhook import send_webhook
from pulpcore.app.models import (
  RepositoryVersion,
  RepositoryContent,
)
from pulp_rpm.app.models import Package as RpmPackage
from pulp_file.app.models import FileContent

from .helpers import (
  compile_payload,
  file_dist_urls,
  file_relpath,
  is_synced,
  published_relpath_rpm,
  rpm_dist_urls,
)

log = logging.getLogger(__name__)


# @receiver(post_save)
# def on_repo_version_created_for_file(sender, instance: RepositoryVersion, created: bool, **kwargs):
#   log.info(f'DEBUG {sender}')

#   def _after_commit():
#     log.info("xxxxx")

@receiver(post_save, sender=RepositoryVersion, weak=False, dispatch_uid="upload_only_when_rv_complete_v1")
def on_repo_version_saved(sender, instance: RepositoryVersion, **kwargs):
  # Only act when the version is visible/complete; creating task flips this to True.
  if not instance.complete:
    return

  def _after_commit():
    # Re-fetch to ensure we see committed state
    rv = RepositoryVersion.objects.select_related("repository").get(pk=instance.pk)
    repo = rv.repository

    # Content added *in this version*
    added_ids = list(
      RepositoryContent.objects
      .filter(repository=repo, version_added=rv)
      .values_list("content_id", flat=True)
    )

    if not added_ids:
      return

    #
    #  RPM upload
    #
    rpm_by_pk = {p.pk: p for p in RpmPackage.objects.filter(pk__in=added_ids)}
    rpm_items = []

    if rpm_by_pk:
      for pk, pkg in rpm_by_pk.items():
        if is_synced(pk):
          continue

        rpm_items.append({
          "name": pkg.name,
          "epoch": pkg.epoch,
          "version": pkg.version,
          "release": pkg.release,
          "arch": pkg.arch,
          "location_href": pkg.location_href,
          "published_relative_path": published_relpath_rpm(pkg),
          "distribution_urls": rpm_dist_urls(pkg, repo),
        })

      if rpm_items:
        payload = compile_payload(
          event_name="rpm.publish",
          repo=repo,
          content=rpm_items,
        )
        send_webhook(payload)

    #
    # File upload
    #
    file_by_pk = {c.pk: c for c in FileContent.objects.filter(pk__in=added_ids)}
    file_items = []

    if file_by_pk:
      for pk, fc in file_by_pk.items():
        if is_synced(pk):
          continue

        file_items.append({
          "relative_path": file_relpath(fc),
          "distribution_urls": file_dist_urls(fc, repo),
        })

      if file_items:
        payload = compile_payload(
          event_name="file.publish",
          repo=repo,
          content=file_items,
        )
        send_webhook(payload)

  if connection.in_atomic_block:
    transaction.on_commit(_after_commit)
  else:
    _after_commit()
