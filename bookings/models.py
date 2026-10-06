from django.db import models
from django.db.models import Q


class Booking(models.Model):
    SERVICE_CHOICES = [
        # Makeup
        ('Engagement Makeup', 'Engagement Makeup'),
        ('Party Makeup', 'Party Makeup'),
        ('Bridal Makeup', 'Bridal Makeup'),
        ('Reception Makeup', 'Reception Makeup'),
        ('Siders Makeup', 'Siders Makeup'),
        ('HD Bridal Makeup', 'HD Bridal Makeup'),
        ('Airbrush Makeup', 'Airbrush Makeup'),
        ('Natural Makeup', 'Natural Makeup'),
        ('Cocktail Makeup', 'Cocktail Makeup'),
        ('Festive Makeup', 'Festive Makeup'),
        ('Baby Shower Makeup', 'Baby Shower Makeup'),
        ('Photoshoot Makeup', 'Photoshoot Makeup'),

        # Beauty
        ('Facial', 'Facial'),
        ('Eyebrow', 'Eyebrow'),
        ('Waxing', 'Waxing'),
        ('Manicure', 'Manicure'),
        ('Pedicure', 'Pedicure'),
        ('Manicure & Pedicure', 'Manicure & Pedicure'),

        # Hair
        ('Hair Styling', 'Hair Styling'),
        ('Hair Spa', 'Hair Spa'),

        # Mehendi
        ('Bridal Mehendi', 'Bridal Mehendi'),
        ('Engagement Mehendi', 'Engagement Mehendi'),
        ('Arabic Mehendi', 'Arabic Mehendi'),
        ('Minimal Mehendi', 'Minimal Mehendi'),
        ('Traditional Mehendi', 'Traditional Mehendi'),
        ('Feet Mehendi', 'Feet Mehendi'),
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