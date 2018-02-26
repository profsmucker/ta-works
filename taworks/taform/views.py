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
from django.db.models import Count, Case, When, IntegerField, Avg
import pulp

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

    emptyApps = False
    AC = authenticated(request)

    ranking_status = list(models.Application.objects.values('course__course_id', 
        'course__section', 'course__instructor_name', 'course__instructor_email', 
        'course__url_hash').annotate(count = Count(Case(When(preference = 1, 
            then = 1), When(preference = 2, then = 1), When(preference = 3, 
            then = 1), output_field = IntegerField())), 
        avgRating = Avg('instructor_preference')))
    
    for r in ranking_status:
        if(r['count']==0):
            r['status']='No Applicants'
        elif(r['avgRating'] is None):
            r['status']='Not Submitted'
        else:
            r['status']='Submitted'
    
    if not ranking_status:
        ranking_status = models.Course.objects.all()
        emptyApps = True

    if 'Upload' in request.POST:
        email_ranking_links()
        context = {
        'success' : 'Ranking email links have been sent.',
        'sent' :True,
        'ranking_status' : ranking_status,
        'AC' : AC
        }
        return render(request, 'taform/ranking_status.html', context)

    context = {
        'sent' : False,
        'ranking_status' : ranking_status,
        'emptyApps' : emptyApps,
        'AC' : AC
    }
    return render(request, 'taform/ranking_status.html', context)

@postpone
def email_ranking_links():
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
    # Google smtp has a limit of 100-150 per day 
    # https://group-mail.com/sending-email/email-send-limits-and-options/
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

def introduction(request):
    if request.method == 'POST':
        return HttpResponseRedirect('application.html')    
    return render(request, 'taform/intro.html')  

def apply(request):
    AC = authenticated(request)
    df = pd.DataFrame(list(models.ApplicationStatus.objects.all().values()))
    status_date, status, app_status = determine_status(df)
    if 'app_status' in request.POST:
        add = models.ApplicationStatus(status=(not status))
        add.save()
        df = pd.DataFrame(list(models.ApplicationStatus.objects.all().values()))
        status_date, status, app_status = determine_status(df)
        return redirect('taform/application.html')
    status_date = status_date + datetime.timedelta(hours=-5)
    front_matter = open(front_matter_path(), "r").read()
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
                'app_status' : app_status,
                'status_date': status_date
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
                    'app_status' : app_status,
                    'status_date': status_date
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
        'app_status' : app_status,
        'status_date': status_date
        }
    return render(request, 'taform/application.html', context)

def application_submitted(request):
    AC = authenticated(request)
    return render(request, 'taform/application_submitted.html', {'AC': AC})

def course_list(request):
    error_msg = 'There is an error with the CSV file. Please refer to the template and try again.'
    AC = authenticated(request)
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        if 'course_export' in request.POST:
            return course_csv()
        if 'Upload' in request.POST and not request.FILES:
            return render(request, 'taform/course_list.html', {'AC' : AC})   
        if 'Upload' in request.POST and request.FILES:
            models.TempCourse.objects.all().delete()
            f = request.FILES['csv_file']
            try:
                save_temp(f)
            except:
                return render(request, 'taform/course_list.html', 
                    {'error': error_msg, 
                    'AC' : AC})   
            is_valid = validate_temp()  
            courses = models.TempCourse.objects.all()
            if is_valid:
                return render(request, 'taform/confirmation.html', 
                    {'courses': courses, 'AC' : AC})
            else:
                return render(request, 'taform/course_list.html', 
                    {'error': error_msg, 
                    'AC' : AC})   
        if 'Submit' in request.POST:
            copy_courses('Course', 'TempCourse')
            return render(request, 'taform/course_success.html', {'AC' : AC})
        if 'Cancel' in request.POST:
            models.TempCourse.objects.all().delete()
            return render(request, 'taform/course_list.html', {'AC' : AC})
        return render(request, 'taform/course_list.html', {'AC' : AC})

def algorithm(request):
    if not request.user.is_authenticated:
        return redirect('login')
    AC = authenticated(request)
    df = pd.DataFrame(list(models.Assignment.objects.all().values()))
    max_date = None
    if not df.empty:
        max_date = max(df['created_at'])
        max_date = max_date + datetime.timedelta(hours=-5)
    context = {'AC' : AC,
               'display_date': max_date}
    if 'algo_run' in request.POST:
        df_application = pd.DataFrame(list(models.Application.objects.all().values()))
        if df_application.empty:
            context = {'AC' : AC,
               'display_date': max_date,
               'no_apps_error': 'There are no applications, no input for algorithm.'}
            return render(request, 'taform/algorithm.html', context)
        else:
            models.Assignment.objects.all().delete()
            result, costs, courses, students, courses_supply = algorithm_run()
            for c in courses:
                for s in students:
                    if result[c][s].value() != 0:
                        pass
                        course = models.Course.objects.get(id=c)
                        student = models.Student.objects.get(id=s)
                        temp = models.Assignment(course = course, student = student, score = costs[c][s])
                        temp.save()
            # if course is not assigned a student
            # add to Assignment with NULL as the student value & score
            df = pd.DataFrame(list(models.Assignment.objects.all().values()))
            max_date = None
            if not df.empty:
                max_date = max(df['created_at'])
                max_date = max_date + datetime.timedelta(hours=-5)
            context = {'AC' : AC,
                   'display_date': max_date}
            return render(request, 'taform/algorithm.html', context)
    if 'algo_export' in request.POST:
        df_assignment = pd.DataFrame(list(models.Assignment.objects.all().values()))
        if df_assignment.empty:
            context = {'AC' : AC,
               'display_date': max_date,
               'no_results_error': 
               'There are no results to export. Make sure students have applied and instructors have ranked students, then run the algorithm.'}
            return render(request, 'taform/algorithm.html', context)
        else:
            return algorithm_export()
    return render(request, 'taform/algorithm.html', context)

def algorithm_run():
    # Format course data
    df_course_info = format_course_info()
    df_course_info.drop(['course_unit'], axis = 1, inplace = True)
    # Format applicant data
    df_ranking_info = format_rankings_info()
    df_ranking_info.drop(['course_unit', 'student_unit'], axis = 1, inplace = True)
    # Format algortihm input
    courses = []
    courses_supply = dict()
    for index, row in df_course_info.iterrows():
        num_pos = row[3] + row[4] + row[5] + row[6]
        courses_supply[row[0]] = num_pos
        courses.append(row[0])
    students = []
    costs = {}
    for i in courses:
        costs[i] = []
    temp = []
    for index, row in df_ranking_info.iterrows():
        if (row[1] not in students):
            students.append(row[1])
        total_rating = row[2] + row[3]
        if (total_rating < 2):
            temp.append([row[0], row[1], 0])
        else:    
            temp.append([row[0], row[1], total_rating])
    for i in  temp:
        costs[i[0]].append(i[2])
    student_demand = dict()
    for i in students:
        student_demand[i] = 1
    costs_list = []
    for i in courses:
        costs_list.append(costs[i])
    # Algorithm run
    costs_list = pulp.makeDict([courses, students], costs_list, 0)
    prob = pulp.LpProblem("TA_Assignment", pulp.LpMaximize)
    assignment = [(c,s) for c in courses for s in students]
    x = pulp.LpVariable.dicts("decision", (courses, students), cat='Binary')
    prob += sum([x[c][s] for (c,s) in assignment]) - 0.01*sum([x[c][s]*costs_list[c][s] for (c,s) in assignment])
    for c in courses:
        prob += sum(x[c][s] for s in students) <= courses_supply[c], \
        "Sum_of_TA_Positions_%s"%c
    for c in courses:
        for s in students:
            prob += x[c][s] <= costs_list[c][s], \
            "Feasibility_{}_{}".format(s, c)
    for s in students:
        prob += sum(x[c][s] for c in courses) <= 1, \
        "Sum_of_Students_%s"%s
    prob.solve()
    return x, costs_list, courses, students, courses_supply

def algorithm_export():
    df = format_algorithm_export()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=TA_Assignment.csv'
    df.to_csv(path_or_buf=response, header=True, index=False, quoting=csv.QUOTE_NONNUMERIC)
    return response

def format_algorithm_export():
    df = pd.DataFrame(list(models.Assignment.objects.all().values()))
    df_courses = pd.DataFrame(list(models.Course.objects.all().values()))
    df_courses['course_unit'] = df_courses['course_subject'] + " " + df_courses['course_id'] + " " + df_courses['section'] + " " + df_courses['course_name']
    df_students = pd.DataFrame(list(models.Student.objects.all().values()))
    df_students['student_unit'] = df_students['first_name'] + " " + df_students['last_name'] + " <" + df_students['quest_id'] + "@edu.uwaterloo.ca>"
    df['s_id'] = df['student_id'].astype(int)
    df_students['s_id'] = df_students['id'].astype(int)
    df['c_id'] = df['course_id'].astype(int)
    df_courses['c_id'] = df_courses['id'].astype(int)
    df = df.merge(df_students, on='s_id', how='left')
    df = df.merge(df_courses, on='c_id', how='left')
    df = df.sort_values(by=['course_unit', 'student_unit'])
    df = df[['course_unit', 'student_unit', 'score']]
    return df

def copy_courses(newtable, oldtable):
    models.Course.objects.all().delete()
    queryset = models.TempCourse.objects.all().values('term', 'course_subject', 
        'course_id', 'section', 'course_name', 'instructor_name', 
        'instructor_email','url_hash')
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
        is_int = False
        try:
            int(line[3])
            is_int = True
        except:
            is_int = False
        if len(line[3]) < 3 and is_int:
            tmp.section = "{0:0>3}".format(line[3])
        else:
            tmp.section = line[3]
        tmp.course_name = line[4]
        tmp.instructor_name = line[5]
        tmp.instructor_email = line[6]
        tmp.url_hash =uuid.uuid4().hex[:26].upper()
        tmp.save()

def instructor_ranking(request, hash):
    AC = authenticated(request)
    url = get_object_or_404(models.Course, url_hash=hash)        
    course = models.Course.objects.filter(url_hash=hash)
    is_ranking_submitted = False
    courseID = course[0].id

    if request.method == 'POST':
        is_ranking_submitted = True
        s_form = models.StudentApps(request.POST)
        a_form = models.Applications(request.POST)
        apps = models.Application.objects.all().filter(course_id = courseID
            ).exclude(preference = 0).order_by('id').order_by('student__sort_name')
        j = 0
        for i in apps:
            obj = models.Application.objects.get(id = i.id)
            obj.instructor_preference = a_form.__dict__['data'].getlist(
                'instructor_preference')[j]
            obj.save()
            j += 1

    apps = models.Application.objects.all().filter(course_id = courseID
        ).exclude(preference = 0).order_by('id').order_by('student__sort_name')
    students = models.Student.objects.all().filter(application__course_id = 
        courseID).exclude(application__preference = 0).order_by('application__id').order_by('sort_name')
    num_apps = apps.count()
    num_students = students.count()

    s_form = [models.StudentApps(prefix=str(x), instance=models.Student(
        )) for x in range(num_students)]
    j = 0
    for i in students:
        s_form[j] = models.StudentApps(instance=i)
        j += 1

    a_form = [models.Applications(prefix=str(x), instance=models.Application(
        )) for x in range(num_apps)]
    k = 0
    for l in apps:
        a_form[k] = models.Applications(instance=l)
        k += 1

    updated_at = None
    if (len(apps) > 0):
        updated_at = apps[0].pref_updated_at + datetime.timedelta(hours=-5)

    context = {
        'course' : course,
        'AC' : AC,
        'is_ranking_submitted' : is_ranking_submitted,
        'success' : 'Your preferences have been updated.',
        'updated_at' : updated_at,
        's_form' : s_form,
        'a_form' : a_form,
    }

    return render(request, 'taform/instructor_ranking.html', context)


def preference_submitted(request):
    return render(request, 'taform/preference_submitted.html')


def assign_tas(request):
    if not request.user.is_authenticated:
        return redirect('login')
    AC = authenticated(request)
    is_ranking_submitted = False
    if request.method == 'POST':
        num = [x for x in models.Course.objects.all()]
        c_form = models.AssignTA(request.POST)
        courses = models.Course.objects.all().order_by(
            'section').order_by('course_id').order_by('id')
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
    updated_at = None
    if (len(courses) > 0):
        updated_at = courses[0].updated_at + datetime.timedelta(hours=-5)
    context = {
        'c_form' : c_form,
        'success' : 'The number of TAs has been successfully updated.',
        'is_ranking_submitted' : is_ranking_submitted,
        'AC' : AC,
        'updated_at' : updated_at
    }
    return render(request, 'taform/number_tas.html', context)

def resume_view(request, respath):
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = my_path + "/media/" + respath
    with open(path, 'r') as pdf:
        response = HttpResponse(pdf.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'inline;filename=' + respath
        return response
    pdf.closed

def upload_front_matter(request):
    AC = authenticated(request)
    context = {'AC' : AC}
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        if 'Upload' in request.POST and not request.FILES:
            return render(request, 'taform/upload_front_matter.html', 
                {'error': 'You must select a file before uploading.', 'AC' : AC})   
        if 'Upload' in request.POST and request.FILES:
            data = request.FILES.get('fm_txt')
            if data.name.split('.')[-1] != 'txt':
                return render(request, 'taform/upload_front_matter.html', 
                    {'error': 'You must select a txt file to upload.', 'AC' : AC})
            front_matter = open(front_matter_path(), "w")
            front_matter.write(data.read())
            front_matter.close()
            return render(request, 'taform/upload_front_matter.html', 
                {'success': 'New front matter uploaded, preview by clicking home and then step 3.', 'AC' : AC})
        return render(request, 'taform/upload_front_matter.html', {'AC' : AC})

def front_matter_path():
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(my_path, "../static/taform/front_matter.txt")
    return path

def export(request):
    AC = authenticated(request)
    context = {'AC' : AC}
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        if 'course_info' in request.POST:
            return export_course_info()
        if 'rankings_info' in request.POST:
            return export_ranking_info()
        return render(request, 'taform/export.html', context)

def export_course_info():
    df = format_course_info()
    df.drop(['id'], axis = 1, inplace = True)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=1_course-info.csv'
    df.to_csv(path_or_buf=response,header=True, index=False)
    return response

def format_course_info():
    df = pd.DataFrame(list(models.Course.objects.all().values()))
    df['course_unit'] = df['course_subject'] + " " + df['course_id'] + " " + df['section'] + " " + df['course_name']
    df.drop(['course_subject', 'course_id', 'section', 'course_name', 'term', 'url_hash'], axis = 1, inplace = True)
    df = df[['id', 'course_unit', 'instructor_name', 'instructor_email', 'full_ta', 'three_quarter_ta', 'half_ta', 'quarter_ta']]
    return df

def export_ranking_info():
    df = format_rankings_info()
    df = df[df.instructor_preference != 0]
    df = df[df.student_preference != 0]
    df.drop(['c_id', 's_id'], axis = 1, inplace = True)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=2_ranking-info.csv'
    df.to_csv(path_or_buf=response,header=True, index=False)
    return response

def format_rankings_info():
    df_courses = pd.DataFrame(list(models.Course.objects.all().values()))
    df_courses['course_num'] = df_courses['course_id']
    df_courses['course_unit'] = df_courses['course_subject'] + " " + df_courses['course_num'] + " " + df_courses['section'] + " " + df_courses['course_name']
    df_courses['c_id'] = df_courses['id']
    df_courses.drop(['course_id', 'id', 'term', 'url_hash', 'full_ta', 'half_ta', 'quarter_ta', 
        'three_quarter_ta', 'instructor_name', 'instructor_email'], axis = 1, inplace = True)
    # get applications info & remove unneccasary columns
    df_apps = pd.DataFrame(list(models.Application.objects.all().values()))
    df_apps['student_preference'] = df_apps['preference']
    df_apps.drop(['id', 'reason', 'reason', 'application_date', 'preference'], axis = 1, inplace = True)
    # get students info & remove unneccasary columns
    df_students = pd.DataFrame(list(models.Student.objects.all().values()))
    df_students['email'] = df_students['quest_id'] + "@edu.uwaterloo.ca"
    df_students['student_unit'] = df_students['first_name'] + " " + df_students['last_name'] + " <" + df_students['email'] +">"
    df_students['s_id'] = df_students['id']
    df_students.drop(['id', 'student_id', 'quest_id', 'department', 'current_program', 'citizenship', 
        'student_visa_expiry_date', 'enrolled_status', 'ta_expectations', 'cv',  'full_ta', 
        'half_ta'], axis = 1, inplace = True)
    # join courses & applications & students
    df = df_apps.merge(df_courses, left_on='course_id', right_on='c_id', how='left')
    df = df.merge(df_students, left_on='student_id', right_on='s_id', how='left')
    df = df.sort_values(by=['course_subject', 'course_num', 'section', 's_id'])
    # format the columns for export
    df.drop(['course_subject', 'course_id', 'section', 'course_name', 'student_id', 
        'first_name', 'last_name', 'email'], axis = 1, inplace = True)
    df = df[['c_id', 's_id', 'course_unit', 'student_unit', 'instructor_preference', 'student_preference']]
    df[['instructor_preference']] = df[['instructor_preference']].fillna(0).astype(int)
    return df

def course_csv():
    df = pd.DataFrame(list(models.Course.objects.all().values()))
    df.drop(['id', 'url_hash',  'full_ta', 'three_quarter_ta', 'half_ta', 'quarter_ta'], axis = 1, inplace = True)
    df = df[['term', 'course_subject','course_id', 'section', 'course_name','instructor_name', 'instructor_email']]
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=course_template.csv'
    df = df.sort_values(by=['course_subject', 'course_id', 'section'])
    df.to_csv(path_or_buf=response, header=False, index=False, quoting=csv.QUOTE_NONNUMERIC)
    return response

def determine_status(df):
    status = False
    if df.empty:
        status_date = datetime.datetime.now()
    else:
        df_max = df[df.status_date == max(df['status_date'])]
        status_date = df_max.iloc[0]['status_date']
        status = df_max.iloc[0]['status']
    app_status = 'Open' if status else 'Closed' 
    return (status_date, status, app_status)

def authenticated(request):
    AC = False
    if request.user.is_authenticated:
        AC = True
    return AC