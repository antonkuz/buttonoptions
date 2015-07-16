# Robot-Human Table Turning

##To run

  1.  navigate to buttonoptions directory
  2.  find out computer's ip
  3. run python/servers/buttonserver.py
  4. in the browser, go to ip:2223/tableturn.html

##Files

####tableturn.html
  - html layout for the survey
  - links our custom css (mystyle.css, font-awesome, favicon), js(js/buttonoptions.js)

####js/buttonoptions.js
  - handles all buttonclicks
  - keeps user specific data (picCount) in sessionData

####servers/buttonserver.py
  - handles post requests from javascript on the client side
  - redirects to html pages

####js/surveyhandler.js
  - catches submit button click on the survey page
  - goes over the input radiobuttons/textfields

####css/*
  - bootstrap for buttons
  - mystyle.css for button positioning

####survey.html
  - questionnaire page (loads after the game)

####lib/*
  - necessary for bootstrap, button handling
  
####fonts/*
  - font-awesome icons we used for buttons

####servers/bottle.py
  - server, no need to modify

####data, videos, images, output, servers/Model2.py
  - survey-specific files. You won't need them

##How to alter for your own needs

####servers/buttonserver.py
  This file is responsible for returning data - instruction images, game status - to the client.
  The client communication comes in the ''' requestData ''' variable. It has data such as what slide the user is currently on, ''' (sessionData["picCount"]) ''' or id of the button that was clicked ''' requestData["buttonID"] '''


'''python
#go to next/prev pic according to button clicked
buttonClicked = requestData["buttonID"]
if sessionData["picCount"]<5:
	if buttonClicked==0:
	  sessionData["picCount"] -= 1
	elif buttonClicked==1:
	  sessionData["picCount"] += 1
'''
  You will need to adjust that for the type of survey/number of slides you have

  For different slides we have different images, button labels.
  Example - return slide1.jpg and don't display 'back' button
'''python
if sessionData["picCount"]==1:
ret = {"imageURL": "images/Slide1.JPG",
       "buttonLabels": ["null", "Next"],
       "instructionText": "Instructions 1/3",
       "sessionData": sessionData,
   "buttonClass": "btn-primary"}
return json.dumps(ret)
'''
  buttonoptions.js deals with the returned json.


