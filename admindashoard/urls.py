from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views


urlpatterns = [
    path("", views.site_admindash, name='homeadmin'),
    path("interests/",views.interests_by_user , name='intersts'),
    path("enrich/",views.enrich , name='enrich')
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


