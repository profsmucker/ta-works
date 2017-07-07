# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.core.validators import MaxValueValidator
from django.core.validators import MinValueValidator
import datetime
from django.forms import ModelForm

# Create your models here.
class Student(models.Model):
    student_id = models.PositiveIntegerField(validators=[MaxValueValidator(99999999), MinValueValidator(10000000)])
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    quest_id = models.CharField(max_length=50)
    department = models.CharField(max_length=50)
    current_program = models.CharField(max_length=50)
    citizenship = models.BooleanField(default=False, blank=True)
    student_visa = models.BooleanField(default=False, blank=True)
    student_visa_expiry_date = models.DateField(null=True, blank=True)
    full_time = models.CharField(max_length=10)
    part_time = models.CharField(max_length=10)
    other = models.CharField(max_length=10)
    cv = models.FileField(upload_to='documents/', null=True, blank=True)
    past_position_one = models.CharField(max_length=255, null=True, blank=True)
    past_position_two = models.CharField(max_length=255, null=True, blank=True)
    past_position_three = models.CharField(max_length=255, null=True, blank=True)

class Course(models.Model):
    term = models.PositiveIntegerField(validators=[MaxValueValidator(9999), MinValueValidator(1000)])
    section = models.PositiveIntegerField(validators=[MaxValueValidator(999), MinValueValidator(0)])
    course_subject = models.CharField(max_length=4)
    course_id = models.PositiveIntegerField(validators=[MaxValueValidator(999), MinValueValidator(0)])
    course_name = models.CharField(max_length=255)
    instructor_name = models.CharField(max_length=255)
    instructor_email = models.CharField(max_length=255)

class Application(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, blank=True)
    application_date = models.DateTimeField(blank=True)
    preference = models.IntegerField(validators=[MaxValueValidator(3), MinValueValidator(-1)], default=-1)
    reason = models.CharField(max_length=255, null=True, blank=True)


class StudentForm(ModelForm):
    class Meta:
        model = Student
        fields = '__all__'

class CourseForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(CourseForm, self).__init__(*args, **kwargs)
        uneditable_fields = ['term', 'section', 'course_id', 'course_name', 'instructor_name', 'instructor_email']
        for field in uneditable_fields:
            self.fields[field].widget.attrs['readonly'] = 'true'

    class Meta:
        model = Course
        fields = '__all__'

class ApplicationForm(ModelForm):
    class Meta:
        model = Application
        exclude = ('student', 'course', 'application_date', )

