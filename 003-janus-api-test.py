#!/usr/bin/env python3

####################################################################
####  pip install websocket_client
####################################################################

import requests
import time
import json
import string
import random
import six
import websocket


def t_generator(size=12, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


OPCODE_DATA = (websocket.ABNF.OPCODE_TEXT, websocket.ABNF.OPCODE_BINARY)


def main():
    ws = websocket.create_connection("ws://127.0.0.1:8188", subprotocols=['janus-protocol'])

    def recv():
        try:
            frame = ws.recv_frame()
        except websocket.WebSocketException:
            return websocket.ABNF.OPCODE_CLOSE, None
        if not frame:
            raise websocket.WebSocketException("Not a valid frame %s" % frame)
        elif frame.opcode in OPCODE_DATA:
            return frame.opcode, frame.data
        elif frame.opcode == websocket.ABNF.OPCODE_CLOSE:
            ws.send_close()
            return frame.opcode, None
        elif frame.opcode == websocket.ABNF.OPCODE_PING:
            ws.pong(frame.data)
            return frame.opcode, frame.data
        return frame.opcode, frame.data

    def recv_ws():
        opcode, data = recv()
        if six.PY3 and opcode == websocket.ABNF.OPCODE_TEXT and isinstance(data, bytes):
            data = str(data, "utf-8")
        if opcode == websocket.ABNF.OPCODE_CLOSE:
            return None
        # console.write(data)
        return data

    msg = {"janus": "info", "transaction": t_generator()}
    ws.send(json.dumps(msg))
    print("info: ", json.loads(recv_ws())["version_string"])
    time.sleep(1)

    msg = {"janus": "create", "transaction": t_generator()}
    ws.send(json.dumps(msg))
    session_id = json.loads(recv_ws())["data"]["id"]
    print("session id: ", session_id)
    time.sleep(1)

    msg = {"janus": "keepalive", "transaction": t_generator(), "session_id": session_id}
    ws.send(json.dumps(msg))
    print("keepalive ack: ", json.loads(recv_ws()))
    time.sleep(1)

    msg = {"janus": "attach", "transaction": t_generator(), "plugin": "janus.plugin.videoroom",
           "session_id": session_id}
    ws.send(json.dumps(msg))
    handle_id = json.loads(recv_ws())["data"]["id"]
    print("handle_id: ", handle_id)
    time.sleep(1)

    room = random.randint(100000, 999999)

    body = {"room": room, "permanent": False, "description": "melot room", "request": "create"}
    msg = {"janus": "message", "transaction": t_generator(), "handle_id": handle_id, "session_id": session_id,
           "body": body}
    ws.send(json.dumps(msg))
    print("creat room ack: ", json.loads(recv_ws()))
    time.sleep(1)

    body = {"request": "join", "room": room, "ptype": "publisher", "display": "ban"}
    msg = {"janus": "message", "transaction": t_generator(), "handle_id": handle_id, "session_id": session_id,
           "body": body}
    ws.send(json.dumps(msg))
    print("join room ack: ", json.loads(recv_ws()))
    time.sleep(1)
    print("join room ack: ", json.loads(recv_ws()))
    time.sleep(1)

    # print("查询参与者...")
    # r = requests.get('http://localhost:8080/api/v1/participants?page=1&per_page=5')
    # print(r.text)
    # time.sleep(1)

    body = {"request": "leave"}
    msg = {"janus": "message", "transaction": t_generator(), "handle_id": handle_id, "session_id": session_id,
           "body": body}
    ws.send(json.dumps(msg))
    print("leave room ack: ", json.loads(recv_ws()))
    time.sleep(1)
    print("leave room ack: ", json.loads(recv_ws()))
    time.sleep(1)

    # print("查询参与者...")
    # r = requests.get('http://localhost:8080/api/v1/participants?page=1&per_page=5')
    # print(r.text)
    # time.sleep(1)
    # print()

    body = {"room": room, "request": "destroy"}
    msg = {"janus": "message", "transaction": t_generator(), "handle_id": handle_id, "session_id": session_id,
           "body": body}
#    ws.send(json.dumps(msg))
#    print("destroy room ack: ", json.loads(recv_ws()))
    time.sleep(1)

    msg = {"janus": "detach", "transaction": t_generator(), "handle_id": handle_id, "session_id": session_id}
    ws.send(json.dumps(msg))
    print("detach ack: ", json.loads(recv_ws()))
    time.sleep(1)

    msg = {"janus": "destroy", "transaction": t_generator(), "session_id": session_id}
    ws.send(json.dumps(msg))
    print("destroy ack: ", json.loads(recv_ws()))
    time.sleep(1)

    return


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
