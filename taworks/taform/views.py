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
from django.template import loader, RequestContext
import csv
from django.contrib.auth import logout as django_logout
import os, tempfile, zipfile
from django.conf import settings
import mimetypes
from wsgiref.util import FileWrapper
import os.path
from django.core import mail
from threading import Thread
import pandas as pd
from django.db.models import Count, Case, When, IntegerField, Avg
import pulp
import math
from django.views.generic.edit import UpdateView
from django.core.mail import send_mail
from .utils import upload

class StudentUpdate(UpdateView):
    form_class = models.StudentEditForm
    model = models.Student
    success_url = '../applicants.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        return super(StudentUpdate, self).dispatch(
            request, *args, **kwargs)

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

    emptyCourses = False
    noApps = False
    AC = authenticated(request)

    courses = models.Course.objects.all().order_by('course_subject','course_id','section')
    ranking_status = list(models.Course.objects.values('course_subject', 'course_id', 'section', 'instructor_name', 'instructor_email', 'url_hash'
        ).filter(application__student__is_disqualified = False).annotate(count=Count(Case(When(application__preference = 1, then = 1
            ), When(application__preference = 2, then = 1), When(application__preference = 3, then = 1
            ),output_field = IntegerField())),avgRating=Avg('application__instructor_preference')
        ).order_by('course_subject','course_id','section'))

    for r in ranking_status:
        if(r['count']==0):
            r['status']='No Applicants'
        elif(r['avgRating']==0):
            r['status']='No Students Ranked'
        else:
            r['status']='Submitted'


    if not courses:
        emptyCourses = True

    if courses and not ranking_status:
        noApps = True


    if 'Upload' in request.POST:
        email_ranking_links(request)
        context = {
        'success' : 'Ranking email links have been sent.',
        'sent' :True,
        'ranking_status' : ranking_status,
        'AC' : AC,
        'emptyCourses' : emptyCourses,
        'noApps': noApps,
        'courses': courses,
        }
        return render(request, 'taform/ranking_status.html', context)

    context = {
        'sent' : False,
        'ranking_status' : ranking_status,
        'emptyCourses' : emptyCourses,
        'AC' : AC,
        'noApps': noApps,
        'courses': courses,
    }
    return render(request, 'taform/ranking_status.html', context)

@postpone
def email_ranking_links(request):
    courses = models.Course.objects.all()

    for i, course in enumerate(courses):
        subject = 'TA Ranking Form for {course_name}'.format(course_name = course.course_name)
        message = """
            <div>Dear {instructor},</div>
            <br/>
            <div>Please click on the link below and follow the instructions to
            complete and submit your rankings for the course 
            ({subject} {id}-{section})</div>
            <br/>
            <div>Link to Ranking Page: 
            {url}</div>
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
                section = course.section, url = (request.build_absolute_uri( '/taform/instructor/' )+ course.url_hash ) )
        send_mail(subject, '', "Associate Chair <{}>".format(os.environ.get('DJANGO_EMAIL_REPLY_TO')), [course.instructor_email, os.environ.get('DJANGO_EMAIL_REPLY_TO')], fail_silently=False, html_message=message)

def home(request):
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        return render(request, 'taform/home.html')

def applicants(request):
    if not request.user.is_authenticated:
        return redirect('login')
    AC = authenticated(request)
    students = models.Student.objects.all().order_by('first_name', 'last_name')
    for i in students:
        i.created_at += datetime.timedelta(hours=-5)
    context = {'AC':AC,
               'students' : students,
               'error': 'Sorry, there are no applicants to display.'}
    if 'export_applicants' in request.POST:
        return export_applicants()
    return render(request, 'taform/applicants.html', context)

def export_applicants():
    df_students = pd.DataFrame(list(models.Student.objects.all().values()))
    df_students = df_students.sort_values(by=['first_name', 'last_name'])
    df_students['email'] = '<' + df_students['quest_id'] + '@uwaterloo.ca>'
    df_students['ta_expectations'] = df_students['ta_expectations'].replace(False, 'No')
    df_students['ta_expectations'] = df_students['ta_expectations'].replace(True, 'Yes')
    df_students['is_disqualified'] = df_students['is_disqualified'].replace(False, 'No')
    df_students['is_disqualified'] = df_students['is_disqualified'].replace(True, 'Yes')
    df_students['created_at'] = df_students['created_at'] + datetime.timedelta(hours=-5)
    df_students['created_at'] = df_students['created_at'].dt.strftime("%Y-%M-%d %H:%M %p")
    df_students = df_students[['is_disqualified', 'student_id', 'first_name', 'last_name', 'email', 'citizenship', 
    'student_visa_expiry_date', 'department', 'current_program','enrolled_status', 'ta_expectations',
    'created_at']]
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=applicant_info.csv'
    df_students.to_csv(path_or_buf=response, header=True, index=False, quoting=csv.QUOTE_NONNUMERIC,encoding='utf-8')
    return response

def logout(request):
    return render(django_logout(request), 'taform/logout.html')

def introduction(request):
    AC = authenticated(request)
    intro_page = open(intro_page_path(), "r").read()
    if request.method == 'POST':
        return HttpResponseRedirect('application.html')    
    return render(request, 'taform/intro.html', {'intro_page': intro_page, 'AC': AC})  

def apply(request):
    AC = authenticated(request)
    df = pd.DataFrame(list(models.ApplicationStatus.objects.all().values()))
    status_date, status, app_status = determine_status(df)
    courses = models.Course.objects.all().order_by('course_subject','course_id','section')
    if 'app_status' in request.POST:
        add = models.ApplicationStatus(status=(not status))
        add.save()
        df = pd.DataFrame(list(models.ApplicationStatus.objects.all().values()))
        status_date, status, app_status = determine_status(df)
        return redirect('taform/application.html')
    status_date = status_date + datetime.timedelta(hours=-5)
    front_matter = open(front_matter_path(), "r").read()
    if request.method == 'POST':
        num = [x for x in models.Course.objects.all().order_by('course_subject','course_id','section')]
        s_form = models.StudentForm(request.POST, request.FILES or None)
        a_forms = [models.ApplicationForm(request.POST, prefix=str(x), 
            instance=models.Application()) for x in range(len(num))]
        context = {
                's_form' : s_form,
                'courses' : courses,
                'app_form' : a_forms,
                'error' : "Student Visa Expiration Date is required if you've "+
                "selected 'Student Visa' as citizenship status.",
                'AC' : AC,
                'app_status' : app_status,
                'status_date': status_date,
                'front_matter': front_matter,
                }
        try:
            citizenship=str(request.POST['citizenship'])
            visa_expiry=str(request.POST['student_visa_expiry_date'])
            if (citizenship == 'Student Visa') and (not visa_expiry):
                return render(request, 'taform/application.html', context)            
            if s_form.is_valid() and all([app.is_valid() for app in a_forms]):
                s = s_form.save(commit=True)
                app_id = s.id
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
                    'courses' : courses,
                    'app_form' : a_forms,
                    'front_matter' : front_matter,
                    'AC' : AC,
                    'app_status' : app_status,
                    'status_date': status_date
                    }
                return render(request, 'taform/application.html', context)
            
            student_id = str(request.POST['student_id'])
            multiple_apps = models.Student.objects.all().filter(student_id=student_id).count()

            if multiple_apps > 1:
               previous_submissions = True
            else:
                previous_submissions = False

            new_apps = models.Application.objects.filter(student_id=app_id).order_by('course__course_subject', 'course__course_id', 'course__section')
            created_at = new_apps[0].application_date + datetime.timedelta(hours=-5)

            context = {
            'AC' : AC,
            'new_apps' : new_apps,
            'student_id' : student_id,
            'app_id' : app_id,
            'previous_submissions': previous_submissions,
            'created_at': created_at,
            'courses': courses,
            }
            return render(request, 'taform/application_submitted.html', context)
        except:
            pass
    num = [x for x in models.Course.objects.all()]
    context = {
        's_form' : models.StudentForm(),
        'courses' :courses,
        'app_form' : [models.ApplicationForm(prefix=str(x), 
            instance=models.Application()) for x in range(len(num))],
        'front_matter' : front_matter,
        'AC' : AC,
        'app_status' : app_status,
        'status_date': status_date
        }
    return render(request, 'taform/application.html', context)

def upload_course_list(request):
    AC = authenticated(request)
    errors = []
    df_courses = pd.DataFrame()
    if not request.user.is_authenticated:
        return redirect('login')
    elif 'course_export' in request.POST:
        df = pd.DataFrame(list(models.Course.objects.all().values()))
        if df.empty:
            upload.template_courses()    
        return course_csv()
    elif 'courseUpload' in request.POST and not request.FILES:
        errors.append('You must select a comma separated file for upload.') 
    elif 'courseUpload' in request.POST and request.FILES:
        file = request.FILES['csv_file']
        if file.name.split('.')[-1] != 'csv':
            errors.append('The file extension must end in .csv.')
        else:
            # for python3: https://stackoverflow.com/questions/57843385/how-to-fix-iterators-should-return-strings-not-bytes-in-django-file-upload
            decoded_file = file.read().decode('utf-8').splitlines()
            data = csv.DictReader(decoded_file, delimiter=',')
            errors = upload.check_field_name(errors, data.fieldnames)
            course_list = []
            if len(errors) == 0:
                # only precede if column header is correct
                errors, course_list = upload.create_course_list(errors, course_list, data)
                # sort it for better display
                course_list = sorted(course_list, key=lambda course: (course[0], course[1], course[2], course[3])) 
                errors = upload.validate_term(errors, course_list)
                errors = upload.validate_length(errors, course_list)
        if len(errors) == 0:
            # only attempt to save if initial checks renders no errors
            errors = upload.save_courses(errors, course_list)
            df_courses = pd.DataFrame(list(models.Course.objects.all().values()))
            if df_courses.empty:
                errors.append("The csv file did not have course information.")
            else:
                df_courses = df_courses[['term', 'course_subject', 'course_id', 'section', 'course_name', 'instructor_name', 'instructor_email']]
    return render(request, 'taform/upload_course_list.html', {'AC' : AC, 'errors' : errors,
        'df_courses' : df_courses.to_html(index=False)})

def algorithm(request):
    if not request.user.is_authenticated:
        return redirect('login')
    AC = authenticated(request)
    df_apps = pd.DataFrame(list(models.Assignment.objects.all().values()))
    df_elg_students = pd.DataFrame(list(models.Student.objects.all().filter(is_disqualified = False).values()))
    max_date = None
    matches =  pd.DataFrame()
    courses_supply = pd.DataFrame()
    students_supply = pd.DataFrame()
    context = None
    if not df_apps.empty and not df_elg_students.empty:
        max_date = max(df_apps['created_at'])
        max_date = max_date + datetime.timedelta(hours=-5)
        matches = format_algorithm_export()
        courses_supply = calculate_courses_without_assignment(matches)
        if (len(courses_supply)) > 0:
            courses_supply.columns = ['Course', 'TA size']
            courses_supply.sort_values(by=['Course', 'TA size'], inplace=True)
        students_supply = calculate_students_without_assignment(matches)
        if (len(students_supply)) > 0:
            students_supply.columns = ['Students without a match']
    context = {'AC' : AC,
               'display_date': max_date,
               'matches': matches.to_html(index=False),
               'courses_supply': courses_supply.to_html(index=False),
               'students_supply': students_supply.to_html(index=False)}
    if 'algo_run' in request.POST:
        models.Assignment.objects.all().delete()
        df_courses = pd.DataFrame(list(models.Course.objects.all().values()))
        df_apps = pd.DataFrame(list(models.Application.objects.all().values()))
        df_elg_students = pd.DataFrame(list(models.Student.objects.all().filter(is_disqualified = False).values()))
        if df_courses.empty or df_apps.empty or df_elg_students.empty:
                context = {'AC' : AC,
                'display_date': max_date,
                'no_results_error': 'The algorithm could not be run. Please ensure:',
                'no_results_error_1': '1. Eligible Students have applied to courses',
                'no_results_error_2': '2. Instructors have ranked students for their courses.',
                'no_results_error_3': '3. The number of teaching assistants per course has been assigned.'}
        else:
            result, costs, courses, students, courses_supply = algorithm_run()
            for c in courses:
                for s in students:
                    if result[c][s].value() != 0:
                        course = models.Course.objects.get(id=c)
                        student = models.Student.objects.get(id=s)
                        temp = models.Assignment(course = course, student = student, score = costs[c][s])
                        temp.save()
            df = pd.DataFrame(list(models.Assignment.objects.all().values()))
            max_date = None
            if not df.empty:
                max_date = max(df['created_at'])
                max_date = max_date + datetime.timedelta(hours=-5)
                matches = format_algorithm_export()
                courses_supply = calculate_courses_without_assignment(matches)
                if (len(courses_supply)) > 0:
                    courses_supply.columns = ['Course', 'TA size']
                    courses_supply.sort_values(by=['Course', 'TA size'], inplace=True)
                students_supply = calculate_students_without_assignment(matches)
                if (len(students_supply)) > 0:
                    students_supply.columns = ['Students without a match']
                context = {'AC' : AC,
                   'display_date': max_date,
                   'matches': matches.to_html(index=False),
                   'courses_supply': courses_supply.to_html(index=False),
                   'students_supply': students_supply.to_html(index=False),
                   'success': 'The algorithm has finished running! Please see the results in tables below.'}
            else:
                context = {'AC' : AC,
                    'display_date': max_date,
                    'no_results_error': 'The algorithm could not be run. Please ensure:',
                    'no_results_error_1': '1. Eligible Students have applied to courses',
                    'no_results_error_2': '2. Instructors have ranked students for their courses.',
                    'no_results_error_3': '3. The number of teaching assistants per course has been assigned.'}
    if request.method == 'POST':
        df_assignment = pd.DataFrame(list(models.Assignment.objects.all().values()))
        df_courses = pd.DataFrame(list(models.Course.objects.all().values()))
        df_elg_students = pd.DataFrame(list(models.Student.objects.all().filter(is_disqualified = False).values()))        
        if df_assignment.empty or df_courses.empty or df_elg_students.empty:
            context = {'AC' : AC,
                'display_date': max_date,
                'no_results_error': 'There are no results to export. Please ensure:',
                'no_results_error_1': '1. Eligible Students have applied to courses',
                'no_results_error_2': '2. Instructors have ranked students for their courses.',
                'no_results_error_3': '3. The number of teaching assistants per course has been assigned.'}
        elif 'algo_export' in request.POST:
            return algorithm_export()
        elif 'student_export' in request.POST:
            return export_dataframe(students_supply, 'students_without_match')
        elif 'course_export' in request.POST:
            return export_dataframe(courses_supply, 'courses_without_match')
    return render(request, 'taform/algorithm.html', context)

def calculate_courses_without_assignment(matches):
    df_course_info = format_course_info()
    courses_supply = dict()
    for index, row in df_course_info.iterrows():
        num_pos = row[4] + row[5] + row[6] + row[7]
        courses_supply[row[1]] = [row[4], row[5], row[6], row[7]]
    for index, row in matches.iterrows():
        if (row['TA size'] == 1.00):
            courses_supply[row['Course']][0] -= 1
        elif (row['TA size'] == 0.75):
            courses_supply[row['Course']][1] -= 1
        elif (row['TA size'] == 0.50):
            courses_supply[row['Course']][2] -=1
        elif (row['TA size'] == 0.25):
            courses_supply[row['Course']][3] -=1
        else:
            #something bad happened
            continue
    available_courses = []
    for i in courses_supply:
        if (sum(courses_supply[i])>0):
            ta_size = 1.00
            for j in courses_supply[i]:
                num = j
                while (num > 0):
                    available_courses.append([i, '%.2f'%ta_size])
                    num -= 1
                ta_size -= 0.25
    available_courses = pd.DataFrame(available_courses)
    return available_courses

def calculate_students_without_assignment(matches):
    students = []
    df_ranking_info = format_rankings_info()
    for index, row in df_ranking_info.iterrows():
        if (row[3] not in students):
            students.append(row[3])
    students_match = matches['Student']
    for i in students_match:
        # gaurd against multiple go pressed
        if i in students:
            students.remove(i)
    students = pd.DataFrame(students)
    return students

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
        if (row[2] == 0 or row[3] == 0):
            temp.append([row[0], row[1], 0])
        else:    
            temp.append([row[0], row[1], row[2] + row[3]])
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
    df.to_csv(path_or_buf=response, header=True, index=False, quoting=csv.QUOTE_NONNUMERIC, encoding='utf-8')
    return response

def export_dataframe(df, name):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=' + name +'.csv'
    df.to_csv(path_or_buf=response, header=True, index=False, quoting=csv.QUOTE_NONNUMERIC, encoding='utf-8')
    return response

def format_algorithm_export():
    df = pd.DataFrame(list(models.Assignment.objects.all().values()))
    df_courses = pd.DataFrame(list(models.Course.objects.all().values()))
    df_students = pd.DataFrame(list(models.Student.objects.all().filter(is_disqualified = False).values()))
    df_courses['course_unit'] = df_courses['course_subject'] + " " + df_courses['course_id'] + " (" + df_courses['section'] + ") " + df_courses['course_name'] + " " + df_courses['instructor_name'] 
    df_students['student_unit'] = df_students['first_name'] + " " + df_students['last_name'] + " <" + df_students['quest_id'] + "@uwaterloo.ca>" + " [app_id=" +  df_students['id'].astype(str)  + "]"
    df['s_id'] = df['student_id'].astype(int)
    df_students['s_id'] = df_students['id'].astype(int)
    df['c_id'] = df['course_id'].astype(int)
    df_courses['c_id'] = df_courses['id'].astype(int)
    df_students = df_students[['s_id', 'student_unit', 'full_ta', 'half_ta']]
    df_course_positions = df_courses[['course_unit', 'full_ta', 'three_quarter_ta', 'half_ta', 'quarter_ta']]
    df_courses = df_courses[['c_id', 'course_unit']]
    df = df.merge(df_students, on='s_id', how='left')
    df = df.merge(df_courses, on='c_id', how='left')
    df = df.sort_values(by=['course_unit', 'student_unit'])
    df = df[['course_unit', 'student_unit', 'score', 'full_ta', 'half_ta']]
    df['prefer full ta'] = df['full_ta']
    for i in range(len(df['prefer full ta'])):
        if df['prefer full ta'][i]:
            df.loc[i,'prefer full ta']= 'Yes'
        else:
            df.loc[i,'prefer full ta'] = ''
    df['prefer half ta'] = df['half_ta']
    for i in range(len(df['prefer half ta'])):
        if df['prefer half ta'][i]:
            df.loc[i,'prefer half ta']= 'Yes'
        else:
            df.loc[i,'prefer half ta'] = ''
    df.drop(['full_ta', 'half_ta'], axis = 1, inplace = True)
    df['TA size'] = -1
    df_course_positions_dict = dict()
    for index, row in df_course_positions.iterrows():
        df_course_positions_dict[row[0]] = [row[1], row[2], row[3], row[4]]
    df = df.sort_values(by=['prefer full ta', 'course_unit', 'score'], ascending=[True, True, True])
    for i in range(len(df['TA size'])):
        # full ta
        if (df_course_positions_dict[df['course_unit'][i]][0]) > 0:
             df.loc[i,'TA size'] = 1.00
             df_course_positions_dict[df['course_unit'][i]][0] -= 1
        # three quarter ta
        elif (df_course_positions_dict[df['course_unit'][i]][1]) > 0:
             df.loc[i,'TA size'] = 0.75
             df_course_positions_dict[df['course_unit'][i]][1] -= 1
        # half ta
        elif (df_course_positions_dict[df['course_unit'][i]][2]) > 0:
             df.loc[i,'TA size'] = 0.50
             df_course_positions_dict[df['course_unit'][i]][2] -= 1
        # quarter ta
        elif (df_course_positions_dict[df['course_unit'][i]][3]) > 0:
             df.loc[i,'TA size'] = 0.25
             df_course_positions_dict[df['course_unit'][i]][3] -= 1
        else:
           # something is broken, default of -1 will persist
           # add to documentation 
           continue
    df = df.sort_values(by=['course_unit', 'score', 'TA size','student_unit'], ascending=[True, True, False, True])
    df = df[['student_unit','course_unit', 'TA size', 'score', 'prefer full ta', 'prefer half ta']]
    df.columns = ['Student', 'Course', 'TA size', 'Score', 'Prefer full ta', 'Prefer half ta']
    df_extra = pd.DataFrame(list(models.Course.objects.all().values()))
    df_extra['course_unit'] = df_extra['course_subject'] + " " + df_extra['course_id'] + " (" + df_extra['section'] + ") " + df_extra['course_name'] + " " + df_extra['instructor_name'] 
    df_extra_positions = df_extra[['course_unit', 'full_ta', 'three_quarter_ta', 'half_ta', 'quarter_ta']]
    df_extra_positions = df_extra_positions[(df_extra_positions.full_ta == 0) & (df_extra_positions.three_quarter_ta == 0) & (df_extra_positions.half_ta == 0) & (df_extra_positions.quarter_ta == 0)]
    df_extra_positions['student_unit'] = 'Course enrollment is either too low currently to support a TA, or the course instructor does not use a TA, or the course is supplied a WEEF TA.'
    df_extra_positions['TA size'] = 0
    df_extra_positions['score'] = 0
    df_extra_positions['prefer full ta'] = ''
    df_extra_positions['prefer half ta'] = ''
    df_extra_positions = df_extra_positions[['student_unit','course_unit', 'TA size', 'score', 'prefer full ta', 'prefer half ta']]
    df_extra_positions.columns = ['Student', 'Course', 'TA size', 'Score', 'Prefer full ta', 'Prefer half ta']
    df = pd.concat([df, df_extra_positions])
    return df

def modify_apps(request, student_pk):
    if not request.user.is_authenticated:
        return redirect('login')

    AC = authenticated(request)
    url = get_object_or_404(models.Student, id=student_pk)
    student = models.Student.objects.filter(id=student_pk)
    appsModified = False

    if request.method == 'POST':
        a_form = models.ModifyApps(request.POST)
        apps = models.Application.objects.all().filter(student_id=student_pk).order_by(
            'course__course_subject','course__course_id','course__section')
        appsModified = True
        j = 0
        for i in apps:
            obj = models.Application.objects.get(id = i.id)
            obj.preference = a_form.__dict__['data'].getlist(
                'preference')[j]
            obj.save()
            j += 1

    apps = models.Application.objects.all().filter(student_id=student_pk).order_by(
            'course__course_subject','course__course_id','course__section')
    courses = models.Course.objects.all().filter(application__student_id = student_pk
        ).order_by('course_subject', 'course_id', 'section')
    appDate = apps[0].application_date + datetime.timedelta(hours=-5)
    num_apps = apps.count()

    a_form = [models.ModifyApps(prefix=str(x), instance=models.Application(
        )) for x in range(num_apps)]
    k = 0
    for l in apps:
        a_form[k] = models.ModifyApps(instance=l)
        k += 1

    context = {
        'student': student,
        'a_form': a_form,
        'courses': courses,
        'AC' : AC,
        'appDate': appDate,
        'appsModified': appsModified,
        'success': 'Your changes to student preferences have been updated.',
    }

    return render(request, 'taform/modify_apps.html', context)

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
        apps = models.Application.objects.all().filter(course_id = courseID, 
            student__is_disqualified = False, preference__in = [1,2,3]).order_by('student__sort_name','id')
        j = 0
        for i in apps:
            obj = models.Application.objects.get(id = i.id)
            obj.instructor_preference = a_form.__dict__['data'].getlist(
                'instructor_preference')[j]
            obj.save()
            j += 1
    apps = models.Application.objects.all().filter(course_id = courseID, 
            student__is_disqualified = False, preference__in = [1,2,3]).order_by('student__sort_name','id')
    students = models.Student.objects.all().filter(application__course_id = 
        courseID, application__preference__in = [1,2,3], is_disqualified = False).order_by('sort_name','application__id')
    num_apps = apps.count()
    num_students = students.count()

    if (apps.count() == 0):
        noApps = True
    else:
        noApps = False

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
        'noApps' : noApps,
    }

    return render(request, 'taform/instructor_ranking.html', context)

def assign_tas(request):
    if not request.user.is_authenticated:
        return redirect('login')
    AC = authenticated(request)
    is_ranking_submitted = False
    if request.method == 'POST':
        num = [x for x in models.Course.objects.all()]
        c_form = models.AssignTA(request.POST)
        courses = models.Course.objects.all().order_by(
            'course_subject','course_id','section')
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
    courses = models.Course.objects.all().order_by('course_subject','course_id','section')
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
        if 'Upload_FM' in request.POST and not request.FILES:
            return render(request, 'taform/upload_front_matter.html', 
                {'error': 'You must select a file before uploading.', 'AC' : AC})   
        if 'Upload_FM' in request.POST and request.FILES:
            data = request.FILES.get('fm_txt')
            if data.name.split('.')[-1] != 'txt':
                return render(request, 'taform/upload_front_matter.html', 
                    {'error': 'You must select a txt file to upload.', 'AC' : AC})
            front_matter = open(front_matter_path(), "w")
            front_matter.write(data.read())
            front_matter.close()
            return render(request, 'taform/upload_front_matter.html', 
                {'success': 'New front matter uploaded, preview by clicking home and then step 3.', 'AC' : AC})

        if 'Upload_Intro' in request.POST and not request.FILES:
            return render(request, 'taform/upload_front_matter.html',
                {'error': 'You must select a file before uploading.', 'AC' : AC})
        if 'Upload_Intro' in request.POST and request.FILES:
            data = request.FILES.get('intro_txt')
            if data.name.split('.')[-1] != 'txt':
                return render(request, 'taform/upload_front_matter.html',
                    {'error': 'You must select a txt file to upload.', 'AC':AC})
            intro_page = open(intro_page_path(), "w")
            intro_page.write(data.read())
            intro_page.close()
            return render(request, 'taform/upload_front_matter.html', 
                {'success': 'New intro page uploaded, preview by clicking home and then step 3.', 'AC' : AC})
        return render(request, 'taform/upload_front_matter.html', {'AC' : AC})

def front_matter_path():
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(my_path, "../static/taform/front_matter.txt")
    return path

def intro_page_path():
    my_path = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(my_path, "../static/taform/intro_page.txt")
    return path

def export(request):
    AC = authenticated(request)
    context = {'AC' : AC}
    if not request.user.is_authenticated:
        return redirect('login')
    else:
        if 'course_info' in request.POST:
            df_course = pd.DataFrame(list(models.Course.objects.all().values()))
            if df_course.empty:
                context = {'AC' : AC,
                           'no_results_error': 'The ranking results could not be exported. Please ensure:',
                          'no_results_error_1': 'Courses have been uploaded and the number of teaching assistants per course has been assigned.'}
                return render(request, 'taform/export.html', context)
            else:
                return export_course_info()
        if 'rankings_info' in request.POST:
            df_course = pd.DataFrame(list(models.Course.objects.all().values()))
            df_apps = pd.DataFrame(list(models.Application.objects.all().values()))
            df_elg_students = pd.DataFrame(list(models.Student.objects.all().filter(is_disqualified = False).values()))
            if df_course.empty or df_apps.empty or df_elg_students.empty:
                context = {'AC' : AC,
                          'no_results_error': 'The ranking results could not be exported. Please ensure:',
                          'no_results_error_1': '1. Eligible students have applied to courses',
                          'no_results_error_2': '2. Instructors have ranked students for their courses.',
                          'no_results_error_3': '3. The number of teaching assistants per course has been assigned.'}
                return render(request, 'taform/export.html', context)
            else:            
                return export_ranking_info()
        return render(request, 'taform/export.html', context)

def export_course_info():
    df = format_course_info()
    df.drop(['id'], axis = 1, inplace = True)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=1_course-info.csv'
    df.to_csv(path_or_buf=response,header=True, index=False, encoding='utf-8')
    return response

def format_course_info():
    df = pd.DataFrame(list(models.Course.objects.all().values()))
    df['course_unit'] = df['course_subject'] + " " + df['course_id'] + " (" + df['section'] + ") " + df['course_name'] + " " + df['instructor_name']
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
    df.to_csv(path_or_buf=response,header=True, index=False, encoding='utf-8')
    return response

def format_rankings_info():
    df_courses = pd.DataFrame(list(models.Course.objects.all().values()))
    df_courses['course_num'] = df_courses['course_id']
    df_courses['course_unit'] = df_courses['course_subject'] + " " + df_courses['course_num'] + " (" + df_courses['section'] + ") " + df_courses['course_name'] + " " + df_courses['instructor_name']
    df_courses['c_id'] = df_courses['id']
    df_courses.drop(['course_id', 'id', 'term', 'url_hash', 'full_ta', 'half_ta', 'quarter_ta', 
        'three_quarter_ta', 'instructor_name', 'instructor_email'], axis = 1, inplace = True)
    # get applications info & remove unneccasary columns
    df_apps = pd.DataFrame(list(models.Application.objects.all().values()))
    df_apps['student_preference'] = df_apps['preference']
    df_apps.drop(['id', 'reason', 'reason', 'application_date', 'preference'], axis = 1, inplace = True)
    # get students info & remove unneccasary columns
    df_students = pd.DataFrame(list(models.Student.objects.all().values()))
    df_students['email'] = df_students['quest_id'] + "@uwaterloo.ca"
    df_students['student_unit'] = df_students['first_name'] + " " + df_students['last_name'] + " <" + df_students['email'] +">" + " [app_id=" + df_students['id'].astype(str) + "]"
    df_students['s_id'] = df_students['id']
    df_students = df_students[df_students.is_disqualified == False]
    df_students.drop(['id', 'student_id', 'quest_id', 'department', 'current_program', 'citizenship', 
        'student_visa_expiry_date', 'enrolled_status', 'ta_expectations', 'cv',  'full_ta', 
        'half_ta'], axis = 1, inplace = True)
    # join courses & applications & students
    df = df_apps.merge(df_courses, left_on='course_id', right_on='c_id', how='inner')
    df = df.merge(df_students, left_on='student_id', right_on='s_id', how='inner')
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
    df.to_csv(path_or_buf=response, header=True, index=False, quoting=csv.QUOTE_NONNUMERIC, encoding='utf-8')
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
