from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MessageSend, OTPCodeSend ,Authentication, SessionList, MessageViewSet, ChatRoomViewSet, PaymentCreate, PaymentCallback

app_name = 'drfchelseru'

router = DefaultRouter()
router.register(r'chatrooms', ChatRoomViewSet, basename='chatroom')
router.register(r'messages', MessageViewSet, basename='messages')

urlpatterns = [
    path('message/send/', MessageSend.as_view(), name='message-send'),
    path('otp/send/', OTPCodeSend.as_view(), name='otp-send'),
    path('authenticate/', Authentication.as_view(), name='auth'),
    path('sessions/', SessionList.as_view(), name='sessions'),

    path('payment/create/', PaymentCreate.as_view(), name='payment-create'),
    path('payment/callback/', PaymentCallback.as_view(), name='payment-callback'),
] + [path('chat/', include(router.urls)),]
