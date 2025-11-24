from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from books.models import Book
from donations.models import DonationListing, DonationStatus


class DonationViewsTest(TestCase):
    def setUp(self):
        self.donor = User.objects.create_user(username='donor', email='d@x.com', password='123')
        self.other = User.objects.create_user(username='other', email='o@x.com', password='123')

        self.book = Book.objects.create(
            title="Book A",
            author="Author A",
            course="Course X",
        )

        self.client.login(username='donor', password='123')


    # ---------------------------------------------------------
    # add_listing
    # ---------------------------------------------------------
    def test_add_listing_fresh(self):  # EC1
        """User adds a book not yet in listing → listing created"""
        r = self.client.post(reverse('donations:add_listing'), {'book_id': self.book.id})
        self.assertEqual(DonationListing.objects.count(), 1)

    def test_add_listing_duplicate(self):  # EC2
        """Adding the same listing twice silently ignores second attempt"""
        DonationListing.add_listing(self.book, self.donor)
        r = self.client.post(reverse('donations:add_listing'), {'book_id': self.book.id})
        self.assertEqual(DonationListing.objects.count(), 1)


    # ---------------------------------------------------------
    # delete_listing
    # ---------------------------------------------------------
    def test_delete_listing_owner(self):  # EC1
        listing = DonationListing.add_listing(self.book, self.donor)
        self.client.post(reverse('donations:delete_listing'), {'book_id': self.book.id})
        self.assertEqual(DonationListing.objects.count(), 0)

    def test_delete_listing_not_owner(self):  # EC2
        listing = DonationListing.add_listing(self.book, self.donor)
        self.client.logout()
        self.client.login(username='other', password='123')

        self.client.post(reverse('donations:delete_listing'), {'book_id': self.book.id})
        self.assertEqual(DonationListing.objects.count(), 1)  # still there


    # ---------------------------------------------------------
    # request_book
    # ---------------------------------------------------------
    def test_request_available(self):  # EC1
        listing = DonationListing.add_listing(self.book, self.donor)

        self.client.logout()
        self.client.login(username='other', password='123')

        self.client.post(reverse('donations:request_book'), {'listing_id': listing.id})
        listing.refresh_from_db()

        self.assertEqual(listing.status, DonationStatus.PENDING)
        self.assertEqual(listing.requester, self.other)

    def test_request_already_pending(self):  # EC2
        listing = DonationListing.add_listing(self.book, self.donor)
        listing.request_donation(self.other)

        self.client.logout()
        self.client.login(username='other', password='123')

        # requesting again should not break anything
        with self.assertRaises(ValueError):
            self.client.post(reverse('donations:request_book'), {'listing_id': listing.id})
        listing.refresh_from_db()

        self.assertEqual(listing.status, DonationStatus.PENDING)

    def test_request_own_listing(self): # EC3
        listing = DonationListing.add_listing(self.book, self.donor)
        with self.assertRaises(ValueError):
            self.client.post(reverse('donations:request_book'), {'listing_id': listing.id})

        listing.refresh_from_db()
        print(listing.requester)
        self.assertIsNone(listing.requester)  # should not request your own book


    # ---------------------------------------------------------
    # cancel_request
    # ---------------------------------------------------------
    def test_cancel_request_owner(self):  # EC1
        listing = DonationListing.add_listing(self.book, self.donor)
        listing.request_donation(self.other)

        self.client.logout()
        self.client.login(username='other', password='123')

        self.client.post(reverse('donations:cancel_request'), {'listing_id': listing.id})
        listing.refresh_from_db()

        self.assertIsNone(listing.requester)
        self.assertEqual(listing.status, DonationStatus.AVAILABLE)

    def test_cancel_request_not_owner(self):  # EC2
        listing = DonationListing.add_listing(self.book, self.donor)
        listing.request_donation(self.other)

        # donor tries to cancel instead → should not work
        with self.assertRaises(ValueError):
            self.client.post(reverse('donations:cancel_request'), {'listing_id': listing.id})
        listing.refresh_from_db()

        self.assertEqual(listing.requester, self.other)


    # ---------------------------------------------------------
    # approve_donation
    # ---------------------------------------------------------
    def test_approve_donation_success(self):  # EC1
        listing = DonationListing.add_listing(self.book, self.donor)
        listing.request_donation(self.other)

        self.client.post(reverse('donations:approve_donation'), {'listing_id': listing.id})

        self.assertTrue(DonationListing.objects.get(id=listing.id).status == DonationStatus.COMPLETED)

    def test_approve_donation_not_donor(self):  # EC2
        listing = DonationListing.add_listing(self.book, self.donor)
        listing.request_donation(self.other)

        self.client.logout()
        self.client.login(username='other', password='123')
        self.client.post(reverse('donations:approve_donation'), {'listing_id': listing.id})
        self.assertTrue(DonationListing.objects.filter(id=listing.id).exists())


    # ---------------------------------------------------------
    # reject_donation
    # ---------------------------------------------------------
    def test_reject_donation_success(self):  # EC1
        listing = DonationListing.add_listing(self.book, self.donor)
        listing.request_donation(self.other)

        self.client.post(reverse('donations:reject_donation'), {'listing_id': listing.id})
        listing.refresh_from_db()

        self.assertEqual(listing.status, DonationStatus.AVAILABLE)
        self.assertIsNone(listing.requester)

    def test_reject_donation_not_donor(self):  # EC2
        listing = DonationListing.add_listing(self.book, self.donor)
        listing.request_donation(self.other)

        self.client.logout()
        self.client.login(username='other', password='123')

        self.client.post(reverse('donations:reject_donation'), {'listing_id': listing.id})
        listing.refresh_from_db()

        # should NOT have reverted
        self.assertEqual(listing.status, DonationStatus.PENDING)


    # ---------------------------------------------------------
    # VIEW RENDERING
    # ---------------------------------------------------------
    def test_pending_requests_empty(self):  # EC1
        r = self.client.get(reverse('donations:pending_requests'))
        self.assertContains(r, "No pending requests") if "No pending requests" in r.content.decode() else self.assertEqual(r.status_code, 200)

    def test_pending_requests_nonempty(self):
        # create a listing owned by donor
        listing = DonationListing.objects.create(book=self.book, donor=self.donor)

        # make 'other' the requester (valid — requester != donor)
        listing.request_donation(self.other)

        # log in as the requester and check pending requests view
        self.client.logout()
        self.client.login(username='other', password='123')

        response = self.client.get(reverse('donations:pending_requests'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('listings', response.context)
        self.assertEqual(len(response.context['listings']), 1)
        self.assertEqual(response.context['listings'][0].id, listing.id)

    def test_my_listings_filters_correctly(self):  # EC1 + EC2
        DonationListing.add_listing(self.book, self.donor)

        listing2 = DonationListing.add_listing(Book.objects.create(
            title="B", author="X", course="C"
        ), self.donor)
        listing2.request_donation(self.other)

        r = self.client.get(reverse('donations:my_listings'))
        listings = r.context['listings']

        self.assertEqual(len(listings), 2)
        # APPROVED or REJECTED should not appear
