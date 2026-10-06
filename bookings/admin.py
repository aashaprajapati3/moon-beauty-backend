
from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'phone',
        'service',
        'date',
        'time',
        'status',
    )

    list_filter = ('status', 'service', 'date')
    search_fields = ('name', 'phone')
    ordering = ('-created_at',)

    list_editable = ('status',)
