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
    url(r'login.html', views.login, name='login'),
    url(r'static/taform/course_template.csv', views.send_file, name='send_file'),
    url(r'intro.html', views.intro, name='intro'),
    url(r'^instructor/(?P<hash>\w+)/$', views.load_url, name='url'),
    url(r'preference_submitted.html', views.preference_submitted, name='preference_submitted'),
    url(r'upload_front_matter.html', views.upload_front_matter, name='upload_front_matter')
]

if settings.DEBUG is True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
