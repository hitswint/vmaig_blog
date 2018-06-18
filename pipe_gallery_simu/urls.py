from django.conf.urls import url
from django.views.generic import TemplateView, DetailView, RedirectView
from pipe_gallery_simu.views import PipegalleryView

urlpatterns = [
    url(r'^pipe_gallery/$', PipegalleryView.as_view(),
        name='pipegallery-view'),
    url(r'^pipe_gallery/simu/$',
        PipegalleryView.simu_submit,
        name='pipegallery-simu-view'),
    url(r'^pipe_gallery/go-to-django/$',
        RedirectView.as_view(url='http://djangoproject.com'),
        name='pipegallery-go-to-django'),
]
