# End to end testing instructions

_You will need to vpn if you aren't on campus wifi and let others know you're about to deploy on the box, only 1 branch can be tested at a time_

### How to ssh into the box and deploy your branch
1. In your terminal enter `ssh team4@team4.uwaterloo.ca`, pw=walkwalk
2. Enter `cd venv/ta-works/taworks/`
3. Here check what branch is deployed currently `git branch`
4. Enter `git pull` -> this will pull all the branches to the box
5. Enter `git checkout 'your branch name'`
6. Enter `git branch` verify that you were able to checkout your branch successfully
7. Enter `sudo /etc/init.d/apache2 restart`, pw=walkwalk
8. Viola, your branch should be deployed
9. Once you're done testing your branch, switch back to master, `git checkout master`
10. Do not push anything from this box(especially master branch) 

### How to get into postgres from the box
1. Follow ssh instructions above to get into the box
2. Enter `sudo -i -u postgres`
3. Enter `psql taform`
4. Enter `\dt` -> verify all the tables are there, look for the prefix ta_form. We currrently have a table for application, course, student and temp_course
_after running the queries below, you will need to press `q` to get out of it_
5. Enter `select * from taform_course;` to see courses uploaded to the database.
6. Enter `select * from taform_application;` to see applications, there should be 1 created for each course
7. After new course uploads, you can verify applications table are empty

### Running the virtual enviornment
1. Enter `source ~/venv/bin/activate`

### Running Migrations
1. Enter `python manage.py makemigrations`
2. Enter `python manage.py migrate`

### Running Static files
1. Enter `python manage.py collectstatic`

### Running Python in Terminal
1. Enter `python manage.py shell`
2. Once the python shell has opened, enter `from taform import *`

### End to end testing on new builds
1. [Go on prod and login](https://team4.uwaterloo.ca/login/)
   * try user:fake pw:fakepw -> it should fail
   * try user:taform pw:!@#QWEasdzxc -> it should let you login
   * verify logging out and then [Go to page directly](https://team4.uwaterloo.ca/taform/home.html) -> redirects you to login again
2. [Go on password reset](https://team4.uwaterloo.ca/taform/password_reset)
    * verify entering your own email won't give you the password reset link to the account 'taform'
    * verify that resetting with the email 'uwtaworks@gmail.com' results in a link to reset password
    * reset the password
    * test login with new password
3. [Go on password change](https://team4.uwaterloo.ca/taform/password_change)
    * verify you can only land on this page if you're logged in
    * change the password back to the original password for 'taform'
    * logout and login with original password
4. [Go on AC view](https://team4.uwaterloo.ca/taform/home.html)
   * verify all the links work and style sheets are applied
5. [Go on course upload](https://team4.uwaterloo.ca/taform/taform/course_list.html)
    * verify CSV template can be downloaded and download it
    * upload a subset of this downloaded template
    * verify home button takes you back to AC view
6. [Go on Change Application Form](https://team4.uwaterloo.ca/taform/upload_front_matter.html)
    * verify you can download existing front matter text file and intro page text file
    * make edits to both files and upload
    * go back to intro page and application page and check your edits are uploaded
7. [Go on application page](https://team4.uwaterloo.ca/taform/application.html)
    * verify subset of courses you uploaded match
    * verify style sheets are applied on this page
    * verify you can submit an application (go to the db and verify entries were made)
    * verify the checkboxes and student visa drop down works
    * verify links in the courses lead to adm
    * verify Expectations and bottom link work
    * verify submission of applications brings you to application submitted page
    * verify you cannot press back from there
    * verify that entering preferenece of 4 will trigger error message on submit (currently a bug, you will see)
    * verify rating "I am unable to TA this course" will not give a enter reason button
    * verify ratings other than "I am unable to TA this course" will give reason button
    * verify you can press enter reason multiple times and the previous entered information is saved
    * verify you cannot go over 255 character limit
    * verify if you press cancel, nothing saves
8. [Go on application page](https://team4.uwaterloo.ca/taform/application.html)
    * verify that if you a not logged in as the AC and the app is closed you do not see it.
    * verify that if you a not logged in as the AC and the app is open you can not see it.
9. [Go on ranking status page](https://team4.uwaterloo.ca/taform/ranking_status.html)
    * _Note: It will actually send emails that are in the course table, check the emails in the database before testing_
    * verify courses uploaded shows up here
    * change email in course database to include your own and test send email feature (alter the emails in the db if you have to)
    * verify email sends with or without optional email box filled out
    * verify emails in your mailbox look like they're suppose to
    * verify that each course has a 'number of applicants' field 
    * verify that each course has a 'Ranking status field'
    * verify that each course has a ranking status 'Link'
    * verify that any course from the DB that does not have applicants still shows in the table
    * take a sample course from the table and search the DB to confirm number of applicants (application table)
    * take a sample course from the table and search the DB to confirm the ranking status (application table - instructor preference)
    * apply to a course and confirm the number of applicants inscreases

10. [Go on number of tas page](https://team4.uwaterloo.ca/taform/number_tas.html)
    * verify that the courses displayed are all courses that are in the database
    * verify that the courses are sorted by 'course_id' and then 'section'
    * verify that the number of tas that are displayed are the same as what is stored in the database
    * change the number of tas and submit - verify that the number was saved to the database
    * verify receiving a response message for submit
    * verify that the form will not accept anything but a numeric answer for # of tas
11. [Go on instructor ranking page](https://team4.uwaterloo.ca/taform/instructor/728848679E284498A8C7D2E2C4/)
    * verify students who put "0" as their preference when applying to courses do not appear on the instructor ranking page for the course
    * verify that multiple instructors can look at their tokenized links at the same time
    * verify that the preferences wrote to the database
    * verify that the preferences are preloaded from the database if the instructor has already submitted them
    * verify that the students are being listed alphabetically by first name 
12. [Go on export page](https://team4.uwaterloo.ca/taform/export.html)
    * verify that the export results for "Export Course Info" match what was uploaded earlier
    * verify that the export results for "Export Rankings Info" match what was uploaded earlier
    * verify that no students who rated a course and no instructors who rated a student zero appear in export

13. [Go on the algorithm page](https://team4.uwaterloo.ca/taform/algorithm.html)
    * Download both csv exports from the [export page](https://team4.uwaterloo.ca/taform/export.html)
        * Use these csv exports as a point of reference for what is saved by the system
    * Run the algorithm. Verify it won't work without applicants or courses in the database.
    * Click all the export buttons. Click them when there are no applicants, no instructor rankings and no TA assignment numbers (results in an error message) and when there are (will output a solution). Click them after a successful algorithm run.
    * Compare the output on the page with the csv exports.
    * Verify that students are not matched with courses they did not apply to, or instructors did not rank them for.
14. [Go to Review Student apps page](https://team4.uwaterloo.ca/taform/applicants.html)
    * verify that all students & their corresponding info is listed in alphabetical order
    * verify that the links to the edit student info & review student rankings work
15. Go to Edit Student apps page (select a student from the Review Student apps page)
    * verify that the information in the edit student app page can be modified
    * verify that when the information is submitted it updates in the "Review Student apps" page
    * verify that if a student is "disqualified" they won't appear in the instructor ranking page
    * verify that if a student is "disqualified" they won't appear in "export rankings"
    * verify that if a student is "disqualified" they won't appear in any matching (or matching exports)
    * verify that if a student is "disqualified" after they are ranked, then they qualify again, the instructor ranking is retained
16. Go to Modify Apps Page (select a student from the Review Student apps page)
    * Click the Go! button on the algorithm page. Click go when there are applicants (will run) and no applicants (results in an error message).
    * Click the export button. Run when there are no applicants, no instructor rankings and no TA assignment numbers (results in an error message) and when there are (will output a solution).
    * Compare the output with the csv exports to make sure the solution is optimal.

****************************************************************************************************
Additional testing instructions:

1. Test the algorithm executable file
    * Download both csv exports from the [export page](https://team4.uwaterloo.ca/taform/export.html)
    * Run the algorithm executable (python2 matchingalgo.py /path-to-course-info/file_name.csv /path-to-ranking-info/file_name.csv > /path-to-output/file_name.csv)
    * Verify that the correct students have been assigned to the correct courses (and in the most optimal way)
