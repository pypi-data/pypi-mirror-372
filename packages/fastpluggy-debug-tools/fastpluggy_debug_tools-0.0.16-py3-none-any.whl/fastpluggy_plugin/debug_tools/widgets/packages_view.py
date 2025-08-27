from typing import Any, Optional, Dict
from fastpluggy.core.widgets import AbstractWidget


class PackagesView(AbstractWidget):
    """
    A widget to display installed packages with search and filter capabilities.
    """
    widget_type = "packages"
    template_name = "debug_tools/widgets/packages_view.html.j2"

    def __init__(self, packages: Dict[str, Dict[str, Any]], title: Optional[str] = None, **kwargs):
        """
        Initialize the PackagesView widget.

        Args:
            packages (Dict[str, Dict[str, Any]]): Dictionary of packages with metadata
            title (Optional[str]): An optional title for the packages view.
        """
        self.packages = packages
        self.packages_list = []
        self.total_count = 0
        kwargs['title'] = title or "Installed Packages"
        super().__init__(**kwargs)

    def process(self, **kwargs) -> None:
        """
        Process the packages data and prepare it for rendering.
        """
        # Convert packages dict to sorted list for easier template handling
        self.packages_list = []
        for key, package_info in self.packages.items():
            self.packages_list.append({
                'key': key,
                'name': package_info['name'],
                'version': package_info['version'],
                'summary': package_info.get('summary', ''),
                'author': package_info.get('author', ''),
                'home_page': package_info.get('home_page', ''),
            })
        
        # Sort packages alphabetically by name
        self.packages_list.sort(key=lambda x: x['name'].lower())
        self.total_count = len(self.packages_list)