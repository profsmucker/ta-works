# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from . import models
from django.urls import reverse
# Create your views here.

def apply(request):
    if request.method == 'POST':
        s_form = models.StudentForm(request.POST, instance=models.Student())
        c_forms = [models.CourseForm(request.POST, prefix=str(x), instance=x) for x in models.Course.objects.all()]
        if s_form.is_valid():
            s_form.save()
        else:
            print s_form
            print "not valid"
        # if all([cf.is_valid() for cf in c_forms]):
        #     for cf in c_forms:
        #         app = models.ApplicationForm(request.POST)
        #         continue
        return HttpResponse("done")
    else:
        c_forms = [models.CourseForm(prefix=str(x), instance=x) for x in models.Course.objects.all()]
        context = {
            's_form' : models.StudentForm(instance=models.Student()),
            'c_forms' : c_forms
            }
        return render(request, 'taform/application.html', context)
