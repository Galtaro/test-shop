from django.urls import path
from root.views import Register, AccountOrdersAPI, AccountOrdersPayAPI, Login, Logout

urlpatterns = [
    path('register/', Register.as_view()),
    path('account/orders/', AccountOrdersAPI.as_view(), name="account-orders"),
    path('account/orders/<int:pk>/pay/', AccountOrdersPayAPI.as_view(), name="account-orders-pay"),
    path('login/', Login.as_view()),
    path('logout/', Logout.as_view())
]