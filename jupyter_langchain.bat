SET CURPATH=%cd%
CALL .venv\Scripts\activate
jupyter notebook --notebook-dir=%CURPATH%
