from typing import List, Optional
from api.payment.models.Payment import Payment

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

  
      