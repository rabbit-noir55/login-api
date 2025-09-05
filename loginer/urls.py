from django.urls import path
from .views import salom_view,salom_vie

urlpatterns = [
    path('log/', salom_view),
    path('salom/', salom_vie),
]
