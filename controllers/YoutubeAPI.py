import requests
import json

def FetchYoutubeAPI(title):
    res = requests.get('https://youtube.googleapis.com/youtube/v3/search?part=snippet&maxResults=1&q='+title+'&key=AIzaSyDaIJdw2Xw_N9ybZZRC3C0IwLdWLSmq-eM')
    response = json.loads(res.text)
    

    if not response.__contains__('kind'):
        print('error on get youtube data api', title, response)
        return None    

    videoID = response['items'][0]['id']['videoId']
    return {
        'youtube_url': 'https://www.youtube.com/watch?v='+videoID,
    }
