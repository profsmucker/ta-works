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
            'quest_id' : 'ecu', 'department' : 'MSCI', 'current_program' : 'MMSC', 'citizenship' : True}

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

    def test_student_form_error_message

class TestApplicationForm(TestCase):
    def test_application_form_does_not_submit_if_not_valid(self):
        application_form = ApplicationForm(data={})
        assert application_form.is_valid() is False, 'Should be invalid if no data is given'

