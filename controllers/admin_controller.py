# controllers/admin_controller.py

from services.admin_service import (
    create_service,
    view_services,
    manage_professionals
)


def admin_dashboard():
    while True:
        print("\n--- ADMIN DASHBOARD ---")
        print("1. Add Service")
        print("2. View Services")
        print("3. Approve Professionals")
        print("4. Logout")

        choice = input("Enter choice: ")

        if choice == "1":
            create_service()
        elif choice == "2":
            view_services()
        elif choice == "3":
            manage_professionals()
        elif choice == "4":
            break
        else:
            print("Invalid choice!")
