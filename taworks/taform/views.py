# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from . import models
from django.urls import reverse
# Create your views here.

def index(request):
    context = {
        'student_form' : models.StudentForm(),
        'course_form' : models.Course.objects.using('mysql').all(),
        'application_form' : models.ApplicationForm()
    }
    return render(request, 'taform/application.html', context)
