from django.urls import path
from product.views import ListApiItem, RetrieveApiItem

app_name = "Product"
urlpatterns = [
    path('items/', ListApiItem.as_view(), name="list-item"),
    path('items/<int:pk>/', RetrieveApiItem.as_view(), name="retrieve-item")
]