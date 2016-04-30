from django.conf.urls import url
from .views import IndexView, UserUpdateView

urlpatterns = [
    url(r'^$', IndexView.as_view(), name='chat-index'),
    url(r'^accounts/update/$', UserUpdateView.as_view(), name='user-update')
]
