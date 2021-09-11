# KryptoTask

## I've tried my best to accomplish the task using sqlite databse but there are some bugs that might be noticed.

Steps to run:
- pip install requirements.txt
- python test.py
- open 127.0.0.1:5000 in browser for home page to login using HTML page (use any name and set password = 'ankit')
- Note: any name can be used, but password has to be 'ankit' (without quotes)

## Making edit in Readme file in response to the mail sent today. 

## API endpoints covered

- /alerts/create : endpoint to create an alert. (can also be accessed using /createAlert)
- /alerts/delete : endpoint to delete and alert. (can also be accessed using /deleteAlert)

## Some additional endpoints added for easy usage:

- /createAlert : Opens the HTML page to enter alert details.
- /deleteAlert : Opens the HTML page to delete an alert.

## Approach

My approach was to use Flask as the framework for building the api since it is easy to use and has a lot of advantages over Django since Falsk is a more scalable framework.
The file test.py runs an infinite loop along with the Flask server, in order to query the coin prices api and fetch all the coin prices. The program makes such requests every 10 seconds. All alerts made by the user are saved in the form of a dictionary in the "coins" variable. Example:  once a user creates the alert for 'bitcoin' and saves price to 500, the dictionary becomes "{'bitcoin' : [500]}" and multple prices can be added to each coin Example: user may have multiple alert prices for bitcoin in the previous example if the user adds another alert for bitcoin for the price 400 then the dictionary becomes : "{'bitcoin' : [500,400] }". Once a coin reaches its desired price, the users are sent an email (in program, the function sendEmail is called).
