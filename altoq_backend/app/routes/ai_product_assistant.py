"""
AI Product-creation assistant powered by Google Gemini.
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
from ..models.product import Product
from ..models.store import Store
from ..models.user import User

load_dotenv()

router = APIRouter(prefix="/api/seller/ai-product-assistant", tags=["ai-assistant"])

class ChatMessage(BaseModel):
    sender: str
    content: str

class ProductChatPayload(BaseModel):
    messages: List[ChatMessage]

class ProductChatResponse(BaseModel):
    reply: str
    product_created: bool

CREATE_PRODUCT_TOOL = {
    "function_declarations": [
        {
            "name": "create_product",
            "description": (
                "Crea un producto en la tienda del usuario. "
                "Llama a esta función SOLO cuando tengas el nombre, precio, "
                "descripción y categoría del producto."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Nombre del producto"},
                    "price": {"type": "number", "description": "Precio del producto en Soles (S/.)"},
                    "description": {"type": "string", "description": "Descripción del producto"},
                    "category": {"type": "string", "description": "Categoría del producto (ej: Ropa, Tecnología)"},
                },
                "required": ["name", "price", "description", "category"],
            },
        }
    ]
}

SYSTEM_INSTRUCTION = (
    "Eres el asistente de IA para crear productos en ALTOQ. "
    "Tu objetivo es ayudar al usuario a publicar un nuevo producto en su tienda. "
    "Pregunta amigablemente uno por uno los siguientes datos:\n"
    "1. Nombre del producto\n"
    "2. Precio (en Soles)\n"
    "3. Descripción detallada\n"
    "4. Categoría\n\n"
    "Reglas:\n"
    "- Saluda y pregunta qué quieren vender.\n"
    "- Pide solo un dato a la vez si falta alguno.\n"
    "- Una vez que tengas los 4 datos obligatorios, muestra un resumen y pregunta si desean confirmar la publicación.\n"
    "- Si el usuario dice 'sí' o confirma, llama a la función `create_product`.\n"
    "- Responde siempre en español y sé conciso."
)

from ..models.category import Category

def _create_product_in_db(
    db: Session,
    user: User,
    *,
    name: str,
    price: float,
    description: str,
    category: str
) -> Product:
    # Verify user has a store
    store = db.query(Store).filter(Store.user_id == user.id).first()
    if not store:
        raise ValueError("Necesitas tener una tienda creada antes de publicar productos.")

    slug = category.lower().replace(" ", "-")
    cat_obj = db.query(Category).filter(
        (Category.slug == slug) | (Category.name.ilike(f"%{category}%"))
    ).first()
    category_id = cat_obj.id if cat_obj else None

    new_product = Product(
        name=name,
        price=price,
        description=description,
        category=category,
        category_id=category_id,
        store_id=store.id,
        store_name=store.name,
        stock=1,
        image="https://placehold.co/300x200?text=Nuevo+Producto"
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@router.post("/chat", response_model=ProductChatResponse)
def chat_with_product_assistant(
    payload: ProductChatPayload,
    current_user_email: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == current_user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY no está configurada")

    try:
        import google.generativeai as genai
    except ImportError:
        raise HTTPException(status_code=500, detail="Falta google-generativeai")

    genai.configure(api_key=api_key)

    categories_db = db.query(Category).all()
    category_names = [c.name for c in categories_db]
    allowed_categories = ", ".join(category_names) if category_names else "General"

    dynamic_instruction = (
        "Eres el asistente de IA para crear productos en ALTOQ. "
        "Tu objetivo es ayudar al usuario a publicar un nuevo producto en su tienda. "
        "Pregunta amigablemente uno por uno los siguientes datos:\n"
        "1. Nombre del producto\n"
        "2. Precio (en Soles)\n"
        "3. Descripción detallada\n"
        "4. Categoría\n\n"
        "Reglas:\n"
        "- Saluda y pregunta qué quieren vender.\n"
        "- Pide solo un dato a la vez si falta alguno.\n"
        f"- IMPORTANTE: No permitas que el usuario invente categorías. El producto SOLO puede pertenecer a una de estas categorías existentes: {allowed_categories}.\n"
        "- Si el usuario da una categoría o producto que no se ajusta, muéstrale la lista de categorías disponibles y pídele que elija una.\n"
        "- Una vez que tengas los 4 datos obligatorios, muestra un resumen y pregunta si desean confirmar la publicación.\n"
        "- Si el usuario dice 'sí' o confirma, llama a la función `create_product`.\n"
        "- Responde siempre en español y sé conciso."
    )

    dynamic_tool = {
        "function_declarations": [
            {
                "name": "create_product",
                "description": (
                    "Crea un producto en la tienda del usuario. "
                    "Llama a esta función SOLO cuando tengas el nombre, precio, "
                    "descripción y categoría del producto."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Nombre del producto"},
                        "price": {"type": "number", "description": "Precio del producto en Soles (S/.)"},
                        "description": {"type": "string", "description": "Descripción del producto"},
                        "category": {
                            "type": "string", 
                            "description": f"Categoría del producto. Debe ser exactamente una de: {allowed_categories}"
                        },
                    },
                    "required": ["name", "price", "description", "category"],
                },
            }
        ]
    }

    history = []
    for msg in payload.messages:
        role = "user" if msg.sender == "user" else "model"
        history.append({"role": role, "parts": [msg.content]})

    if not history or history[-1]["role"] != "user":
        raise HTTPException(status_code=400, detail="El último mensaje debe ser del usuario")

    model = genai.GenerativeModel(
        model_name="gemini-3.1-flash-lite",
        system_instruction=dynamic_instruction,
        tools=[dynamic_tool],
    )

    last_user_msg = history.pop()
    chat = model.start_chat(history=history)

    try:
        response = chat.send_message(last_user_msg["parts"][0])
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=502, detail=f"Error con Gemini: {str(e)}")

    product_created = False
    reply_text = ""

    for candidate in response.candidates:
        for part in candidate.content.parts:
            if hasattr(part, "text") and part.text:
                reply_text += part.text

            if hasattr(part, "function_call") and part.function_call:
                fc = part.function_call
                if fc.name == "create_product":
                    args = dict(fc.args)
                    try:
                        new_prod = _create_product_in_db(
                            db,
                            user,
                            name=args.get("name", ""),
                            price=float(args.get("price", 0.0)),
                            description=args.get("description", ""),
                            category=args.get("category", "General")
                        )
                        product_created = True

                        func_response = genai.protos.Part(
                            function_response=genai.protos.FunctionResponse(
                                name="create_product",
                                response={"result": json.dumps({"success": True})}
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
                        reply_text = f"Error al crear el producto: {str(e)}"

    if not reply_text:
        reply_text = "Procesado."

    return ProductChatResponse(reply=reply_text, product_created=product_created)
