
import numpy as np
from controllers.DBInteractor import GetNumberUserNItems, RatingData, RealUserIDs, TrainProgress, UpdateUserRecommendations

class Dataset:
  def __init__(self):
    self.reload()

  def user_count(self):
    return self._counts[0]

  def reload(self):
    self._counts = GetNumberUserNItems()
    self._datasets = RatingData()
    self._real_user_ids = RealUserIDs()

  def item_count(self):
    return self._counts[1]

  def users(self):
    return self._datasets[0]

  def items(self):
    return self._datasets[1]

  def ratings(self):
    return self._datasets[2]

  def real_users(self):
    return self._real_user_ids

  def set_train_state(self, message):
    TrainProgress(message)

  def set_recommendations(self, user_ids, film_ids, ratings):

    user_film_ratings = np.zeros((len(ratings), 3))
    user_film_ratings[:, 0] = user_ids
    user_film_ratings[:, 1] = film_ids
    user_film_ratings[:, 2] = ratings

    UpdateUserRecommendations(user_film_ratings)

