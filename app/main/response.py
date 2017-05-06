import flask

import flask

_base_dic = {
    'code':0,
}

def error(code,msg):
    return flask.jsonify(status=code,msg=msg)

def response(code, result):
    return flask.jsonify(status=code, result=result)