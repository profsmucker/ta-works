# taworks

### Existing Bugs:
1. In the page Teaching Assistant Assignment (Step 8) -> Pressing `Go` multiple times will cause the table to display multiple duplicates and incorrect # of positions available. This bug also affects the `export` csv and will persist. Quick fix is to press `Go` once and only once.
2. When you run the algorithm after disqualifying a student there is a resulting server 500 error

### Solved Bugs:
1.
2.
3.

### System Instructions:
0. Login to the Application - (https://team4.uwaterloo.ca/login/)
1. [Review Applicants]
	* Function: This page allows the AC to view basic student information and access links to edit student information, disqualify students from the TA process and change student rankings for courses. This page also allows the AC to export all current student information.
	* Scenarios for Use: 
		* 1 - The AC can export a complete list of applicant information to send to the GC. 
		* 2 - The AC can access links to edit student information, disqualify students from the TA process and change student rankings for courses.
	* How to Use: 
		* Login to the Application - (https://team4.uwaterloo.ca/login/)
		* Open Step 5, Review Applicants - (https://team4.uwaterloo.ca/taform/applicants.html)
		* Review the students that have applied.
		* Select 'Edit student info' on the student you would like disqualify or edit the basic information of.
		* Select 'Edit rankings' on the student you would like to modify course preference for.
		* Export the student information listed in the table using the "export applicants" button in the top right.
2. [Edit Student Information]
	* Function: This page allows the AC to edit basic student information and disqualify students from the matching process. 
	* Scenarios for Use: 
		** 1 - A student has made a mistake on their application form and would like the AC to change it. 
		** 2 - The AC want to disqualify a student from the process or prevent a duplicate application from moving forward.
	* How to Use: 
		* Refer to Step 0
		* Open Step 5, Review Applicants - (https://team4.uwaterloo.ca/taform/applicants.html)
		* Review the students that have applied.
		* Select 'Edit student info' on the student you would like disqualify or edit the basic information of.
		* The screen you will see lists the students basic information for the upcoming term as well as the ability to "disqualify" the applicant.
		* You are able to change the students basic informaiton at this time.
		* If you decide to "disqualify" an applicant, they will not appear in the instructor rankings or the final matches.
		* When you select submit you will be re-directed to the Applicant page where you can see the changes you have made for that student.
3. [Modify Apps]
	* Function: This page allows the AC to modify any students preference for teaching all courses offered in the upcoming term. 
	* Scenarios for Use: 
		** 1 - A student has made a mistake on their application form and would like the AC to change it. 
		** 2 - The AC needs to force a match between a student and class.
	* How to Use: 
		* Step 0
		* Open Step 5, Review Applicants - (https://team4.uwaterloo.ca/taform/applicants.html)
		* Review the students that have applied.
		* Select 'Edit rankings' on the student you would like to modify course preference for.
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
	* Function This page allows the AC to run the matching algorithm to match students to courses and the ability to export the following in separate csvs:
		1. Students that didn't get matched by the algorithm
		2. Courses that still need a position filled
		3. Matching results of the algorithm
	* Unhappy with results?
		* Exclude students, adjust student ratings, adjust instructor ratings or adjust number of positions available and run it again.
		* Another alternative is exporting the course_info and student_info from the previous step and run it with the old excel heuristic.
4. [Open/Close the TA Application]
	* Function: This page allows the AC view the application page which is what the student's see. Additionally, this page allows the AC to change the status of the application page between "Closed" and "Open". 
	* Scenarios for Use: 
		** 1 - The AC who wants to change the status of the application. 
		** 2 - The AC wants to view the content of the form, including the front matter if it gets updated from the "Change Application Form" step.
		** 3 - Students when they want to submit an application. It is important to note that they will NOT have access to the Open/Close funtionality from Scenario 1.
	* How to Use If You Are the AC: 
		* Refer to Step 0
		* Open Step 3, Open/Close the TA Application - (https://team4.uwaterloo.ca/taform/application.html)
		* Press "Change Status" to change the status of the application. 
		* When the first line "Application Status" is red and says "Closed", then the form is not live and students can not apply or access the application page.
		* When the first line "Application Status" is green and says "Open", then the form is live and students can apply.
		* You are able to view the from matter of the form. The front matter consists of everything below the Application Status functionality to the top of "Basic Information".
		
