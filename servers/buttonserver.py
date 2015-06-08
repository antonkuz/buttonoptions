from bottle import Bottle, run, static_file, request,response
import json

app = Bottle()
idCounter = 0

@app.route('/static/<path:path>')
def server_static(path):
  return static_file(path, root=".")

@app.post('/ui/button') # or @route('/login', method='POST')
def do_click():
  totalPicsNum = 19; #bad style
  userid = int( request.cookies.get('id', '0') )
  if userid == 0:
    global idCounter
    idCounter += 1
    response.set_cookie('id', str(idCounter))
  requestData = json.loads(request.body.getvalue())
  sessionData = requestData["sessionData"]
  buttonClicked = requestData["buttonID"]
  with open("log.txt", 'a') as f:
    f.write("User {} clicked on button {}\n".format(userid,buttonClicked))
  print("User {} clicked on button {}\n".format(userid,buttonClicked))
  print('User ip = {}'.format(request.remote_addr))
  if buttonClicked==0:
    if sessionData["picCount"] > 1:
      sessionData["picCount"] -= 1
  elif sessionData["picCount"] < totalPicsNum:
      sessionData["picCount"] += 1
  picCount = sessionData["picCount"]
  imageLink = "images/{}.jpg".format(picCount)
  ret = {"imageURL": imageLink,
         "buttonLabels": ["Prev", "Next"],
         "instructionText": "Cat #{}".format(picCount),
         "sessionData": sessionData}
  return json.dumps(ret)

run(app, host='localhost', port=8080)