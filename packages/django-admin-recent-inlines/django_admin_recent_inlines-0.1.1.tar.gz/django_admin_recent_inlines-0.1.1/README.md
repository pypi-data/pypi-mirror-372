# Django Admin Recent Inlines

A Django package that provides a `RecentTabularInline` class for displaying recent related objects in Django admin with a "View All" link.

## Features

- **Recent Inlines**: Display only the most recent related objects in Django admin
- **View All Link**: Automatically adds a "View All" link when there are more objects than the display limit
- **Configurable Limit**: Set the maximum number of related objects to display
- **Django Admin Integration**: Seamlessly integrates with Django's admin interface

## Installation

```bash
pip install django-admin-recent-inlines
```

## Usage

### Basic Usage

```python
from django.contrib import admin
from django_admin_recent_inlines.admin import RecentTabularInline
from .models import ParentModel, ChildModel

class ChildInline(RecentTabularInline):
    model = ChildModel
    maximum_number_of_related_rows_to_display = 5  # Show only 5 most recent

@admin.register(ParentModel)
class ParentAdmin(admin.ModelAdmin):
    inlines = [ChildInline]
```

### Configuration Options

- `maximum_number_of_related_rows_to_display`: Number of recent objects to display (default: 5)
- `template`: Custom template for the inline (default: uses the provided template)
- All standard `TabularInline` options are supported

### How It Works

1. The `RecentTabularInline` limits the queryset to show only the most recent related objects
2. When there are more objects than the display limit, a "View All" link is automatically added
3. The "View All" link takes you to the filtered changelist view showing all related objects
4. The link includes the count of total related objects

## Requirements

- Python 3.11+
- Django 4.0+

## Development

### Setup

```bash
git clone https://github.com/AugendLimited/django-admin-recent-inlines.git
cd django-admin-recent-inlines
poetry install
```

### Running Tests

```bash
poetry run pytest
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
