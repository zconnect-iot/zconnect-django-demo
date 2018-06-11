# https://github.com/dfunckt/django-rules#best-practices

import logging

from django.db import models
import rules

from zconnect.util.rules import orify_perm
from django_demo.util.groups import get_parental_chain

logger = logging.getLogger(__name__)


@rules.predicate
def can_view_demo_device(user, obj):
    """Extend basic zconnect check to check for parents too"""
    from django_demo.models import SiteGroup

    # This is the 'basic' check - it will have already been done in zconnect due
    # to orifying that check with this one.
    # all_orgs = Organization.objects.filter(
    #     models.Q(pk__in=user.organizations_organization.all()) & models.Q(pk__in=obj.orgs.all())
    # )

    # If the device was in a Site, we would have already queried it in the
    # zconnect rule check, so we just need to check distributors and companies.
    # There will always be exactly 1 company and 1 distributor for each Site, so
    # this should be possible in 2 queries per device.

    c_filter = models.Q(company_id__in=user.orgs.all())
    d_filter = models.Q(company__distributor_id__in=user.orgs.all())

    o_filter = models.Q(pk__in=obj.orgs.all())

    # Query for all sites where their organisation is common with the object and
    # either the company or distributor is also in that group
    sites = SiteGroup.objects.filter(
        (c_filter | d_filter) & o_filter
    )

    return any(sites)

@rules.predicate
def can_view_group(user, obj):
    if user.is_superuser:
        logger.debug("Superuser can access any group")
        return True

    user_orgs = set([i.id for i in user.orgs.all()])

    if not user_orgs:
        logger.debug("User in no organizations")
        return False

    logger.debug("User organizations: %s", user_orgs)

    # Find all the orgs in parental chain
    parental_orgs = get_parental_chain(obj)

    return any(user_orgs & parental_orgs)

orify_perm("django_demo.view_demodevice", can_view_demo_device)
orify_perm("django_demo.change_demodevice", can_view_demo_device)

for group_type in ["site", "company", "distributor"]:
    rules.add_perm("django_demo.view_{}group".format(group_type), can_view_group)
