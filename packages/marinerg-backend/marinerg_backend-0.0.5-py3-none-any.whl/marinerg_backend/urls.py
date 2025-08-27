"""
URL configuration
"""

from django.urls import include, path
from rest_framework import routers

import ichec_django_core.urls
import marinerg_facility.urls
import marinerg_test_access.urls
import marinerg_data_access.urls

router = routers.DefaultRouter()
ichec_django_core.urls.register_drf_views(router)
marinerg_facility.urls.register_drf_views(router)
marinerg_test_access.urls.register_drf_views(router)
marinerg_data_access.urls.register_drf_views(router)

urlpatterns = [
    path("api/", include(router.urls)),
    path("api/", include("marinerg_test_access.urls")),
    path("api/", include("marinerg_facility.urls")),
    path("", include("ichec_django_core.urls"))]
