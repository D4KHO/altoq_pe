"""
Script de migraciones para AltoQ Backend.
Equivalente a 'php artisan migrate' de Laravel.

Uso:
    python migrate.py                    -> Ejecuta todas las migraciones pendientes (alembic upgrade head)
    python migrate.py create "mensaje"   -> Crea una nueva migracion automatica (alembic revision --autogenerate)
    python migrate.py rollback           -> Revierte la ultima migracion (alembic downgrade -1)
    python migrate.py status             -> Muestra el estado actual de las migraciones (alembic current)
    python migrate.py history            -> Muestra el historial de migraciones (alembic history)
"""

import sys
import os
import subprocess


def get_venv_python():
    """Busca el Python del entorno virtual automaticamente."""
    # Directorio donde esta este script
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Buscar el venv en el directorio del proyecto
    venv_python = os.path.join(base_dir, "venv", "Scripts", "python.exe")
    if os.path.exists(venv_python):
        return venv_python

    # Si no existe en Windows, probar formato Linux/Mac
    venv_python = os.path.join(base_dir, "venv", "bin", "python")
    if os.path.exists(venv_python):
        return venv_python

    # Si no se encuentra venv, usar el Python actual
    return sys.executable


def run_alembic(args: list[str]):
    """Ejecuta un comando de alembic usando el Python del venv."""
    python_exe = get_venv_python()
    cmd = [python_exe, "-m", "alembic"] + args
    print(f"  Ejecutando: {' '.join(cmd)}")
    print("-" * 50)
    result = subprocess.run(cmd, cwd=os.path.dirname(os.path.abspath(__file__)))
    sys.exit(result.returncode)


def main():
    if len(sys.argv) < 2:
        # Sin argumentos -> ejecutar migraciones (equivalente a 'php artisan migrate')
        print("[MIGRATE] Ejecutando migraciones pendientes...")
        run_alembic(["upgrade", "head"])
        return

    command = sys.argv[1].lower()

    if command in ("up", "migrate", "upgrade"):
        print("[MIGRATE] Ejecutando migraciones pendientes...")
        run_alembic(["upgrade", "head"])

    elif command in ("create", "make", "new"):
        if len(sys.argv) < 3:
            print("[ERROR] Debes proporcionar un mensaje para la migracion.")
            print('   Ejemplo: python migrate.py create "agregar campo telefono"')
            sys.exit(1)
        message = sys.argv[2]
        print(f"[CREATE] Creando nueva migracion: '{message}'...")
        run_alembic(["revision", "--autogenerate", "-m", message])

    elif command in ("rollback", "down", "downgrade"):
        steps = sys.argv[2] if len(sys.argv) > 2 else "1"
        print(f"[ROLLBACK] Revirtiendo {steps} migracion(es)...")
        run_alembic(["downgrade", f"-{steps}"])

    elif command in ("status", "current"):
        print("[STATUS] Estado actual de las migraciones:")
        run_alembic(["current"])

    elif command in ("history", "log"):
        print("[HISTORY] Historial de migraciones:")
        run_alembic(["history", "--verbose"])

    elif command in ("reset",):
        print("[RESET] Revirtiendo TODAS las migraciones (base)...")
        run_alembic(["downgrade", "base"])

    elif command in ("help", "-h", "--help"):
        print(__doc__)

    else:
        print(f"[ERROR] Comando desconocido: '{command}'")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
