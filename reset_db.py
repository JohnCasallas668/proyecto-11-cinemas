from app import create_app, db
from app.models import Seat, Reservation, CinemasCard, Transaction, CashRegister

def reset_database():
    app = create_app()
    with app.app_context():
        # Drop all tables
        print("Dropping all database tables...")
        db.drop_all()
        
        # Create all tables
        print("Creating database tables...")
        db.create_all()
        
        # Import and run the seat initialization
        from app.models import initialize_cinema_seats
        print("Initializing cinema seats...")
        initialize_cinema_seats()
        
        print("Database reset and initialized successfully!")

if __name__ == "__main__":
    reset_database()
