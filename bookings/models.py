from django.db import models
from django.db.models import Q


class Booking(models.Model):
    SERVICE_CHOICES = [
        ('Bridal Makeup', 'Bridal Makeup'),
        ('Party Makeup', 'Party Makeup'),
        ('Facial & Skincare', 'Facial & Skincare'),
        ('Hair Styling', 'Hair Styling'),
    ]

    TIME_CHOICES = [
        ('10:00 AM', '10:00 AM'),
        ('12:00 PM', '12:00 PM'),
        ('2:00 PM', '2:00 PM'),
        ('4:00 PM', '4:00 PM'),
        ('6:00 PM', '6:00 PM'),
    ]

    CANCELLATION_REASON_CHOICES = [
        ('Changed my plans', 'Changed my plans'),
        ('Found another service', 'Found another service'),
        ('Booked by mistake', 'Booked by mistake'),
        ('Not available at this time', 'Not available at this time'),
        ('Other', 'Other'),
    ]

    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=10)

    service = models.CharField(
        max_length=50,
        choices=SERVICE_CHOICES
    )

    date = models.DateField()

    time = models.CharField(
        max_length=20,
        choices=TIME_CHOICES
    )

    address = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=[
            ('Pending', 'Pending'),
            ('Confirmed', 'Confirmed'),
            ('Cancelled', 'Cancelled'),
        ],
        default='Pending'
    )

    cancellation_reason = models.CharField(
        max_length=100,
        choices=CANCELLATION_REASON_CHOICES,
        blank=True,
        default=''
    )

    reschedule_reason = models.TextField(
        blank=True,
        default=''
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['date', 'time'],
                condition=Q(
                    status__in=['Pending', 'Confirmed']
                ),
                name='unique_active_booking_time'
            )
        ]

    def __str__(self):
        return (
            f"{self.name} - "
            f"{self.service} ({self.date})"
        )