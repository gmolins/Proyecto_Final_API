from datetime import datetime
import random
from sqlmodel import Session
from db.database import engine, create_db_and_tables, drop_db_and_tables
from models.user import User
from models.order import Order
from models.status import Status
from auth.hashing import hash_password  # Importamos la función para hashear contraseñas

def seed_data(num_dummies=5):
    with Session(engine) as session:
        # Crear usuarios
        try:
            users = []
            for i in range(num_dummies):
                users.append(User(username=f"User {i}", email=f"user{i}@example.com", role=random.choice(["user", "viewer"]), hashed_password=hash_password(f"password{i}"), created_at=datetime.now()))
            users.append(User(username=f"User {num_dummies}", email=f"admin{num_dummies}@example.com", role="admin", hashed_password=hash_password(f"admin{num_dummies}"), created_at=datetime.now()))
            session.add_all(users)
            session.commit()
        except Exception as e:
            print(f"Error creating users: {e}")

        # Crear todos linkados a usuarios
        try:
            todos = []
            for j in range(num_dummies):
                todos.append(Order(created_at=datetime.now(), user_id=j+1))
            session.add_all(todos)
            session.commit()
        except Exception as e:
            print(f"Error creating todos: {e}")

        # Crear status
        try:
            status1 = Status(name=f"Order Created", color=f"Yellow")
            status1 = Status(name=f"Order Placed", color=f"Blue")
            status2 = Status(name=f"Payment Complete", color=f"Green")
            status3 = Status(name=f"Delivered", color=f"Purple")
            status3 = Status(name=f"RMA", color=f"Red")
            session.add_all([status1, status2, status3])
            session.commit()
        except Exception as e:
            print(f"Error creating status: {e}")
        
    print("Tables seeded successfully!")

if __name__ == "__main__":
    # Borrar la base de datos y las tablas existentes
    drop_db_and_tables() 
    # Crear la base de datos y las tablas
    create_db_and_tables()
    # Alimentar las tablas con datos dummy
    seed_data()
