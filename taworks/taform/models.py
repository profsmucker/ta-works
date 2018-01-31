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
    last_name = models.CharField(max_length=50)
    quest_id = models.CharField(max_length=50, 
        help_text="Quest ID is what is used to login to UW Learn and Quest, eg. anleblon")
    department = models.CharField(max_length=50)
    PROGRAMS = (('phd', 'PHD'), ('masc', 'MASC'), ('mmsc', 'MMSC'), ('other', 'Other'))
    current_program = models.CharField(max_length=50, choices=PROGRAMS, 
        help_text="If you are not in the MSCI department, please select 'Other'.")
    RESIDENTIAL_STATUS = (('canadian citizen', 'Canadian Citizen/Permanent Resident'), ('student visa', 'Student Visa'))
    citizenship = models.CharField(null=False, max_length=50, choices=RESIDENTIAL_STATUS)
    student_visa_expiry_date = models.DateField(null=True, blank=True,
        help_text="Must be in form: yyyy-mm-dd")
    ENROLLED = (('full time', 'Full-Time'), ('part time', 'Part-Time'), ('other', 'Other'))
    enrolled_status = models.CharField(max_length=50, choices=ENROLLED)
    ta_expectations = models.BooleanField(default=False, blank=True)
    cv = models.FileField(upload_to='documents/', null=True, blank=True)
    full_ta = models.BooleanField(default=False, blank=True)
    three_quarter_ta = models.BooleanField(default=False, blank=True)
    half_ta = models.BooleanField(default=False, blank=True)
    quarter_ta = models.BooleanField(default=False, blank=True)

class Course(models.Model):
    term = models.PositiveIntegerField(validators=[MaxValueValidator(9999), MinValueValidator(1000)], null=True)
    course_subject = models.CharField(max_length=255, null=True)
    course_id = models.CharField(max_length=255, null=True)
    section = models.CharField(max_length=255, null=True)
    course_name = models.CharField(max_length=255, null=True)
    instructor_name = models.CharField(max_length=255, blank=True, null=True)
    instructor_email = models.CharField(max_length=255, blank=True, null=True)
    url_hash = models.CharField("Url", blank=False, max_length=50, unique=True, null=True)
    full_ta = models.PositiveIntegerField(blank=True, null=True, default=0)
    three_quarter_ta = models.PositiveIntegerField(blank=True, null=True, default=0)
    half_ta = models.PositiveIntegerField(blank=True, null=True, default=0)
    quarter_ta = models.PositiveIntegerField(blank=True, null=True, default=0)

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
    preference = models.IntegerField(validators=[MaxValueValidator(3), MinValueValidator(0)])
    reason = models.CharField(max_length=255, null=True, blank=True)

class StudentForm(ModelForm):
    class Meta:
        model = Student
        fields = '__all__'
        error_messages = {'student_id':{'invalid':'test message', }, }
        widgets = {'past_position_one':Textarea(attrs={'cols':80,'rows':5}), 'past_position_two':Textarea(
            attrs={'cols':80, 'rows':5}), 'past_position_three':Textarea(attrs={'cols':80, 'rows':5})}

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
        widgets = {'full_ta':Textarea(attrs={'cols':3,'rows':1, 'style':'resize:none;'}),
        'three_quarter_ta':Textarea(attrs={'cols':3,'rows':1, 'style':'resize:none;'}),
        'half_ta':Textarea(attrs={'cols':3,'rows':1, 'style':'resize:none;'}),
        'quarter_ta':Textarea(attrs={'cols':3,'rows':1, 'style':'resize:none;'}) }

class ApplicationForm(ModelForm):
    class Meta:
        model = Application
        exclude = ('student', 'course', 'application_date', )
        widgets = {'reason': Textarea(attrs={'cols':50, 'rows':1}), 'preference': Textarea(
            attrs={'cols':15,' rows':1})}