"""
Tutorial Interactivo de Migraciones
====================================

Este script demuestra cómo usar el sistema de migraciones de AltoQ Backend,
que funciona similar a las migraciones de Laravel.

Ejecuta este script para ver ejemplos prácticos de uso.
"""

def print_header(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def print_command(cmd, description):
    print(f"\n📝 {description}")
    print(f"   $ {cmd}")

def main():
    print_header("SISTEMA DE MIGRACIONES - ALTOQ BACKEND")
    
    print("\n🚀 Este proyecto usa Alembic para manejar migraciones de base de datos.")
    print("   Los comandos son similares a php artisan migrate de Laravel.\n")
    
    # Comandos básicos
    print_header("1. COMANDOS BÁSICOS")
    
    print_command("python migrate.py", "Ejecutar migraciones pendientes")
    print("   Equivalente Laravel: php artisan migrate")
    print("   → Aplica todas las migraciones que aún no se han ejecutado")
    
    print_command("python migrate.py status", "Ver estado actual")
    print("   Equivalente Laravel: php artisan migrate:status")
    print("   → Muestra qué migraciones se han ejecutado y cuáles faltan")
    
    print_command("python migrate.py history", "Ver historial completo")
    print("   Equivalente Laravel: php artisan migrate:show")
    print("   → Muestra todas las migraciones disponibles")
    
    # Crear migraciones
    print_header("2. CREAR NUEVAS MIGRACIONES")
    
    print_command('python migrate.py create "agregar campo telefono a users"', 
                  "Crear una nueva migración")
    print("   Equivalente Laravel: php artisan make:migration agregar_campo_telefono")
    print("   → Genera automáticamente una migración basada en cambios en modelos")
    
    print("\n   📋 Flujo de trabajo:")
    print("   1. Modificas un modelo en app/models/")
    print("   2. Ejecutas: python migrate.py create 'descripción'")
    print("   3. Revisas el archivo generado en alembic/versions/")
    print("   4. Ejecutas: python migrate.py")
    
    # Revertir migraciones
    print_header("3. REVERTIR MIGRACIONES")
    
    print_command("python migrate.py rollback", "Revertir última migración")
    print("   Equivalente Laravel: php artisan migrate:rollback")
    print("   → Deshace la última migración ejecutada")
    
    print_command("python migrate.py rollback 3", "Revertir N migraciones")
    print("   → Revierte las últimas 3 migraciones")
    
    print_command("python migrate.py reset", "Revertir TODO")
    print("   Equivalente Laravel: php artisan migrate:reset")
    print("   → Revierte todas las migraciones hasta el estado inicial")
    
    print_command("python migrate.py fresh", "Recrear BD desde cero")
    print("   Equivalente Laravel: php artisan migrate:fresh")
    print("   → ⚠️  PELIGROSO: Elimina toda la BD y la recrea")
    
    # Ejemplo práctico
    print_header("4. EJEMPLO PRÁCTICO")
    
    print("\n📝 Escenario: Quieres agregar un campo 'phone' a la tabla users")
    print()
    print("   Paso 1: Modificar el modelo")
    print("   ──────────────────────────")
    print("   # app/models/user.py")
    print("   class User(Base):")
    print("       # ... campos existentes ...")
    print("       phone = Column(String(20), nullable=True)  # Nuevo campo")
    print()
    print("   Paso 2: Crear la migración")
    print("   ──────────────────────────")
    print('   $ python migrate.py create "agregar campo phone a users"')
    print()
    print("   Paso 3: Revisar la migración generada")
    print("   ────────────────────────────────────")
    print("   # alembic/versions/XXXX_agregar_campo_phone_a_users.py")
    print("   def upgrade():")
    print("       op.add_column('users', sa.Column('phone', sa.String(20), nullable=True))")
    print()
    print("   def downgrade():")
    print("       op.drop_column('users', 'phone')")
    print()
    print("   Paso 4: Ejecutar la migración")
    print("   ────────────────────────────")
    print("   $ python migrate.py")
    print()
    print("   Paso 5: Si necesitas revertir")
    print("   ────────────────────────────")
    print("   $ python migrate.py rollback")
    
    # Recursos adicionales
    print_header("5. RECURSOS ADICIONALES")
    
    print("\n📚 Documentación:")
    print("   • QUICKSTART_MIGRATIONS.md - Guía rápida de inicio")
    print("   • MIGRATIONS_GUIDE.md - Documentación completa")
    print("   • README.md - Información general del proyecto")
    
    print("\n🔗 Enlaces útiles:")
    print("   • Documentación de Alembic: https://alembic.sqlalchemy.org/")
    print("   • Documentación de SQLAlchemy: https://docs.sqlalchemy.org/")
    
    print("\n✨ ¡Listo! Ahora puedes usar el sistema de migraciones.")
    print("   Ejecuta 'python migrate.py help' para ver todos los comandos.\n")

if __name__ == "__main__":
    main()
