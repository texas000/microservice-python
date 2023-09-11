import logging

def successResponse(data):
    logging.warning(f'[RES]: {data}')
    return {
        "data": data,
        "status": 200
    }

def clientErrorResponse(data):
    logging.warning(f'[RES]: {data}')
    return {
        "data": data,
        "status": 400
    }

def serverErrorResponse(data):
    logging.error(f'[RES]: {data}')
    return {
        "data": data,
        "status": 500
    }
