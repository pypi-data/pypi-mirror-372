
from django.urls import re_path

from djpsa.halo import views

app_name = 'djpsa.halo'


urlpatterns = [
    re_path(
        r'^ticket/$',
        view=views.TicketCallBackView.as_view(),
        name='ticket_callback'
    ),
]
