from controllers.Wrapper import wrap_ok_status, wrap_failed_status
from controllers.DBInteractor import GetTrainProgress

def GetProgressOfTrain():
  data = GetTrainProgress()

  return wrap_ok_status(data)
