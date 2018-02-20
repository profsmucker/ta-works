
"""
How to run this file:
python matchingalgo.py /path-to-course-info /path-to-ranking-info
"""


### Set-up Algorithm variables ###

import pandas as pd
import sys
import pulp

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
    if (total_rating < 2):
        temp.append([row[0], row[1], 0])
    else:    
        temp.append([row[0], row[1], total_rating])

# create the cost matrix
for i in  temp:
    # print i[0]
    costs[i[0]].append(i[2])

# demand here for all the students will be 1 since they can only be assigned to at max 1 course
student_demand = dict()

for i in students:
    student_demand[i] = 1

costs_list = []

for i in courses:
    costs_list.append(costs[i])


### Algorithm formulation ###

costs_list = pulp.makeDict([courses, students], costs_list, 0)

# create the LP object, set up as a maximization problem
prob = pulp.LpProblem("TA_Assignment", pulp.LpMaximize)

# create a list of possible assignments
assignment = [(c,s) for c in courses for s in students]

# variables created to determine optimal assignment
x = pulp.LpVariable.dicts("decision", (courses, students), cat='Binary')
prob += sum([x[c][s] for (c,s) in assignment]) - 0.01*sum([x[c][s]*costs_list[c][s] for (c,s) in assignment])

# add constraint
for c in courses:
    prob += sum(x[c][s] for s in students) <= courses_supply[c], \
    "Sum_of_TA_Positions_%s"%c
for c in courses:
    for s in students:
        prob += x[c][s] <= costs_list[c][s], \
        "Feasibility_{}_{}".format(s, c)
for s in students:
    prob += sum(x[c][s] for c in courses) <= 1, \
    "Sum_of_Students_%s"%s

prob.solve()

# for v in prob.variables():
#     print v.name, "=", v.varValue
# print "Total Cost of TA assignments = ", prob.objective.value()

for c in courses:
    for s in students:
        if x[c][s].value() != 0:
            print(c, s, x[c][s].value())

