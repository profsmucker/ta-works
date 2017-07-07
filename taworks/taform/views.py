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
        a_forms = [models.ApplicationForm(request.POST)]
        print a_forms, "THIS IS A FORMS"
        if s_form.is_valid():
            s = s_form.save()
            print s.id, "THIS -----------"
            q = models.Application()
            q.student = models.Student.objects.get(id=s.id)
            q.course = models.Course.objects.get(id=7)
            q.save()
        else:
            # print s_form
            print "not valid"
        # print c_forms[0], "this is the first course"
        # if all([cf.is_valid() for cf in c_forms]):
            # print 'c_form valid'
        # else:
            # print 'c_form not valid'
            # for cf in c_forms:
            #     app = models.ApplicationForm(request.POST)
            #     if app.is_valid():
            #         app.save()
            #     else:
            #         print "app not valid"
            #     continue
        return HttpResponse("done")
    else:
        c_forms = [models.CourseForm(prefix=str(x), instance=x) for x in models.Course.objects.all()]
        context = {
            's_form' : models.StudentForm(instance=models.Student()),
            'courses' : models.Course.objects.all(),
            'app_form' : [models.ApplicationForm(prefix=str(x), instance=models.Application()) for x in range(2)]
            }
        return render(request, 'taform/application.html', context)
