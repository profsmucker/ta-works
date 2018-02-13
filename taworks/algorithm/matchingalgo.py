"""
How to run this file:
python /path-to-course-info /path-to-ranking-info matchingalgo.py
"""

import pandas as pd
import sys


df_course_info = pd.read_csv(sys.argv[1], header=None, sep=',')
df_ranking_info = pd.read_csv(sys.argv[2], header=None, sep=',')

# warehouse
courses = []

# supply
courses_supply = dict()

for index, row in df_course_info.iterrows():
    num_pos = row[3] + row[4] + row[5] + row[6]
    courses_supply[row[0]] = num_pos
    courses.append(row[0])

# bars, set here because we want uniqness
students = []

# list of cost for each assignment
costs = {}

for i in courses:
    costs[i] = []

temp = []
for index, row in df_ranking_info.iterrows():
    if (row[1] not in students):
        students.append(row[1])
    total_rating = row[2] + row[3]
    temp.append([row[0], row[1], total_rating])

# create the cost matrix
for i in  temp:
    costs[i[0]].append(i[2])

# demand here for all the students will be 1 since they can only be assigned to at max 1 course
student_demand = dict()

for i in students:
    student_demand[i] = 1

# sample of what we can use to for the model
print ('courses', courses)
print ('supply', courses_supply)
print ('students', students)
print ('demand', student_demand)
print ('costs', costs)