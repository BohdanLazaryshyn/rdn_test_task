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
```

1)The first script, after starting the program, will run every day after 12:00 and check whether the market has closed, after which it will read information from the site. You can adjust the frequency of checking requests to the site itself in the "job" function. It is in the file "main".
### how to run the script
```
python main.py
```


2)The second script launches an endpoint with a form where you can specify the date you are interested in and retrieve information for that date. 
### how to run the script
```
cd RDN_Flask
python flask_end.py
```

Optional: For two scripts, it is possible to store information in a file and a database. for this you need to uncomment the relevant functions at the bottom of the scripts.