# CIS571_P1
Project 1 for CIS 571. Implements a website that invokes 2 APIs from online and 2 of my own.

## How to use
To use this application, you will first have to install Python 3. I am currently using version 3.7.6.
You will also need pip to install packages.
To install all the packages that are used, run `python3 -m pip install -r requirements.txt`.
From there you will need to set the secret key used by the app configuration file. To do that, run 
the script `set_secret_key.sh`. Then you can run the web app. `python3 waitress_server.py` should work.
