from typing import ClassVar, Any

import psutil
from fastpluggy.core.widgets import AbstractWidget
from pydantic import BaseModel, Field


class PsutilAnalyzerWidget(AbstractWidget):
    widget_type: ClassVar[str] = ""

    ""
    widget_type = "psutil_analyzer"

    template_name: str = "debug_tools/psutil_analyzer.html.j2"

    class ConfigModel(BaseModel):
        class Config:
            title = "PSUtil Analyzer Widget Configuration"
        
        title: str = Field(default="PSUtil Memory Analysis Dashboard", description="Widget title")

    def __init__(self, **config: Any):
        super().__init__()
        cfg = self.ConfigModel(**config)
        self.title = cfg.title

    def process(self, **kwargs):
        """Render the PSUtil Analyzer widget using the template."""

        # Get process information using psutil
        process = psutil.Process()
        self.process_dict = process.as_dict()
        
