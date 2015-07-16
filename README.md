# Robot-Human Table Turning

##To run:

  1.  navigate to buttonoptions directory
  2.  find out computer's ip
  3. run python/servers/buttonserver.py
  4. in the browser, go to ip:2223/tableturn.html

##Understanding this example:

  ###Files

  ####tableturn.html
  - html layout for the survey
  - links our custom css (mystyle.css, font-awesome), js(js/buttonoptions.js)

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
  
  ####fonts/*
  - font-awesome icons we used for buttons

  ####servers/bottle.py
  - server, no need to modify

  ####servers/Model2.py
  - our survey-specific python module
  - all the web controls are in buttonserver, so it's completely modular