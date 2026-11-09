# main.py

from services.auth_service import (
    register_user,
    verify_otp,
    login_user
)

from controllers.admin_controller import admin_dashboard
from controllers.customer_controller import customer_dashboard
from controllers.professional_controller import professional_dashboard


def main_menu():
    while True:
        print("\n===== WORKBUDDY =====")
        print("1. Register")
        print("2. Login")
        print("3. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            register_flow()
        elif choice == "2":
            login_flow()
        elif choice == "3":
            break
        else:
            print("Invalid choice!")


# ---------------- REGISTER ----------------
def register_flow():
    name = input("Name: ")
    email = input("Email: ")
    phone = input("Phone: ")
    password = input("Password: ")

    print("1. Admin  2. Customer  3. Professional")
    role_map = {"1": "admin", "2": "customer", "3": "professional"}

    role = role_map.get(input("Choose role: "))

    if not role:
        print("Invalid role!")
        return

    register_result = register_user(name, email, phone, password, role)
    if not register_result:
        return
        
    user_id, otp = register_result

    if user_id:
        otp = input("Enter OTP: ")
        if verify_otp(user_id, otp):
            if role == "professional":
                from controllers.professional_controller import handle_profile_creation
                handle_profile_creation({"id": user_id, "role": role})


# ---------------- LOGIN ----------------
def login_flow():
    phone = input("Phone: ")
    password = input("Password: ")

    user = login_user(phone, password)

    if user:
        role_dashboard(user)


# ---------------- ROLE DASHBOARD ----------------
def role_dashboard(user):
    if user["role"] == "admin":
        admin_dashboard()
    elif user["role"] == "customer":
        customer_dashboard(user)
    elif user["role"] == "professional":
        professional_dashboard(user)

if __name__ == "__main__":
    main_menu()