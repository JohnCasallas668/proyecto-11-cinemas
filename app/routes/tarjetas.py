from flask import Blueprint, render_template, redirect, url_for, flash, request
from app import db
from app.models import CinemasCard
from app.forms import CinemasCardForm, RechargeCardForm

tarjetas_bp = Blueprint('tarjetas', __name__, url_prefix='/tarjetas')

@tarjetas_bp.route('/crear', methods=['GET', 'POST'])
def crear_tarjeta():
    """Create a new CINEMAS card"""
    form = CinemasCardForm()
    
    if form.validate_on_submit():
        # Create a new card
        nueva_tarjeta = CinemasCard(
            nombre=form.nombre.data,
            apellido=form.apellido.data,
            cedula=form.cedula.data,
            balance=form.saldo_inicial.data
        )
        
        try:
            db.session.add(nueva_tarjeta)
            db.session.commit()
            flash(f'Tarjeta CINEMAS creada exitosamente para {nueva_tarjeta.nombre} {nueva_tarjeta.apellido}', 'success')
            return redirect(url_for('tarjetas.ver_tarjeta', cedula=nueva_tarjeta.cedula))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear la tarjeta: {str(e)}', 'danger')
    
    return render_template('tarjetas/crear_tarjeta.html', form=form)

@tarjetas_bp.route('/recargar', methods=['GET', 'POST'])
def recargar_tarjeta():
    """Recharge a CINEMAS card"""
    form = RechargeCardForm()
    
    if form.validate_on_submit():
        # Find the card
        tarjeta = CinemasCard.query.filter_by(cedula=form.cedula.data).first()
        
        if tarjeta and tarjeta.active:
            # Update balance
            tarjeta.balance += form.monto.data
            
            try:
                db.session.commit()
                flash(f'Tarjeta recargada exitosamente. Nuevo saldo: ${tarjeta.balance:,.0f}', 'success')
                return redirect(url_for('tarjetas.ver_tarjeta', cedula=tarjeta.cedula))
            except Exception as e:
                db.session.rollback()
                flash(f'Error al recargar la tarjeta: {str(e)}', 'danger')
        else:
            flash('La tarjeta no existe o está inactiva', 'danger')
    
    return render_template('tarjetas/recargar_tarjeta.html', form=form)

@tarjetas_bp.route('/consultar', methods=['GET', 'POST'])
def consultar_tarjeta():
    """Search for a card by cedula"""
    cedula = request.args.get('cedula', '')
    
    if cedula:
        return redirect(url_for('tarjetas.ver_tarjeta', cedula=cedula))
    
    return render_template('tarjetas/consultar_tarjeta.html')

@tarjetas_bp.route('/ver/<cedula>')
def ver_tarjeta(cedula):
    """View details of a specific card"""
    tarjeta = CinemasCard.query.filter_by(cedula=cedula).first_or_404()
    return render_template('tarjetas/ver_tarjeta.html', tarjeta=tarjeta)
