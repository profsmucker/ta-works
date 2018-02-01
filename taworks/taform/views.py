# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import *
from django.http import HttpResponse, HttpResponseRedirect
from . import models
from django.urls import reverse
import datetime
from django.core.files.storage import FileSystemStorage
from django .contrib import messages
from django.db import connection, transaction
from django.template import loader,RequestContext
import csv
import codecs
from django.contrib.auth import logout as django_logout
import os, tempfile, zipfile
from django.conf import settings
import mimetypes
from wsgiref.util import FileWrapper
from access_tokens import scope, tokens
import uuid 
from taform.models import Course, Application, Student
from itertools import chain
from django.db.models import Q

import uuid
import os.path

def home(request):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        return render(request, 'taform/home.html')

def logout(request):
    return render(django_logout(request), 'taform/logout.html')

def login(request):
    return render(django_logout(request), 'registration/login.html') 

def intro(request): 
    if request.method == 'POST':
        return render(request, 'taform/application.html')
    return render(request, 'taform/intro.html')  

def apply(request):
    front_matter = open(front_matter_path(), "r").read()
    if request.method == 'POST':
        num = [x for x in models.Course.objects.all()]
        s_form = models.StudentForm(request.POST, request.FILES or None)
        a_forms = [models.ApplicationForm(request.POST, prefix=str(x), instance=models.Application()) for x in range(len(num))]
        context = {
                's_form' : s_form,
                'courses' : models.Course.objects.all(),
                'app_form' : a_forms,
                'error' : "Error: The student ID must be 8 characters."
                }
        try:
            studentID=str(request.POST['student_id'])
            if len(studentID) > 8:
                return render(request, 'taform/application.html', context)            
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
                    'app_form' : a_forms,
                    'front_matter' : front_matter
                    }
                return render(request, 'taform/application.html', context)
            context = None
            return HttpResponseRedirect('application_submitted.html')
        except:
            pass
    num = [x for x in models.Course.objects.all()]
    context = {
        's_form' : models.StudentForm(),
        'courses' : models.Course.objects.all(),
        'app_form' : [models.ApplicationForm(prefix=str(x), instance=models.Application()) for x in range(len(num))],
        'front_matter' : front_matter
        }
    return render(request, 'taform/application.html', context)

def application_submitted(request):
    return render(request, 'taform/application_submitted.html')

def course_list(request):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        if 'Upload' in request.POST and not request.FILES:
            return render(request, 'taform/course_list.html', {'error': 'You must select a file before uploading.'})   
        if 'Upload' in request.POST and request.FILES:
            models.TempCourse.objects.all().delete()
            f = request.FILES['csv_file']
            try:
                save_temp(f)
            except:
                return render(request, 'taform/course_list.html', {'error': 'There is an error with the CSV file. Please refer to the template and try again.'})   
            is_valid = validate_temp()  
            courses = models.TempCourse.objects.all()
            if is_valid:
                return render(request, 'taform/confirmation.html', {'courses': courses})
            else:
                return render(request, 'taform/course_list.html', {'error': 'There is an error with the CSV file. Please refer to the template and try again.'})   
        if 'Submit' in request.POST:
            copy_courses('Course', 'TempCourse')
            return render(request, 'taform/course_success.html', {})
        if 'Cancel' in request.POST:
            models.TempCourse.objects.all().delete()
            return render(request, 'taform/course_list.html', {})
        return render(request, 'taform/course_list.html', {})

def copy_courses(newtable, oldtable):
    models.Course.objects.all().delete()
    queryset = models.TempCourse.objects.all().values('term', 'course_subject', 'course_id', 'section', 'course_name', 'instructor_name', 'instructor_email','url_hash')
    newobjects = [models.Course(**values) for values in queryset]
    models.Course.objects.bulk_create(newobjects)

def send_file(request):
    filename = 'static/taform/course_template.csv' # Select your file here.
    wrapper = FileWrapper(open(filename))
    content_type = mimetypes.guess_type(filename)[0]
    response = HttpResponse(wrapper,content_type=content_type)
    response['Content-Length'] = os.path.getsize(filename)    
    response['Content-Disposition'] = 'attachment; filename=course_template.csv'
    return response
    
def validate_temp():
    courses = models.TempCourse.objects.all()
    if not courses.exists():
        return False

    for course in courses:
        if not course.term or course.term<1000 or course.term>9999 or not course.course_id or not course.course_subject or not course.section or not course.course_name:
            return False
    return True

def save_temp(f):
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
        tmp.url_hash =uuid.uuid4().hex[:26].upper()
        tmp.save()

def load_url(request, hash):
    url = get_object_or_404(models.Course, url_hash=hash)        
    courses = models.Course.objects.filter(url_hash=hash)
    course_id = courses[0].id
    apps = models.Application.objects.filter(course_id=course_id).exclude(preference=0)
    num_students = apps.count()

    student_info = []

    for i in range(0,num_students):
        temp = {}
        student = models.Student.objects.filter(id=apps[i].student_id)
        temp['student_id'] = (apps[i].student_id)
        temp['reason'] = (apps[i].reason)
        temp['first_name'] = (student[0].first_name)
        temp['last_name'] = (student[0].last_name)
        temp['email'] = (student[0].quest_id+'@uwaterloo.ca')
        temp['past_position_one'] = (student[0].past_position_one)
        temp['past_position_two'] = (student[0].past_position_two)
        temp['past_position_three'] = (student[0].past_position_three)
        temp['cv'] = (student[0].cv)
        student_info.append(temp)
   
    student_info = sorted(student_info, key=lambda k: k['first_name']) 


    if request.method == 'POST':
        num = [x for x in apps]
        form = models.InstructorForm(request.POST)
        print form.__dict__['data'].getlist('instructor_preference')
        counter = 0
        for f in range(0,num_students):
            obj = models.Application.objects.get(student_id=student_info[counter]['student_id'],course_id=course_id)
            obj.instructor_preference = form.__dict__['data'].getlist('instructor_preference')[f]
            obj.save()
            counter=counter+1
        return HttpResponseRedirect('preference_submitted.html')
    else:
        num = [x for x in apps]
        form = [models.InstructorForm(prefix=str(x), instance=models.Application()) for x in range(len(num))]
        j = 0
        for i in apps:
            form[j] = models.InstructorForm(instance=i)
            j += 1

    context = {
        'courses' : courses,
        'student' : student_info,
        'i_forms' : form
    }

    return render_to_response('taform/instructor_ranking.html', context)


def preference_submitted(request):
    return render(request, 'taform/preference_submitted.html')


def upload_front_matter(request):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        if 'Upload' in request.POST and not request.FILES:
            return render(request, 'taform/upload_front_matter.html', {'error': 'You must select a file before uploading.'})   
        if 'Upload' in request.POST and request.FILES:
            data = request.FILES.get('fm_txt')
            if data.name.split('.')[-1] != 'txt':
                return render(request, 'taform/upload_front_matter.html', {'error': 'You must select a txt file to upload.'})
            front_matter = open(front_matter_path(), "w")
            front_matter.write(data.read())
            front_matter.close()
            return render(request, 'taform/upload_front_matter.html', {'success': 'New front matter uploaded, preview by clicking home and then step 3.'})
        return render(request, 'taform/upload_front_matter.html')

def front_matter_path():
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(my_path, "../static/taform/front_matter.txt")
    return path
