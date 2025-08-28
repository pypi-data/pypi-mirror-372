from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin): #Userprofile registreren in de admin en de velden tonen (welke kolommen) #TODO list filtering?
    list_display = ("user", "display_name", "updated_at")
