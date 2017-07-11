# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.core.validators import MaxValueValidator
from django.core.validators import MinValueValidator
import datetime
from django.forms import ModelForm, Textarea, CharField
from datetimewidget.widgets import DateTimeWidget, DateWidget, TimeWidget, DateInput

# Create your models here.
class Student(models.Model):
    student_id = models.PositiveIntegerField(validators=[MaxValueValidator(99999999), MinValueValidator(10000000)])
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    quest_id = models.CharField(max_length=50, help_text='')
    department = models.CharField(max_length=50)
    PROGRAMS = (('phd','PHD'),('masc','MASC'),('mmsc','MMSC'),('other','Other'))
    current_program = models.CharField(max_length=50,choices=PROGRAMS)
    RESIDENTIAL_STATUS = (('canadian citizen','Canadian Citizen/Permanent Resident'),('student visa','Student Visa'))
    citizenship = models.CharField(null=False,max_length=50,choices=RESIDENTIAL_STATUS)
    student_visa_expiry_date = models.DateField(null=True, blank=True)
    ENROLLED = (('full time', 'Full-Time'), ('part time', 'Part-Time'),('other','Other'))
    enrolled_status = models.CharField(max_length=50,choices=ENROLLED)
    ta_expectations = models.BooleanField(default=False, blank=True)
    cv = models.FileField(upload_to='documents/', null=True, blank=True)
    full_ta = models.BooleanField(default=False, blank=True)
    three_quarter_ta = models.BooleanField(default=False, blank=True)
    half_ta = models.BooleanField(default=False, blank=True)
    quarter_ta = models.BooleanField(default=False, blank=True)
    past_position_one = models.CharField(max_length=1000, null=True, blank=True)
    past_position_two = models.CharField(max_length=1000, null=True, blank=True)
    past_position_three = models.CharField(max_length=1000, null=True, blank=True)

class Course(models.Model):
    term = models.PositiveIntegerField(validators=[MaxValueValidator(9999), MinValueValidator(1000)])
    course_subject = models.CharField(max_length=255)
    course_id = models.CharField(max_length=255)
    section = models.CharField(max_length=255)
    course_name = models.CharField(max_length=255)
    instructor_name = models.CharField(max_length=255, null=True, blank=True)
    instructor_email = models.CharField(max_length=255, null=True, blank=True)

class Application(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, blank=True)
    application_date = models.DateTimeField(auto_now_add=True)
    preference = models.IntegerField(validators=[MaxValueValidator(3), MinValueValidator(-1)])
    reason = models.CharField(max_length=255, null=True, blank=True)

class StudentForm(ModelForm):
    class Meta:
        model = Student
        fields = '__all__'
        help_texts = {'quest_id': 'Quest ID is what you use to login to UW Learn and Quest. Ex. anleblon'}
        labels = {"student_visa_expiry_date":"Visa Expiry Date"}
        widgets = {'student_visa_expiry_date':DateInput(format=('%d-%m-%Y'), attrs={'placeholder':'yy/mm/dd'}),'past_position_one':Textarea(attrs={'cols':80,'rows':5}), 'past_position_two':Textarea(attrs={'cols':80,'rows':5}), 'past_position_three':Textarea(attrs={'cols':80,'rows':5})}

class ApplicationForm(ModelForm):
    class Meta:
        model = Application
        exclude = ('student', 'course', 'application_date', )
        widgets = {'reason': Textarea(attrs={'cols':50,'rows':1}),'preference': Textarea(attrs={'cols':15,'rows':1})}