import asyncio
import json
import logging
import uuid

import websockets
from websockets.exceptions import ConnectionClosed
from config import Config

logging.basicConfig(level=logging.DEBUG if Config.DEBUG else logging.INFO)

ROOMS = {}  # session_id : { 'client': ws, 'agent': ws }
print("WEBSOCKETS LIB PATH:", websockets.__file__)
print("WEBSOCKETS VERSION:", websockets.__version__)
async def handler(ws, path=None):
    session_id = None
    role = None
    try:
        async for msg_raw in ws:
            try:
                msg = json.loads(msg_raw)
            except Exception:
                await ws.send(json.dumps({"type": "error", "reason": "invalid_json"}))
                continue

            msg_type = msg.get("type")
            if msg_type == "join":
                session_id = msg.get("room") or msg.get("session_id")
                role = msg.get("side") or msg.get("role")
                if not session_id or role not in ("client", "agent"):
                    await ws.send(json.dumps({"type": "error", "reason": "user_not_authorized"}))
                    continue

                if session_id not in ROOMS:
                    ROOMS[session_id] = {}
                    logging.info(f"Created new room {session_id}")
                if role in ROOMS[session_id]:
                    await ws.send(json.dumps({"type": "error", "reason": f"{role}_already_joined"}))
                    continue
                ROOMS[session_id][role] = ws
                await ws.send(json.dumps({"type": "joined", "session_id": session_id, "side": role}))
                logging.info(f"{role} joined room {session_id} ({len(ROOMS[session_id])}/2)")
                # If both connected, optionally notify both
                if len(ROOMS[session_id]) == 2:
                    for _role, _ws in ROOMS[session_id].items():
                        await _ws.send(json.dumps(
                            {"type": "ready", "session_id": session_id}
                        ))

            elif msg_type in ("offer", "answer", "ice"):
                # Relay to other side in same room
                if not session_id or session_id not in ROOMS:
                    await ws.send(json.dumps({"type": "error", "reason": "not_joined_to_room"}))
                    continue
                target_role = "agent" if role == "client" else "client"
                target_ws = ROOMS[session_id].get(target_role)
                if target_ws:
                    await target_ws.send(json.dumps(msg))
                    logging.debug(f"Relayed {msg_type} from {role} to {target_role} in {session_id}")
                else:
                    await ws.send(json.dumps({"type": "error", "reason": f"{target_role}_not_connected"}))
            elif msg_type == "leave":
                await ws.close()
            elif msg_type == "ping":
                await ws.send(json.dumps({"type": "pong"}))
            else:
                await ws.send(json.dumps({"type": "error", "reason": f"unknown_type_{msg_type}"}))
    except ConnectionClosed:
        pass
    finally:
        if session_id and role and session_id in ROOMS and ROOMS[session_id].get(role) is ws:
            del ROOMS[session_id][role]
            logging.info(f"{role} left room {session_id}")
            
            other_role = "agent" if role == "client" else "client"
            ws2 = ROOMS[session_id].get(other_role)
            if ws2:
                try:
                    await ws2.send(json.dumps({"type": "peer_left", "role": role}))
                except:
                    pass
            if not ROOMS[session_id]:
                del ROOMS[session_id]
                logging.info(f"Room {session_id} closed")


async def main():
    server = await websockets.serve(
        handler,
        Config.HOST,
        Config.PORT,
        origins=Config.ALLOWED_ORIGINS if Config.ALLOWED_ORIGINS != ["*"] else None
    )
    logging.info(f"Signaling Server started at ws://{Config.HOST}:{Config.PORT}")
    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
