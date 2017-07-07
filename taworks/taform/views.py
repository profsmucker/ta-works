# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from . import models
from django.urls import reverse
import datetime
# Create your views here.

def apply(request):
    if request.method == 'POST':
        num = [x for x in models.Course.objects.all()]
        s_form = models.StudentForm(request.POST, instance=models.Student())
        a_forms = [models.ApplicationForm(request.POST, prefix=str(x), instance=models.Application()) for x in range(len(num))]
        print a_forms, "THIS IS A FORMS"
        if s_form.is_valid() and all([app.is_valid() for app in a_forms]):
            s = s_form.save()
            print s.id, "THIS -----------"
            course_number = 0
            for app in a_forms:
                app = app.save(commit=False)
                print app
                app.student = models.Student.objects.get(id=s.id)
                print app.student, 'afterwards'
                app.course = num[course_number]
                app.application_date = str(datetime.datetime.now())
                app.save()
                print 'save the app', app
                course_number += 1
            # q = models.Application()
            # q.student = models.Student.objects.get(id=s.id)
            # q.course = models.Course.objects.get(id=7)
            # q.save()
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
        num = [x for x in models.Course.objects.all()]
        context = {
            's_form' : models.StudentForm(instance=models.Student()),
            'courses' : models.Course.objects.all(),
            'app_form' : [models.ApplicationForm(prefix=str(x), instance=models.Application()) for x in range(len(num))]
            }
        return render(request, 'taform/application.html', context)
