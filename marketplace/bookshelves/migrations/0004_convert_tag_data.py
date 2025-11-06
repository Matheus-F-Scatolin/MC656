# Data migration to convert integer tag values to string values
from django.db import migrations


def convert_tags_to_strings(apps, schema_editor):
    """Convert existing integer tag values to string values"""
    BookshelfItem = apps.get_model('bookshelves', 'BookshelfItem')
    
    # Django should handle this conversion automatically since we're using
    # the same string values ('0', '1', '2', '3') as the integer values
    # However, we'll include this migration for explicit documentation
    # and to handle any edge cases
    
    for item in BookshelfItem.objects.all():
        # Ensure tag is stored as string
        item.tag = str(item.tag)
        item.save()


def reverse_convert_tags_to_integers(apps, schema_editor):
    """Convert string tag values back to integer values for rollback"""
    BookshelfItem = apps.get_model('bookshelves', 'BookshelfItem')
    
    tag_mapping = {'0': 0, '1': 1, '2': 2, '3': 3}
    
    for item in BookshelfItem.objects.all():
        # Convert string back to integer for rollback
        item.tag = tag_mapping.get(item.tag, 0)
        item.save()


class Migration(migrations.Migration):
    dependencies = [
        ('bookshelves', '0003_alter_bookshelfitem_tag'),
    ]

    operations = [
        migrations.RunPython(
            convert_tags_to_strings,
            reverse_convert_tags_to_integers
        ),
    ]