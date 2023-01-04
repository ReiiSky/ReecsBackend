import requests
import json

def FetchIMDBFilm(imdbID):
    # res = requests.get('https://www.omdbapi.com/?i=tt'+imdbID+'&apikey=81c6ddf6')
    res = requests.get(' https://www.omdbapi.com/?i=tt'+imdbID+'&apikey=3c1e2fd9')
    response = json.loads(res.text)
    
    if not response.__contains__('Title'):
        print('error on get film detail', imdbID, response)
        return None

    rating = 6

    if response.__contains__('imdbRating'):
        rating = response['imdbRating']

    try:
        rating = float(rating) / 2
    except:
        rating = 6

    return {
        'image_url': response['Poster'],
        'rating': rating, 
        'description': response['Plot']
    }
    