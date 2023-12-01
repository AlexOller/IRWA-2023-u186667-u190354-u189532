README

Done by Gabriel Galindo, Alex Oller, Jordi Comellas

This part of the project constists on a folder where we have the main code, named web_app.py and the auxiliar files. Here you can find the csv representing all the tweets clicked in all the sessions that use that code. In templates we find the html files used to execute the Flask. In order to execute the code and open the search engine we need to do the following:

1. First download and unzip the folder. Once done open a cmd and redirect to that folder (cd "path").

2. Now we need to create an environment:
```bash
  - pip3 install virtualenv
  - virtualenv .
  - source bin/activate (for macOS) -----   Scripts\activate.bat (for windows)
```

3. Download all the libraries by executing the following commands in the enviroment created
```bash
  pip install Flask pandas nltk faker
  pip install requests
  pip install numpy
  pip install httpagentparser
  pip install time
  pip install datetime
  pip install json
  pip install random
```

4. Now we can execute the code by:
```bash
  python -V
  # Make sure we use Python 3
  python web_app.py
```
    It will print several lines in the terminal. Copy the URL similar to "http://127.0.0.1:8088/" and paste it in your browser. 


5. Finally you can use the search engine. You can click on the different URLs of the tweets, and there find the stats and dashboards of the session. 