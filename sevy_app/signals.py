from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CarBooking, Trip, Transaction, PlatformCommission

@receiver(post_save, sender=CarBooking)
def cancel_related_booking_records(sender, instance, **kwargs):
    if instance.status == 'cancelled':
        # Cancel related transactions
        Transaction.objects.filter(
            related_id=instance.booking_id,
            status__in=['pending', 'waitingapproval', 'wait_approval']
        ).update(status='cancelled')
        
        # Cancel related platform commissions
        PlatformCommission.objects.filter(
            related_id=instance.booking_id,
            status='pending'
        ).update(status='cancelled')

@receiver(post_save, sender=Trip)
def cancel_related_trip_records(sender, instance, **kwargs):
    if instance.status == 'cancelled':
        # Cancel related transactions
        Transaction.objects.filter(
            related_id=instance.trip_id,
            status__in=['pending', 'waitingapproval', 'wait_approval']
        ).update(status='cancelled')
        
        # Cancel related platform commissions
        PlatformCommission.objects.filter(
            related_id=instance.trip_id,
            status='pending'
        ).update(status='cancelled')
