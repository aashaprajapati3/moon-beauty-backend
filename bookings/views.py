import json
from django.contrib.auth import logout
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.db import IntegrityError, transaction
from django.utils.dateparse import parse_date

from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Booking
from .serializers import BookingSerializer
from rest_framework.permissions import IsAdminUser
from rest_framework.generics import ListAPIView

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
                {'error': 'Invalid date. Use YYYY-MM-DD.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        booked_times = list(
            Booking.objects.filter(
                date=selected_date,
                status__in=['Pending', 'Confirmed']
            ).values_list('time', flat=True).distinct()
        )

        return Response({'booked_times': booked_times})


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
                {'error': 'Booking not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        new_status = request.data.get('status')

        if new_status not in ['Confirmed', 'Cancelled']:
            return Response(
                {'error': 'Status must be Confirmed or Cancelled.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if booking.status == 'Cancelled':
            return Response(
                {'error': 'This booking is already cancelled.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        booking.status = new_status
        booking.save(update_fields=['status'])

        return Response({
            'message': f'Booking {new_status.lower()} successfully.',
            'booking': BookingSerializer(booking).data
        })
@method_decorator(ensure_csrf_cookie, name="dispatch")
@method_decorator(csrf_protect, name="dispatch")
class AdminLoginView(View):
    def get(self, request):
        return JsonResponse({"message": "CSRF cookie set."})

    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse(
                {"error": "Invalid request."},
                status=400
            )

        username = data.get("username", "").strip()
        password = data.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is None or not user.is_staff:
            return JsonResponse(
                {"error": "Invalid admin credentials."},
                status=401
            )

        login(request, user)

        return JsonResponse({"message": "Login successful."})

class AdminLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({
            "message": "Logged out successfully"
        })