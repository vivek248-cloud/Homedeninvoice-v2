from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import *

admin.site.register(Client)
admin.site.register(Project)
admin.site.register(FloorType)
admin.site.register(RoomType)
admin.site.register(FullSemi)
admin.site.register(Spend)
admin.site.register(Payment)
