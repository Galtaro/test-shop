from django.urls import path
from product.views import ListApiItem, RetrieveApiItem, ListApiBucket, CreateApiBucketItem, \
    RetrieveApiBucketItem, UpdateDestroyApiBucketItem, CreateApiItem, UpdateDestroyApiItem, UpdateApiDiscount, \
    UpdateDestroyApiPromocode, ListCreateApiPromocode, UpdateApiBucketPromocodeTotalPrice, \
    ListCreateApiCashback, UpdateApiCashback, CreateApiCheckout, ApiCashbackPayment


app_name = "Product"

urlpatterns = [
    path('items/', ListApiItem.as_view(), name="list-item"),
    path('items/<int:pk>/', RetrieveApiItem.as_view(), name="retrieve-item"),
    path('items/create_item/', CreateApiItem.as_view(), name="create-item"),
    path('items/<int:pk>/update_destroy_item/', UpdateDestroyApiItem.as_view(), name="update-destroy-item"),
    path('items/<int:pk>/add_to_bucket/', CreateApiBucketItem.as_view(), name="create-bucket-item"),
    path('items/<int:pk>/update_discount/', UpdateApiDiscount.as_view(), name="update-item-discount"),
    path('bucket/', ListApiBucket.as_view(), name="list-bucket-item"),
    path('bucket/items/<int:pk>/', RetrieveApiBucketItem.as_view(), name="retrieve-item-bucket"),
    path('bucket/items/<int:pk>/update_destroy_bucket_item/', UpdateDestroyApiBucketItem.as_view(), name="update-destroy-bucket-item"),
    path('bucket/add_promocode/', UpdateApiBucketPromocodeTotalPrice.as_view(), name="update-bucket-promocode-total-price"),
    path('bucket/create_checkout/', CreateApiCheckout.as_view(), name="create-checkout"),
    path('bucket/cashback/', ApiCashbackPayment.as_view(), name="cashback-payment"),
    path('promocode/', ListCreateApiPromocode.as_view(), name="list-create-promocode"),
    path('promocode/<int:pk>/update_destroy_promocode/', UpdateDestroyApiPromocode.as_view(), name="update-destroy-promocode"),
    path('cashback/', ListCreateApiCashback.as_view(), name="list-create-cashback"),
    path('cashback/<int:pk>/update_cashback/', UpdateApiCashback.as_view(), name="update-cashback"),
]