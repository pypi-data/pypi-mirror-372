# Django Flex Menu

A flexible menu management system for Django built around [anytree](https://github.com/c0fec0de/anytree).


## Features

- Modular, tree-based design for easy customization and extension
- Flexible URL resolution
- Object-based processing for detail view menus
- **Thread-safe processing** for concurrent requests
- Request-specific menu state isolation
- Simple template system with single `template` attribute per component
- **Child type validation** for theme-specific menu classes

## Installation


## API

Once you have a menu instance, you can modify it in the following ways:

```python

main_menu = Menu("Site Menu")
child_menu = MenuLink("My Child", url="/my-child")

# Append a child
main_menu.append(child_menu)

# Get a child instance by name
child_menu = main_menu.get("My Child")

# Pop a child (note this is done via the child menu, not the parent menu)
child = child_menu.pop()

# Extend a menu with a list of menu items
main_menu.extend([child_menu, child_menu2, child_menu3])

# Insert child/children at a specific position
main_menu.insert(child_menu, 2)

# Insert child after another named child
main_menu.insert_after(child_menu, "My Other Child")
```

## Configuration

### Logging URL Resolution Failures

By default, URL resolution failures are only logged when `DEBUG=True`. To control this behavior:

```python
# In your Django settings
FLEX_MENU_LOG_URL_FAILURES = False  # Disable logging (recommended for production)
FLEX_MENU_LOG_URL_FAILURES = True   # Always log failures
# Default: settings.DEBUG
```

See [CONFIGURATION.md](CONFIGURATION.md) for detailed configuration options.

## Performance Considerations

For optimal performance in production:

- **Avoid `menu.copy()`** during request processing - it's expensive
- **Cache permission checks** when possible - use `@lru_cache` or Django's cache framework
- **Pre-resolve static URLs** during app startup for menus that don't change
- **Use lazy evaluation** - check parent visibility before processing children
- **Consider menu depth** - deep hierarchies can impact performance

See [PERFORMANCE.md](PERFORMANCE.md) for detailed optimization strategies.

## Thread Safety

⚠️ **Important**: The menu processing is now **thread-safe** for concurrent requests. Each request gets its own processed copy to prevent race conditions.

See [THREAD_SAFETY.md](THREAD_SAFETY.md) for detailed information about concurrency handling.

## Theme-Specific Menu Classes

Create type-safe theme-specific menu classes:

```python
class Bootstrap5DropdownMenu(Menu):
    template = "bootstrap5/dropdown-menu.html"
    allowed_children = ['Bootstrap5DropdownMenuLink']

class Bootstrap5DropdownMenuLink(MenuLink):
    template = "bootstrap5/dropdown-item.html"

# Type validation prevents mixing incompatible components
dropdown = Bootstrap5DropdownMenu("User Menu")
dropdown.append(Bootstrap5DropdownMenuLink("Profile", view_name="profile"))  # ✅ OK
dropdown.append(MenuLink("Settings", view_name="settings"))  # ❌ TypeError!
```

See [THEME_CLASSES.md](THEME_CLASSES.md) for detailed examples and patterns.


## See also

[django-account-management](https://github.com/SamuelJennings/django-account-management)
