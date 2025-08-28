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

import pytest
from unittest.mock import Mock, patch
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QKeySequence

from wperf_cmn_visualizer.help import HelpPage


class TestHelpPage:
    """Tests for the HelpPage dialog."""

    @pytest.fixture
    def parent_widget(self):
        return QWidget()

    @pytest.fixture
    def mock_cmn_metrics(self):
        metrics = Mock()
        metrics.metric_names = ["metric1", "metric2", "metric3"]
        return metrics

    @patch('wperf_cmn_visualizer.help.QShortcut')
    def test_keyboard_shortcuts_setup(self, mock_shortcut, parent_widget):
        """Test both toggle shortcut and Escape are bound."""
        shortcut_key = QKeySequence("F1")
        HelpPage(parent_widget, shortcut_key)

        assert mock_shortcut.call_count == 2
        calls = mock_shortcut.call_args_list
        shortcut_keys = [call[0][0] for call in calls]
        assert shortcut_key in shortcut_keys
        assert QKeySequence("Escape") in shortcut_keys

    def test_cmn_section_handles_missing_data_gracefully(self, parent_widget):
        """Test CMN section when data is missing or malformed."""
        # Test with None CMN
        help_page = HelpPage(parent_widget, QKeySequence("?"), None)
        cmn_section = help_page._create_cmn_section()
        assert cmn_section is not None

        # Test with CMN but missing attributes
        cmn = Mock()
        del cmn.meshes
        del cmn.num_meshes
        del cmn.topology_json

        # should not raise exceptions
        help_page = HelpPage(parent_widget, QKeySequence("?"), cmn)
        cmn_section = help_page._create_cmn_section()

        assert cmn_section is not None

    def test_metrics_section_displays_metric_names(self, parent_widget, mock_cmn_metrics):
        """Test metrics section shows numbered list of metric names."""
        help_page = HelpPage(parent_widget, QKeySequence("?"), None, mock_cmn_metrics)
        metrics_section = help_page._create_metrics_section()
        assert metrics_section is not None
