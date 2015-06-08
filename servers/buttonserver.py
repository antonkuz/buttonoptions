from bottle import Bottle, run, static_file, request
import json

app = Bottle()

@app.route('/static/<path:path>')
def server_static(path):
    return static_file(path, root=".")

@app.post('/ui/button') # or @route('/login', method='POST')
def do_click():
    totalPicsNum = 19; #bad style
    requestData = json.loads(request.body.getvalue())
    sessionData = requestData["sessionData"]
    buttonClicked = requestData["buttonID"]
    f = open('log.txt', 'a')
    f.write("User clicked on button {}\n".format(buttonClicked))
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