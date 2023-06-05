import numpy as np
import re
import random
from controllers.Database import conn
from controllers.IMDBApi import FetchIMDBFilm

def gen_random_numbers_in_range(low, high, n):
    return random.sample(range(low, high), n)

def GetUserByUsername(username):
    cursor = conn.cursor()

    cursor.execute('select id, username, password from users where username = \''+username+'\'')
    rows = cursor.fetchall()
    cursor.close()
    
    for row in rows:
        return {'id': row[0], 'username': row[1], 'password': row[2]}

    return None

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

def GetRecommendationMovies(userID, limit = 40):
    cursor = conn.cursor()
    cursor.execute("""select
    *
    from
    (
        select
        f.id as film_id,
        f.image_url,
        f.title,
        f.released_year as release_date,
        genres,
        (
            select
            avg(rating)
            from
            ratings
            where
            film_id = f.id
        ) ratings,
        (
            select
            rating
            from
            ratings
            where
            user_id = %s
            and film_id = f.id
        ) given_rating,
        rec.predicted_ratings,
        f.description
        from
        recommendations rec
        inner join films f on rec.film_id = f.id
        where
        rec.user_id = %s
    ) predicted
    order by
    predicted_ratings desc limit %s;""", (userID, userID, limit))
    rows = cursor.fetchall()

    cursor.close()
    films = []
    for row in rows:
        films.append({
            'film_id': row[0],
            'image_url': row[1],
            'title': row[2],
            'release_date': row[3],
            'genres': row[4],
            'rating': {'given': mx(row[6]), 'predict': mx(row[7]), 'real': mx(row[5])},
            'description': row[8],
        })

    return {
        'recommendations': films,
    }

def GetSearchMovie(query = ""):
    q = """lower(title) like '%"""+query.lower()+"""%'"""
    if re.match(r'^([\s\d]+)$', query) is not None:
        q = "film_id = "+query
    cursor = conn.cursor()
    cursor.execute("""
    select
  id as film_id,
  image_url,
  title,
  released_year as release_date,
  genres,
  ratings
    from
  films where
  """+q+"""
  order by id;""")
    rows = cursor.fetchall()

    cursor.close()
    films = []
    for row in rows:
        films.append({
            'film_id': row[0],
            'image_url': row[1],
            'title': row[2],
            'release_date': row[3],
            'genres': row[4],
            'rating': {'given': None, 'predict': None, 'real': mx(row[5])},
        })

    return {
        'recommendations': films,
    }

def GetFilmCredits(cursor, creditIDs):
    credits = []
    cursor.execute('select id, name from credits where id in ('+', '.join([str(id) for id in creditIDs])+')', ())
    rows = cursor.fetchall()

    for row in rows:
        credits.append({
            'id': row[0],
            'name': row[1],
        })

    return credits


# Update
def GetRandomMovieOnlogin():
    idx = gen_random_numbers_in_range(0, 3234, 64)

    films = []
    cursor = conn.cursor()
    cursor.execute("""
    select
    id as film_id,
    image_url,
    title,
    released_year as release_date,
    genres,
    (select avg(rating) from ratings where film_id = f.id) ratings
    from films f where f.id in ("""+",".join([str(a) for a in idx])+""");""", ())
    rows = cursor.fetchall()

    for row in rows:
        films.append({
            'film_id': row[0],
            'image_url': row[1],
            'title': row[2],
            'release_date': row[3],
            'genres': row[4],
            'rating': {'given': None, 'predict': None, 'real': mx(row[5])},
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
        genres,
        (select avg(rating) from ratings where film_id = f.id) rating,
        trailer_url,
        description,
        coalesce((select rating from ratings where user_id = """+str(userID)+""" and film_id = f.id limit 1), 0) given_rating,
        (select predicted_ratings from recommendations where user_id = """+str(userID)+"""  and film_id = f.id) predicted_ratings,
        director_ids, writer_ids, cast_ids
    from
        films f
    where id = """+str(id))
    rows = cursor.fetchall()

    for row in rows:
        directors = GetFilmCredits(cursor, row[10])
        writers   = GetFilmCredits(cursor, row[11])
        casters   = GetFilmCredits(cursor, row[12])
        return {
            'film_id': row[0],
            'title': row[1],
            'image_url': row[2],
            'release_date': row[3],
            'genres': row[4],
            'rating': {'given': mx(row[8]), 'predict': mx(row[9]), 'real': mx(row[5])},
            'trailer_url': row[6],
            'description': row[7],
            'directors': directors,
            'writers': writers,
            'casters': casters,
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
            'insert into recommendations (user_id, film_id, predicted_ratings) values (%s, %s, %s, %s) on conflict (user_id, film_id) do update set predicted_ratings = %s',
            (int(userID), int(filmID), float(rating), float(rating))
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

    cursor.execute("select id, ratings from films order by id")

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

    if v > 5:
        return 5

    v = round(v * 100) / 100
    return v


# Training Stuff
def GetNumberUserNItems():
    cursor = conn.cursor()

    cursor.execute("""
        select (
            select count(id) from users
        ) user_count,
        (
            select count(id) from films
        ) film_count"""
    )

    rows = cursor.fetchall()
    cursor.close()

    return rows[0]

def RatingData():
    cursor = conn.cursor()

    cursor.execute('select user_id, film_id, rating from ratings order by user_id, film_id');
    rows = cursor.fetchall()

    cursor.close()

    user_ids = []
    film_ids = []
    ratings  = []

    for row in rows:
        user_ids.append(row[0])
        film_ids.append(row[1])
        ratings.append(row[2])

    return user_ids, film_ids, ratings

def RealUserIDs():
    cursor = conn.cursor()

    cursor.execute('select id from users where password is not null order by id')

    rows = cursor.fetchall()
    cursor.close()

    return [row[0] for row in rows]

def TrainProgress(message):
    cursor = conn.cursor()
    cursor.execute('insert into state (code, message) values (\'train-state\', %s) on conflict (code) do update set message = %s', (message, message))
    cursor.close()

def GetTrainProgress():
    cursor = conn.cursor()
    cursor.execute('select message from state where code = \'train-state\' and message != \'\'')

    rows = cursor.fetchall()
    cursor.close()

    if len(rows) <= 0:
        return {}

    return rows[0]

def UpdateUserRecommendations(ratings):
    cursor = conn.cursor()

    for rating in ratings:
        cursor.execute('insert into recommendations (user_id, film_id, predicted_ratings) values (%s, %s, %s) on conflict (user_id, film_id) do update set predicted_ratings = %s', (rating[0], rating[1], rating[2], rating[2]))
    
    cursor.close()
