from controllers.Wrapper import wrap_ok_status, wrap_failed_status
from controllers.DBInteractor import GetUserByUsername, RegisterUser

def Login(data):
    if not data.__contains__('username') or not data.__contains__('password'):
        return wrap_failed_status(None, 'username and password required')

    username = data['username']
    password = data['password']

    user = GetUserByUsername(username)

    if user == None:
        return wrap_failed_status(None, 'user not found, or password error')

    if user['username'] != username or user['password'] != password:
        return wrap_failed_status(None, 'user not found, or password error')

    response = {"user_id": user['id']}

    return wrap_ok_status(response)

def Register(data):
    if not data.__contains__('username') or not data.__contains__('password'):
        return wrap_failed_status(None, 'username and password required')

    username = data['username']
    password = data['password']
    interest = data['interest']
    notInterest = data['notInterest']
    
    user = GetUserByUsername(username)

    if user != None:
        return wrap_failed_status(None, 'user exist')

    user = RegisterUser(username, password, interest, notInterest)

    response = {"user_id": user['id']}

    return wrap_ok_status(response)


