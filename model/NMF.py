import numpy as np
import tensorflow as tf
import keras
from keras.models import Sequential, Model
from keras.layers import Embedding, Input, Dense, Multiply, Reshape, Flatten, Concatenate
from tensorflow.keras.optimizers.legacy import Adam

class NMF:
  def __init__(self, num_user, num_item, embedding_size=32, hidden_layers=[64, 32, 16, 8], batch_size=32, learning_rate = 0.004):
    tf.keras.utils.set_random_seed(0)

    self.num_user = num_user
    self.num_item = num_item

    self.input_count     = 1
    self.embedding_size = embedding_size
    self.hidden_layers  = hidden_layers
    self.batch_size     = batch_size
    self.learning_rate  = learning_rate

  def new_embedding(self, input_count, data_count, latent_count, name):
    return Embedding(
      input_dim=data_count,
      output_dim=latent_count,
      name=name,
      input_length=input_count
    )

  def new_dense(self, dense_count, name, activation='relu'):
    return Dense(dense_count,
      activation=activation,
      name = name,
    )

  def build(self):
    user_input = Input(shape=(self.input_count,), dtype='int32', name = 'user_input')
    item_input = Input(shape=(self.input_count,), dtype='int32', name = 'item_input')

    user_mlp_embedding = self.new_embedding(self.input_count, self.num_user, self.embedding_size, 'user_mlp_embedding')(user_input)
    item_mlp_embedding = self.new_embedding(self.input_count, self.num_item, self.embedding_size, 'item_mlp_embedding')(item_input)

    user_mf_embedding = self.new_embedding(self.input_count, self.num_user, self.embedding_size, 'user_mf_embedding')(user_input)
    item_mf_embedding = self.new_embedding(self.input_count, self.num_item, self.embedding_size, 'item_mf_embedding')(item_input)

    # MLP
    user_mlp_vector = Flatten()(user_mlp_embedding)
    item_mlp_vector = Flatten()(item_mlp_embedding)

    mlp_input_concat  = Concatenate(axis=1)([user_mlp_vector, item_mlp_vector])
    last_hidden_layer = mlp_input_concat

    for idx in range(len(self.hidden_layers)):
      dense_count = self.hidden_layers[idx]

      if idx == len(self.hidden_layers) - 1:
        last_hidden_layer = self.new_dense(dense_count, 'MLP_FINAL')(last_hidden_layer)
        continue

      if idx % 2 == 0:
        continue

      last_hidden_layer = self.new_dense(dense_count, 'hidden-'+str(idx)+'-'+str(dense_count))(last_hidden_layer)

    MLP = last_hidden_layer

    # GMF
    user_mf_vector = Flatten()(user_mf_embedding)
    item_mf_vector = Flatten()(item_mf_embedding)

    GMF = Multiply(name='GMF_FINAL')([user_mf_vector, item_mf_vector])

    ncf_input_concat = Concatenate(axis=1)([GMF, MLP])

    NCF = self.new_dense(1, 'NEUMF')(ncf_input_concat)

    model = Model(inputs=[
      user_input,
      item_input,
    ], outputs=NCF)

    opt_adam = Adam(learning_rate = self.learning_rate)
    model.compile(
      optimizer=opt_adam,
      loss= ['mean_absolute_error'],
    )

    self.model = model
  
  def fit(self, input_users, input_films, output_ratings, epochs = 20, verbose = 0, funcs = []):
    callbacks = [CustomCallback(func, epochs) for func in funcs]

    self.model.fit([[
      np.array(input_users),
      np.array(input_films),
    ]],
      np.array(output_ratings),
      epochs=epochs,
      batch_size=self.batch_size,
      verbose=verbose,
      callbacks=callbacks,
    )

  def predict(self, input_users, input_films):
    return self.model.predict([
      np.array(input_users),
      np.array(input_films),
    ]).reshape((-1))


class CustomCallback(keras.callbacks.Callback):
  def __init__(self, func, epochs):
    self.func = func
    self.epochs = epochs

  def on_epoch_end(self, epoch, logs=None):
    self.func(epoch, self.epochs, logs['loss'])
