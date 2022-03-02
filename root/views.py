from django.contrib.auth import authenticate, login, logout
from rest_framework.generics import CreateAPIView, ListAPIView, GenericAPIView
from rest_framework.permissions import IsAuthenticated
from root.serializers import CreateUserSerializer, AccountOrdersSerializer, LoginUserSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from product.models import Bucket, Order
from root.utils.account import count_amount_of_accrued_cashback


class Register(CreateAPIView):
    serializer_class = CreateUserSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        user_id = response.data['id']
        bucket = Bucket.objects.get(owner_id=user_id)
        response.set_cookie("bucket", bucket.id)
        return response


class Login(GenericAPIView):
    serializer_class = LoginUserSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data["username"]
        password = serializer.validated_data["password_1"]
        user = authenticate(username=username, password=password)
        if user is None:
            return Response("user with this credential doesn't exist ")
        login(request, user)
        return Response("authenticate successful", status=status.HTTP_200_OK)


class Logout(APIView):
    def post(self, request):
        logout(request)
        return Response("logout successful", status=status.HTTP_200_OK)


class AccountOrdersAPI(ListAPIView):
    serializer_class = AccountOrdersSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Order.objects.filter(account=user)
        return queryset


class AccountOrdersPayAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, **kwargs):
        order_id = kwargs["pk"]
        user = request.user
        order = Order.objects.get(id=order_id)
        if order.payment_status:
            return Response("This order has already been paid.", status=status.HTTP_406_NOT_ACCEPTABLE)
        count_amount_of_accrued_cashback(user=user, order=order)
        return Response("Payment completed successfully", status=status.HTTP_200_OK)


