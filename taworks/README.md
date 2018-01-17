# ta-works

##_you will need to vpn if you aren't on campus wifi_
##_let others know you're about to deploy on the box, only 1 branch can be tested at a time_

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

### End to end testing on new builds
1. [Go on prod and login](https://team4.uwaterloo.ca/login/)
   * try user:fake pw:fakepw -> it should fail
   * try user:taform pw:!@#QWEasdzxc -> it should let you login
   * verify logging out and then [Go to page directly](https://team4.uwaterloo.ca/taform/home.html) -> redirects you to login again
2. [Go on AC view](https://team4.uwaterloo.ca/taform/home.html)
   * verify all the links work and style sheets are applied
3. [Go on course upload](https://team4.uwaterloo.ca/taform/taform/course_list.html)
    * verify CSV template can be downloaded and download it
    * upload a subset of this downloaded template
    * verify home button takes you back to AC view
4. [Go on application page](https://team4.uwaterloo.ca/taform/application.html)
    * verify subset of courses you uploaded match
    * verify style sheets are applied on this page
    * verify you can submit an application (go to the db and verify entries were made)
    * verify the checkboxes and student visa drop down works
    * verify links in the courses lead to adm
    * verify Expectations and bottom link work
    * verify submission of applications brings you to application submitted page
    * verify you cannot press back from there
