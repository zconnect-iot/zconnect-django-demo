from django.contrib import admin

from .models import CompanyGroup, DistributorGroup, Mapping, SiteGroup, WiringMapping

admin.site.register(WiringMapping)
admin.site.register(Mapping)
admin.site.register(SiteGroup)
admin.site.register(CompanyGroup)
admin.site.register(DistributorGroup)
