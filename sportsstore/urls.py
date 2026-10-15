from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "BoltSports Administration"
admin.site.site_title = "BoltSports Admin Portal"
admin.site.index_title = "Welcome to BoltSports Dashboard"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('store.urls')),
]

# Serve uploaded product images while developing
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
