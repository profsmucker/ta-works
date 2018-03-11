from .. import models
import uuid

def template_courses():
    course = models.Course(term = 1185, 
        course_subject = 'MSCI', 
        course_id = '211',
        section = '001',
        course_name = 'Organizational Behaviour',
        instructor_name = 'Kejia Zhu',
        instructor_email = 'kejia.zhu@uwaterloo.ca'
    )
    course.save()

def check_field_name(errors, fieldnames):
    expected = ['term', 'course_subject', 'course_id', 'section', 'course_name', 'instructor_name', 'instructor_email']
    if fieldnames:
        for i in expected:
            if i not in fieldnames:
                errors.append("The following column header is missing: " + i)
    else:
        errors.append("The file needs the following columns: " + str(expected))
    return errors
def create_course_list(errors, course_list, data):
    course_units = dict()
    for i in data:
        course_unit = i['course_subject'] + " " + i['course_id'] + " (" + i['section'] + ") " + i['course_name'] + " " + i['instructor_name'] 
        if len(course_unit) == 6: #6 represents the spaces and parenthesis from course_unit
            # empty row here, skip it
            continue
        if course_unit not in course_units:
            course_units[course_unit] = True
            course_list.append([i['term'], i['course_subject'], i['course_id'], i['section'], i['course_name'], i['instructor_name'], i['instructor_email']])
        else:
            errors.append("Duplicate course found: " + course_unit)
    return errors, course_list

def validate_term(errors, course_list):
    for i in course_list:
        try:
            term = int(i[0])
            if term < 1000 or term > 9999:
                errors.append('The following row needs term to be a four digit number: '+ str(i))
        except:
            errors.append('The following row needs term to be an integer: ' + str(i))
            continue
    return errors

def validate_length(errors, course_list):
    for i in course_list:
        for j in course_list:
            if len(j) > 255:
                errors.append('The following value is greater than the allowed 255 chars: '+ str(j))
    return errors

def save_courses(errors, course_list):
    models.Course.objects.all().delete()
    models.Student.objects.all().delete()
    j = 0
    for i in course_list:
        sec = check_section(i[3])
        try:
            course = models.Course(term = int(i[0]), 
                course_subject = str(i[1]), 
                course_id = str(i[2]),
                section = sec,
                course_name = str(i[4]),
                instructor_name = str(i[5]),
                instructor_email = str(i[6]),
                url_hash = str(uuid.uuid4()) + str(j)
            )
            course.save()
        except:
            errors.append("The following row had issues with saving: " + str(i))
        j += 1
    return errors

def check_section(section):
    if len(section) > 3:
        return section
    sec = section
    try:
        sec = int(sec)
        sec = "{0:0>3}".format(sec)
    except:
        pass
    return sec

def send_file(request):
    filename = 'static/taform/course_template.csv' # Select your file here.
    wrapper = FileWrapper(open(filename))
    content_type = mimetypes.guess_type(filename)[0]
    response = HttpResponse(wrapper,content_type=content_type)
    response['Content-Length'] = os.path.getsize(filename)    
    response['Content-Disposition'] = 'attachment; filename=course_template.csv'
    return response