from django.urls import path
from . import views

app_name = 'donations'

urlpatterns = [
    # Page views
    path("my-listings/", views.my_listings, name="my_listings"),
    path("pending-requests/", views.pending_requests, name="pending_requests"),

    # Actions
    path("add/", views.add_listing, name="add_listing"),
    path("delete/", views.delete_listing, name="delete_listing"),
    path("request/", views.request_book, name="request_book"),
    path("cancel/", views.cancel_request, name="cancel_request"),
    path("approve/", views.approve_donation, name="approve_donation"),
    path("reject/", views.reject_donation, name="reject_donation"),
]