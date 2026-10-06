from rest_framework import serializers
from .models import Booking


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking

        fields = [
            'id',
            'name',
            'phone',
            'service',
            'date',
            'time',
            'address',
            'status',
            'cancellation_reason',
            'reschedule_reason',
            'created_at',
            'updated_at',
        ]

        read_only_fields = [
            'id',
            'status',
            'created_at',
            'updated_at',
        ]

        validators = []

    def validate_phone(self, value):
        if not value.isdigit() or len(value) != 10:
            raise serializers.ValidationError(
                "Enter a valid 10-digit phone number."
            )

        return value

    def validate(self, attrs):
        date = attrs.get('date')
        time = attrs.get('time')

        if date and time:
            existing_booking = Booking.objects.filter(
                date=date,
                time=time,
                status__in=['Pending', 'Confirmed']
            ).exists()

            if existing_booking:
                raise serializers.ValidationError({
                    'time': (
                        "This time slot is already booked. "
                        "Please select another time."
                    )
                })

        return attrs