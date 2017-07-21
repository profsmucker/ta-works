# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from .models import Student, Course, Application, StudentForm, ApplicationForm
import datetime
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from StringIO import StringIO
from django.core.files.uploadedfile import InMemoryUploadedFile

# Create your tests here.
class TestStudentForm(TestCase):
    def test_student_form_does_not_submit_if_not_valid(self):
        student_form = StudentForm(data={})
        assert student_form.is_valid() is False, 'Should be invalid if no data is given'

    def test_student_form_is_valid(self):
        """
        This test mocks student form data and checks it submits into the database
        """
        im = Image.new(mode='RGB', size=(200, 200))
        im_io = StringIO()
        im.save(im_io, 'JPEG')
        im_io.seek(0)
        file = InMemoryUploadedFile(
            im_io, None, 'random.jpg', 'image/jpeg', im_io.len, None
        )
        file_dict = {'file': file}
        post_dict = {'student_id' : 10000001, 'first_name' : 'Edward', 'last_name' : 'Cullin',
            'quest_id' : 'ecu', 'department' : 'MSCI', 'current_program' : 'MMSC', 'citizenship' : 'canadian citizen', 'enrolled_status' : 'full time'}

        student_form = StudentForm(data=post_dict, files=file_dict)
        assert student_form.is_valid() is True, 'Should be valid if data and file is given'
        submitted = student_form.save()
        self.assertEqual(submitted.student_id, 10000001)
        self.assertEqual(submitted.first_name, 'Edward')
        self.assertEqual(submitted.last_name, 'Cullin')
        self.assertEqual(submitted.quest_id, 'ecu')
        self.assertEqual(submitted.department, 'MSCI')
        self.assertEqual(submitted.current_program, 'MMSC')
        self.assertEqual(submitted.citizenship, True)

    def test_student_form_error_message(TestCase):
        """
        Error message test to be written when form is complete with error messages
        TODO...............
        """

class TestApplicationForm(TestCase):
    def test_application_form_does_not_submit_if_not_valid(self):
        application_form = ApplicationForm(data={})
        assert application_form.is_valid() is False, 'Should be invalid if no data is given'

    def test_application_form_is_valid(self):
        """
        Test application form when it's valid and invalid and that data exist in the database after submission
        """
        post_dict = {'student_id' : 10000001, 'first_name' : 'Edward', 'last_name' : 'Cullin',
            'quest_id' : 'ecu', 'department' : 'MSCI', 'current_program' : 'MMSC', 'citizenship' : 'canadian citizen', 'enrolled_status' : 'full time'}
        student_form = StudentForm(data=post_dict)
        student_submitted = student_form.save()
        course_dict = {'term' : 1111, 'course_subject' : 'MSCI', 'course_id' : '445', 'section' :'002', 
            'course_name' : 'Telecommunications', 'instructor_name' : 'Penny Lee', 'instructor_email' : 'penle@uwaterloo.ca'}
        app_data = {'preference' : 1, 'reason' : 'No'}
        application_form = ApplicationForm(instance=Application())
        assert application_form.is_valid() is False, 'Should be invalid because preference not selected'
        application_form = ApplicationForm(data=app_data)
        assert application_form.is_valid() is True, 'Should be valid because preference is selected'
        application_form = application_form.save(commit=False)
        application_form.student = Student.objects.get(id=student_submitted.id)
        c = Course()
        c.term = course_dict['term']
        c.course_subject = course_dict['course_subject']
        c.course_id = course_dict['course_id']
        c.section = course_dict['section']
        c.course_name = course_dict['course_name']
        c.save()
        application_form.course = c
        application_form.save()
        self.assertEqual(application_form.student.student_id, 10000001)
        self.assertEqual(application_form.student.first_name, 'Edward')
        self.assertEqual(application_form.student.last_name, 'Cullin')
        self.assertEqual(application_form.student.quest_id, 'ecu')
        self.assertEqual(application_form.student.department, 'MSCI')
        self.assertEqual(application_form.student.current_program, 'MMSC')
        self.assertEqual(application_form.student.citizenship, 'canadian citizen')
        self.assertEqual(application_form.student.enrolled_status, 'full time')
        self.assertEqual(application_form.course.term, 1111)
        self.assertEqual(application_form.course.course_subject, 'MSCI')
        self.assertEqual(application_form.course.course_id, '445')
        self.assertEqual(application_form.course.section, '002')
        self.assertEqual(application_form.course.course_name, 'Telecommunications')
