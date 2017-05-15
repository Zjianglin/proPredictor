import flask

import flask

_base_dic = {
    'code':0,
}

def error(code,msg):
    return flask.jsonify(msg=msg), code

def response(code, result):
    return flask.jsonify(result=result), code