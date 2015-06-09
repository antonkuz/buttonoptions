from bottle import Bottle, run, static_file, request,response
import json
import string
import random
import json

app = Bottle()
data = dict()

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

  ##cookie generated on info slide
  if sessionData["picCount"]==1:
    gen_id = ''.join(random.choice(string.ascii_uppercase +
      string.digits) for _ in range(6))
    response.set_cookie('mturk_id', gen_id, max_age=60*60, path='/')
    print("generated {}".format(gen_id))
    data[gen_id] = []

  ##test##
  else:
    print("cookie set to: {}".format(request.cookies.get('mturk_id','NOT SET')))  
  ##test##
  buttonClicked = requestData["buttonID"]
  #append to button click log
  if (sessionData["picCount"]>1):
    mturk_id = request.cookies.get('mturk_id','NO ID');
    with open("log.txt", 'a') as f:
      f.write("User {} clicked on button {}\n".format(mturk_id,buttonClicked))
    data[mturk_id].append(buttonClicked)
    print("User {} (ip = {}) clicked on button {}\n".format(mturk_id,request.remote_addr,buttonClicked))
  #pics navigation
  if buttonClicked==0:
    if sessionData["picCount"] > 1:
      sessionData["picCount"] -= 1
  elif sessionData["picCount"] < totalPicsNum:
      sessionData["picCount"] += 1
  picCount = sessionData["picCount"]
  imageLink = "images/{}.jpg".format(picCount)

  #returning next pic. take care of disabling buttons on edges
  if sessionData["picCount"]==1:
    ret = {"imageURL": imageLink,
           "buttonLabels": ["Prev", "Next"],
           "instructionText": "Cat #{}".format(picCount),
           "sessionData": sessionData,
           "disabled": '#left-button'}
  elif sessionData["picCount"]==totalPicsNum:
    ret = {"imageURL": imageLink,
           "buttonLabels": ["Prev", "Next"],
           "instructionText": "Cat #{}".format(picCount),
           "sessionData": sessionData,
           "disabled": '#right-button'}
  ########test for survey
  elif sessionData["picCount"]==4:
    ret = {"toSurvey":True}
  ####################
  else:
    ret = {"imageURL": imageLink,
           "buttonLabels": ["Prev", "Next"],
           "instructionText": "Cat #{}".format(picCount),
           "sessionData": sessionData}
  return json.dumps(ret)

@app.post('/submit_survey')
def handle_survey():
  mturk_id = request.cookies.get('mturk_id', 'EXPIRED')
  # with open("log.txt", 'a') as f:
  #   f.write("user {}: 'a' answer is {}\n".format(mturk_id,request.forms.get('a')))
  #   f.write("user {}: 'b' answer is {}\n".format(mturk_id,request.forms.get('b')))
  data[mturk_id].append(request.forms.get('a'))
  data[mturk_id].append(request.forms.get('b'))
  print("user {}: 'a' answer is {}".format(mturk_id,request.forms.get('a')))
  print("user {}: 'b' answer is {}".format(mturk_id,request.forms.get('b')))
  with open('log.json', 'w') as outfile:
    json.dump(data, outfile)
  return "<p> Your answers have been submitted. ID for mturk: {}".format(mturk_id)

run(app, host='localhost', port=8080)