from django.urls import path
from .views import GetBestResponseView  # Asegúrate de que sea la clase

urlpatterns = [
    path('consulta_instruccion/', GetBestResponseView.as_view(), name='consulta_instruccion'),
]
