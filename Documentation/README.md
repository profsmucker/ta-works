# taworks

### Existing Bugs:
1. In the page Teaching Assistant Assignment (Step 8) -> Pressing `Go` multiple times will cause the table to display multiple duplicates and incorrect # of positions available. This bug also affects the `export` csv and will persist. Quick fix is to press `Go` once and only once.

### Solved Bugs:
1.
2.
3.

### System Instructions:
0. Login to the Application - (https://team4.uwaterloo.ca/login/)
1. 
2.
3. [Modify Apps](404)
	* Function: This page allows the AC to modify any students preference for teaching all courses offered in the upcoming term. 
	* Scenarios for Use: 1 - A student has made a mistake on their application form and would like the AC to change it. 2 - The AC needs to force a match between a student and class.
	* How to Use: 
		* Open Step X, Modify or Delete Student Applications - ()
		* Review the students that have applied.
		* Select 'Make Preference Changes' on the student you would like to modify course preference for.
		* The screen you know see lists all of the courses for the upcoming term, along with the student's preference to TA each of them.
		* If you would like to make a change to the preference, select a different score in the preference drop down for the corresponding course.
		* When you are satisfied with your changes, hit 'Submit' in the bottom left hand corner. This will save your changes.
		* When the page has refreshed, you will see a 'confirmation of changes' message, along with the updated scores in the preference drop down.
		* to complete this process for a different student, press the 'Back' button in the top right hand corner of the screen.
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
