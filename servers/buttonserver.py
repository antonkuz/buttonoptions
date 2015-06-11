from bottle import Bottle, run, static_file, request,response
import json
import string
import random
import json
import Model2

app = Bottle()
surveyData = dict()
d=dict()


@app.route('/static/<path:path>')
def server_static(path):
  return static_file(path, root=".")

@app.post('/ui/button') # or @route('/login', method='POST')
def do_click():
  #manually set value
  totalPicsNum = 19
  survey_duration = 60*60 #1 hour. after that cookie expires
  requestData = json.loads(request.body.getvalue())
  sessionData = requestData["sessionData"]

  if "toSurvey" in sessionData:
    return json.dumps({"toSurvey":True})

  #generate a cookie on info slide
  if sessionData["picCount"]==1:
    gen_id = ''.join(random.choice(string.ascii_uppercase +
      string.digits) for _ in range(6))
    response.set_cookie('mturk_id', gen_id, max_age=60*60, path='/')
    global surveyData
    surveyData[gen_id] = []
    ret = {"imageURL": "images/100.jpg",
           "buttonLabels": ["Clockwise", "Counterclockwise"],
           "instructionText": "Turn the table",
           "sessionData": sessionData}
    sessionData["picCount"] += 1
    return json.dumps(ret)
  #print("cookie set to: {}".format(request.cookies.get('mturk_id','NOT SET')))  

  buttonClicked = requestData["buttonID"]
  #get next move#
  global d
  currTableTheta, resultState, resultBelief, resultHAction, resultRAction = \
   Model2.getMove(d,request.cookies.get('mturk_id','NOT SET'),buttonClicked)
  #end get next move#

  if currTableTheta==42:
    imageLink = "images/18.jpg"
    sessionData["toSurvey"] = True
    ret = {"imageURL": imageLink,
           "buttonLabels": ["null","Proceed to next step"],
           "instructionText": "GAME OVER",
           "sessionData": sessionData}
    return json.dumps(ret)
  else:
    instructionString ='''
      The current angle is: {}<br>
      The current state is: {}<br>
      The current belief is: {}<br>
      You did action: {}<br>
      Robot did action: {}<br>
    '''.format(currTableTheta, resultState, resultBelief, resultHAction, resultRAction)

    ret = {"imageURL": "images/{}.jpg".format(currTableTheta),
           "buttonLabels": ["Clockwise", "Counterclockwise"],
           "instructionText": instructionString,
           "sessionData": sessionData}
    return json.dumps(ret)

@app.post('/submit_survey')
def handle_survey():
  mturk_id = request.cookies.get('mturk_id', 'EXPIRED')
  # with open("log.txt", 'a') as f:
  #   f.write("user {}: 'a' answer is {}\n".format(mturk_id,request.forms.get('a')))
  #   f.write("user {}: 'b' answer is {}\n".format(mturk_id,request.forms.get('b')))
  surveyData[mturk_id].append(request.forms.get('a'))
  surveyData[mturk_id].append(request.forms.get('b'))
  print("user {}: 'a' answer is {}".format(mturk_id,request.forms.get('a')))
  print("user {}: 'b' answer is {}".format(mturk_id,request.forms.get('b')))
  with open('log.json', 'a') as outfile:
    json.dump(surveyData, outfile)
  return "<p> Your answers have been submitted. ID for mturk: {}".format(mturk_id)

run(app, host='0.0.0.0', port=2223)
