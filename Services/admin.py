from django.contrib import admin
from .models import WasteReport

@admin.register(WasteReport)
class WasteReportAdmin(admin.ModelAdmin):
    list_display = ('user', 'waste_type', 'estimate_amt', 'location', 'date_reported', 'collected')
    list_filter = ('collected', 'waste_type', 'date_reported')
    search_fields = ('user__username', 'waste_type', 'location')
