import urllib.parse
from flask import Flask, request, json
from flask_cors import CORS, cross_origin
from controllers.UserController import Login, Register
from controllers.ModelController import Train, Test
from controllers.MovieController import GetRecommendations, GetMovieDetail, GetRandomMovieForLogin, CreateRating, GetMovieHistories, DeleteMovieHistory

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/login', methods=['POST'])
@cross_origin()
def LoginHandler():
    data = json.loads(request.data)
    response = Login(data)

    status = 200

    if response['status'] != 'ok':
        status = 400

    return app.response_class(
        response=json.dumps(response),
        status=status,
        mimetype='application/json'
    )

@app.route('/register', methods=['POST'])
@cross_origin()
def RegisterHandler():
    data = json.loads(request.data)
    response = Register(data)

    status = 200

    if response['status'] != 'ok':
        status = 400

    return app.response_class(
        response=json.dumps(response),
        status=status,
        mimetype='application/json'
    )

@app.route('/movies/model/train', methods=['GET'])
@cross_origin()
def MoviesModelTrain():
    percentageOnly = request.headers['Percentage-Only']
    response = Train(percentageOnly)

    status = 200

    if response['status'] != 'ok':
        status = 400

    return app.response_class(
        response=json.dumps(response),
        status=status,
        mimetype='application/json'
    )

@app.route('/movies/model/test', methods=['POST'])
@cross_origin()
def MoviesModelTest():
    data = json.loads(request.data)
    response = Test(data)

    status = 200

    if response['status'] != 'ok':
        status = 400

    return app.response_class(
        response=json.dumps(response),
        status=status,
        mimetype='application/json'
    )


@app.route('/movies', methods=['GET'])
@cross_origin()
def GetRecommendationsHandler():
    status = 200 
    query = urllib.parse.unquote(request.query_string)
    userID = int(request.headers['User-Id'])
    recommendations = GetRecommendations(userID, query)

    return app.response_class(
        response=json.dumps(recommendations),
        status=status,
        mimetype='application/json'
    )

@app.route('/movies/detail/<id>', methods=['GET'])
@cross_origin()
def GetMovieDetailHandler(id):
    status = 200
    userID = int(request.headers['User-Id'])
    detail = GetMovieDetail(userID, id)

    return app.response_class(
        response=json.dumps(detail),
        status=status,
        mimetype='application/json'
    )

@app.route('/login/movies', methods=['GET'])
@cross_origin()
def GetLoginMovies():
    status = 200
    detail = GetRandomMovieForLogin()

    return app.response_class(
        response=json.dumps(detail),
        status=status,
        mimetype='application/json'
    )

@app.route('/movies/rating/<id>', methods=['POST'])
@cross_origin()
def PostRating(id):
    status = 200
    userID = int(request.headers['User-Id'])
    movieID = int(id)

    data = json.loads(request.data)
    response = CreateRating(userID, movieID, data)

    return app.response_class(
        response=json.dumps(response),
        status=status,
        mimetype='application/json'
    )

@app.route('/movies/history', methods=['GET'])
@cross_origin()
def GetMovieHistory():
    status = 200
    userID = int(request.headers['User-Id'])
    response = GetMovieHistories(userID)

    return app.response_class(
        response=json.dumps(response),
        status=status,
        mimetype='application/json'
    )

@app.route('/movies/rating/<id>', methods=['DELETE'])
@cross_origin()
def DeleteRating(id):
    status = 200
    userID = int(request.headers['User-Id'])
    response = DeleteMovieHistory(userID, id)

    return app.response_class(
        response=json.dumps(response),
        status=status,
        mimetype='application/json'
    )

if __name__ == '__main__':
    app.debug = False
    app.run(threaded=True)
