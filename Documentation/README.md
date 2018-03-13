# TA Works

### Existing Bugs:
1. In the page Teaching Assistant Assignment (Step 8) -> Pressing `Run Algorithm` multiple times will cause the table to display multiple duplicates and incorrect # of positions available. This bug also affects the `export` csv and will persist. Quick fix is to press `Run Algorithm` once and only once.
    
2. During application, if a student does not upload a PDF. It won't error on submission but it would error when instructors or associate chair tries to view the resume.

3. During the application process, if errors exist in the form the applicant will have to re-upload their CV and re-check the confirmation buttons.

### Solved Bugs:
1. A popup is added and warning the user it may take up to 1 minute to reduce the bug of multiple `Run Algorithm` clicks.
2. A unique course is identified as 'course_subject' + 'course_id']  + ('section') + 'course_name' + 'instructor_name' and if duplicates courses are uploaded, the backend matching algorithm will handle it correctly but the frontend will not.


### Usability Issues:
1. Help Tips on TA Application Form require the cursor to be removed from the hover area of the tool tip before being able to click into the textbox. 
2. On Course Template download, sections will appear without leading '0' paddings but on upload it will pad it for you.

### Configuration Instructions:
1. How to change the config file on the server:
	* ssh into box as root user (https://github.com/j2kan/ta-works/tree/master/taworks#how-to-ssh-into-the-box-and-deploy-your-branch)
	* run `sudo vi /var/www/environment.ini`
	* make the appropriate changes

### System Instructions:
0. Password reset using the Associate Chair email `msciugch@connect.uwaterloo.ca` as the reset email address. Check your junk mail.
0. Login to the Application - (https://team4.uwaterloo.ca/login/)
1. Upload Courses
	* Function: This page is the starting point of the system. This allows the AC to upload a csv with the course information for the upcoming term. All proceeding steps require this information to be correct.
	* Scenarios for Use:
		* 1 - At the beginning of each ranking period, the AC needs to upload the new courses.
		* 2 - Information from a previous course upload is incorrect and must be changed. WARNING: The AC should only consider resolving a course issue this way if the TA Application Form has not yet been opened. Uploading courses resets the database and all information (including applications) will be lost.
	* How to Use:
		* Open Step 2, Upload Courses (https://team4.uwaterloo.ca/taform/upload_course_list.html)
		* Review the rules for uploading courses - i.e. the file must be a csv and meet the requirements identified on screen.
		* Download what is currently in the database to have a starting example.
		* Make changes in Excel, do not add any additional information than what is required.
		* Save it as a comma separated value. 
		* Upload the file. If there are any errors, address them through Excel.
		* Verify one last time that the information is correct. Make changes if required.
		* Submit the course information to the database.
		* Please make sure your file is comma separated and not any other delimiter.
2. Open/Close the TA Application
	* Function: This page allows the AC view the application page which is what the student's see. Additionally, this page allows the AC to change the status of the application page between "Closed" and "Open". 
	* This page contains the application form consists of both the introduction information as well as the application itself.
	* Scenarios for Use: 
		* 1 - The AC who wants to change the status of the application. 
		* 2 - The AC wants to view the content of the form, including the front matter if it gets updated from the "Change Application Form" step.
		* 3 - Students when they want to submit an application. It is important to note that they will NOT have access to the Open/Close functionality from Scenario 1.
	* How to Use If You Are the AC: 
		* Refer to Step 0
		* Open Step 3, Open/Close the TA Application - (https://team4.uwaterloo.ca/taform/application.html)
		* Press "Change Status" to change the status of the application. 
		* When the first line "Application Status" is red and says "Closed", then the form is not live and when the page is accessed, students will see a message indicating the system is closed at this time.
		* When the first line "Application Status" is green and says "Open", then the form is live and students can apply.
		* You are able to view the front matter of the form. The front matter consists of everything below the Application Status functionality to the top of "Basic Information".
3. Change Application Form
	* Function: This page allows the AC to change the text on two pages, the Application Intro Page (https://team4.uwaterloo.ca/taform/) and the Application Page (https://team4.uwaterloo.ca/taform/application.html).
	* Scenarios for Use:
		* 1 - Application guidelines have changed.
		* 2 - The term needs to be changed.
		* 3 - A reference link has become outdated.
	* How to Use:
		* Open Step 4, Change Application Form - (https://team4.uwaterloo.ca/taform/upload_front_matter.html)
		* For each file you may change (Intro Page, Front Matter), review the current page.
		* Download the file you would like to change.
		* Make changes within the downloaded file. Ensure you are using HTML syntax and save the file as .txt.
		* To test changes locally you may save the file as .html and preview in your browser. If you do this, resave the file as a .txt file.
		* Select the file you would like to upload.
		* Upload the file.
		* Review the changes by previewing the page you changed again.  
4. Review Applicants
	* Function: This page allows the AC to view basic student information and access links to edit student information and disqualify students from the TA process and change student rankings for courses. This page also allows the AC to export all current student information.
	* Scenarios for Use: 
		* 1 - The AC can export a complete list of applicant information to send to the GC. 
		* 2 - The AC can access links to edit student information, disqualify students from the TA process and change student rankings for courses.
		* 3 - The AC can look for duplicate students. The column headers sort the table to help the AC detect these duplicates.
	* How to Use: 
		* Login to the Application - (https://team4.uwaterloo.ca/login/)
		* Open Step 5, Review Applicants - (https://team4.uwaterloo.ca/taform/applicants.html)
		* Review the students that have applied.
		* Select 'Edit Student Info' on the student you would like disqualify or edit the basic information of.
		* Select 'Edit Rankings' on the student you would like to modify course preference for.
		* Export the student information listed in the table using the 'Export Applicants' button in the top right.
5. Edit Student Information
	* Function: This page allows the AC to edit basic student information and disqualify students from the matching process. 
	* Scenarios for Use: 
		* 1 - A student has made a mistake on their application form and would like the AC to change it. 
		* 2 - The AC want to disqualify a student from the process or prevent a duplicate application from moving forward.
	* How to Use: 
		* Refer to Step 0
		* Open Step 5, Review Applicants - (https://team4.uwaterloo.ca/taform/applicants.html)
		* Review the students that have applied.
		* Select 'Edit Student Info' on the student you would like disqualify or edit the basic information of.
		* The screen you will see lists the student's basic information for the upcoming term as well as the ability to "disqualify" the applicant.
		* You are able to change the students basic information at this time.
		* If you decide to "disqualify" an applicant, they will not appear in the instructor rankings or the final matches.
		* When you select submit you will be re-directed to the Applicant page where you can see the changes you have made for that student.
6. Modify Apps
	* Function: This page allows the AC to modify any student's preference for teaching all courses offered in the upcoming term. 
	* Scenarios for Use: 
		* 1 - A student has made a mistake on their application form and would like the AC to change it. 
		* 2 - The AC needs to force a match between a student and class.
	* How to Use: 
		* Step 0
		* Open Step 5, Review Applicants - (https://team4.uwaterloo.ca/taform/applicants.html)
		* Review the students that have applied.
		* Select 'Edit Rankings' on the student you would like to modify course preference for.
		* This screen will see lists all of the courses for the upcoming term for the selected student. You will see the student's preference for each course.
		* If you would like to make a change to the preference, select a different score in the preference drop down for the corresponding course.
		* When you are satisfied with your changes, hit 'Submit' in the bottom left hand corner. This will save your changes.
		* When the page has refreshed, you will see a 'confirmation of changes' message, along with the updated scores in the preference drop down.
		* To complete this process for a different student, press the 'Back' button in the top right hand corner of the screen.
Last step. [Go on the algorithm page](https://team4.uwaterloo.ca/taform/algorithm.html)
	* You should only land on this page after the following:
		1. Closed applications so no more students can apply.
		2. Assigned the number of teaching assistant positions available for each course.
		3. Check that all rankings are submitted either by the instructor of the course or yourself.
7. Assign Number of TAs
	* Function: This page allows the AC to update the number of TAs needed per course. The AC can enter in integer values (including 0) for the following type of TA positions:
		* 1 TA
		* 3/4 TA
		* 1/2 TA
		* 1/4 TA
	* Per course, the number of TA's will be totaled in the last column
	* This step must be filled out prior to running the matching algorithm in step 10.
8. Send Ranking Links, Monitor Replies
	* Function: This page allows the AC to: send out applicant ranking links to all instructors, view the number of applicants for each course, identify classes that do not have applicants, identify which instructors have not yet ranked applicants, send manual reminder emails to instructors that have not yet ranked, update instructor rankings for applicants
	* Scenarios for Use: 
		* 1 - An instructor has asked the AC to complete the ranking for them. 
		* 2 - The Ranking deadline is approaching and the AC needs to determine which instructors still need to rank.
		* 3 - A reminder email needs to be sent to instructors to complete ranking.
		* 4 - The instructor rankings need to be changed to force a match with the algorithm.
	* How to Use: 
		* Refer to Step 0
		* Open Step 7, Send Ranking Links, Monitor Replies - (https://team4.uwaterloo.ca/taform/ranking_status.html)
		* Review the number of applications for each course and which courses do not have applications.
		* If you are visiting the page to send out all ranking emails, click the 'Send Ranking Emails' button.
		* In a few days, check the status of ranking submissions for each course.
		* If you are visiting the page to modify an instructor's rankings, click on the ranking status 'Link' for the corresponding course.
		* When the deadline for ranking submissions approaches, copy the ranking status 'Link' and use the provided email to send a reminder to the instructor.
9. Export Course and Ranking Information
	* Function: This page allows the AC to:
		* Export the courses currently in the database with the corresponding number of TAs needed
		* Export the ranking information for student and instructor
	* Scenarios for Use:
		* 1 - The AC needs to have these files archived for historical purposes.
		* 2 - The AC wants to run these through the matching algorithm outside of the application.
	* All exports will be a CSV
10. Assign Teaching Assistants
	* Function: This page allows the AC to:
		* Run the matching algorithm
		* Export the students without a position after the match
		* Export the courses that did not get matched
		* Export the final matching result between courses and students
	* All exports will be a CSV
	* The AC should have these files archived for historical purposes.
	* When running the algorithm, the AC should press "Solve Model" followed by "Yes" if they would like to run the algorithm. The AC can also select "No" and the process will not run.
	* The AC can also see the algorithm results without having to export them. The AC should scroll down to view 
		* The students without a position after the match
		* The courses that did not get matched
		* The final matching result between courses and students
	* Unhappy with results?
		* Exclude students, adjust student ratings, adjust instructor ratings or adjust number of positions available and run it again.
		* Another alternative is exporting the course_info and student_info from the previous step and run it with the old excel heuristic.

### Backup Database / Media Files
* Backup
	* The database and media files (resumes) can be backed up by running `python manage.py archive` in the /ta-works/taworks directory on the server. This will create a file on the server containing all data that was in the system at time of archive. 
* Use Backup
	* unzip the archive file - this will result in having a data.json file
	* run `python manage.py loaddata /path/to/data.json` within the /ta-works/taworks directory on the server. 
	* verify the upload within the postgres DB

### Changes you might need:
1. To update the expectations and teaching assistantships management sciences link. You will have to have to change it inside `templates/application.html`.

### Security checklist:
0. [Django security documentation](https://docs.djangoproject.com/en/2.0/topics/security/)
1. Using a secure-only CSRF cookie makes it more difficult for network traffic sniffers to steal the CSRF token.
2. Using a secure-only session cookie makes it more difficult for network traffic sniffers to hijack user sessions.
3. Redirect all connections to HTTPS.
4. Activate the browser's XSS filtering and help prevent XSS attacks.
5. Prevent the browser from identifying content types incorrectly.
6. Django’s querysets are protected from SQL injection since their queries are constructed using query parameterization.
7. Python code is outside of the Web server’s root. 
8. Postgres database cannot be connected via remote host

### Future Improvements
 * Security
	* 1 - Throttle requests for authentication
		> Tips: Limit the number of attempts for login.
	* 2 - Limit the accessibility of your caching system and database using a firewall.
	* 3 - Server side limit file size of cv upload to prevent DOS attacks
		> Tips: Configure the server to only accept specific type of file and size.
* System Features
	* 4 - Email students their applications as confirmation with what they applied.
		> Tips: Replicate the `email_ranking_links()` function in views but for students. Content of the email needs to be changed. This function can be called upon calling POST in the `apply()` function in Views.py.
	* 5 - Ranking a course 1,2,3 as a student without a reason should trigger the student to go back and add a reason.
		> Tips: Have validation checks put in `apply()` function within View.py. These checks should identify if a reason is missing for a course ranked 1,2 or 3. If any check fails, return an error message that identifies a reason is needed for each course ranked 1,2, or 3. Logic for Student ID validation can be applied here.
	* 6 - Add historical data to the system
		> Tips: Would have to use primary keys for all courses OR include the `term` within the unique identifier. All database queries within Views.py would need to be updated to include this additional filter on terms or changed to a primary key filter. Additionally, the `upload_course_list()` function would need to be updated to not clear the database upon upload.
* Usability
	* 8 - Left align headings on Applicants table.
		> Tips: Use CSS align property within the Applicants `th` CSS class.
	* 9 - Format Applicants table header to be the same as all other tables in the system.
		> Tips: Identify the CSS class of the table style you are trying to replicate. Modify the Applicants table CSS class to replicate the `th` styling you want.
	* 10 - Add ascending/descending arrows to the Applicants table for sorting.
		> Tips: This would have to be done through jQuery. Leverage jQuery existing libraries. 
	* 11 -  More explicit error messaging for Student ID entry on the Edit Student Information Page.
		> Tips: Use the error messaging for Student ID that is currently used for the application.html page. Within views and on POST, there are built in validation checks for the length of the Student ID. 
Formulation
	* 12 - Favor students who select 'MASc' or 'PhD' for their current program
		> Tips: Add a term in the objective function to favour thesis students. This term can be made up of:
		>> sum(Xij * Ti) over student i and course j, where Ti = 1 if the student is thesis based and 0 otherwise

		>> Ti is a parameter determined by the value of 'current_program' in the Student table

		>> Ti will need to be added to the parameters in the 'algorithm_run()' method in views.py

		>> the sum(Xij * Ti) will need to be added to the objective value

		>> the performance of the algorithm will need to be tested before and after the change
