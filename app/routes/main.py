from flask import Blueprint, render_template, redirect, url_for, current_app, flash
from app import db
from app.models import Seat, SeatStatus, CashRegister

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Homepage showing the cinema seating layout"""
    seats = Seat.query.order_by(Seat.row, Seat.number).all()
    
    # Group seats by row for easier display
    seats_by_row = {}
    for seat in seats:
        if seat.row not in seats_by_row:
            seats_by_row[seat.row] = []
        seats_by_row[seat.row].append(seat)
    
    # Get ordered rows (A-K)
    ordered_rows = sorted(seats_by_row.keys())
    
    return render_template('index.html', 
                          seats_by_row=seats_by_row, 
                          ordered_rows=ordered_rows,
                          SeatStatus=SeatStatus)

@main_bp.route('/caja')
def cash_register():
    """View showing the cash register balance"""
    try:
        register = CashRegister.get_instance()
        if register is None:
            # Si no hay registro, crear uno nuevo
            register = CashRegister(cash_balance=0.0, card_balance=0.0)
            db.session.add(register)
            db.session.commit()
    except Exception as e:
        # En caso de error, crear un objeto con valores por defecto
        register = type('obj', (object,), {'cash_balance': 0.0, 'card_balance': 0.0})
        flash(f'Error al obtener el registro de caja: {str(e)}', 'danger')
    
    return render_template('cash_register.html', register=register)

# Error handlers
@main_bp.app_errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template('error.html', 
                          error_code=404,
                          error_message="Página no encontrada",
                          error_description="La página que estás buscando no existe o ha sido movida."), 404

@main_bp.app_errorhandler(500)
def internal_server_error(e):
    """Handle 500 errors"""
    return render_template('error.html', 
                          error_code=500,
                          error_message="Error interno del servidor",
                          error_description="Ha ocurrido un error inesperado. Por favor, inténtalo de nuevo más tarde."), 500
