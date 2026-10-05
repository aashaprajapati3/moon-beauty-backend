
from django.urls import path
from .views import AdminLogoutView
from .views import (
    BookingListCreateView,
    BookingAvailabilityView,
    AdminBookingListView,
    AdminBookingStatusView,
    AdminLoginView,
)

urlpatterns = [
    path('', BookingListCreateView.as_view(), name='booking-list-create'),

    path(
        'availability/',
        BookingAvailabilityView.as_view(),
        name='booking-availability'
    ),

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
    )   ]
