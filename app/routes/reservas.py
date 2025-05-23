from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from app import db
from app.models import Reservation, Seat, SeatStatus, PaymentStatus
from app.forms import ReservationForm, CancelReservationForm
import json

reservas_bp = Blueprint('reservas', __name__, url_prefix='/reservas')

@reservas_bp.route('/crear', methods=['GET', 'POST'])
def crear_reserva():
    form = ReservationForm()
    
    if request.method == 'POST':
        # Obtener datos directamente del request
        cedula = request.form.get('cedula')
        selected_seats = request.form.get('selected_seats', '')
        
        print(f"Datos recibidos - Cédula: {cedula}, Asientos: {selected_seats}")
        
        # Validar datos
        if not cedula or not cedula.isdigit() or len(cedula) < 6 or len(cedula) > 12:
            flash('La cédula debe contener entre 6 y 12 dígitos numéricos', 'danger')
            return redirect(url_for('reservas.crear_reserva'))
        
        seat_ids = selected_seats.split(',') if selected_seats else []
        
        if not seat_ids or seat_ids[0] == '':
            flash('Debe seleccionar al menos un asiento', 'danger')
            return redirect(url_for('reservas.crear_reserva'))
        
        if len(seat_ids) > 8:
            flash('No puede reservar más de 8 asientos', 'danger')
            return redirect(url_for('reservas.crear_reserva'))
        
        # Crear nueva reserva
        nueva_reserva = Reservation(cedula=cedula)
        db.session.add(nueva_reserva)
        
        try:
            db.session.commit()
            print(f"Reserva creada con ID: {nueva_reserva.id}")
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear la reserva: {str(e)}', 'danger')
            return redirect(url_for('reservas.crear_reserva'))
        
        # Actualizar estado de asientos
        seat_count = 0
        for seat_id in seat_ids:
            if seat_id:  # Omitir cadenas vacías
                try:
                    seat = Seat.query.get(int(seat_id))
                    if seat and seat.status == SeatStatus.AVAILABLE.value:
                        seat.status = SeatStatus.RESERVED.value
                        seat.reservation_id = nueva_reserva.id
                        seat_count += 1
                        print(f"Asiento {seat.row}{seat.number} reservado")
                    else:
                        if seat:
                            print(f"Asiento {seat.row}{seat.number} no disponible, estado: {seat.status}")
                            flash(f'El asiento {seat.row}{seat.number} no está disponible y no se incluyó en la reserva', 'warning')
                        else:
                            print(f"Asiento con ID {seat_id} no encontrado")
                            flash(f'El asiento con ID {seat_id} no existe', 'warning')
                except Exception as e:
                    print(f"Error al procesar asiento {seat_id}: {str(e)}")
                    flash(f'Error al procesar asiento: {str(e)}', 'warning')
        
        if seat_count == 0:
            # Si no se pudo reservar ningún asiento, eliminar la reserva
            try:
                db.session.delete(nueva_reserva)
                db.session.commit()
                flash('No se pudo reservar ningún asiento. La reserva ha sido cancelada.', 'danger')
                return redirect(url_for('reservas.crear_reserva'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error al cancelar la reserva: {str(e)}', 'danger')
                return redirect(url_for('reservas.crear_reserva'))
        
        try:
            db.session.commit()
            flash(f'Reserva creada exitosamente con {seat_count} asiento(s). ID de reserva: {nueva_reserva.id}', 'success')
            return redirect(url_for('reservas.ver_reserva', id=nueva_reserva.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al finalizar la reserva: {str(e)}', 'danger')
            return redirect(url_for('reservas.crear_reserva'))
    
    # Obtener todos los asientos para mostrar el estado actual
    all_seats = Seat.query.order_by(Seat.row, Seat.number).all()
    
    # Debug: Print seat status counts
    status_counts = {}
    for seat in all_seats:
        status_counts[seat.status] = status_counts.get(seat.status, 0) + 1
    print(f"Seat status counts: {status_counts}")
    
    # Debug: Print first few seats
    print("\nFirst 5 seats:")
    for seat in all_seats[:5]:
        print(f"Seat {seat.row}{seat.number}: {seat.status} (type: {seat.seat_type}, id: {seat.id})")
    
    # Create a dictionary of seats for easier lookup in the template
    seats_dict = {f"{seat.row}{seat.number}": seat for seat in all_seats}
    
    return render_template('reservas/crear_reserva.html', 
                          form=form, 
                          all_seats=all_seats,
                          seats_dict=seats_dict,
                          SeatStatus=SeatStatus)  # Pass the SeatStatus enum to the template

@reservas_bp.route('/cancelar', methods=['GET', 'POST'])
def cancelar_reserva():
    """Cancel a reservation"""
    form = CancelReservationForm()
    
    if form.validate_on_submit():
        # Find the most recent unpaid reservation for this cedula
        reserva = Reservation.query.filter_by(
            cedula=form.cedula.data,
            payment_status=PaymentStatus.PENDING.value
        ).order_by(Reservation.created_at.desc()).first()
        
        if not reserva:
            flash('No se encontró ninguna reserva pendiente para esta cédula', 'danger')
            return redirect(url_for('reservas.cancelar_reserva'))
        
        # Update seat status
        for seat in reserva.seats:
            seat.status = SeatStatus.AVAILABLE.value
            seat.reservation_id = None
        
        # Delete the reservation
        db.session.delete(reserva)
        
        try:
            db.session.commit()
            flash('Reserva cancelada exitosamente', 'success')
            return redirect(url_for('main.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al cancelar la reserva: {str(e)}', 'danger')
    
    return render_template('reservas/cancelar_reserva.html', form=form)

@reservas_bp.route('/ver/<int:id>')
def ver_reserva(id):
    """View details of a specific reservation"""
    reserva = Reservation.query.get_or_404(id)
    return render_template('reservas/ver_reserva.html', reserva=reserva)

@reservas_bp.route('/consultar', methods=['GET', 'POST'])
def consultar_reserva():
    """Search for a reservation by cedula"""
    cedula = request.args.get('cedula', '')
    
    if cedula:
        # Find the most recent reservation for this cedula
        reserva = Reservation.query.filter_by(cedula=cedula).order_by(Reservation.created_at.desc()).first()
        
        if reserva:
            return redirect(url_for('reservas.ver_reserva', id=reserva.id))
        else:
            flash('No se encontró ninguna reserva para esta cédula', 'danger')
    
    return render_template('reservas/consultar_reserva.html')

@reservas_bp.route('/debug/seats')
def debug_seats():
    """Debug endpoint to check seat statuses"""
    seats = Seat.query.order_by(Seat.row, Seat.number).all()
    
    seat_data = []
    for seat in seats:
        seat_data.append({
            'id': seat.id,
            'row': seat.row,
            'number': seat.number,
            'status': seat.status,
            'type': seat.seat_type,
            'reservation_id': seat.reservation_id
        })
    
    return jsonify({
        'total_seats': len(seat_data),
        'available': len([s for s in seat_data if s['status'] == 'Disponible']),
        'reserved': len([s for s in seat_data if s['status'] == 'Reservada']),
        'sold': len([s for s in seat_data if s['status'] == 'Vendida']),
        'seats': seat_data
    })

@reservas_bp.route('/estado_asientos')
def estado_asientos():
    """API endpoint to get the current status of all seats"""
    seats = Seat.query.order_by(Seat.row, Seat.number).all()
    
    seat_status = {}
    for seat in seats:
        seat_status[f"{seat.row}{seat.number}"] = {
            'id': seat.id,
            'status': seat.status,
            'type': seat.seat_type,
            'reservation_id': seat.reservation_id
        }
    
    return jsonify(seat_status)
