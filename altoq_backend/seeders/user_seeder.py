from sqlalchemy.orm import Session
from app.models.user import User
from app.utils.security import get_password_hash

SELLERS_DATA = [
    {"name": "Mariela Espinoza", "phone": "+51 987 654 321"},
    {"name": "Carlos Huamán", "phone": "+51 954 123 456"},
    {"name": "Sandra Beltrán", "phone": "+51 991 882 773"},
    {"name": "Diego Benavides", "phone": "+51 922 333 444"},
    {"name": "Gabriela Paz", "phone": "+51 966 555 444"},
    {"name": "Jorge Mendoza", "phone": "+51 988 777 666"},
    {"name": "Natalia Rivas", "phone": "+51 944 332 211"},
    {"name": "Víctor Cáceres", "phone": "+51 912 345 678"},
    {"name": "Fabrizio Rossi", "phone": "+51 933 666 999"},
    {"name": "Rosa María Ortiz", "phone": "+51 966 333 111"}
]

def run(db: Session):
    print("\n[2/5] Sembrando usuarios...")
    
    # 1. Crear comprador genérico
    buyer_user = db.query(User).filter(User.email == "buyer_demo@example.com").first()
    if not buyer_user:
        buyer_user = User(
            email="buyer_demo@example.com",
            name="Juan Perez (Demo Compras)",
            password=get_password_hash("password123"),
            address="Av. Larco 456, Miraflores, Lima",
            phone="+51 988 888 888",
            role="buyer"
        )
        db.add(buyer_user)
        db.commit()
        print("  + Usuario comprador demo creado.")
    else:
        print("  ~ Usuario comprador demo ya existe.")

    # 2. Crear vendedores
    for i, s_data in enumerate(SELLERS_DATA, 1):
        seller_email = f"vendedor{i}@example.com"
        seller = db.query(User).filter(User.email == seller_email).first()
        if not seller:
            seller = User(
                email=seller_email,
                name=s_data["name"],
                password=get_password_hash("password123"),
                phone=s_data["phone"],
                address=f"Calle Comercio {100 + i}, Lima",
                role="seller"
            )
            db.add(seller)
            db.commit()
            print(f"  + Vendedor creado: {s_data['name']} ({seller_email})")
        else:
            print(f"  ~ Vendedor ya existe: {s_data['name']} ({seller_email})")
