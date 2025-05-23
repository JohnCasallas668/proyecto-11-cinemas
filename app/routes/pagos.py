from flask import Blueprint, render_template, redirect, url_for, flash, request
from app import db
from app.models import Reservation, Seat, SeatStatus, PaymentStatus, PaymentMethod, Transaction, CinemasCard, CashRegister
from app.forms import PaymentForm, CancelPaymentForm

pagos_bp = Blueprint('pagos', __name__, url_prefix='/pagos')

@pagos_bp.route('/realizar', methods=['GET', 'POST'])
def realizar_pago():
    """Process payment for a reservation"""
    form = PaymentForm()
    
    if form.validate_on_submit():
        # Find the most recent unpaid reservation for this cedula
        reserva = Reservation.query.filter_by(
            cedula=form.cedula.data,
            payment_status=PaymentStatus.PENDING.value
        ).order_by(Reservation.created_at.desc()).first()
        
        if not reserva:
            flash('No se encontró ninguna reserva pendiente para esta cédula', 'danger')
            return redirect(url_for('pagos.realizar_pago'))
        
        # Process payment based on selected method
        if form.payment_method.data == 'cash':
            # Cash payment
            amount = reserva.total_price
            payment_method = PaymentMethod.CASH.value
            
            # Update cash register
            register = CashRegister.get_instance()
            register.cash_balance += amount
            
        else:  # Card payment
            # Find the card
            tarjeta = CinemasCard.query.filter_by(cedula=form.cedula.data).first()
            
            if not tarjeta or not tarjeta.active:
                flash('No se encontró una tarjeta CINEMAS activa para esta cédula', 'danger')
                return redirect(url_for('pagos.realizar_pago'))
            
            # Apply discount
            amount = reserva.discounted_price
            payment_method = PaymentMethod.CARD.value
            
            # Check if card has enough balance
            if tarjeta.balance < amount:
                flash(f'Saldo insuficiente. Saldo actual: ${tarjeta.balance:,.0f}, Monto a pagar: ${amount:,.0f}', 'danger')
                return redirect(url_for('pagos.realizar_pago'))
            
            # Update card balance
            tarjeta.balance -= amount
            
            # Update cash register
            register = CashRegister.get_instance()
            register.card_balance += amount
        
        # Create transaction record
        transaction = Transaction(
            reservation_id=reserva.id,
            payment_method=payment_method,
            amount=amount,
            cedula=form.cedula.data
        )
        db.session.add(transaction)
        
        # Update reservation status
        reserva.payment_status = PaymentStatus.PAID.value
        
        # Update seat status
        for seat in reserva.seats:
            seat.status = SeatStatus.SOLD.value
        
        try:
            db.session.commit()
            flash(f'Pago realizado exitosamente. Monto: ${amount:,.0f}', 'success')
            return redirect(url_for('pagos.ver_transaccion', id=transaction.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al procesar el pago: {str(e)}', 'danger')
    
    return render_template('pagos/realizar_pago.html', form=form)

@pagos_bp.route('/anular', methods=['GET', 'POST'])
def anular_pago():
    """Cancel a payment and refund"""
    form = CancelPaymentForm()
    
    if form.validate_on_submit():
        # Find the transaction
        transaction = Transaction.query.get(form.transaction_id.data)
        
        if not transaction or transaction.cedula != form.cedula.data:
            flash('No se encontró la transacción especificada para esta cédula', 'danger')
            return redirect(url_for('pagos.anular_pago'))
        
        # Get the reservation
        reserva = transaction.reservation
        
        # Check if the reservation exists and is paid
        if not reserva or reserva.payment_status != PaymentStatus.PAID.value:
            flash('La reserva asociada no existe o no está pagada', 'danger')
            return redirect(url_for('pagos.anular_pago'))
        
        # Process refund based on payment method
        if transaction.payment_method == PaymentMethod.CASH.value:
            # Update cash register
            register = CashRegister.get_instance()
            register.cash_balance -= transaction.amount
            
        else:  # Card payment
            # Find the card
            tarjeta = CinemasCard.query.filter_by(cedula=transaction.cedula).first()
            
            if not tarjeta:
                flash('No se encontró la tarjeta CINEMAS asociada a esta transacción', 'danger')
                return redirect(url_for('pagos.anular_pago'))
            
            # Refund to card
            tarjeta.balance += transaction.amount
            
            # Update cash register
            register = CashRegister.get_instance()
            register.card_balance -= transaction.amount
        
        # Update reservation status
        reserva.payment_status = PaymentStatus.PENDING.value
        
        # Update seat status
        for seat in reserva.seats:
            seat.status = SeatStatus.RESERVED.value
        
        # Delete the transaction
        db.session.delete(transaction)
        
        try:
            db.session.commit()
            flash(f'Pago anulado exitosamente. Monto reembolsado: ${transaction.amount:,.0f}', 'success')
            return redirect(url_for('reservas.ver_reserva', id=reserva.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al anular el pago: {str(e)}', 'danger')
    
    return render_template('pagos/anular_pago.html', form=form)

@pagos_bp.route('/transaccion/<int:id>')
def ver_transaccion(id):
    """View details of a specific transaction"""
    transaction = Transaction.query.get_or_404(id)
    return render_template('pagos/ver_transaccion.html', transaction=transaction)
