from controllers.Wrapper import wrap_ok_status
from controllers.DBInteractor import LoadNMFDataset, GetRealUserIDs, TrainIDsToFilm, UpdateRecommendation, GetMoviesRating
import controllers.Models as m
from keras.models import load_model
import numpy as np

kerasModel = load_model('model-128.h5')
isInTrained = False

def Train(percentageOnly):
    global isInTrained
    percentage = m.TrainPercentage()

    print(percentage)
    trainStatus = {
        'percentage': percentage,
    }

    if not isInTrained:
        isInTrained = True
        dataset = LoadNMFDataset()
        InitializeNMF(dataset)
        userIDs = GetRealUserIDs()

        for userID in userIDs:
            userFilmIDs = TrainIDsToFilm(dataset['unique_film'], userID - 1)
            prediction = m.Predict(userFilmIDs[0], userFilmIDs[1])
            predictionFlatted = prediction.reshape((-1))
            UpdateRecommendation(userID, userFilmIDs[1], predictionFlatted)

        isInTrained = False

    trainStatus['is_trained'] = isInTrained
    return wrap_ok_status(trainStatus, 'ok')

def Test(payload):
    dataList = payload['lists']

    label = dataList[0]
    data = dataList[1:]

    split = lambda d: d.split(',')
    parse = lambda l: [int(v) for v in split(l)]
    parseAll = lambda ls: [parse(p) for p in ls]

    parsedData = parseAll(data)
    predicted = []

    # for d in parsedData:
    #     pr = m.Predict(np.array([d[0]]), np.array([d[1]]))

    #     predicted.append({'user_id': d[0], 'film_id': d[1], 'given': d[2], 'predicted': pr})

    filmsRating = GetMoviesRating()

    datanp = np.array(parsedData)
    prs = kerasModel.predict([datanp[:, 0], datanp[:, 1]])
    # prs = m.Predict(datanp[:, 0], datanp[:, 1])
    idx = 0
    for d in parsedData:
       predicted.append({'user_id': d[0], 'film_id': d[1], 'given': d[2], 'film_rating': filmsRating[d[1] + 1], 'predicted': float(prs[idx][0])})
       idx += 1

    return wrap_ok_status({'predict_list': predicted}, 'ok')



def InitializeNMF(dataset):
    m.InitModel(dataset['unique_user'], dataset['unique_film'], 15)
    m.Train(dataset['user_ids'], dataset['movie_ids'], dataset['ratings'])
