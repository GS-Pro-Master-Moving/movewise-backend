from django.db import models
from api.operator.models.Operator import Operator
from api.order.models.Order import Order
from api.truck.models.Truck import Truck
from api.payment.models.Payment import Payment
from django.utils import timezone
from django.db.models.signals import pre_delete
from django.dispatch import receiver

class Assign(models.Model):
    """
    Model that represents an assignment between an operator, order, truck and payment.
    """
    operator = models.ForeignKey(
        Operator, 
        on_delete=models.CASCADE, 
        related_name="assignments"
    )
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name="assignments"
    )
    truck = models.ForeignKey(
        Truck, 
        on_delete=models.CASCADE, 
        related_name="assignments", 
        null=True, 
        blank=True
    )
    payment = models.ForeignKey(
        Payment,
        on_delete=models.SET_NULL,
        related_name="assignments",
        null=True,
        blank=True
    )
    assigned_at = models.DateField(null=True, blank=True)
    rol = models.CharField(max_length=100, null=True, blank=True)
    additional_costs = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    
    class Meta:
        db_table = 'api_assign'
        #unique_together = ('operator', 'order', 'truck')
        app_label = 'api'

    def __str__(self):
        return f"{self.operator} assigned to {self.order} with {self.truck}"
    
    def save(self, *args, **kwargs):
        """
        Overrides the save method to ensure changes are recorded
        in the audit table
        """
        is_new = self._state.adding

        if is_new:
            # Usar timezone.now().date() para obtener solo la fecha
            self.assigned_at = self.assigned_at or timezone.now().date()
            # Primero guardamos la nueva asignación
            super().save(*args, **kwargs)
        else:
            # Si es una actualización, obtenemos la instancia actual
            try:
                old_instance = Assign.objects.get(pk=self.pk)
                old_values = {
                    'operator': old_instance.operator,
                    'order': old_instance.order,
                    'truck': old_instance.truck,
                    'payment': old_instance.payment,
                    'assigned_at': old_instance.assigned_at,
                    'rol': old_instance.rol
                }
                
                # Guardamos los cambios
                super().save(*args, **kwargs)
                
                # Comparamos los valores para ver si hubo cambios
                new_values = {
                    'operator': self.operator,
                    'order': self.order,
                    'truck': self.truck,
                    'payment': self.payment,
                    'assigned_at': self.assigned_at,
                    'rol': self.rol
                }

                # Solo creamos un registro si algo cambió
                if any(old_values[field] != new_values[field] for field in old_values):
                    # Convertir dates a datetime para el audit
                    old_assigned_at_dt = None
                    new_assigned_at_dt = None
                    
                    if old_values['assigned_at']:
                        old_assigned_at_dt = timezone.make_aware(
                            timezone.datetime.combine(old_values['assigned_at'], timezone.datetime.min.time())
                        )
                    
                    if new_values['assigned_at']:
                        new_assigned_at_dt = timezone.make_aware(
                            timezone.datetime.combine(new_values['assigned_at'], timezone.datetime.min.time())
                        )
                    
                    AssignAudit.objects.create(
                        assign=self,
                        old_operator=old_values['operator'],
                        new_operator=new_values['operator'],
                        old_order=old_values['order'],
                        new_order=new_values['order'],
                        old_truck=old_values['truck'],
                        new_truck=new_values['truck'],
                        old_payment=old_values['payment'],
                        new_payment=new_values['payment'],
                        old_assigned_at=old_assigned_at_dt,
                        new_assigned_at=new_assigned_at_dt,
                        old_rol=old_values['rol'],
                        new_rol=new_values['rol']
                    )
            except Assign.DoesNotExist:
                # Si por alguna razón no encontramos la instancia, solo guardamos
                super().save(*args, **kwargs)

@receiver(pre_delete, sender=Assign)
def assign_pre_delete(sender, instance, **kwargs):
    """
    Signal handler to create an audit record before assign deletion
    """
    # Convertir date a datetime para el audit
    old_assigned_at_dt = None
    if instance.assigned_at:
        old_assigned_at_dt = timezone.make_aware(
            timezone.datetime.combine(instance.assigned_at, timezone.datetime.min.time())
        )
    
    AssignAudit.objects.create(
        assign=instance,
        old_operator=instance.operator,
        new_operator=None,
        old_order=instance.order,
        new_order=None,
        old_truck=instance.truck,
        new_truck=None,
        old_payment=instance.payment,
        new_payment=None,
        old_assigned_at=old_assigned_at_dt,
        new_assigned_at=None,
        old_rol=instance.rol,
        new_rol=None
    )

#audit assign
class AssignAudit(models.Model):
    """
    Model for auditing changes made to assignments.
    Records the history of modifications to the main assignment fields.
    """
    id = models.AutoField(
        primary_key=True,
        db_column='id_assign_audit'
    )
    assign = models.ForeignKey(Assign, on_delete=models.CASCADE, related_name='audit_records', db_column='id_assign', help_text="Assignment to which this audit record belongs")
    old_operator = models.ForeignKey(Operator, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_records_as_old_operator')
    new_operator = models.ForeignKey(Operator, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_records_as_new_operator')
    old_order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_records_as_old_order')
    new_order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_records_as_new_order')
    old_truck = models.ForeignKey(Truck, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_records_as_old_truck')
    new_truck = models.ForeignKey(Truck, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_records_as_new_truck')
    old_payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_records_as_old_payment')
    new_payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_records_as_new_payment')
    old_assigned_at = models.DateTimeField(null=True, blank=True)
    new_assigned_at = models.DateTimeField(null=True, blank=True)
    old_rol = models.CharField(max_length=100, null=True, blank=True)
    new_rol = models.CharField(max_length=100, null=True, blank=True)
    modified_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'api_assign_audit'
        #unique_together = ('assign',)
        app_label = 'api'
        ordering = ['-modified_at']

    def __str__(self):
        return f"Assign Audit#: {self.assign.id} - {self.modified_at}"