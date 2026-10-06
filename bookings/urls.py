from django.urls import path

from .views import (
    BookingListCreateView,
    BookingAvailabilityView,
    CustomerCancelBookingView,
    CustomerRescheduleBookingView,
    AdminBookingListView,
    AdminBookingStatusView,
    AdminLoginView,
    AdminLogoutView,
)


urlpatterns = [

    path(
        '',
        BookingListCreateView.as_view(),
        name='booking-list-create'
    ),

    path(
        'availability/',
        BookingAvailabilityView.as_view(),
        name='booking-availability'
    ),

    # Customer booking management
    path(
        'customer/cancel/',
        CustomerCancelBookingView.as_view(),
        name='customer-cancel-booking'
    ),

    path(
        'customer/reschedule/',
        CustomerRescheduleBookingView.as_view(),
        name='customer-reschedule-booking'
    ),

    # Admin
    path(
        'admin/login/',
        AdminLoginView.as_view(),
        name='admin-login'
    ),

    path(
        'admin/',
        AdminBookingListView.as_view(),
        name='admin-booking-list'
    ),

    path(
        'admin/<int:pk>/status/',
        AdminBookingStatusView.as_view(),
        name='admin-booking-status'
    ),

    path(
        'admin/logout/',
        AdminLogoutView.as_view(),
        name='admin-logout'
    ),
]