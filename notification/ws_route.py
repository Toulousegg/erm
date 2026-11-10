from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from notification.notification_services import manager
from core.database import SessionLocal
from core.security import get_user_from_token


ws_route = APIRouter()


@ws_route.websocket("/ws")
async def websocket_notifications(websocket: WebSocket):
    session = SessionLocal()

    try:

        token = websocket.query_params.get("token")

        await websocket.accept() # no puede ser... 30 min buscando el error y nunca habia aceptado la conexion 👽👽👽

        if not token:
            await websocket.close()
            return

        user = get_user_from_token(token, session)
        
        if not user:
            await websocket.close(code=1008)
            return

        company_id = user.company_id

        await manager.connect(websocket, user.id, company_id)

        try:
            while True:
                await websocket.receive_text()

        except WebSocketDisconnect:
            manager.disconnect(websocket, user.id, company_id)

    finally:
        session.close()