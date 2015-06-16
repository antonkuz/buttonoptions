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

  #init dictionary of users
  global d

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
    ret = {"imageURL": "images/Slide1.JPG",
           "buttonLabels": ["null", "Next"],
           "instructionText": "Instructions 1/3",
           "sessionData": sessionData,
       "buttonClass": "btn-primary"}
    return json.dumps(ret)

  if sessionData["picCount"]==2:
    ret = {"imageURL": "images/Slide2.JPG",
           "buttonLabels": ["null", "Next"],
           "instructionText": " ",
           "sessionData": sessionData,
       "buttonClass": "btn-primary"}
    return json.dumps(ret)

  if sessionData["picCount"]==3:
    ret = {"imageURL": "images/Slide3.JPG",
           "buttonLabels": ["Prev", "Next"],
           "instructionText": " ",
           "sessionData": sessionData}
    return json.dumps(ret)
  
  if sessionData["picCount"]==4:
    ret = {"imageURL": "images/Slide4.JPG",
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
  
  #following code may need mturk_id, so get it once now
  mturk_id = request.cookies.get('mturk_id','NOT SET')

  if sessionData["picCount"]==7:
    ret = {"imageURL": "images/Slide5.JPG",
           "buttonLabels": ["null", "START"],
           "instructionText": " ",
           "sessionData": sessionData,
       "buttonClass": "btn-primary"}
    data[mturk_id].append("round two")
    sessionData["picCount"]+=1       
    return json.dumps(ret)

  if sessionData["picCount"]==8:
    Model2.restartTask(d,mturk_id,prevTableTheta)
    ret = {"imageURL": "images/T100.JPG",
           "buttonLabels": ['<i class="fa fa-2x fa-rotate-right fa-rotate-225"></i>',
                            '<i class="fa fa-2x fa-rotate-left fa-rotate-135"></i>'],
           "instructionText": "Choose how you would like to rotate the table.",
           "sessionData": sessionData,
       "buttonClass": "btn-success"}
    sessionData["picCount"]+=1  
    return json.dumps(ret)  
  
  #record in log
  data[mturk_id].append(buttonClicked)

  #get next move#
  currTableTheta, message = \
    Model2.getMove(d,request.cookies.get('mturk_id','NOT SET'),buttonClicked)

  if currTableTheta==0 or currTableTheta==180:
    imageLink = "images/T{}.JPG".format(currTableTheta)
    if sessionData["picCount"]==6:
      prevTableTheta = currTableTheta
      sessionData["picCount"]+=1
    elif sessionData["picCount"]==9:
      sessionData["toSurvey"] = True
    ret = {"imageURL": imageLink,
           "buttonLabels": ["null","Next"],
           "instructionText": "The table is in a horizontal position. You finished the task!",
           "sessionData": sessionData}
    return json.dumps(ret)
  else:
    ret = {"imageURL": "images/T{}.JPG".format(currTableTheta),
           "buttonLabels": ['<i class="fa fa-2x fa-rotate-right fa-rotate-225"></i>',
                            '<i class="fa fa-2x fa-rotate-left fa-rotate-135"></i>'],
           "instructionText": message,
           "sessionData": sessionData,
           "buttonClass": "btn-success"}
    return json.dumps(ret)

@app.post('/submit_survey')
def handle_survey():
  mturk_id = request.cookies.get('mturk_id', 'EXPIRED')
  for i in xrange(1,16):
    data[mturk_id].append(request.forms.get(str(i)))
  with open('log.json', 'w') as outfile:
    json.dump(data, outfile)
  print("User {} submitted the survey".format(mturk_id))
  return "<p> Your answers have been submitted. ID for mturk: {}".format(mturk_id)

def backupLog():
  i=1
  while (os.path.isfile("log-backup-{}.json".format(i))):
    i+=1
  shutil.copy("log.json","log-backup-{}.json".format(i))
 
Model2.globalsInit()
backupLog()
run(app, host='0.0.0.0', port=2223)