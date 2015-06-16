from bottle import Bottle, run, static_file, request,response
import json
import string
import random
import json
import Model2
import os
import shutil
import time 

app = Bottle()
data = dict()
d=dict()
prevTableTheta = -1


@app.route('<path:path>')
def server_static(path):
  return static_file(path, root=".")

@app.post('/ui/button') # or @route('/login', method='POST')
def do_click():
  global prevTableTheta

  #add artificial delay
  time.sleep(0.5)

  #manually set value
  totalPicsNum = 19
  survey_duration = 60*60 #1 hour. after that cookie expires
  requestData = json.loads(request.body.getvalue())
  sessionData = requestData["sessionData"]

  if "toSurvey" in sessionData:
    return json.dumps({"toSurvey":True})

  #init log variable
  global data

  #go to next/prev pic according to button clicked
  buttonClicked = requestData["buttonID"]
  if sessionData["picCount"]<5:
    if buttonClicked==0:
      sessionData["picCount"] -= 1
    elif buttonClicked==1:
      sessionData["picCount"] += 1

  if sessionData["picCount"]==1:
    ret = {"imageURL": "images/Slide1.jpg",
           "buttonLabels": ["null", "Next"],
           "instructionText": "Instructions 1/3",
           "sessionData": sessionData,
		   "buttonClass": "btn-primary"}
    return json.dumps(ret)

  if sessionData["picCount"]==2:
    ret = {"imageURL": "images/Slide2.jpg",
           "buttonLabels": ["null", "Next"],
           "instructionText": " ",
           "sessionData": sessionData,
		   "buttonClass": "btn-primary"}
    return json.dumps(ret)

  if sessionData["picCount"]==3:
    ret = {"imageURL": "images/Slide3.jpg",
           "buttonLabels": ["Prev", "Next"],
           "instructionText": " ",
           "sessionData": sessionData}
    return json.dumps(ret)
	
  if sessionData["picCount"]==4:
    ret = {"imageURL": "images/Slide4.jpg",
           "buttonLabels": ["Prev", "START"],
           "instructionText": " ",
           "sessionData": sessionData}
    return json.dumps(ret)

  if sessionData["picCount"]==5:
    #generate a cookie with user's ID
    gen_id = ''.join(random.choice(string.ascii_uppercase +
      string.digits) for _ in range(6))
    response.set_cookie('mturk_id', gen_id, max_age=60*60, path='/')
    data[gen_id] = []
    ret = {"imageURL": "images/T100.JPG",
           "buttonLabels": ['<i class="fa fa-2x fa-rotate-right fa-rotate-225"></i>',
                            '<i class="fa fa-2x fa-rotate-left fa-rotate-135"></i>'],
           "instructionText": "Choose how you would like to rotate the table.",
           "sessionData": sessionData,
		   "buttonClass": "btn-success"}
    sessionData["picCount"]+=1       
    return json.dumps(ret)
  
  if sessionData["picCount"]==7:
    ret = {"imageURL": "images/Slide5.jpg",
           "buttonLabels": ["null", "START"],
           "instructionText": " ",
           "sessionData": sessionData,
		   "buttonClass": "btn-primary"}
    sessionData["picCount"]+=1       
    return json.dumps(ret)

  if sessionData["picCount"]==8:
    Model2.restartTask(d,request.cookies.get('mturk_id','NOT SET'),prevTableTheta)
    ret = {"imageURL": "images/T100.JPG",
           "buttonLabels": ['<i class="fa fa-2x fa-rotate-right fa-rotate-225"></i>',
                            '<i class="fa fa-2x fa-rotate-left fa-rotate-135"></i>'],
           "instructionText": "Choose how you would like to rotate the table.",
           "sessionData": sessionData,
		   "buttonClass": "btn-success"}
    sessionData["picCount"]+=1  
    return json.dumps(ret)	
	
  #record in log
  mturk_id = request.cookies.get('mturk_id','NOT SET')
  data[mturk_id].append(buttonClicked)
  

  # if sessionData["picCount"]==5:
  # #instructions for the second round

  #get next move#
  global d
  currTableTheta, resultState, resultBelief, resultHAction, resultRAction, message = \
   Model2.getMove(d,request.cookies.get('mturk_id','NOT SET'),buttonClicked)

  if currTableTheta==0 or currTableTheta==180:
    imageLink = "images/T{}.JPG".format(currTableTheta)
    if sessionData["picCount"]==6:
	  prevTableTheta = currTableTheta
	  sessionData["picCount"]+=1
    elif sessionData["picCount"]==8:  
      sessionData["toSurvey"] = True
    ret = {"imageURL": imageLink,
           "buttonLabels": ["null","Next"],
            "instructionText": "The table is in a horizontal position. You finished the task!",
           "sessionData": sessionData}
    return json.dumps(ret)
  else:
    instructionString ='''
      The current angle is: {}<br>
      The current state is: {}<br>
      The current belief is: {}<br>
      You did action: {}<br>
      Robot did action: {}<br>
	  {}<br>
    '''.format(currTableTheta, resultState, resultBelief, resultHAction, resultRAction, message)

    ret = {"imageURL": "images/T{}.JPG".format(currTableTheta),
           "buttonLabels": ['<i class="fa fa-2x fa-rotate-right fa-rotate-225"></i>',
                            '<i class="fa fa-2x fa-rotate-left fa-rotate-135"></i>'],
           "instructionText": instructionString,
           "sessionData": sessionData,
		   "buttonClass": "btn-success"}
    return json.dumps(ret)

@app.post('/submit_survey')
def handle_survey():
  mturk_id = request.cookies.get('mturk_id', 'EXPIRED')
  data[mturk_id].append(request.forms.get('a'))
  data[mturk_id].append(request.forms.get('b'))
  #print("user {}: 'a' answer is {}".format(mturk_id,request.forms.get('a')))
  #print("user {}: 'b' answer is {}".format(mturk_id,request.forms.get('b')))
  with open('log.json', 'w') as outfile:
    json.dump(data, outfile)
  return "<p> Your answers have been submitted. ID for mturk: {}".format(mturk_id)

def backupLog():
  i=1
  while (os.path.isfile("log-backup-{}.json".format(i))):
    i+=1
  shutil.copy("log.json","log-backup-{}.json".format(i))

Model2.globalsInit()
backupLog()
run(app, host='0.0.0.0', port=2223)
