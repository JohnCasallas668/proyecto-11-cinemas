from app import db
from datetime import datetime
from enum import Enum

class SeatType(Enum):
    GENERAL = "General"
    PREFERENTIAL = "Preferencial"

class SeatStatus(Enum):
    AVAILABLE = "Disponible"
    RESERVED = "Reservada"
    SOLD = "Vendida"

class PaymentStatus(Enum):
    PENDING = "Pendiente"
    PAID = "Pagada"

class PaymentMethod(Enum):
    CASH = "Efectivo"
    CARD = "Tarjeta CINEMAS"

class Seat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    row = db.Column(db.String(1), nullable=False)  # A-K
    number = db.Column(db.Integer, nullable=False)  # 1-20
    seat_type = db.Column(db.String(20), nullable=False)  # General or Preferencial
    status = db.Column(db.String(20), nullable=False, default=SeatStatus.AVAILABLE.value)
    reservation_id = db.Column(db.Integer, db.ForeignKey('reservation.id'), nullable=True)
    
    @property
    def price(self):
        if self.seat_type == SeatType.GENERAL.value:
            return 8000
        else:  # Preferencial
            return 11000
    
    def __repr__(self):
        return f"<Seat {self.row}{self.number} ({self.seat_type})>"

class CinemasCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cedula = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    balance = db.Column(db.Float, nullable=False, default=70000)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<CinemasCard {self.cedula}>"

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cedula = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    payment_status = db.Column(db.String(20), default=PaymentStatus.PENDING.value)
    seats = db.relationship('Seat', backref='reservation', lazy=True)
    
    @property
    def total_price(self):
        return sum(seat.price for seat in self.seats)
    
    @property
    def discounted_price(self):
        # 10% discount for CINEMAS card
        return self.total_price * 0.9
    
    def __repr__(self):
        return f"<Reservation {self.id} by {self.cedula}>"

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reservation_id = db.Column(db.Integer, db.ForeignKey('reservation.id'), nullable=False)
    payment_method = db.Column(db.String(20), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    cedula = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    reservation = db.relationship('Reservation', backref='transactions')
    
    def __repr__(self):
        return f"<Transaction {self.id} for Reservation {self.reservation_id}>"

class CashRegister(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cash_balance = db.Column(db.Float, default=0)
    card_balance = db.Column(db.Float, default=0)
    
    @classmethod
    def get_instance(cls):
        register = cls.query.first()
        if not register:
            register = cls()
            db.session.add(register)
            db.session.commit()
        return register

def initialize_cinema_seats():
    """Initialize the cinema seats if they don't exist yet"""
    # Check if seats already exist
    if Seat.query.first() is not None:
        return
    
    try:
        # Create seats for rows A-K and numbers 1-20
        for row in 'ABCDEFGHIJK':
            for number in range(1, 21):
                # Determine seat type based on row
                if row in 'ABCDEFGH':
                    seat_type = SeatType.GENERAL.value
                else:  # rows I-K
                    seat_type = SeatType.PREFERENTIAL.value
                
                # Create the seat
                seat = Seat(
                    row=row,
                    number=number,
                    seat_type=seat_type,
                    status=SeatStatus.AVAILABLE.value  # This will be 'Disponible'
                )
                db.session.add(seat)
        
        # Create cash register instance with initial values
        register = CashRegister(cash_balance=0.0, card_balance=0.0)
        db.session.add(register)
        
        db.session.commit()
        print("Asientos del cine inicializados correctamente con estado 'Disponible'")
    except Exception as e:
        db.session.rollback()
        print(f"Error al inicializar los asientos: {str(e)}")
        raise
