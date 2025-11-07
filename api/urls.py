

from django.urls import path

from .views import (
    LoginUser,
    RegisterUser,
    SmartLocationUVIndexView,
    SunExposureListCreate,
    SunExposureSummaryView,
    UVIndexView,
)


urlpatterns = [
    path("register/", RegisterUser.as_view(), name="register"),
    path("login/", LoginUser.as_view(), name="login"),
    path("sun_exposure/", SunExposureListCreate.as_view(), name="sun_exposure"),
    path("sun_exposure/summary/", SunExposureSummaryView.as_view(), name="sun_exposure_summary"),
    path("uv_index/<str:latitude>/<str:longitude>/", UVIndexView.as_view(), name="uv_index"),
    path(
        "smart_location_uv_index/",
        SmartLocationUVIndexView.as_view(),
        name="smart_location_uv_index",
    ),
]

