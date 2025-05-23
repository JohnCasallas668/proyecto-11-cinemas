from app import create_app, db
from app.models import Seat, SeatStatus, SeatType

def reset_seats():
    """Reset all seats to available status"""
    app = create_app()
    with app.app_context():
        # Verificar si hay asientos
        seats_count = Seat.query.count()
        print(f"Total de asientos encontrados: {seats_count}")
        
        if seats_count == 0:
            print("No hay asientos en la base de datos. Creando asientos...")
            # Crear asientos para filas A-K y números 1-20
            for row in 'ABCDEFGHIJK':
                for number in range(1, 21):
                    # Determinar tipo de asiento basado en la fila
                    if row in 'ABCDEFGH':
                        seat_type = SeatType.GENERAL.value
                    else:  # filas I-K
                        seat_type = SeatType.PREFERENTIAL.value
                    
                    # Crear el asiento
                    seat = Seat(
                        row=row,
                        number=number,
                        seat_type=seat_type,
                        status=SeatStatus.AVAILABLE.value
                    )
                    db.session.add(seat)
            
            db.session.commit()
            print(f"Se crearon {Seat.query.count()} asientos.")
        else:
            # Resetear todos los asientos a disponible
            print("Reseteando todos los asientos a estado disponible...")
            Seat.query.update({Seat.status: SeatStatus.AVAILABLE.value, Seat.reservation_id: None})
            db.session.commit()
            print(f"Se resetearon {Seat.query.count()} asientos.")
        
        # Verificar estado final
        available_seats = Seat.query.filter_by(status=SeatStatus.AVAILABLE.value).count()
        print(f"Asientos disponibles después del reset: {available_seats}")

if __name__ == "__main__":
    reset_seats()
