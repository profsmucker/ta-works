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
import os.path
from django.core import mail
from threading import Thread
import pandas as pd

# This is to provide annotation for methods that need a separate thread
def postpone(function):
  def decorator(*args, **kwargs):
    t = Thread(target = function, args=args, kwargs=kwargs)
    t.daemon = True
    t.start()
  return decorator

def ranking_status(request):
    if not request.user.is_authenticated:
        return redirect('login')
    elif 'Upload' in request.POST:
        email_ranking_links(request.POST['email'])
        return render(request, 'taform/ranking_status.html', 
            {'success': 'Ranking email links have been sent.', 'sent': True })
    return render(request, 'taform/ranking_status.html', {'sent': False})

@postpone
def email_ranking_links(report_email = None):
    connection = mail.get_connection()
    connection.open()

    courses = models.Course.objects.all()
    email = []

    for i, course in enumerate(courses):
        tmp = mail.EmailMessage(
            'TA Ranking Form for {course_name}'.format(
                course_name = course.course_name),
            """
            <div>Dear {instructor},</div>
            <br/>
            <div>Please click on the link below and follow the instructions to
            complete and submit your rankings for the course 
            ({subject} {id}-{section})</div>
            <br/>
            <div>Link to Ranking Page: 
            https://team4.uwaterloo.ca/taform/instructor/{url}</div>
            <br/>
            <div>Regards,</div>
            <div>Associate Chair for Undergraduate Studies, Management Sciences
            </div>
            <br/>
            <div><b>*Note: If you are the Instructor for more than one course in the 
            upcoming term, you will receive an email for each course. Important: 
            Links are specific to each class.
            You may also need to be on campus wifi or vpn if you are remote.</b></div>
            """.format(instructor = course.instructor_name, 
                subject = course.course_subject, id = course.course_id, 
                section = course.section, url = course.url_hash),
            'uwtaworks@gmail.com',
            [course.instructor_email],
            ['uwtaworks@gmail.com'],
            connection=connection,
        )
        tmp.content_subtype = 'html'
        email.append(tmp)

    if (len(report_email) > 0):
        # filter courses for emails without @ symbol
        missing_instructor_email =models.Course.objects.all().exclude(
            instructor_email__contains='@')
        # filter courses for emails with @ symbol
        have_instructor_email = models.Course.objects.all().filter(
            instructor_email__contains='@')

        missing_emails, email_list = "", ""

        for i in missing_instructor_email:
            missing_emails += '<div>{subject} {id}-{section} {instructor_name} (Email N/A)</div>'.format(
                subject = i.course_subject, id = i.course_id, section = i.section, 
                instructor_name = i.instructor_name)


        for i in have_instructor_email:
            email_list += '<div>{subject} {id}-{section} {instructor_name} ({instructor_email})</div>'.format(
                subject = i.course_subject, id = i.course_id, section = i.section, 
                instructor_name = i.instructor_name, 
                instructor_email = i.instructor_email)

        ac_email = mail.EmailMessage(
            'RANKING EMAILS SENT - TAWORKS SYSTEM REPORT',
            """
            <div><b>***TAWORKS EMAIL REPORT***</b></div>
            <br/>
            <div>Emails with request for rankings have been sent to course instructors.
            If no email was available please login to the system and provide 
            rankings for those courses:</div>
            <br/>
            <div><font color="red"><b>No Email Available</b></font></div>
            {missing_email_list}
            <br/>
            <div><font color="red"><b>Success – Emails sent to Instructors</b></font></div>
            {successful_email_list}
            <br/>
            <div>To complete rankings for courses and view Instructor submitted rankings,
            <a href="https://team4.uwaterloo.ca/login">login to the 
            Rankings Status page in TAWorks</a>.</div>
            """.format(missing_email_list = missing_emails, 
                successful_email_list = email_list),
            'uwtaworks@gmail.com',
            [report_email],
            connection=connection
        )
        ac_email.content_subtype = 'html'
        email.append(ac_email)

    # Google smtp has a limit of 100-150 per day https://group-mail.com/sending-email/email-send-limits-and-options/
    # It'll take a while for MSCI to hit 100 instructors, just an FYI here
    connection.send_messages(email)
    connection.close()

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
        return HttpResponseRedirect('application.html')    
    return render(request, 'taform/intro.html')  

def apply(request):
    front_matter = open(front_matter_path(), "r").read()
    AC = False
    if request.user.is_authenticated:
        AC = True
    if request.method == 'POST':
        num = [x for x in models.Course.objects.all()]
        s_form = models.StudentForm(request.POST, request.FILES or None)
        a_forms = [models.ApplicationForm(request.POST, prefix=str(x), 
            instance=models.Application()) for x in range(len(num))]
        context = {
                's_form' : s_form,
                'courses' : models.Course.objects.all(),
                'app_form' : a_forms,
                'error' : "Error: The student ID must be 8 characters.",
                'AC' : AC,
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
                    'front_matter' : front_matter,
                    'AC' : AC,
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
        'app_form' : [models.ApplicationForm(prefix=str(x), 
            instance=models.Application()) for x in range(len(num))],
        'front_matter' : front_matter,
        'AC' : AC,
        }
    return render(request, 'taform/application.html', context)

def application_submitted(request):
    return render(request, 'taform/application_submitted.html')

def course_list(request):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        if 'course_export' in request.POST:
            return course_CSV()
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
    apps = models.Application.objects.filter(course_id=course_id).exclude(preference=0).order_by('student__first_name')
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
        temp['cv'] = (student[0].cv)
        student_info.append(temp)

    if request.method == 'POST':
        form = models.InstructorForm(request.POST)
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

    return render(request, 'taform/instructor_ranking.html', context)


def preference_submitted(request):
    return render(request, 'taform/preference_submitted.html')


def assign_tas(request):
    if not request.user.is_authenticated:
        return redirect('login')
    is_ranking_submitted = False
    if request.method == 'POST':
        num = [x for x in models.Course.objects.all()]
        c_form = models.AssignTA(request.POST)
        courses = models.Course.objects.all().order_by('section').order_by('course_id').order_by('id')
        is_ranking_submitted = True
        j = 0
        for i in courses:
            obj = models.Course.objects.get(id=i.id)
            obj.full_ta = c_form.__dict__['data'].getlist('full_ta')[j]
            obj.three_quarter_ta = c_form.__dict__['data'].getlist('three_quarter_ta')[j]
            obj.half_ta = c_form.__dict__['data'].getlist('half_ta')[j]
            obj.quarter_ta = c_form.__dict__['data'].getlist('quarter_ta')[j]
            obj.save()
            j += 1
        
    courses = models.Course.objects.all().order_by('section').order_by('course_id').order_by('id')
    num = [x for x in models.Course.objects.all()]
    c_form = [models.AssignTA(prefix=str(x), instance=models.Course()) for x in range(len(num))]
    j = 0
    for i in courses:
        c_form[j] = models.AssignTA(instance=i)
        j += 1
    context = {
        'c_form' : c_form,
        'success' : 'The number of TAs has been successfully updated.',
        'is_ranking_submitted' : is_ranking_submitted,
    }
    return render(request, 'taform/number_tas.html', context)

def upload_front_matter(request):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        if 'Upload' in request.POST and not request.FILES:
            return render(request, 'taform/upload_front_matter.html', 
                {'error': 'You must select a file before uploading.'})   
        if 'Upload' in request.POST and request.FILES:
            data = request.FILES.get('fm_txt')
            if data.name.split('.')[-1] != 'txt':
                return render(request, 'taform/upload_front_matter.html', 
                    {'error': 'You must select a txt file to upload.'})
            front_matter = open(front_matter_path(), "w")
            front_matter.write(data.read())
            front_matter.close()
            return render(request, 'taform/upload_front_matter.html', 
                {'success': 'New front matter uploaded, preview by clicking home and then step 3.'})
        return render(request, 'taform/upload_front_matter.html')

def front_matter_path():
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(my_path, "../static/taform/front_matter.txt")
    return path

def export(request):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        if 'course_info' in request.POST:
            return export_TA_count()
        if 'rankings_info' in request.POST:
            return export_Rankings()
        return render(request, 'taform/export.html')

def export_TA_count():
    df = pd.DataFrame(list(models.Course.objects.all().values()))
    df['course_unit'] = df['course_subject'] + " " + df['course_id'] + " " + df['section'] + " " + df['course_name']
    df.drop(['course_subject', 'course_id', 'section', 'course_name', 'term', 'id', 'url_hash'], axis = 1, inplace = True)
    df = df[['course_unit', 'instructor_name', 'instructor_email', 'full_ta', 'three_quarter_ta', 'half_ta', 'quarter_ta']]
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=1_course-info.csv'
    df.to_csv(path_or_buf=response,header=False, index=False)
    return response

def export_Rankings():
    # get courses info & remove unneccasary columns
    df_courses = pd.DataFrame(list(models.Course.objects.all().values()))
    df_courses['course_num'] = df_courses['course_id']
    df_courses['course_unit'] = df_courses['course_subject'] + " " + df_courses['course_num'] + " " + df_courses['section'] + " " + df_courses['course_name']
    df_courses['c_id'] = df_courses['id']
    df_courses.drop(['course_id', 'id', 'term', 'url_hash', 'full_ta', 'half_ta', 'quarter_ta', 
        'three_quarter_ta', 'instructor_name', 'instructor_email'], axis = 1, inplace = True)
    # get applications info & remove unneccasary columns
    df_apps = pd.DataFrame(list(models.Application.objects.all().values()))
    df_apps = df_apps[df_apps.preference != 0]
    df_apps = df_apps[df_apps.instructor_preference != 0]
    df_apps.drop(['id', 'reason', 'reason', 'application_date'], axis = 1, inplace = True)
    # get students info & remove unneccasary columns
    df_students = pd.DataFrame(list(models.Student.objects.all().values()))
    df_students['email'] = df_students['quest_id'] + "@edu.uwaterlo.ca"
    df_students['student_unit'] = df_students['first_name'] + " " + df_students['last_name'] + " (" + df_students['email'] +")"
    df_students['s_id'] = df_students['id']
    df_students.drop(['id', 'student_id', 'quest_id', 'department', 'current_program', 'citizenship', 
        'student_visa_expiry_date', 'enrolled_status', 'ta_expectations', 'cv',  'full_ta', 
        'three_quarter_ta', 'half_ta', 'quarter_ta'], axis = 1, inplace = True)
    # join courses & applications & students
    df = df_apps.merge(df_courses, left_on='course_id', right_on='c_id', how='left')
    df = df.merge(df_students, left_on='student_id', right_on='s_id', how='left')
    # format the columns for export
    df.drop(['course_subject', 'course_id', 'section', 'course_name', 'c_id', 's_id', 'student_id', 
        'first_name', 'last_name', 'email'], axis = 1, inplace = True)
    df = df[['course_unit', 'student_unit', 'instructor_preference', 'preference']]
    # export
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=2_ranking-info.csv'
    df.to_csv(path_or_buf=response,header=False, index=False)
    return response

def course_CSV():
    df = pd.DataFrame(list(models.Course.objects.all().values()))
    df.drop(['id', 'url_hash',  'full_ta', 'three_quarter_ta', 'half_ta', 'quarter_ta'], axis = 1, inplace = True)
    df = df[['term', 'course_subject','course_id', 'section', 'course_name','instructor_name', 'instructor_email']]
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=course_template.csv'
    df.to_csv(path_or_buf=response, index=False, header=True,
         quoting=csv.QUOTE_NONNUMERIC)
    return response