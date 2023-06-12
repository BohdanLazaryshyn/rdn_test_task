# These are two scripts for reading information about the results of the "electricity market for the next day".

## Нow to prepare the project for launch
```
- Write in Git Bash
git clone https://github.com/BohdanLazaryshyn/rdn_test_task
- Open the project in your interpreter
python -m venv venv
venv\Scripts\activate (on Windows)
source venv/bin/activate (on macOS)
pip install -r requirements.txt
lask db init
flask db migrate -m "Initial migration."
flask db upgrade
```

1)The first script, after starting the program, will run every day after 12:00 and check whether the market has closed, after which it will read information from the site. You can adjust the frequency of checking requests to the site itself in the "job" function. It is in the file "main".
### how to run the script
```
python main.py
```


2)It provides an opportunity to parse information for a specific date and store it in the database, as well as search for information in the database by date. 
### how to run the script
```
python flask_end.py
Running on http://127.0.0.1:5000

```
