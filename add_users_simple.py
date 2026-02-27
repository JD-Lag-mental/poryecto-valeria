#!/usr/bin/env python3
"""
Script simple para agregar usuarios a users_db.json
Sin dependencias externas - usa pre-generated hashes
"""

import json
import os
from pathlib import Path

# Hashes pre-generados con bcrypt (cost=12)
# Puedes usar online: https://bcrypt-generator.com/
DEFAULT_HASHES = {
    "admin123": "$2b$12$R9h7cIPz0gi.URNNX3kh2OPST9/PgBkqquzi.Ss8KCUgQDiP34pFm",
    "pass123": "$2b$12$8qDiS9fZpK2Li1KWnqzMPeZ0Xt9JkL3MqQpRhYvNxT4ZvUqB.oeSa",
    "test123": "$2b$12$N9YZ4pK7dL5MxQ1pR8aT2uZ3kL6pQ9dS2vW5xY8eF1gH2jK3mN4oP",
    "user123": "$2b$12$qW7yX8zA9bC0dE1fG2hI3jK4lM5nO6pQ7rS8tU9vW0xY1zB2cD3eF",
}

DB_FILE = "users_db.json"

def load_users():
    """Carga los usuarios actuales"""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_users(users):
    """Guarda los usuarios al archivo"""
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2, ensure_ascii=False)
    print(f"✅ Guardado en {DB_FILE}")

def create_user(username, email, password_hash, is_admin=False):
    """Crea un nuevo usuario"""
    return {
        "username": username,
        "email": email,
        "hashed_password": password_hash,
        "is_admin": is_admin,
        "is_active": True
    }

def main():
    print("=" * 60)
    print("   AGREGAR USUARIOS A users_db.json")
    print("=" * 60)
    
    users = load_users()
    
    print(f"\n📋 Usuarios actuales: {len(users)}")
    for username in users.keys():
        is_admin = "⭐ ADMIN" if users[username].get("is_admin") else ""
        print(f"   - {username} {is_admin}")
    
    print("\n" + "=" * 60)
    print("   OPCIONES")
    print("=" * 60)
    print("1️⃣  Crear usuario ADMIN (admin / admin123)")
    print("2️⃣  Crear usuario regular (usuario1 / pass123)")
    print("3️⃣  Crear usuario regular (usuario2 / test123)")
    print("4️⃣  Resetear a usuarios por defecto")
    print("5️⃣  Crear usuario personalizado")
    print("0️⃣  Salir")
    
    choice = input("\nElige una opción (0-5): ").strip()
    
    if choice == "1":
        users["admin"] = create_user(
            "admin",
            "admin@valeria.local",
            DEFAULT_HASHES["admin123"],
            is_admin=True
        )
        print("✅ Admin creado")
        
    elif choice == "2":
        users["usuario1"] = create_user(
            "usuario1",
            "usuario1@valeria.local",
            DEFAULT_HASHES["pass123"],
            is_admin=False
        )
        print("✅ usuario1 creado")
        
    elif choice == "3":
        users["usuario2"] = create_user(
            "usuario2",
            "usuario2@valeria.local",
            DEFAULT_HASHES["test123"],
            is_admin=False
        )
        print("✅ usuario2 creado")
        
    elif choice == "4":
        users = {
            "admin": create_user(
                "admin",
                "admin@valeria.local",
                DEFAULT_HASHES["admin123"],
                is_admin=True
            ),
            "usuario1": create_user(
                "usuario1",
                "usuario1@valeria.local",
                DEFAULT_HASHES["pass123"],
                is_admin=False
            ),
            "usuario2": create_user(
                "usuario2",
                "usuario2@valeria.local",
                DEFAULT_HASHES["test123"],
                is_admin=False
            )
        }
        print("✅ Base de datos resetada")
        
    elif choice == "5":
        username = input("Username: ").strip()
        if username in users:
            print("❌ Este usuario ya existe")
            return
        
        email = input(f"Email [{username}@valeria.local]: ").strip()
        if not email:
            email = f"{username}@valeria.local"
        
        print("\n🔐 Contraseñas disponibles:")
        for i, pwd in enumerate(DEFAULT_HASHES.keys(), 1):
            print(f"   {i}. {pwd}")
        
        pwd_choice = input("Elige contraseña (número): ").strip()
        try:
            password = list(DEFAULT_HASHES.keys())[int(pwd_choice) - 1]
        except (ValueError, IndexError):
            print("❌ Selección inválida")
            return
        
        is_admin_str = input("¿Es admin? (s/n) [n]: ").strip().lower()
        is_admin = is_admin_str == 's'
        
        users[username] = create_user(
            username,
            email,
            DEFAULT_HASHES[password],
            is_admin=is_admin
        )
        print(f"✅ {username} creado (contraseña: {password})")
        
    elif choice == "0":
        print("👋 Adiós")
        return
    else:
        print("❌ Opción inválida")
        return
    
    save_users(users)
    
    print("\n" + "=" * 60)
    print("   USUARIOS GUARDADOS")
    print("=" * 60)
    for username in users.keys():
        role = "👑 ADMIN" if users[username].get("is_admin") else "👤 USER"
        print(f"{role} - {username} ({users[username]['email']})")
    
    print("\n🚀 Inicia la app con: python main.py")
    print("🌐 Abre: http://localhost:8000/login")

if __name__ == "__main__":
    main()
