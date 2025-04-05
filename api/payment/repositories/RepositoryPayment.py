from typing import List, Optional
from api.payment.models.Payment import Payment, PaymentAudit

class RepositoryPayment:
    def create(self, payment_data: dict) -> Payment:
        """
        Crea un nuevo registro de pago.
        """
        return Payment.objects.create(**payment_data)

    def get(self, payment_id: int) -> Optional[Payment]:
        """
        Obtiene un pago por su ID.
        """
        try:
            return Payment.objects.get(id_pay=payment_id)
        except Payment.DoesNotExist:
            return None

    def list(self) -> List[Payment]:
        """
        Obtiene todos los pagos registrados.
        """
        return list(Payment.objects.all())

    def update(self, payment_id: int, payment_data: dict) -> Optional[Payment]:
        """
        Actualiza un pago existente.
        """
        try:
            payment = Payment.objects.get(id_pay=payment_id)
            for key, value in payment_data.items():
                setattr(payment, key, value)
            payment.save()
            return payment
        except Payment.DoesNotExist:
            return None

    def delete(self, payment_id: int) -> bool:
        """
        Elimina un pago por su ID.
        """
        try:
            payment = Payment.objects.get(id_pay=payment_id)
            payment.delete()
            return True
        except Payment.DoesNotExist:
            return False

    def get_audit_history(self, payment_id: int) -> List[dict]:
        """
        Obtiene el historial de auditoría de un pago.
        """
        audit_records = PaymentAudit.objects.filter(payment_id=payment_id).order_by('-modified_at')
        return [
            {
                'id': record.id,
                'old_amount': record.old_amount,
                'new_amount': record.new_amount,
                'old_status': record.old_status,
                'new_status': record.new_status,
                'old_bonus': record.old_bonus,
                'new_bonus': record.new_bonus,
                'old_date_start': record.old_date_start,
                'new_date_start': record.new_date_start,
                'old_date_end': record.old_date_end,
                'new_date_end': record.new_date_end,
                'modified_by': record.modified_by.username if record.modified_by else None,
                'modified_at': record.modified_at
            }
            for record in audit_records
        ] 