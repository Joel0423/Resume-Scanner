#setup- open the terminal in the cloned repository

```python -m venv .venv```  
```pip install -r requirements.txt```  

create a environment variable called 'SQLALCHEMY_DATABASE_URI'  
with value - mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}  
replace stuff in {} with actual values of your database  

inside the resume-scanner folder

#to run-  

in the terminal-  

```flask --app main run --debug```
  
or- run the main.py file
