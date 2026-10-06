import json

from django.contrib.auth import logout, authenticate, login
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import (
    csrf_protect,
    ensure_csrf_cookie
)
from django.utils.decorators import method_decorator
from django.db import IntegrityError, transaction
from django.utils.dateparse import parse_date
from django.middleware.csrf import get_token
from django.utils import timezone

from rest_framework import generics, status
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAdminUser
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.exceptions import ValidationError

from .models import Booking
from .serializers import BookingSerializer


class BookingListCreateView(generics.ListCreateAPIView):
    queryset = Booking.objects.all().order_by('-created_at')
    serializer_class = BookingSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        if self.request.method == 'GET':
            booking_id = self.request.query_params.get('id')
            phone = self.request.query_params.get('phone')

            if not booking_id or not phone:
                return Booking.objects.none()

            return Booking.objects.filter(
                id=booking_id,
                phone=phone
            )

        return Booking.objects.all().order_by('-created_at')

    def perform_create(self, serializer):
        try:
            with transaction.atomic():
                serializer.save()

        except IntegrityError:
            raise ValidationError({
                'time': (
                    "This time slot is already booked. "
                    "Please select another time."
                )
            })


class BookingAvailabilityView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        date_value = request.query_params.get('date')

        if not date_value:
            return Response(
                {'error': 'Please provide a date.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        selected_date = parse_date(date_value)

        if selected_date is None:
            return Response(
                {
                    'error': (
                        'Invalid date. '
                        'Use YYYY-MM-DD.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        booked_times = list(
            Booking.objects.filter(
                date=selected_date,
                status__in=['Pending', 'Confirmed']
            )
            .values_list('time', flat=True)
            .distinct()
        )

        return Response({
            'booked_times': booked_times
        })


# --------------------------------------------------
# CUSTOMER CANCEL
# --------------------------------------------------

class CustomerCancelBookingView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        booking_id = request.data.get('id')
        phone = request.data.get('phone')
        reason = request.data.get(
            'reason',
            'Other'
        )

        if not booking_id or not phone:
            return Response(
                {
                    'error': (
                        'Booking ID and phone number are required.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            booking = Booking.objects.get(
                id=booking_id,
                phone=phone
            )

        except Booking.DoesNotExist:
            return Response(
                {
                    'error': (
                        'Booking not found. '
                        'Please check your details.'
                    )
                },
                status=status.HTTP_404_NOT_FOUND
            )

        if booking.status == 'Cancelled':
            return Response(
                {
                    'error': (
                        'This booking is already cancelled.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        booking.status = 'Cancelled'
        booking.cancellation_reason = reason

        booking.save(
            update_fields=[
                'status',
                'cancellation_reason',
                'updated_at'
            ]
        )

        return Response({
            'message': 'Booking cancelled successfully.',
            'booking': BookingSerializer(booking).data
        })


# --------------------------------------------------
# CUSTOMER RESCHEDULE
# --------------------------------------------------

class CustomerRescheduleBookingView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        booking_id = request.data.get('id')
        phone = request.data.get('phone')
        new_date = request.data.get('date')
        new_time = request.data.get('time')
        reason = request.data.get(
            'reason',
            ''
        )

        if not all([
            booking_id,
            phone,
            new_date,
            new_time
        ]):
            return Response(
                {
                    'error': (
                        'Booking ID, phone, date '
                        'and time are required.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            booking = Booking.objects.get(
                id=booking_id,
                phone=phone
            )

        except Booking.DoesNotExist:
            return Response(
                {
                    'error': 'Booking not found.'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        if booking.status == 'Cancelled':
            return Response(
                {
                    'error': (
                        'Cancelled bookings cannot be rescheduled.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        parsed_date = parse_date(str(new_date))

        if parsed_date is None:
            return Response(
                {
                    'error': (
                        'Invalid date. Use YYYY-MM-DD.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if parsed_date < timezone.localdate():
            return Response(
                {
                    'error': (
                        'Please select today or a future date.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        valid_times = [
            choice[0]
            for choice in Booking.TIME_CHOICES
        ]

        if new_time not in valid_times:
            return Response(
                {
                    'error': 'Please select a valid time slot.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        slot_taken = Booking.objects.filter(
            date=parsed_date,
            time=new_time,
            status__in=['Pending', 'Confirmed']
        ).exclude(
            id=booking.id
        ).exists()

        if slot_taken:
            return Response(
                {
                    'error': (
                        'This time slot is already booked. '
                        'Please select another time.'
                    )
                },
                status=status.HTTP_409_CONFLICT
            )

        try:
            with transaction.atomic():

                booking.date = parsed_date
                booking.time = new_time

                # Rescheduled booking goes back to Pending
                # so admin can confirm the new appointment.
                booking.status = 'Pending'

                booking.reschedule_reason = reason

                booking.save()

        except IntegrityError:
            return Response(
                {
                    'error': (
                        'This time slot was just booked. '
                        'Please select another time.'
                    )
                },
                status=status.HTTP_409_CONFLICT
            )

        return Response({
            'message': (
                'Booking rescheduled successfully. '
                'Waiting for confirmation.'
            ),
            'booking': BookingSerializer(booking).data
        })


# --------------------------------------------------
# ADMIN
# --------------------------------------------------

class AdminBookingListView(ListAPIView):
    queryset = Booking.objects.all().order_by('-created_at')
    serializer_class = BookingSerializer
    permission_classes = [IsAdminUser]


class AdminBookingStatusView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):

        try:
            booking = Booking.objects.get(pk=pk)

        except Booking.DoesNotExist:
            return Response(
                {
                    'error': 'Booking not found.'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        new_status = request.data.get('status')

        if new_status not in [
            'Confirmed',
            'Cancelled'
        ]:
            return Response(
                {
                    'error': (
                        'Status must be '
                        'Confirmed or Cancelled.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if booking.status == 'Cancelled':
            return Response(
                {
                    'error': (
                        'This booking is already cancelled.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        booking.status = new_status

        if new_status == 'Confirmed':
            booking.reschedule_reason = ''

        booking.save(
            update_fields=[
                'status',
                'reschedule_reason',
                'updated_at'
            ]
        )

        return Response({
            'message': (
                f'Booking {new_status.lower()} successfully.'
            ),
            'booking': BookingSerializer(booking).data
        })


# --------------------------------------------------
# ADMIN LOGIN
# --------------------------------------------------

@method_decorator(
    ensure_csrf_cookie,
    name="dispatch"
)
@method_decorator(
    csrf_protect,
    name="dispatch"
)
class AdminLoginView(View):

    def get(self, request):
        csrf_token = get_token(request)

        return JsonResponse({
            "csrf_token": csrf_token
        })

    def post(self, request):

        try:
            data = json.loads(request.body)

        except json.JSONDecodeError:
            return JsonResponse(
                {
                    "error": "Invalid request."
                },
                status=400
            )

        username = data.get(
            "username",
            ""
        ).strip()

        password = data.get(
            "password",
            ""
        )

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is None or not user.is_staff:
            return JsonResponse(
                {
                    "error": (
                        "Invalid admin credentials."
                    )
                },
                status=401
            )

        login(request, user)

        return JsonResponse({
            "message": "Login successful."
        })


class AdminLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)

        return Response({
            "message": "Logged out successfully"
        })