"""
AI Store-creation assistant powered by Google Gemini.

The endpoint receives the full conversation history from the frontend,
forwards it to Gemini (with function-calling enabled), and – when the
model decides it has gathered all required data – automatically creates
the store in the database.
"""

from __future__ import annotations

import json
import os
import traceback
from typing import List, Optional

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user
from ..models.store import Store
from ..models.user import User
from ..schemas.user import UserRole

load_dotenv()

# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------
router = APIRouter(prefix="/api/seller/ai-store-assistant", tags=["ai-assistant"])

# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class ChatMessage(BaseModel):
    sender: str          # 'user' | 'assistant'
    content: str

class ChatPayload(BaseModel):
    messages: List[ChatMessage]

class ChatResponse(BaseModel):
    reply: str
    store_created: bool

# ---------------------------------------------------------------------------
# Gemini tool definition (function-calling)
# ---------------------------------------------------------------------------
CREATE_STORE_TOOL = {
    "function_declarations": [
        {
            "name": "create_store",
            "description": (
                "Crea una tienda en la base de datos del marketplace ALTOQ. "
                "Llama a esta función SOLO cuando hayas recopilado al menos "
                "el nombre, email y descripción de la tienda del usuario."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Nombre de la tienda",
                    },
                    "email": {
                        "type": "string",
                        "description": "Correo electrónico de contacto de la tienda",
                    },
                    "description": {
                        "type": "string",
                        "description": "Descripción breve de la tienda y lo que vende",
                    },
                    "ruc": {
                        "type": "string",
                        "description": "RUC de la tienda (opcional)",
                    },
                    "phone": {
                        "type": "string",
                        "description": "Teléfono de contacto (opcional)",
                    },
                    "owner_name": {
                        "type": "string",
                        "description": "Nombre del dueño de la tienda (opcional)",
                    },
                },
                "required": ["name", "email", "description"],
            },
        }
    ]
}

SYSTEM_INSTRUCTION = (
    "Eres el asistente virtual de ALTOQ, un marketplace peruano. "
    "Tu misión es ayudar al usuario a crear su tienda de forma conversacional y amigable. "
    "Debes recopilar la siguiente información:\n"
    "  1. Nombre de la tienda (obligatorio)\n"
    "  2. Descripción / qué productos vende (obligatorio)\n"
    "  3. Correo electrónico de contacto de la tienda (obligatorio)\n"
    "  4. RUC (opcional)\n"
    "  5. Teléfono de contacto (opcional)\n"
    "  6. Nombre del dueño (opcional)\n\n"
    "Reglas:\n"
    "- Saluda amigablemente al inicio.\n"
    "- Haz las preguntas de forma natural, una a la vez.\n"
    "- Cuando tengas al menos el nombre, email y descripción, muestra un resumen "
    "  y pregunta al usuario si quiere confirmar la creación.\n"
    "- Si el usuario confirma, llama a la función create_store con los datos recopilados.\n"
    "- Si el usuario quiere cambiar algo, permite la corrección antes de crear.\n"
    "- Responde siempre en español.\n"
    "- Sé conciso pero amigable. Usa emojis moderadamente.\n"
)


# ---------------------------------------------------------------------------
# Helper: create the store in DB
# ---------------------------------------------------------------------------
def _create_store_in_db(
    db: Session,
    user: User,
    *,
    name: str,
    email: str,
    description: str,
    ruc: str | None = None,
    phone: str | None = None,
    owner_name: str | None = None,
) -> Store:
    """Persist a new Store row linked to the authenticated user."""
    existing = db.query(Store).filter(Store.user_id == user.id).first()
    if existing:
        raise ValueError("El usuario ya tiene una tienda registrada.")

    new_store = Store(
        name=name,
        email=email,
        description=description,
        ruc=ruc,
        phone=phone,
        owner_name=owner_name or user.name,
        user_id=user.id,
        status="active",
    )
    db.add(new_store)

    # Upgrade role
    if user.role in (UserRole.BUYER, "BUYER"):
        user.role = UserRole.BOTH

    db.commit()
    db.refresh(new_store)
    return new_store


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------
@router.post("/chat", response_model=ChatResponse)
def chat_with_assistant(
    payload: ChatPayload,
    current_user_email: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Conversational endpoint for the AI store-creation assistant.

    The frontend sends the full message history on every request.
    Gemini processes it and either responds with text or calls the
    ``create_store`` tool to persist the store.
    """
    # ------------------------------------------------------------------
    # 0. Resolve user
    # ------------------------------------------------------------------
    user = db.query(User).filter(User.email == current_user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # ------------------------------------------------------------------
    # 1. Lazy-import google.generativeai (fails fast if key missing)
    # ------------------------------------------------------------------
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY no está configurada en el archivo .env",
        )

    try:
        import google.generativeai as genai
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="El paquete google-generativeai no está instalado. Ejecuta: pip install google-generativeai",
        )

    genai.configure(api_key=api_key)

    # ------------------------------------------------------------------
    # 2. Build conversation history in Gemini format
    # ------------------------------------------------------------------
    history = []
    for msg in payload.messages:
        role = "user" if msg.sender == "user" else "model"
        history.append({"role": role, "parts": [msg.content]})

    # ------------------------------------------------------------------
    # 3. Create model & start chat
    # ------------------------------------------------------------------
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=SYSTEM_INSTRUCTION,
        tools=[CREATE_STORE_TOOL],
    )

    # Separate last user message from history to send via chat.send_message
    if not history or history[-1]["role"] != "user":
        raise HTTPException(status_code=400, detail="El último mensaje debe ser del usuario")

    last_user_msg = history.pop()
    chat = model.start_chat(history=history)

    try:
        response = chat.send_message(last_user_msg["parts"][0])
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=502, detail=f"Error comunicándose con Gemini: {str(e)}")

    # ------------------------------------------------------------------
    # 4. Handle function call (if any)
    # ------------------------------------------------------------------
    store_created = False
    reply_text = ""

    for candidate in response.candidates:
        for part in candidate.content.parts:
            # Text response
            if hasattr(part, "text") and part.text:
                reply_text += part.text

            # Function call
            if hasattr(part, "function_call") and part.function_call:
                fc = part.function_call
                if fc.name == "create_store":
                    args = dict(fc.args)
                    try:
                        new_store = _create_store_in_db(
                            db,
                            user,
                            name=args.get("name", ""),
                            email=args.get("email", ""),
                            description=args.get("description", ""),
                            ruc=args.get("ruc"),
                            phone=args.get("phone"),
                            owner_name=args.get("owner_name"),
                        )
                        store_created = True

                        # Send function result back to Gemini for a nice closing message
                        func_response = genai.protos.Part(
                            function_response=genai.protos.FunctionResponse(
                                name="create_store",
                                response={"result": json.dumps({
                                    "success": True,
                                    "store_id": new_store.id,
                                    "store_name": new_store.name,
                                })},
                            )
                        )
                        follow_up = chat.send_message(func_response)
                        reply_text = ""
                        for c2 in follow_up.candidates:
                            for p2 in c2.content.parts:
                                if hasattr(p2, "text") and p2.text:
                                    reply_text += p2.text

                    except ValueError as ve:
                        reply_text = str(ve)
                    except Exception as e:
                        traceback.print_exc()
                        reply_text = f"Ocurrió un error al crear la tienda: {str(e)}"

    if not reply_text:
        reply_text = "Lo siento, no pude generar una respuesta. Por favor intenta de nuevo."

    return ChatResponse(reply=reply_text, store_created=store_created)
