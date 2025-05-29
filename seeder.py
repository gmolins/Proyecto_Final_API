from datetime import datetime
import random
from sqlmodel import Session
from db.database import engine, create_db_and_tables, drop_db_and_tables
from models.user import User
from models.todo import TodoList
from models.task import Task
from models.status import Status
from auth.hashing import hash_password  # Importamos la función para hashear contraseñas

def seed_data(num_dummies=5):
    with Session(engine) as session:
        # Crear usuarios
        try:
            users = []
            for i in range(num_dummies):
                users.append(User(username=f"User {i}", email=f"user{i}@example.com", role=random.choice(["user", "viewer"]), hashed_password=hash_password(f"password{i}"), created_at=datetime.now()))
            users.append(User(username=f"User {num_dummies}", email=f"admin{i}@example.com", role="admin", hashed_password=hash_password(f"admin{num_dummies}"), created_at=datetime.now()))
            session.add_all(users)
            session.commit()
        except Exception as e:
            print(f"Error creating users: {e}")

        # Crear todos linkados a usuarios
        try:
            todos = []
            for j in range(num_dummies):
                todos.append(TodoList(title=f"Todo entry {j}", description=f"Todo list for entry {j}", created_at=datetime.now(), user=users[j]))
            session.add_all(todos)
            session.commit()
        except Exception as e:
            print(f"Error creating todos: {e}")

        # Crear status
        try:
            status1 = Status(name=f"WIP", color=f"Blue")
            status2 = Status(name=f"Completed", color=f"Green")
            status3 = Status(name=f"Blocker", color=f"Red")
            session.add_all([status1, status2, status3])
            session.commit()
        except Exception as e:
            print(f"Error creating status: {e}")

        # Crear tasks
        try:
            tasks = []
            for k in range(num_dummies):
                tasks.append(Task(title=f"Task {k}", description=f"Content for task {k}", is_completed=False, created_at=datetime.now(), todolist_id=k+1, status_id=random.choice([1,2,3])))
            session.add_all(tasks)
            session.commit()
        except Exception as e:
            print(f"Error creating tasks: {e}")
        
    print("Tables seeded successfully!")

if __name__ == "__main__":
    # Borrar la base de datos y las tablas existentes
    drop_db_and_tables() 
    # Crear la base de datos y las tablas
    create_db_and_tables()
    # Alimentar las tablas con datos dummy
    seed_data()
