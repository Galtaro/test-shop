from rest_framework.generics import CreateAPIView, GenericAPIView
from root.serializers import CreateUserSerializer, LoginUserSerializer
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import login, authenticate, logout
from rest_framework.views import APIView
from product.models import Bucket


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
