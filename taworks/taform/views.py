# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from . import models
from django.urls import reverse
import datetime
from django.core.files.storage import FileSystemStorage
<<<<<<< HEAD
from django .contrib import messages
=======
from django.db import connection, transaction
from django.template import loader
import csv
import codecs
>>>>>>> master

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

def course_list(request):
    if 'Upload' in request.POST and request.FILES:
        models.TempCourse.objects.all().delete()
        f = request.FILES['csv_file']
        SaveTemp(f)
        courses = models.TempCourse.objects.all()
        template = loader.get_template("taform/confirmation.html")
        return render(request, 'taform/confirmation.html', {'courses': courses})
    if 'Submit' in request.POST:
        CopyCourses('Course', 'TempCourse')
        return render(request, 'taform/test.html', {})
    if 'Cancel' in request.POST:
        models.TempCourse.objects.all().delete()
        return render(request, 'taform/course_list.html', {})
    return render(request, 'taform/course_list.html', {})

def SaveTemp(f):
    csvreader = csv.reader(f)
    next(csvreader)
    for line in csvreader:
        tmp = models.TempCourse.objects.create()
        tmp.term = line[0]
        tmp.course_subject = line[1]
        tmp.course_id = line[2]
        tmp.section = line[3]
        tmp.course_name = line[4]
        tmp.instructor_name = line[5]
        tmp.instructor_email = line[6]
        tmp.save()

def CopyCourses(newtable, oldtable):
    models.Course.objects.all().delete()
    queryset = models.TempCourse.objects.all().values('term', 'course_subject', 'course_id', 'section', 'course_name', 'instructor_name', 'instructor_email')
    newobjects = [models.Course(**values) for values in queryset]
    models.Course.objects.bulk_create(newobjects)

