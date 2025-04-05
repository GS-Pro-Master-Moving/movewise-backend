from django.db import models
from django.conf import settings
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
        Overrides the save method to ensure changes are recorded
        in the audit table
        """
        is_new = self._state.adding
        
        if is_new:
            self.date_payment = self.date_payment or timezone.now().date()
        
        # Save previous state if object exists
        if not is_new:
            old_instance = Payment.objects.get(pk=self.pk)
            old_values = {
                'value': old_instance.value,
                'status': old_instance.status,
                'bonus': old_instance.bonus,
                'date_start': old_instance.date_start,
                'date_end': old_instance.date_end
            }
        
        # Save payment
        super().save(*args, **kwargs)
        
        # Create audit record if not a new object
        if not is_new:
            new_values = {
                'value': self.value,
                'status': self.status,
                'bonus': self.bonus,
                'date_start': self.date_start,
                'date_end': self.date_end
            }
            
            # Only create record if there were changes
            if old_values != new_values:
                PaymentAudit.objects.create(
                    payment=self,
                    old_amount=old_values['value'],
                    new_amount=new_values['value'],
                    old_status=old_values['status'],
                    new_status=new_values['status'],
                    old_bonus=old_values['bonus'],
                    new_bonus=new_values['bonus'],
                    old_date_start=old_values['date_start'],
                    new_date_start=new_values['date_start'],
                    old_date_end=old_values['date_end'],
                    new_date_end=new_values['date_end']
                )

@receiver(pre_delete, sender=Payment)
def payment_pre_delete(sender, instance, **kwargs):
    """
    Signal handler to create an audit record before payment deletion
    """
    PaymentAudit.objects.create(
        payment=instance,
        old_amount=instance.value,
        new_amount=0,
        old_status=instance.status,
        new_status=PaymentStatus.DELETED,
        old_bonus=instance.bonus,
        new_bonus=0,
        old_date_start=instance.date_start,
        new_date_start=None,
        old_date_end=instance.date_end,
        new_date_end=None
    )

class PaymentAudit(models.Model):
    """
    Model for auditing changes made to payments.
    Records the history of modifications to the main payment fields.
    """
    id = models.AutoField(
        primary_key=True,
        db_column='id_payment_audit'
    )
    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name='audit_records',
        db_column='id_pay',
        help_text="Payment to which this audit record belongs"
    )
    old_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Previous value amount"
    )
    new_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="New value amount"
    )
    old_status = models.CharField(
        max_length=50,
        help_text="Previous payment status"
    )
    new_status = models.CharField(
        max_length=50,
        help_text="New payment status"
    )
    old_bonus = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Previous bonus value"
    )
    new_bonus = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="New bonus value"
    )
    old_date_start = models.DateField(
        null=True,
        blank=True,
        help_text="Previous start date"
    )
    new_date_start = models.DateField(
        null=True,
        blank=True,
        help_text="New start date"
    )
    old_date_end = models.DateField(
        null=True,
        blank=True,
        help_text="Previous end date"
    )
    new_date_end = models.DateField(
        null=True,
        blank=True,
        help_text="New end date"
    )
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        db_column='modified_by',
        help_text="User who made the modification"
    )
    modified_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time of modification"
    )

    class Meta:
        db_table = 'api_payment_audit'
        verbose_name = 'Payment Audit'
        verbose_name_plural = 'Payment Audits'
        app_label = 'api'
        ordering = ['-modified_at']

    def __str__(self):
        return f"Payment Audit #{self.payment.id_pay} - {self.modified_at}"