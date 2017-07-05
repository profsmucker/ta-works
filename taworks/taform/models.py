# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.core.validators import MaxLengthValidator
from django.core.validators import MinLengthValidator
import datetime
from django.forms import ModelForm

# Create your models here.
class Student(models.Model):
    student_id = models.PositiveIntegerField(validators=[MaxLengthValidator(8), MinLengthValidator(8)])
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    quest_id = models.CharField(max_length=50)
    department = models.CharField(max_length=50)
    current_program = models.CharField(max_length=50)
    citizenship = models.BooleanField(default=False, blank=True)
    student_visa = models.BooleanField(default=False, blank=True)
    student_visa_expiry_date = models.DateField(blank=True)
    full_time = models.CharField(max_length=10)
    part_time = models.CharField(max_length=10)
    other = models.CharField(max_length=10)
    cv = models.FileField(upload_to='documents/', blank=True)
    past_position_one = models.CharField(max_length=255, blank=True)
    past_position_two = models.CharField(max_length=255, blank=True)
    past_position_three = models.CharField(max_length=255, blank=True)

class Course(models.Model):
    term = models.PositiveIntegerField(validators=[MaxLengthValidator(4), MinLengthValidator(4)])
    section = models.PositiveIntegerField(validators=[MaxLengthValidator(3), MinLengthValidator(3)])
    course_id = models.CharField(max_length=8)
    course_name = models.CharField(max_length=255)
    instructor_name = models.CharField(max_length=255)
    instructor_email = models.CharField(max_length=255)

class Application(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, blank=True)
    preference = models.IntegerField(validators=[MaxLengthValidator(1), MinLengthValidator(1)], blank=True)
    reason = models.CharField(max_length=255, blank=True)
    application_date = str(datetime.datetime.now())

class StudentForm(ModelForm):
    class Meta:
        model = Student
        fields = '__all__'

class CourseForm(ModelForm):
    class Meta:
        model = Course
        fields = '__all__'

class ApplicationForm(ModelForm):
    class Meta:
        model = Application
        fields = '__all__'


