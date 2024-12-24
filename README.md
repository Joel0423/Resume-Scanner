#setup- open the terminal in the cloned repository

```python -m venv .venv```  
```pip install -r requirements.txt```

#to run-
open the resume-scanner folder

create a file- config.py  
paste this-  
```
DB_USERNAME = "root"
DB_PASSWORD = ""
DB_HOST = "localhost"
DB_NAME = "resume_scanner_db"
DB_PORT = "3306"

SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
```  
  

in the terminal-  

```flask --app main run --debug```
  
or- run the main.py file
