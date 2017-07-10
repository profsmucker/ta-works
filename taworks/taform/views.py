# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from . import models
from django.urls import reverse
import datetime
from django.core.files.storage import FileSystemStorage

def apply(request):
    if request.method == 'POST':
        num = [x for x in models.Course.objects.all()]
        s_form = models.StudentForm(request.POST, request.FILES or None)
        a_forms = [models.ApplicationForm(request.POST, prefix=str(x), instance=models.Application()) for x in range(len(num))]
        if s_form.is_valid() and all([app.is_valid() for app in a_forms]):
            s = s_form.save(commit=True)
            course_number = 0
            for app in a_forms:
                app = app.save(commit=False)
                app.student = models.Student.objects.get(id=s.id)
                app.course = num[course_number]
                app.save()
                course_number += 1
        else:
            context = {
                's_form' : s_form,
                'courses' : models.Course.objects.all(),
                'app_form' : a_forms
                }
            return render(request, 'taform/application.html', context)
        context = None
        return HttpResponseRedirect('application_submitted.html')
    else:
        num = [x for x in models.Course.objects.all()]
        context = {
            's_form' : models.StudentForm(),
            'courses' : models.Course.objects.all(),
            'app_form' : [models.ApplicationForm(prefix=str(x), instance=models.Application()) for x in range(len(num))]
            }
        return render(request, 'taform/application.html', context)

def application_submitted(request):
    return render(request, 'taform/application_submitted.html')
