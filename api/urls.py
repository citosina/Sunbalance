

from django.urls import path
from .views import RegisterUser, LoginUser, SunExposureListCreate, UVIndexView, SmartLocationUVIndexView




urlpatterns = [
    path('register/', RegisterUser.as_view(), name='register'),
    path('login/', LoginUser.as_view(), name='login'),
    path('sun_exposure/', SunExposureListCreate.as_view(), name='sun_exposure'),  # Add this line
    path('uv_index/<str:latitude>/<str:longitude>/', UVIndexView.as_view(), name='uv_index'),
    path('smart_location_uv_index/', SmartLocationUVIndexView.as_view(), name='smart_location_uv_index'),
]

