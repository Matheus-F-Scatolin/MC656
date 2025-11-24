from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST

from .models import DonationListing, DonationStatus
from books.models import Book

@login_required
def my_listings(request):
    listings = DonationListing.objects.filter(donor=request.user, status__in=('A','P')).order_by('-status', '-added_at')
    return render(request, 'donations/my_listings.html', {'listings': listings})


@login_required
def pending_requests(request):
    listings = DonationListing.objects.filter(
        requester=request.user,
        status=DonationStatus.PENDING
    )
    return render(request, 'donations/pending_requests.html', {'listings': listings})


@login_required
@require_POST
def add_listing(request):
    book_id = request.POST.get("book_id")
    book = get_object_or_404(Book, id=book_id)

    try:
        DonationListing.add_listing(book, request.user)
    except IntegrityError as e:
        pass  # let the user believe it's the first time they're doing this...

    return redirect('donations:my_listings')


@login_required
@require_POST
def delete_listing(request):
    book_id = request.POST.get("book_id")
    book = get_object_or_404(Book, id=book_id)

    DonationListing.objects.filter(book=book, donor=request.user).delete()
    return redirect('donations:my_listings')


@login_required
@require_POST
def request_book(request):
    listing_id = request.POST.get("listing_id")
    listing = get_object_or_404(DonationListing, id=listing_id)

    listing.request_donation(request.user)

    return redirect('donations:pending_requests')

@login_required
@require_POST
def cancel_request(request):
    listing_id = request.POST.get("listing_id")
    listing = get_object_or_404(DonationListing, id=listing_id)
    listing.cancel_donation(request.user)

    return redirect('donations:pending_requests')

@login_required
@require_POST
def approve_donation(request):
    listing_id = request.POST.get("listing_id")
    listing = get_object_or_404(DonationListing, id=listing_id, donor=request.user)

    listing.approve_donation()
    listing.save()

    redirect('donations:my_listings')


@login_required
@require_POST
def reject_donation(request):
    listing_id = request.POST.get("listing_id")
    listing = get_object_or_404(DonationListing, id=listing_id, donor=request.user)

    listing.reject_donation()
    listing.save()

    return redirect('donations:my_listings')
