# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.core.validators import MaxValueValidator
from django.core.validators import MinValueValidator
import datetime
from django.forms import ModelForm, Textarea, CharField
from django import forms
from django.contrib.admin import widgets

# Create your models here.
class Student(models.Model):
    student_id = models.PositiveIntegerField(help_text="This must be an 8 digit number.", 
        validators=[MaxValueValidator(99999999), MinValueValidator(10000000)])
    first_name = models.CharField(max_length=50)
    sort_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50)
    quest_id = models.CharField(max_length=50, 
        help_text="Quest ID is what is used to login to UW Learn and Quest, eg. anleblon")
    department = models.CharField(max_length=50)
    PROGRAMS = (('PhD', 'PHD'), ('MASC', 'MASC'), ('MMSC', 'MMSC'), ('Other', 'Other'))
    current_program = models.CharField(max_length=50, choices=PROGRAMS, 
        help_text="If you are not in the MSCI department, please select 'Other'.")
    RESIDENTIAL_STATUS = (('Canadian Citizen', 'Canadian Citizen/Permanent Resident'), 
        ('Student Visa', 'Student Visa'))
    citizenship = models.CharField(null=False, max_length=50, choices=RESIDENTIAL_STATUS)
    student_visa_expiry_date = models.DateField(null=True, blank=True,
        help_text="Must be in form: yyyy-mm-dd")
    ENROLLED = (('Full-Time', 'Full-Time'), ('Part-Time', 'Part-Time'), ('Other', 'Other'))
    enrolled_status = models.CharField(max_length=50, choices=ENROLLED)
    expectTAtions = ((True, 'Yes'), (False, 'No'))
    ta_expectations = models.BooleanField(default=False, choices=expectTAtions)
    cv = models.FileField(upload_to='documents/', null=True, blank=True)
    full_ta = models.BooleanField(default=False, blank=True)
    half_ta = models.BooleanField(default=False, blank=True)
    is_disqualified = models.BooleanField(default=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    def save(self):
        if self.first_name:
            self.first_name = self.first_name.strip()
            self.sort_name = self.first_name.lower()
        else:
            self.sort_name = ''
        super(Student, self).save()

class Course(models.Model):
    term = models.PositiveIntegerField(validators=[MaxValueValidator(9999), MinValueValidator(1000)], null=True)
    course_subject = models.CharField(max_length=255, null=True)
    course_id = models.CharField(max_length=255, null=True)
    section = models.CharField(max_length=255, null=True)
    course_name = models.CharField(max_length=255, null=True)
    instructor_name = models.CharField(max_length=255, blank=True, null=True)
    instructor_email = models.CharField(max_length=255, blank=True, null=True)
    url_hash = models.CharField("Url", blank=False, max_length=50, unique=True, null=True)
    full_ta = models.PositiveIntegerField(blank=False, null=False, default=0,validators=[MaxValueValidator(15), MinValueValidator(0)])
    three_quarter_ta = models.PositiveIntegerField(blank=False, null=False, default=0,validators=[MaxValueValidator(15), MinValueValidator(0)])
    half_ta = models.PositiveIntegerField(blank=False, null=False, default=0,validators=[MaxValueValidator(15), MinValueValidator(0)])
    quarter_ta = models.PositiveIntegerField(blank=False, null=False, default=0,validators=[MaxValueValidator(15), MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class TempCourse(models.Model):
    term = models.PositiveIntegerField(validators=[MaxValueValidator(9999), MinValueValidator(1000)], null=True)
    course_subject = models.CharField(max_length=255, null=True)
    course_id = models.CharField(max_length=255, null=True)
    section = models.CharField(max_length=255, null=True)
    course_name = models.CharField(max_length=255, null=True)
    instructor_name = models.CharField(max_length=255, blank=True, null=True)
    instructor_email = models.CharField(max_length=255, blank=True, null=True)
    url_hash = models.CharField("Url", blank=False, max_length=50, unique=True, null=True)

class Application(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, blank=True)
    application_date = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(max_length=1500, null=True, blank=True)
    STUDENT_PREFERENCE = ((1,'1-Most Preferred'),(2,'2'),(3,'3-Least Preferred'),(0,'I am unable to TA this course'))
    preference = models.IntegerField(choices=STUDENT_PREFERENCE, default = 0)
    ratings = ((1,'1-Most Preferred'),(2,'2'),(3,'3'),(4,'4'),(5,'5-Least Preferred'),(0,'Not Ranked'))
    instructor_preference = models.IntegerField(null=True,choices=ratings, 
        help_text="1 - Most Preferred, 5 - Least Preferred, 0 - Not Ranked", default =0)
    pref_updated_at = models.DateTimeField(auto_now=True)

class StudentForm(ModelForm):
    class Meta:
        model = Student
        fields = '__all__'
        error_messages = {'student_id':{'invalid':'test message', }, }
        widgets = {'past_position_one':Textarea(attrs={'cols':80,'rows':5}), 'past_position_two':Textarea(
            attrs={'cols':80, 'rows':5}), 'past_position_three':Textarea(attrs={'cols':80, 'rows':5})}

class StudentApps(ModelForm):
    def __init__(self, *args, **kwargs):
        super(StudentApps,self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['readonly']=True
        self.fields['first_name'].disabled
        self.fields['last_name'].widget.attrs['readonly']=True
        self.fields['last_name'].disabled
        self.fields['quest_id'].widget.attrs['readonly']=True
        self.fields['quest_id'].disabled
        self.fields['cv'].widget.attrs['readonly']=True
        self.fields['cv'].disabled
        self.fields['student_id'].widget.attrs['readonly']=True
        self.fields['student_id'].disabled
        self.fields['sort_name'].widget.attrs['readonly']=True
        self.fields['sort_name'].disabled
    class Meta:
        model = Student
        fields = ['student_id', 'first_name', 'last_name', 'quest_id', 'cv', 'sort_name']

class StudentEditForm(ModelForm):
    class Meta:
        model = Student
        fields = '__all__'
        exclude = ('student_visa_expiry_date', 'citizenship')

class Applications(ModelForm):
    class Meta:
        model = Application
        fields = ['reason', 'student', 'course', 'instructor_preference']

class ModifyApps(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ModifyApps,self).__init__(*args, **kwargs)
        self.fields['reason'].widget.attrs['readonly']=True
        self.fields['reason'].disabled
    class Meta:
        model = Application
        fields =['reason', 'preference']

class AssignTA(ModelForm):
    def __init__(self, *args, **kwargs):
        super(AssignTA,self).__init__(*args, **kwargs)
        self.fields['term'].widget.attrs['readonly']=True
        self.fields['term'].disabled
        self.fields['course_subject'].widget.attrs['readonly']=True
        self.fields['course_subject'].disabled
        self.fields['course_id'].widget.attrs['readonly']=True
        self.fields['course_id'].disabled
        self.fields['section'].widget.attrs['readonly']=True
        self.fields['section'].disabled
        self.fields['course_name'].widget.attrs['readonly']=True
        self.fields['course_name'].disabled
        self.fields['instructor_name'].widget.attrs['readonly']=True
        self.fields['instructor_name'].disabled
        self.fields['instructor_email'].widget.attrs['readonly']=True
        self.fields['instructor_email'].disabled
    class Meta:
        model = Course
        fields = '__all__'
        exclude = ('url_hash',)

class ApplicationForm(ModelForm):
    class Meta:
        model = Application
        exclude = ('student', 'course', 'application_date', 'instructor_preference', )
    def __init__(self, *args, **kwargs):
        super(ApplicationForm, self).__init__(*args, **kwargs)
        self.fields['preference'].widget.attrs={
         'class': 'pref_class'}
        self.fields['reason'].widget.attrs={
         'class': 'reason_class'}
        # get rid of the default reason label
        self.fields['reason'].label = ""

class InstructorForm(ModelForm):
    class Meta:
        model = Application
        fields = ['instructor_preference']

class ApplicationStatus(models.Model):
    status_date = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=False, blank=True)

class Assignment(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    solution_num = models.PositiveIntegerField(blank=False, null=False, default=0)
    score = models.PositiveIntegerField(blank=False, null=True)