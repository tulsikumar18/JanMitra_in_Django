from django.contrib import admin

from django.urls import include, path

from django.views.generic import TemplateView

from django.conf import settings

from django.conf.urls.static import static

from django.conf.urls.i18n import set_language


urlpatterns = [
    path("admin/",admin.site.urls),
    path("",TemplateView.as_view(template_name="home.html"),name="home"),
    path("users/",include("apps.users.urls")),
    path("issues/",include("apps.issues.urls")),
    path("i18n/setlang/",set_language,name="set_language"),
    path("rewards/", include("apps.rewards.urls")),
    path("notifications/", include("apps.notifications.urls")),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)