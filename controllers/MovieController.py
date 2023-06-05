from controllers.Wrapper import wrap_ok_status, wrap_failed_status
from controllers.DBInteractor import GetRecommendationMovies, GetMoviesDetail, GetRandomMovieOnlogin, RatingMovieCreated, GetUserMovieHistories, DeleteRating, GetSearchMovie

def GetRecommendations(userID, titleQuery):
    data = []

    if len(titleQuery) == 0:
        data = GetRecommendationMovies(userID)
    else:
        data = GetSearchMovie(titleQuery)

    return wrap_ok_status(data)

def GetMovieDetail(userID, id):
    data = GetMoviesDetail(userID, id)

    return wrap_ok_status(data)

def GetRandomMovieForLogin():
    data = GetRandomMovieOnlogin()

    return wrap_ok_status(data)

def CreateRating(userID, movieID, data):
    if int(userID) < 0 or int(movieID) < 0 or not data.__contains__('rating'):
        return wrap_failed_status(None, 'user id, movie id, or rating data not valid')

    rating = data['rating']

    if rating > 5 or rating <= 0:
        return wrap_failed_status(None, 'rating should between 1 and 5')

    RatingMovieCreated(userID, movieID, rating)
    return wrap_ok_status(None, 'ok')

def GetMovieHistories(userID):
    if int(userID) <= 0:
        return wrap_failed_status(None, 'user id not valid')

    histories = {
        'histories': GetUserMovieHistories(userID),
    }

    return wrap_ok_status(histories)

def DeleteMovieHistory(userID, filmID):
    if int(userID) <= 0 or int(filmID) <= 0:
        return wrap_failed_status(None, 'user id or film id not valid')

    DeleteRating(userID, filmID)

    return wrap_ok_status(None, 'ok')


