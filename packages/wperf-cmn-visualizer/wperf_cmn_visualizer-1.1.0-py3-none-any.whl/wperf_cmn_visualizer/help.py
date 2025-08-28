# BSD 3-Clause License
#
# Copyright (c) 2025, Arm Limited
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
Help Page Dialogue Box module.
Vertically scrollable list of useful information.

Include CMN rendering legend, metrics list,
Versioning information etc.
"""

from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut, QColor
import numpy as np
from typing import Optional, Any

from .config import Config
from .renderer import CMNRenderer
from .cmn import CMN
from .cmn_metrics import CMNMetrics
from . import __version__


class ColorBox(QLabel):
    """Colored box for legend display."""

    def __init__(self, color: QColor, size: tuple[int, int] = (16, 16)) -> None:
        super().__init__()
        self.setFixedSize(*size)
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {color.name()};
            }}
        """)


class ShapeBox(QLabel):
    """Text box with shape styling."""

    def __init__(self, text: str, is_pill: bool = False, size: tuple[int, int] = (32, 16)) -> None:
        super().__init__(text)
        self.setFixedSize(*size)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(f"""
            QLabel {{
                background-color: black;
                color: white;
                border-radius: {size[1] / 2 if is_pill else 2}px;
            }}
        """)


class HelpPage(QDialog):
    """Help dialog with scrollable content."""

    def __init__(self, parent: QWidget, toggle_shortcut: QKeySequence,
                 cmn: Optional[CMN] = None, cmn_metrics: Optional[CMNMetrics] = None):
        super().__init__(parent)
        self.cmn = cmn
        self.cmn_metrics = cmn_metrics

        self.setWindowTitle(f"{Config.MAIN_WINDOW_TITLE} - Help")
        self.setFixedSize(300, 400)

        # bind provided sequence to close. Also escape to close.
        QShortcut(toggle_shortcut, self).activated.connect(self.close)
        QShortcut(QKeySequence("Escape"), self).activated.connect(self.close)

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Initialize the dialog UI."""
        layout = QVBoxLayout(self)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)

        content = QWidget()
        content_layout = QVBoxLayout(content)

        sections = [
            self._create_legend_section(),
            self._create_cmn_section(),
            self._create_metrics_section(),
            self._create_about_section(),
            self._create_version_section()
        ]

        for section in sections:
            content_layout.addWidget(section)
        content_layout.addStretch()

        scroll_area.setWidget(content)
        layout.addWidget(scroll_area)

    def _create_section(self, title: str, content: list[QWidget]) -> QWidget:
        """Create a titled section with content."""
        container = QWidget()
        layout = QVBoxLayout(container)

        title_label = QLabel(f"<h3>{title}</h3>")
        layout.addWidget(title_label)

        for item in content:
            layout.addWidget(item)

        return container

    def _create_info_label(self, name: str, value: Any) -> QLabel:
        """Create an info label with name and value."""
        label = QLabel(f"{name}: {value}")
        label.setWordWrap(True)
        return label

    def _create_legend_section(self) -> QWidget:
        """Create legend section with colors and shapes."""

        def create_legend_item(icon: QWidget, text: str) -> QWidget:
            """Create a single legend item with icon and text."""
            container = QWidget()
            layout = QHBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)

            layout.addWidget(icon)
            layout.addWidget(QLabel(text))
            layout.addStretch()

            return container

        items = []

        # Add color legend for DTC domains
        # only add if metrics not present.
        if self.cmn and hasattr(self.cmn, 'meshes') and not self.cmn_metrics:
            dtcs = np.unique(np.concatenate([
                mesh["xps"]["dtc_domain"].flatten()
                for mesh in self.cmn.meshes
            ]))
            for value in dtcs:
                color = CMNRenderer.dtc_color_map[value % len(CMNRenderer.dtc_color_map)]
                items.append(create_legend_item(ColorBox(color), f"DN & DTC domain {value}"))

        # add shapes legend for coord and node IDs
        shapes = [
            (ShapeBox("(x,y)", False, (28, 16)), "XP (column,row) coordinate"),
            (ShapeBox("aaa", True, (32, 16)), "Node ID (decimal)")
        ]
        for shape_box, description in shapes:
            items.append(create_legend_item(shape_box, description))

        return self._create_section("Legend", items)

    def _create_cmn_section(self) -> QWidget:
        """Create CMN information section."""
        items = []

        if not self.cmn:
            items.append(QLabel("No CMN information available"))
            return self._create_section("CMN", items)

        # Add mesh count from attribute
        if hasattr(self.cmn, "num_meshes") and self.cmn.num_meshes is not None:
            items.append(self._create_info_label("Mesh Count", int(self.cmn.num_meshes)))

        # Add topology information from json
        if hasattr(self.cmn, "topology_json") and isinstance(self.cmn.topology_json, dict):
            topology_fields = [
                ("processor_type", "Processor Type"),
                ("generator", "Generator"),
            ]
            for key, display_name in topology_fields:
                if key in self.cmn.topology_json and self.cmn.topology_json[key] is not None:
                    items.append(self._create_info_label(display_name, self.cmn.topology_json[key]))

        return self._create_section("CMN", items)

    def _create_metrics_section(self) -> QWidget:
        """Create metrics section."""
        items = []
        if self.cmn_metrics and hasattr(self.cmn_metrics, 'metric_names'):
            for i, metric_name in enumerate(self.cmn_metrics.metric_names, 1):
                label = QLabel(f"{i}. {metric_name}")
                label.setWordWrap(True)
                items.append(label)
        else:
            items.append(QLabel("No metrics currently loaded"))

        return self._create_section("Metrics", items)

    def _create_about_section(self) -> QWidget:
        """Create about section."""
        label = QLabel(f"{Config.ABOUT_STRING}.")
        label.setWordWrap(True)
        return self._create_section("About", [label])

    def _create_version_section(self) -> QWidget:
        """Create version section."""
        return self._create_section("Version", [QLabel(__version__)])
