from django.db import models
from django.contrib.auth.models import User
from books.models import Book

class DonationStatus(models.TextChoices):
    AVAILABLE = 'A', 'Available'
    PENDING = 'P', 'Pending'
    COMPLETED = 'C', 'Completed'

class DonationListing(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    donor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="donations_given"
    )
    requester = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        related_name="donations_requested"
    )

    status = models.CharField(
        max_length=1,
        choices=DonationStatus.choices,
        default=DonationStatus.AVAILABLE
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('book', 'donor',)  # Same user can't donate multiple copies

    @classmethod
    def add_listing(cls, book, user):
        if book is None:
            raise ValueError('Book cannot be None')
        if user is None:
            raise ValueError('User cannot be None')
        return DonationListing.objects.get_or_create(book=book, donor=user)[0]

    def request_donation(self, requesting_user):
        if requesting_user is None:
            raise ValueError('requesting_user cannot be None')
        if requesting_user == self.donor:
            raise ValueError('Cannot request your own book')
        if self.status != DonationStatus.AVAILABLE:
            raise ValueError("Requested book is not available")

        self.requester = requesting_user
        self.status = DonationStatus.PENDING
        self.save()

    def cancel_donation(self, requesting_user):
        if requesting_user is None:
            raise ValueError('requesting_user cannot be None')
        if self.status != DonationStatus.PENDING:
            raise ValueError("Book wasn't requested")
        if self.requester != requesting_user:
            raise ValueError('Request was made by another user')

        self.requester = None
        self.status = DonationStatus.AVAILABLE
        self.save()

    def approve_donation(self):
        if self.status != DonationStatus.PENDING:
            raise ValueError("Only pending donations can be approved")
        self.status = DonationStatus.COMPLETED
        self.save()

    def reject_donation(self):
        if self.status != DonationStatus.PENDING:
            raise ValueError("Only pending donations can be rejected")
        self.status = DonationStatus.AVAILABLE
        self.requester = None
        self.save()
