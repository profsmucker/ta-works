# TA Works - Environment Set Up
_Instructions are for Mac OS_

### Initial Environment Set-up:
1. [Install Homebrew and install Postgress](https://launchschool.com/blog/how-to-install-postgresql-on-a-mac)
   * Run command: `brew install postgresql`
2. Install python 2.7 and pip
   * [Install python 2.7/pip](https://pip.pypa.io/en/stable/installing/)

### Initial Clone of ta-works:
1. Access the directory of where you would like the repo to live
   * [Documentation](https://stackoverflow.com/questions/9547730/how-to-navigate-to-to-different-directories-in-the-terminal-mac)
2. Run command: git clone ...

### Using Git:
[Documentation](https://github.com/codepath/ios_guides/wiki/Using-Git-with-Terminal)

### Initial Database Set-Up:
1. Postgresql database set-up:
   * Start the database: `brew services start postgresql`
   * Type all commands in taworks/setup.txt

### Running the Application:
1. Install the required python packages for this application   
   * `pip install -r requirements.txt`
2. Make migrations
   * Enter `python manage.py makemigrations`
   * Enter `python manage.py migrate`
3. Run static files
   * Enter `python manage.py collectstatic`
4. Run the app!
   * Enter `python manage.py runserver`
