from django.db.models import Q
from .models import Book


# === Base Strategy ===
class BookSearchStrategy:
    """Base class for all book search strategies."""
    def search(self, request):
        raise NotImplementedError("Search method must be implemented by subclass")


# === Concrete Strategies ===
class TitleSearchStrategy(BookSearchStrategy):
    def search(self, request):
        query = request.GET.get("q", "").strip()
        if not query:
            return Book.objects.all()
        return Book.objects.filter(title__icontains=query).distinct()


class AuthorSearchStrategy(BookSearchStrategy):
    def search(self, request):
        query = request.GET.get("q", "").strip()
        if not query:
            return Book.objects.all()
        return Book.objects.filter(author__icontains=query).distinct()


class CourseSearchStrategy(BookSearchStrategy):
    def search(self, request):
        query = request.GET.get("q", "").strip()
        if not query:
            return Book.objects.all()
        return Book.objects.filter(course__icontains=query).distinct()


class CombinedSearchStrategy(BookSearchStrategy):
    def search(self, request):
        query = request.GET.get("q", "").strip()
        if not query:
            return Book.objects.all()
        return Book.objects.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(course__icontains=query)
        ).distinct()


class AdvancedSearchStrategy(BookSearchStrategy):
    def search(self, request):
        """Advanced search combining multiple fields conjunctively."""
        title = request.GET.get("title", "").strip()
        author = request.GET.get("author", "").strip()
        course = request.GET.get("course", "").strip()

        queryset = Book.objects.all()
        if title:
            queryset = queryset.filter(title__icontains=title)
        if author:
            queryset = queryset.filter(author__icontains=author)
        if course:
            queryset = queryset.filter(course__icontains=course)

        return queryset.distinct()


# === Context / Service ===
class BookSearchService:
    """Context class selecting and delegating to the right search strategy."""

    def __init__(self, strategy='combined'):
        self.strategies = {
            'title': TitleSearchStrategy(),
            'author': AuthorSearchStrategy(),
            'course': CourseSearchStrategy(),
            'combined': CombinedSearchStrategy(),
            'advanced': AdvancedSearchStrategy(),
        }

        if isinstance(strategy, BookSearchStrategy):
            self.strategy = strategy
        else:
            self.strategy = self.strategies.get(strategy, self.strategies['combined'])

    def search(self, request):
        return self.strategy.search(request)

    def set_strategy(self, strategy):
        if isinstance(strategy, BookSearchStrategy):
            self.strategy = strategy
        else:
            self.strategy = self.strategies.get(strategy, self.strategies['combined'])