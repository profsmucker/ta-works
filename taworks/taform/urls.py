from django.conf.urls import url
from . import views
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordChangeView,
    PasswordChangeDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView
)

urlpatterns = [
    url(r'^$', views.introduction, name='introduction'),
    url(r'application.html', views.apply, name='application'),
    url(r'application_submitted.html', views.application_submitted, name='application_submitted'),
    url(r'course_list.html', views.course_list, name='course_list'),
    url(r'home.html', views.home, name='home'),
    url(r'logout.html', views.logout, name='logout'),
    url(r'login/$', auth_views.login, name='login'),
    url(r'static/taform/course_template.csv', views.send_file, name='send_file'),
    url(r'^instructor/(?P<hash>\w+)/$', views.instructor_ranking, name='instructor_ranking'),
    url(r'^modify_apps/(?P<student_pk>\w+)/$', views.modify_apps, name='modify_apps'),
    url(r'number_tas.html', views.assign_tas, name='number_tas'),
    url(r'upload_front_matter.html', views.upload_front_matter, name='upload_front_matter'),
    url(r'ranking_status.html', views.ranking_status, name='ranking_status'),
    url(r'export.html', views.export, name='export'),
    url(r'^password_change/$',
        PasswordChangeView.as_view(template_name='accounts/password_change_form.html'),
        name='password_change'),
    url(r'^password_change/done/$',
        PasswordChangeDoneView.as_view(template_name='accounts/password_change_done.html'),
        name='password_change_done'),

    url(r'^password_reset/$',
        PasswordResetView.as_view(template_name='accounts/password_reset_form.html'),
        name='password_reset'),
    url(r'^password_reset/done/$',
        PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'),
        name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'),
        name='password_reset_confirm'),
    url(r'^reset/done/$',
        PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'),
        name='password_reset_complete'),
    url(r'^favicon.ico/$', lambda x: HttpResponseRedirect(settings.STATIC_URL+'favicon/favicon.ico')),
    url(r'^media/(?P<respath>.*)$', views.resume_view, name='res'),
    url(r'algorithm.html', views.algorithm, name='algorithm'),
    url(r'applicants.html', views.applicants, name='applicants'),
    url(r'student/(?P<pk>[\w-]+)$', views.StudentUpdate.as_view(), name='student_update'),  
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)