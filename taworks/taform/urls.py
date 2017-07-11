from django.conf.urls import url
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    url(r'^$', views.apply, name='apply'),
    url(r'application.html', views.apply, name='application'),
    url(r'application_submitted.html', views.application_submitted, name='application_submitted'),
    url(r'course_list.html', views.course_list, name='course_list'),
    url(r'home.html', views.home, name='home'),
    url(r'logout.html', views.logout, name='logout'),
    url(r'static/taform/course_template.csv', views.send_file, name='send_file'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
