# ta-works

### Initial environment set-up:
1. [Install Homebrew and install Postgress](https://launchschool.com/blog/how-to-install-postgresql-on-a-mac)
   * Run command: brew install postgresql
2. Install python 2.7 and pip
   * [Install python 2.7/pip](https://pip.pypa.io/en/stable/installing/)
   
### Initial database set-up:
1. Postgresql database set-up:
   * Start the database: brew services start postgresql
   * Type all commands in taworks/setup.txt

### Initial clone of ta-works:
1. Go to the directory you want the repo in command line
   * [Documentation](https://stackoverflow.com/questions/9547730/how-to-navigate-to-to-different-directories-in-the-terminal-mac)
2. Run command: git clone ...
   
### Using git:
[Documentaiton](https://github.com/codepath/ios_guides/wiki/Using-Git-with-Terminal)

### Running the application:
1. Install the required python packages for this application   
   * pip install requirements.txt
2. Launch the app
   * python manage.py migrate
   * python manage.py runserver
