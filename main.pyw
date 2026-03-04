from frontend.app import App
from database.database import initialize_database

if __name__ == "__main__":
    # Ensure the database is ready before starting the app
    initialize_database()
    
    app = App()
    app.mainloop()