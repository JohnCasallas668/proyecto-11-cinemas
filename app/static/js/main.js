/**
 * CineApp - Main JavaScript
 * 
 * This file contains the main JavaScript functionality for the CineApp application.
 * It includes functions for seat selection, form validation, and UI enhancements.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize seat selection if on reservation page
    if (document.querySelector('.seat-container')) {
        initializeSeatSelection();
    }
    
    // Initialize payment method selection if on payment page
    if (document.querySelector('.payment-option')) {
        initializePaymentSelection();
    }
    
    // Add animation to cards with card-hover class
    document.querySelectorAll('.card-hover').forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 10px 20px rgba(0, 0, 0, 0.1)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 0 0 rgba(0, 0, 0, 0.1)';
        });
    });
    
    // Add fade-out to alert messages after 5 seconds
    document.querySelectorAll('.alert:not(.alert-permanent)').forEach(alert => {
        setTimeout(() => {
            alert.classList.add('fade');
            setTimeout(() => {
                alert.remove();
            }, 500);
        }, 5000);
    });
});

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Initialize seat selection functionality
 */
function initializeSeatSelection() {
    // Variables
    const maxSeats = 8;
    let selectedSeats = [];
    const selectedSeatsInput = document.getElementById('selectedSeatsInput');
    const selectedSeatsList = document.getElementById('selectedSeatsList');
    const totalSeatsElement = document.getElementById('totalSeats');
    const totalPriceElement = document.getElementById('totalPrice');
    const submitButton = document.getElementById('submitReservation');
    const maxSeatsWarning = document.getElementById('maxSeatsWarning');
    
    if (!selectedSeatsInput || !selectedSeatsList) return;
    
    // Add click event to all available seats
    document.querySelectorAll('.seat-available').forEach(seat => {
        seat.addEventListener('click', function() {
            const seatId = this.dataset.seatId;
            const seatRow = this.dataset.seatRow;
            const seatNumber = this.dataset.seatNumber;
            const seatType = this.dataset.seatType;
            const seatPrice = parseInt(this.dataset.seatPrice);
            
            // Check if seat is already selected
            const seatIndex = selectedSeats.findIndex(s => s.id === seatId);
            
            if (seatIndex === -1) {
                // Add seat if not already selected and not exceeding max seats
                if (selectedSeats.length < maxSeats) {
                    selectedSeats.push({
                        id: seatId,
                        row: seatRow,
                        number: seatNumber,
                        type: seatType,
                        price: seatPrice
                    });
                    this.classList.add('seat-selected');
                    this.classList.remove('seat-available');
                    
                    // Hide warning if it was shown
                    if (maxSeatsWarning) {
                        maxSeatsWarning.style.display = 'none';
                    }
                } else {
                    // Show warning if exceeding max seats
                    if (maxSeatsWarning) {
                        maxSeatsWarning.style.display = 'block';
                        setTimeout(() => {
                            maxSeatsWarning.style.display = 'none';
                        }, 3000);
                    }
                }
            } else {
                // Remove seat if already selected
                selectedSeats.splice(seatIndex, 1);
                this.classList.remove('seat-selected');
                this.classList.add('seat-available');
                
                // Hide warning if it was shown
                if (maxSeatsWarning) {
                    maxSeatsWarning.style.display = 'none';
                }
            }
            
            updateSummary();
        });
    });
    
    // Update reservation summary
    function updateSummary() {
        // Update hidden input
        selectedSeatsInput.value = selectedSeats.map(seat => seat.id).join(',');
        
        // Update selected seats list
        if (selectedSeats.length === 0) {
            selectedSeatsList.innerHTML = `
                <li class="list-group-item text-center text-muted">
                    <em>No hay asientos seleccionados</em>
                </li>
            `;
        } else {
            selectedSeatsList.innerHTML = '';
            selectedSeats.forEach(seat => {
                selectedSeatsList.innerHTML += `
                    <li class="list-group-item d-flex justify-content-between align-items-center">
                        <div>
                            <span class="badge bg-${seat.type === 'General' ? 'success' : 'primary'} me-2">${seat.row}${seat.number}</span>
                            ${seat.type}
                        </div>
                        <span>$${seat.price.toLocaleString()}</span>
                    </li>
                `;
            });
        }
        
        // Update totals
        const totalSeats = selectedSeats.length;
        const totalPrice = selectedSeats.reduce((sum, seat) => sum + seat.price, 0);
        
        if (totalSeatsElement) {
            totalSeatsElement.textContent = totalSeats;
        }
        
        if (totalPriceElement) {
            totalPriceElement.textContent = `$${totalPrice.toLocaleString()}`;
        }
        
        // Enable/disable submit button
        if (submitButton) {
            submitButton.disabled = totalSeats === 0;
        }
    }
}

/**
 * Initialize payment method selection
 */
function initializePaymentSelection() {
    const paymentOptions = document.querySelectorAll('.payment-option input[type="radio"]');
    
    paymentOptions.forEach(option => {
        option.addEventListener('change', function() {
            // Remove selection from all cards
            document.querySelectorAll('.payment-option .card').forEach(card => {
                card.classList.remove('border-success', 'border-primary');
                card.classList.add('border-secondary');
            });
            
            // Add selection to the selected card
            if (this.value === 'cash') {
                this.closest('.payment-option').querySelector('.card').classList.remove('border-secondary');
                this.closest('.payment-option').querySelector('.card').classList.add('border-success');
            } else {
                this.closest('.payment-option').querySelector('.card').classList.remove('border-secondary');
                this.closest('.payment-option').querySelector('.card').classList.add('border-primary');
            }
        });
    });
}
