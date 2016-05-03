from django.conf.urls import url, include
from .views import IndexView, UserUpdateView
from .views_rest import MessageViewSet, TagViewSet
from rest_framework.routers import DefaultRouter

# Create a router and register our viewsets with it.
router = DefaultRouter(trailing_slash=False)
router.register(r'message', MessageViewSet)
router.register(r'tag', TagViewSet)

urlpatterns = [
    url(r'^$', IndexView.as_view(), name='chat-index'),
    url(r'^accounts/update/$', UserUpdateView.as_view(), name='user-update'),
    url(r'^api/', include(router.urls)),
]
