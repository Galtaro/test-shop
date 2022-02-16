from django.urls import path
from product.views import ListApiItem, RetrieveApiItem, BucketApi, AddBucketApi, DeleteBucketApiItem, \
    RetrieveApiBucketItem, UpdateBucketApiItem, AddApiItem, DeleteApiItem, UpdateApiItem, AddDiscountApi, \
    PromocodeApi, UpdatePromocodeApi, AddPromocodeApi, DeletePromocodeApi, UpdateBucketApiPromocodeTotalPrice


app_name = "Product"

urlpatterns = [
    path('items/', ListApiItem.as_view(), name="list-item"),
    path('items/<int:pk>/', RetrieveApiItem.as_view(), name="retrieve-item"),
    path('items/add_item/', AddApiItem.as_view(), name="add-item"),
    path('items/<int:pk>/delete/', DeleteApiItem.as_view(), name="delete-item"),
    path('items/<int:pk>/update/', UpdateApiItem.as_view(), name="update-item"),
    path('bucket/', BucketApi.as_view(), name="bucket-item"),
    path('items/<int:pk>/add_to_bucket/', AddBucketApi.as_view(), name="add-bucket"),
    path('bucket/items/<int:pk>/', RetrieveApiBucketItem.as_view(), name="retrieve-item-bucket"),
    path('bucket/items/<int:pk>/delete/', DeleteBucketApiItem.as_view(), name="delete-item-bucket"),
    path('bucket/items/<int:pk>/update/', UpdateBucketApiItem.as_view(), name="update-item-bucket"),
    path('bucket/promocode/', UpdateBucketApiPromocodeTotalPrice.as_view(), name="update-bucket-promocode-total-price"),
    path('items/<int:pk>/add_discount/', AddDiscountApi.as_view(), name="add-item-discount"),
    path('promocode/', PromocodeApi.as_view(), name="list-promocode"),
    path('promocode/add_promocode', AddPromocodeApi.as_view(), name="add-promocode"),
    path('promocode/<int:pk>/update/', UpdatePromocodeApi.as_view(), name="update-promocode"),
    path('promocode/<int:pk>/delete/', DeletePromocodeApi.as_view(), name="delete-promocode"),
]