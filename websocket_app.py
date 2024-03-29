import asyncio
import json
import websockets
from model.NMF import NMF
from dataset import datasets
import time

model = None
dataset = None
connections = []

async def handler(websocket, path):
  connections.append(websocket)

  while True:
    try:
      data = await websocket.recv()
      if data == 'retrain':
        dataset.reload()
        HandleTrain()
        HandlePredict()
        await HandleReload()
        dataset.set_train_state('')

      if data == 'exit':
        break
    except:
      connections.remove(websocket)
      return

  await websocket.close()
  connections.remove(websocket)

async def HandleReload():
  global dataset
  for conn in connections:
    try:
      await conn.send('\{"event": "reload"\}')
    except:
      pass

def HandleTrainProgress(current, target, loss):
  global dataset

  dataset.set_train_state(json.dumps({
    'event': 'train-progress',
    'current': current + 1,
    'target': target,
    'loss': loss
  }))

def HandleTrain():
  global model
  global dataset

  model = initializeModel(dataset.user_count(), dataset.item_count())
  model.build()

  model.fit(
    dataset.users(),
    dataset.items(),
    dataset.ratings(),
    verbose=1,
    epochs=5,
    funcs=[HandleTrainProgress]
  )

def HandlePredict():
  global dataset

  user_ids = dataset.real_users()

  film_count = dataset.item_count()
  film_ids = [i for i in range(film_count)]

  for user_id in user_ids:
    current_user_id_list = [user_id for _ in range(film_count)]

    predictions = model.predict(current_user_id_list, film_ids)
    dataset.set_recommendations(current_user_id_list, film_ids, predictions)

def initializeModel(num_users, num_items):
  return NMF(num_users, num_items, learning_rate=0.0005)

def main():
  global dataset

  dataset = datasets.Dataset()
  # HandleTrain()
  # HandlePredict()

  dataset.set_train_state('')

  port = 5001
  start_server = websockets.serve(handler, '0.0.0.0', port)

  print('Server running on: '+str(port))
  loop = asyncio.get_event_loop()
  loop.run_until_complete(start_server)
  loop.run_forever()

if __name__ == '__main__':
  main()
