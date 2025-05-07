from django.db import models
from django.utils import timezone
from django.db.models.signals import pre_delete
from django.dispatch import receiver

class PaymentStatus(models.TextChoices):
    """
    Enumeration of possible payment statuses
    """
    PENDING = 'pending', 'Pending'
    COMPLETED = 'completed', 'Completed'
    FAILED = 'failed', 'Failed'
    REFUNDED = 'refunded', 'Refunded'
    CANCELLED = 'cancelled', 'Cancelled'
    DELETED = 'deleted', 'Deleted'

class Payment(models.Model):
    """
    Model that represents a payment in the system.
    """
    id_pay = models.AutoField(primary_key=True, unique=True)
    value = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        null=False,
        blank=False
    )
    date_payment = models.DateTimeField(
        null=True,
        blank=True
    )
    bonus = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    status = models.CharField(
        max_length=50
    )
    date_start = models.DateField(
        null=True,
        blank=True
    )
    date_end = models.DateField(
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'api_payment'
        app_label = 'api'

    def __str__(self):
        return f"Payment #{self.id_pay} - ${self.value}"

    def save(self, *args, **kwargs):
        """
        Overrides the save method to set the payment date.
        """
        is_new = self._state.adding
        
        if is_new:
            self.date_payment = self.date_payment or timezone.now().date()
        
        # Save payment
        super().save(*args, **kwargs)

@receiver(pre_delete, sender=Payment)
def payment_pre_delete(sender, instance, **kwargs):
    """
    Signal handler before payment deletion
    """
    pass  # No audit record is created