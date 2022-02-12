from django.urls import path
from product.views import ListApiItem, RetrieveApiItem, BucketApi, AddBucketApi, DeleteBucketApiItem, \
    RetrieveApiBucketItem, UpdateBucketApiItem

app_name = "Product"
urlpatterns = [
    path('items/', ListApiItem.as_view(), name="list-item"),
    path('items/<int:pk>/', RetrieveApiItem.as_view(), name="retrieve-item"),
    path('bucket/', BucketApi.as_view(), name="bucket-item"),
    path('items/<int:pk>/add_to_bucket/', AddBucketApi.as_view(), name="add-bucket"),
    path('bucket/items/<int:pk>/', RetrieveApiBucketItem.as_view(), name="retrieve-item-bucket"),
    path('bucket/items/<int:pk>/delete/', DeleteBucketApiItem.as_view(), name="delete-item-bucket"),
    path('bucket/items/<int:pk>/update/', UpdateBucketApiItem.as_view(), name="update-item-bucket")
]