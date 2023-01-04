def wrap_ok_status(data, message = None):
    return {"status": "ok", "data": data, 'message': message}

def wrap_failed_status(data, message = None):
    return {"status": "failed", "data": data, 'message': message}
