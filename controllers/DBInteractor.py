import numpy as np
from controllers.Database import conn
from controllers.IMDBApi import FetchIMDBFilm

def LoadNMFDataset():
    cursor = conn.cursor()

    cursor.execute(
    """select 
	(select id from users order by id desc limit 1) user_count,
    (select count(*) from films) film_count"""
    )

    unique_data = cursor.fetchone() 

    unique_user = unique_data[0] + 1
    unique_film = unique_data[1] + 1

    cursor.execute("select r.user_id, f.f_sorted_id, r.rating from ratings r inner join films f on r.film_id = f.id")
    ratings_rows = cursor.fetchall()

    user_ids = np.zeros((len(ratings_rows)))
    movie_ids = np.zeros((len(ratings_rows)))
    ratings = np.zeros((len(ratings_rows)))

    idx = 0
    for row in ratings_rows:
        user_ids[idx] = int(row[0]) - 1
        movie_ids[idx] = int(row[1]) - 1
        ratings[idx] = row[2]

        idx += 1

    cursor.close()

    return {
        'unique_user': unique_user,
        'unique_film': unique_film,
        'user_ids': user_ids,
        'movie_ids': movie_ids,
        'ratings': ratings,
        'unique_film_ids': np.unique(movie_ids),
    }


def GetUserByUsername(username):
    cursor = conn.cursor()

    cursor.execute('select id, username, password from users where username = \''+username+'\'')
    rows = cursor.fetchall()
    cursor.close()
    
    for row in rows:
        return {'id': row[0], 'username': row[1], 'password': row[2]}

    return None

def GetRealUserIDs():
    cursor = conn.cursor()

    userIDs = []
    cursor.execute('select id from users where password is not null')
    rows = cursor.fetchall()

    for row in rows:
        userIDs.append(row[0])

    cursor.close()
    return userIDs

def TrainIDsToFilm(filmLength, userid):
    userIDs = np.zeros(filmLength, dtype=np.int32)
    userIDs.fill(userid)

    filmIDs = np.arange(filmLength, dtype=np.int32)

    return [userIDs, filmIDs]


def GetListOfUninterestedFilm(userID):
    cursor = conn.cursor()

    cursor.execute('SELECT f.id FROM FILMS f where id not in (select film_id from ratings where user_id = '+str(userID)+') order by f.id;')
    rows = cursor.fetchall()

    userIDs = np.array([range(len(rows))])
    userIDs.fill(userID)
    userIDs = userIDs.reshape((len(rows)))

    filmIDs = np.array([row[0] for row in rows])
    filmIDs = filmIDs.reshape((len(filmIDs)))

    cursor.close()

    return [userIDs, filmIDs]

def RegisterUser(username, password, interests, notInterests): 
    cursor = conn.cursor()

    cursor.execute('insert into users (username, password) values (%s, %s) returning *', (username, password))
    rowReturned = cursor.fetchone()
    newID = rowReturned[0]

    for interest in interests:
        cursor.execute('insert into ratings (user_id, film_id, rating) values (%s, %s, %s)', (newID, interest, 5))

    for notInterest in notInterests:
        cursor.execute('insert into ratings (user_id, film_id, rating) values (%s, %s, %s)', (newID, notInterest, 2))

    cursor.close()

    newUser = {'id': newID}
    return newUser

def GetRecommendationMovies(userID, limit = 100):
    cursor = conn.cursor()
    cursor.execute("""select * from (
  select
  f.id as film_id,
  f.image_url,
  f.title,
  f.released_year as release_date,
  string_to_array(f.genres, ',') genres,
  f.ratings,
  (
    select
      rating
    from
      ratings
    where
      user_id = %s
      and film_id = f.id
    limit
      1
  ) given_rating,
  rec.predicted_ratings,
  f.description
from
  recommendations rec
  inner join films f on rec.film_id = f.f_sorted_id
where
  rec.user_id = %s
order by
  rec.predicted_ratings desc
) predicted order by given_rating desc, predicted.predicted_ratings desc limit %s;""", (userID, userID, limit))
    rows = cursor.fetchall()

    cursor.close()
    films = []
    for row in rows:
        if row[4] is None:
            updateFilmExternalData(row[0])

        films.append({
            'film_id': row[0],
            'image_url': row[1],
            'title': row[2],
            'release_date': row[3],
            'genres': row[4],
            'rating': {'given': mx(row[6]), 'predict': mx(row[7]), 'real': mx(row[5])},
            'description': row[8]
        })

    return {
        'recommendations': films,
    }

def GetSearchMovie(query = ""):
    cursor = conn.cursor()
    cursor.execute("""
select
  id as film_id,
  image_url,
  title,
  released_year as release_date,
  string_to_array(genres, ',') genres,
  ratings
from
  films where lower(title) like '%"""+query.lower()+"""%' order by id limit 100;""")
    rows = cursor.fetchall()

    cursor.close()
    films = []
    for row in rows:
        if row[4] is None:
            updateFilmExternalData(row[0])

        films.append({
            'film_id': row[0],
            'image_url': row[1],
            'title': row[2],
            'release_date': row[3],
            'genres': row[4],
            'rating': {'given': None, 'predict': 3, 'real': mx(row[5])},
        })

    return {
        'recommendations': films,
    }

def GetRandomMovieOnlogin():
    idx = np.random.randint(193608, size=500) + 1

    films = []
    for a in idx:
        cursor = conn.cursor()
        cursor.execute("""
    select
    id as film_id,
    image_url,
    title,
    released_year as release_date,
    string_to_array(genres, ',') genres,
    ratings
    from films where id > """+str(a)+""" order by film_id limit 1;""", ())
        rows = cursor.fetchall()

        for row in rows:
            updateFilmExternalData(row[0])

            films.append({
                'film_id': row[0],
                'image_url': row[1],
                'title': row[2],
                'release_date': row[3],
                'genres': row[4],
                'rating': {'given': None, 'predict': 3, 'real': mx(row[5])},
            })
        cursor.close()

    return {
        'recommendations': films,
    }

def GetRandomMovieOnlogin():
    idx = np.random.randint(193608, size=201) + 1

    films = []
    for a in idx:
        cursor = conn.cursor()
        cursor.execute("""
    select
    id as film_id,
    image_url,
    title,
    released_year as release_date,
    string_to_array(genres, ',') genres,
    ratings
    from films where id > """+str(a)+""" order by film_id limit 1;""", ())
        rows = cursor.fetchall()

        for row in rows:
            updateFilmExternalData(row[0])

            films.append({
                'film_id': row[0],
                'image_url': row[1],
                'title': row[2],
                'release_date': row[3],
                'genres': row[4],
                'rating': {'given': None, 'predict': 3, 'real': mx(row[5])},
            })
        cursor.close()

    return {
        'recommendations': films,
    }

def GetMoviesDetail(userID, id):
    cursor = conn.cursor()
    cursor.execute("""
select
  id as film_id,
  title,
  image_url,
  released_year as release_date,
  string_to_array(genres, ',') genres,
  ratings,
  trailer_url,
  description,
  coalesce((select rating from ratings where user_id = """+str(userID)+""" and film_id = f.id limit 1), 0) given_rating,
  (select predicted_ratings from recommendations where user_id = """+str(userID)+""" and film_id = f.f_sorted_id ) predicted_ratings
from
  films f
  where id = """+str(id))
    rows = cursor.fetchall()

    moviesRecs = GetRecommendationMovies(userID, 10)

    for row in rows:

        recs = []
        for rec in moviesRecs['recommendations']:
            recs.append(rec)

        return {
            'film_id': row[0],
            'title': row[1],
            'image_url': row[2],
            'release_date': row[3],
            'genres': row[4],
            'rating': {'given': mx(row[8]), 'predict': mx(row[9]), 'real': mx(row[5])},
            'trailer_url': row[6],
            'description': row[7],
            'recommendations': recs,
        }

    cursor.close()
    return None

def updateFilmExternalData(id):
    cursor = conn.cursor()
    cursor.execute('select title, imdb_id, released_year from films where description is null and id = '+str(id))

    rows = cursor.fetchall()

    if len(rows) <= 0:
        return
    
    row = rows[0]

    imdb_id = row[1]

    fromIMDB = FetchIMDBFilm(imdb_id)

    description = None
    imageURL = None
    rating = None

    if fromIMDB is not None:
        description = fromIMDB['description']
        imageURL = fromIMDB['image_url']
        rating = fromIMDB['rating']
    else:
        cursor.close()
        return

    cursor.execute('update films set image_url = %s, ratings = %s, description = %s where id = %s', (imageURL, rating, description, id))
    cursor.close()

    return {
        'rating': rating
    }

def RatingMovieCreated(userID, movieID, rating):
    cursor = conn.cursor()
    try:
        cursor.execute(
            'insert into ratings (user_id, film_id, rating) values (%s, %s, %s) on conflict (user_id, film_id) do update set rating = %s',
            (userID, movieID, rating, rating),
        )
    except:
        print("Something else went wrong")

    cursor.close()

def UpdateRecommendation(userID, filmIDs, ratings):
    cursor = conn.cursor()
    for [filmID, rating] in zip(filmIDs, ratings):
        cursor.execute(
            'insert into recommendations (user_id, film_id, predicted_ratings) values (%s, %s, %s) on conflict (user_id, film_id) do update set predicted_ratings = %s',
            (int(userID), int(filmID + 1), float(rating), float(rating)),
        )

    cursor.close()

def GetUserMovieHistories(userID):
    cursor = conn.cursor()
    histories = []

    cursor.execute("""
    select
r.film_id,
f.image_url,
f.title,
f.released_year,
r.rating,
r.created_at,
f.genres
from
ratings r
inner join films f on r.film_id = f.id
where r.user_id = """+str(userID)+" order by r.created_at")

    rows = cursor.fetchall()

    if len(rows) <= 0:
        return

    for row in rows:
        histories.append({
            'film_id': row[0],
            'image_url': row[1],
            'title': row[2],
            'released_year': row[3],
            'rating': mx(row[4]),
            'created_at': row[5],
            'genres': row[6],
        })

    cursor.close()

    return histories

def GetMoviesRating():
    cursor = conn.cursor()
    films = {}

    cursor.execute("select f_sorted_id, ratings from films order by f_sorted_id")

    rows = cursor.fetchall()

    if len(rows) <= 0:
        return

    for row in rows:
        films[row[0]] = row[1]

    cursor.close()

    return films

def DeleteRating(userID, filmID):
    cursor = conn.cursor()
    cursor.execute("delete from ratings where user_id = %s and film_id = %s", (userID, filmID))
    cursor.close()


def mx (v):
    if v is None:
        return None

    if v >= 5:
        return 5

    return v