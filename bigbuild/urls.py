from django.conf.urls import url
from bigbuild import views

urlpatterns = [
    # Static assets
    url(
        r'^projects/(?P<slug>[-\w]+)/static/(?P<path>.*)$',
        views.page_static_serve,
        name='page-detail-static'
    ),
]
