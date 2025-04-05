from typing import List, Optional
from django.utils import timezone
from api.payment.models.Payment import Payment, PaymentStatus
from api.payment.repositories.RepositoryPayment import RepositoryPayment

class ServicesPayment:
    """
    Implementation of the Payment service.
    Provides business logic to manage payments.
    """

    def __init__(self):
        self.repository = RepositoryPayment()

    def create_payment(self, payment_data: dict) -> Payment:
        """
        Creates a new payment with business validations.
        """
        # Ensures that the payment date is present
        if 'date_payment' not in payment_data:
            payment_data['date_payment'] = timezone.now().date()

        # Validates the payment status
        if 'status' in payment_data and payment_data['status'] not in dict(PaymentStatus.choices):
            raise ValueError(f"Invalid payment status. Valid options: {', '.join(dict(PaymentStatus.choices).keys())}")

        # Validates that the amount is positive
        if float(payment_data.get('value', 0)) <= 0:
            raise ValueError("The payment amount must be greater than zero")

        # If there is a bonus, validates that it is positive
        if 'bonus' in payment_data and payment_data['bonus'] is not None:
            if float(payment_data['bonus']) < 0:
                raise ValueError("The bonus cannot be negative")

        return self.repository.create(payment_data)

    def get_payment(self, payment_id: int) -> Optional[Payment]:
        """
        Gets a payment by its ID.
        """
        return self.repository.get(payment_id)

    def list_payments(self) -> List[Payment]:
        """
        Lists all payments.
        """
        return self.repository.list()

    def update_payment(self, payment_id: int, payment_data: dict) -> Optional[Payment]:
        """
        Updates a payment with business validations.
        """
        print(f'INTO UPDATE PAYMENT ServicesPayment {payment_data}')
        # Gets the existing payment
        existing_payment = self.repository.get(payment_id)
        if not existing_payment:
            return None

        # Validates that no field can be modified if the payment is completed
        if existing_payment.status == PaymentStatus.COMPLETED:
            raise ValueError("Cannot modify a payment that is already completed")

        # Validates the new status if provided
        if 'status' in payment_data:
            if payment_data['status'] not in dict(PaymentStatus.choices):
                raise ValueError(f"Invalid payment status. Valid options: {', '.join(dict(PaymentStatus.choices).keys())}")

        # Validates the amount if provided
        if 'Value' in payment_data:
            if float(payment_data['Value']) <= 0:
                raise ValueError("The payment amount must be greater than zero")

        # Validates the bonus if provided
        if 'bonus' in payment_data and payment_data['bonus'] is not None:
            if float(payment_data['bonus']) < 0:
                raise ValueError("The bonus cannot be negative")

        return self.repository.update(payment_id, payment_data)

    def delete_payment(self, payment_id: int) -> bool:
        """
        Deletes a payment if possible.
        """
        # Gets the existing payment
        existing_payment = self.repository.get(payment_id)
        if not existing_payment:
            return False

        # Does not allow deleting completed payments
        if existing_payment.status == PaymentStatus.COMPLETED:
            raise ValueError("Cannot delete completed payments")

        return self.repository.delete(payment_id)
