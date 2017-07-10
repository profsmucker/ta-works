from django.conf.urls import url

from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    url(r'^$', views.apply, name='apply'),
    url(r'application_submitted.html', views.application_submitted, name='application_submitted'),
    url(r'course_list.html', views.course_list, name='course_list'),
    #url(r'confirmation.html', views.Course_list, name='confirmation'),
    #url(r'test.html', views.Course_list, name='test'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)