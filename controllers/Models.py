from keras.models import Model
from keras.layers import Embedding, Flatten, Input, Dense, Concatenate, Dot
from keras.optimizers import Adam
import tensorflow as tf

class NMF:
    def __init__(self, num_user, num_movie, latent_dim = 2, lr = 0.05, epochs=100) -> None:
        # Define inputs
        movie_input = Input(shape=[1],name='movie-input')
        user_input = Input(shape=[1], name='user-input')

        # MLP Embeddings
        movie_embedding_mlp = Embedding(num_movie, latent_dim, name='movie-embedding-mlp')(movie_input)
        movie_vec_mlp = Flatten(name='flatten-movie-mlp')(movie_embedding_mlp)

        user_embedding_mlp = Embedding(num_user, latent_dim, name='user-embedding-mlp')(user_input)
        user_vec_mlp = Flatten(name='flatten-user-mlp')(user_embedding_mlp)

        # MF Embeddings
        movie_embedding_mf = Embedding(num_movie, latent_dim, name='movie-embedding-mf')(movie_input)
        movie_vec_mf = Flatten(name='flatten-movie-mf')(movie_embedding_mf)

        user_embedding_mf = Embedding(num_user, latent_dim, name='user-embedding-mf')(user_input)
        user_vec_mf = Flatten(name='flatten-user-mf')(user_embedding_mf)

        # MLP layers
        concat = Concatenate()([movie_vec_mlp, user_vec_mlp])
        out_mlp = Dense(5, name='fc-1', activation='relu')(concat)

        # Prediction from both layers
        pred_mlp = Dense(4, name='pred-mlp', activation='relu')(out_mlp)
        # pred_mf = layers.Concatenate()([movie_vec_mf, user_vec_mf])
        pred_mf = Dot(name='dot_mf', normalize=False, axes=1)([user_vec_mf, movie_vec_mf])
        combine_mlp_mf = Concatenate()([pred_mf, pred_mlp])

        # Final prediction
        result = Dense(1, name='result', activation='relu')(combine_mlp_mf)

        model = Model([user_input, movie_input], result)
        model.compile(optimizer=Adam(learning_rate=lr), loss='mean_absolute_error')

        self.model = model
        self.epochs = epochs

    def train(self, input_user_id, input_movie_id, input_test_rating):
        cb = EpochProgressCallback()
        self.predictable_model = self.model.fit(
            [input_user_id, input_movie_id],
            input_test_rating,
            epochs=self.epochs,
            callbacks=[cb]
        ).model

    def predict(self, input_user_id, input_movie_id):
        predicted = self.predictable_model.predict(
            [input_user_id, input_movie_id]
        )

        return predicted

    def save(self):
        self.model.save('model.h5')

ModelNMF: NMF = None

current_epoch = 0
EpochCount = 3
# EpochCount = 10
LR = 0.001

def InitModel(num_user, num_movie, latent_dim = 10):
    global ModelNMF
    ModelNMF = NMF(num_user, num_movie, latent_dim, LR, EpochCount)

def Train(input_user_id, input_movie_id, input_test_rating):
    global current_epoch
    ModelNMF.train(input_user_id, input_movie_id, input_test_rating)
    current_epoch = 0

def Predict(input_user_id, input_movie_id):
    return ModelNMF.predict(input_user_id, input_movie_id)

def TrainPercentage():
    return current_epoch * 1.0 / EpochCount

class EpochProgressCallback(tf.keras.callbacks.Callback):
    def on_epoch_end(self, epoch, logs={}):
        global current_epoch
        current_epoch = epoch






# m = NMF(5, 3, 4, 0.01, epochs=200)
# m.train(
#     np.array([1, 1, 2, 2, 3, 4, 4, 5]),
#     np.array([2, 3, 1, 2, 2, 1, 3, 1]),

#     np.array([3, 4, 4, 4, 1, 5, 1, 4])
# )

# x_test_user = np.array([4])
# x_test_move = np.array([2])


# print(m.predict(x_test_user, x_test_move))



