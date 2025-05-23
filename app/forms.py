from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SubmitField, SelectField, HiddenField, IntegerField
from wtforms.validators import DataRequired, Length, NumberRange, ValidationError, Regexp
from app.models import CinemasCard, Seat, SeatStatus

class CinemasCardForm(FlaskForm):
    nombre = StringField('Nombre', validators=[
        DataRequired(message="El nombre es obligatorio"),
        Length(min=2, max=100, message="El nombre debe tener entre 2 y 100 caracteres")
    ])
    apellido = StringField('Apellido', validators=[
        DataRequired(message="El apellido es obligatorio"),
        Length(min=2, max=100, message="El apellido debe tener entre 2 y 100 caracteres")
    ])
    cedula = StringField('Cédula', validators=[
        DataRequired(message="La cédula es obligatoria"),
        Regexp(r'^\d{6,12}$', message="La cédula debe contener entre 6 y 12 dígitos numéricos")
    ])
    saldo_inicial = FloatField('Saldo Inicial', default=70000, validators=[
        DataRequired(message="El saldo inicial es obligatorio"),
        NumberRange(min=70000, message="El saldo inicial debe ser de al menos $70,000")
    ])
    submit = SubmitField('Crear Tarjeta')
    
    def validate_cedula(self, cedula):
        # Check if a card with this cedula already exists
        card = CinemasCard.query.filter_by(cedula=cedula.data).first()
        if card:
            raise ValidationError('Ya existe una tarjeta con esta cédula.')

class RechargeCardForm(FlaskForm):
    cedula = StringField('Cédula', validators=[
        DataRequired(message="La cédula es obligatoria"),
        Regexp(r'^\d{6,12}$', message="La cédula debe contener entre 6 y 12 dígitos numéricos")
    ])
    monto = FloatField('Monto de Recarga', default=50000, validators=[
        DataRequired(message="El monto de recarga es obligatorio"),
        NumberRange(min=50000, max=50000, message="El monto de recarga debe ser exactamente $50,000")
    ])
    submit = SubmitField('Recargar Tarjeta')
    
    def validate_cedula(self, cedula):
        # Check if a card with this cedula exists
        card = CinemasCard.query.filter_by(cedula=cedula.data).first()
        if not card:
            raise ValidationError('No existe una tarjeta con esta cédula.')

class ReservationForm(FlaskForm):
    cedula = StringField('Cédula', validators=[
        DataRequired(message="La cédula es obligatoria"),
        Regexp(r'^\d{6,12}$', message="La cédula debe contener entre 6 y 12 dígitos numéricos")
    ])
    selected_seats = HiddenField('Asientos Seleccionados', validators=[
        DataRequired(message="Debe seleccionar al menos un asiento")
    ])
    submit = SubmitField('Crear Reserva')
    
    def validate_selected_seats(self, selected_seats):
        # Check if the number of selected seats is not more than 8
        seats_list = selected_seats.data.split(',')
        if len(seats_list) > 8:
            raise ValidationError('No puede reservar más de 8 asientos.')
        
        # Check if all selected seats are available
        for seat_id in seats_list:
            if seat_id:  # Skip empty strings
                seat = Seat.query.get(int(seat_id))
                if not seat or seat.status != SeatStatus.AVAILABLE.value:
                    raise ValidationError(f'El asiento {seat.row}{seat.number} no está disponible.')

class CancelReservationForm(FlaskForm):
    cedula = StringField('Cédula', validators=[
        DataRequired(message="La cédula es obligatoria"),
        Regexp(r'^\d{6,12}$', message="La cédula debe contener entre 6 y 12 dígitos numéricos")
    ])
    submit = SubmitField('Cancelar Reserva')

class PaymentForm(FlaskForm):
    cedula = StringField('Cédula', validators=[
        DataRequired(message="La cédula es obligatoria"),
        Regexp(r'^\d{6,12}$', message="La cédula debe contener entre 6 y 12 dígitos numéricos")
    ])
    payment_method = SelectField('Método de Pago', choices=[
        ('cash', 'Efectivo'),
        ('card', 'Tarjeta CINEMAS')
    ], validators=[DataRequired(message="Debe seleccionar un método de pago")])
    submit = SubmitField('Realizar Pago')

class CancelPaymentForm(FlaskForm):
    cedula = StringField('Cédula', validators=[
        DataRequired(message="La cédula es obligatoria"),
        Regexp(r'^\d{6,12}$', message="La cédula debe contener entre 6 y 12 dígitos numéricos")
    ])
    transaction_id = IntegerField('ID de Transacción', validators=[
        DataRequired(message="El ID de transacción es obligatorio")
    ])
    reason = StringField('Motivo', validators=[
        DataRequired(message="El motivo es obligatorio"),
        Length(min=5, max=200, message="El motivo debe tener entre 5 y 200 caracteres")
    ])
    submit = SubmitField('Anular Pago')
