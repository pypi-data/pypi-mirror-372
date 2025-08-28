#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bandgap Tauc-Plot GUI
Final: only Direct (2) and Indirect (1/2) transitions (forbidden removed),
no fit-line controls, sticky fit line (never auto-resets), editable titles,
legend fix, robust UX, manual margins (no constrained/tight layout),
bold x-axis with hν (eV), robust endpoint dragging (separate endpoint artists),
customizable Y labels for Absorbance and Transmittance.
"""

import sys
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QLabel, QComboBox, QLineEdit, QFileDialog,
    QColorDialog, QGroupBox, QMessageBox, QCheckBox,
    QTabWidget, QRadioButton, QButtonGroup, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
from matplotlib.figure import Figure
from matplotlib.ticker import MultipleLocator, AutoMinorLocator

# ---- Matplotlib base style ----
plt.style.use('default')
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif']
plt.rcParams['axes.labelweight'] = 'normal'
plt.rcParams['axes.titleweight'] = 'bold'
plt.rcParams['axes.titlesize'] = 16
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['ytick.labelsize'] = 12
plt.rcParams['grid.color'] = '#dddddd'
plt.rcParams['grid.linestyle'] = '--'
plt.rcParams['grid.linewidth'] = 0.5
plt.rcParams['axes.edgecolor'] = '#555555'


class TaucPlotGUI(QWidget):
    """
    PyQt5 GUI for Tauc plot band gap analysis with thickness support.
    - Load one or many files (CSV/TXT/XLSX). First two columns = wavelength (nm), absorbance (a.u.).
    - Choose transition: Direct (2), Indirect (1/2).
    - Thickness d with units → alpha [cm^-1] via α = (2.303 * A) / d(cm).
    - Auto linear fit initializes once; draggable endpoints; never auto-resets after that.
    - Export plot or Tauc data.
    """

    TRANSITION_MAP = {
        "Direct (2)": {"power": 2.0},
        "Indirect (1/2)": {"power": 0.5},
    }

    def __init__(self):
        super().__init__()

        # Data containers
        self.wavelength = None
        self.absorbance = None
        self.transmittance = None
        self.E = None
        self.y = None

        # Bandgap / fit
        self.Eg = np.nan
        self._fit_m = None
        self._fit_c = None

        # Fit/drag state
        self.dragging = False
        self.dragged_point = None
        self.fit_line = None
        self.fit_line_data_x = None  # endpoints in data coords (E, y)
        self.fit_line_data_y = None

        # Explicit endpoint artists (for robust visibility/dragging)
        self.fit_pt_start = None
        self.fit_pt_end = None

        # Colors
        self.abs_color = "#4CAF50"
        self.trans_color = "#FFC107"
        self.tauc_color = "#336699"
        self.fit_color = "#E54F3D"

        # Tick configuration
        self._tick_cfg = {"x_major": None, "x_minor": None, "y_major": None, "y_minor": None}

        # Legend/marker config
        self._legend_label_default = "Tauc Plot"
        self._legend_label = self._legend_label_default
        self._marker_choice = "None"
        self._marker_hollow = False

        # Numeric style controls
        self._line_width = 2
        self._fit_width = 2
        self._title_size = 16
        self._label_size = 14
        self._legend_size = 12
        self._tick_size = 12

        # Universal axis controls
        self.x_min_input = None; self.x_max_input = None; self.x_step_input = None
        self.y_min_input = None; self.y_max_input = None; self.y_step_input = None

        # Editable titles
        self._abs_title_text = "UV-Vis Absorbance Spectrum"
        self._trans_title_text = "UV-Vis Transmittance Spectrum"

        # Editable Y labels for Absorbance/Transmittance
        self._abs_ylabel_text = "Absorbance (a.u.)"
        self._trans_ylabel_text = "Transmittance (%)"

        # Window/UI
        self.setWindowTitle("Band Gap Energy Calculator - Tauc Plot")
        self.setGeometry(100, 100, 1200, 800)
        self.set_qss_style()
        self.init_ui()

        QTimer.singleShot(0, self.update_plot)

    # ------------------ UI ------------------
    def set_qss_style(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                color: #2b2b2b;
                font-family: 'Inter', 'Segoe UI', sans-serif;
            }
            QPushButton {
                background-color: #cccccc;
                border: 2px solid #aaaaaa;
                border-radius: 8px;
                padding: 10px 15px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #dddddd; }
            QPushButton:pressed { background-color: #bbbbbb; }
            QGroupBox {
                border: 2px solid #aaaaaa;
                border-radius: 10px;
                margin-top: 20px;
                font-size: 16px;
                font-weight: bold;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
            }
            QLabel { font-size: 14px; color: #555555; }
            QLineEdit, QComboBox {
                background-color: #dddddd;
                border: 1px solid #aaaaaa;
                border-radius: 5px;
                padding: 5px;
                color: #2b2b2b;
            }
            QRadioButton { font-size: 14px; }
            QTabWidget::pane { border-top: 2px solid #aaaaaa; background: #f0f0f0; }
            QTabBar::tab {
                background: #dddddd;
                border: 2px solid #aaaaaa;
                border-bottom-color: #aaaaaa;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                min-width: 8ex;
                padding: 6px;
                font-weight: bold;
            }
            QTabBar::tab:selected { background: #f0f0f0; border-bottom-color: #f0f0f0; }
        """)

    def init_ui(self):
        self.main_h_layout = QHBoxLayout(self)
        self.main_h_layout.setContentsMargins(10, 10, 10, 10)
        self.main_h_layout.setSpacing(10)

        # Left panel
        self.controls_layout = QVBoxLayout()
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_data_controls(), "Data & Range")
        self.tabs.addTab(self.create_plot_controls(), "Plot Settings")
        self.tabs.addTab(self.create_tick_controls(), "Axis Ticks")
        self.tabs.addTab(self.create_style_controls_numbers(), "Styling (Numbers)")
        self.tabs.addTab(self.create_export_controls(), "Export Plot")
        self.tabs.addTab(self.create_tauc_data_export_controls(), "TAUC data")
        self.controls_layout.addWidget(self.tabs)
        self.controls_layout.addStretch(1)
        self.main_h_layout.addLayout(self.controls_layout, 1)

        # Right panel: plot
        self.plot_layout = QVBoxLayout()
        self.plot_layout.setContentsMargins(0, 0, 0, 0)

        # NOTE: no constrained_layout or tight_layout
        self.canvas_figure = Figure(figsize=(8, 6), dpi=120, facecolor='white')
        self.ax = self.canvas_figure.add_subplot(111, facecolor='#f7f7f7')
        self.canvas = Canvas(self.canvas_figure)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.plot_layout.addWidget(self.canvas, 1)

        self.bandgap_label = QLabel("Estimated Band Gap: -- eV")
        self.bandgap_label.setAlignment(Qt.AlignCenter)
        self.bandgap_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #36a2eb;")
        self.plot_layout.addWidget(self.bandgap_label)

        self.main_h_layout.addLayout(self.plot_layout, 3)

        # Mouse events
        self.canvas.mpl_connect("button_press_event", self.on_click)
        self.canvas.mpl_connect("motion_notify_event", self.on_drag)
        self.canvas.mpl_connect("button_release_event", self.on_release)

    def create_data_controls(self):
        data_tab = QWidget()
        layout = QVBoxLayout()

        load_btn = QPushButton("Load UV-Vis (CSV/TXT/XLSX)")
        load_btn.setToolTip("Select one or more files. First two columns must be: wavelength (nm), absorbance (a.u.).")
        load_btn.clicked.connect(self.load_data)
        layout.addWidget(load_btn)

        self.loaded_info_label = QLabel("No file loaded")
        layout.addWidget(self.loaded_info_label)

        group = QGroupBox("Axis & Range Controls")
        form_layout = QFormLayout()

        # Wavelength range
        wl_layout = QHBoxLayout()
        self.min_wl_input = QLineEdit(); self.min_wl_input.setPlaceholderText("auto")
        self.max_wl_input = QLineEdit(); self.max_wl_input.setPlaceholderText("auto")
        self.min_wl_input.editingFinished.connect(self.update_plot)
        self.max_wl_input.editingFinished.connect(self.update_plot)
        wl_layout.addWidget(QLabel("Min (nm):")); wl_layout.addWidget(self.min_wl_input)
        wl_layout.addWidget(QLabel("Max (nm):")); wl_layout.addWidget(self.max_wl_input)
        form_layout.addRow("Wavelength:", wl_layout)

        # Absorbance Y range
        abs_y_layout = QHBoxLayout()
        self.min_abs_y_input = QLineEdit(); self.min_abs_y_input.setPlaceholderText("auto")
        self.max_abs_y_input = QLineEdit(); self.max_abs_y_input.setPlaceholderText("auto")
        self.min_abs_y_input.editingFinished.connect(self.update_plot)
        self.max_abs_y_input.editingFinished.connect(self.update_plot)
        abs_y_layout.addWidget(QLabel("Min Y:")); abs_y_layout.addWidget(self.min_abs_y_input)
        abs_y_layout.addWidget(QLabel("Max Y:")); abs_y_layout.addWidget(self.max_abs_y_input)
        form_layout.addRow("Absorbance:", abs_y_layout)

        # Transmittance Y range
        trans_y_layout = QHBoxLayout()
        self.min_trans_y_input = QLineEdit(); self.min_trans_y_input.setPlaceholderText("auto")
        self.max_trans_y_input = QLineEdit(); self.max_trans_y_input.setPlaceholderText("auto")
        self.min_trans_y_input.editingFinished.connect(self.update_plot)
        self.max_trans_y_input.editingFinished.connect(self.update_plot)
        trans_y_layout.addWidget(QLabel("Min Y:")); trans_y_layout.addWidget(self.min_trans_y_input)
        trans_y_layout.addWidget(QLabel("Max Y:")); trans_y_layout.addWidget(self.max_trans_y_input)
        form_layout.addRow("Transmittance:", trans_y_layout)

        # Thickness
        thickness_layout = QHBoxLayout()
        self.thickness_input = QLineEdit(); self.thickness_input.setPlaceholderText("1.0")
        self.thickness_input.setToolTip("Film thickness value (positive number). α units = cm⁻¹ (d is converted to cm).")
        self.thickness_input.editingFinished.connect(self.update_plot)
        self.thickness_unit_box = QComboBox(); self.thickness_unit_box.addItems(["cm", "mm", "µm", "nm"])
        self.thickness_unit_box.setToolTip("Thickness units. α = 2.303*A / d (d in cm).")
        self.thickness_unit_box.currentIndexChanged.connect(self.update_plot)
        thickness_layout.addWidget(QLabel("d:")); thickness_layout.addWidget(self.thickness_input); thickness_layout.addWidget(self.thickness_unit_box)
        form_layout.addRow("Thin-film thickness:", thickness_layout)

        # Universal axis ranges/steps
        axis_group = QGroupBox("Custom Axis Ranges (All Graphs)")
        axis_form = QFormLayout()

        self.x_min_input = QLineEdit(); self.x_min_input.setPlaceholderText("auto")
        self.x_max_input = QLineEdit(); self.x_max_input.setPlaceholderText("auto")
        self.x_step_input = QLineEdit(); self.x_step_input.setPlaceholderText("auto")
        for w in (self.x_min_input, self.x_max_input, self.x_step_input):
            w.editingFinished.connect(self.update_plot)
        x_row = QHBoxLayout()
        x_row.addWidget(QLabel("Min:")); x_row.addWidget(self.x_min_input)
        x_row.addWidget(QLabel("Max:")); x_row.addWidget(self.x_max_input)
        x_row.addWidget(QLabel("Step:")); x_row.addWidget(self.x_step_input)
        axis_form.addRow("X-axis:", x_row)

        self.y_min_input = QLineEdit(); self.y_min_input.setPlaceholderText("auto")
        self.y_max_input = QLineEdit(); self.y_max_input.setPlaceholderText("auto")
        self.y_step_input = QLineEdit(); self.y_step_input.setPlaceholderText("auto")
        for w in (self.y_min_input, self.y_max_input, self.y_step_input):
            w.editingFinished.connect(self.update_plot)
        y_row = QHBoxLayout()
        y_row.addWidget(QLabel("Min:")); y_row.addWidget(self.y_min_input)
        y_row.addWidget(QLabel("Max:")); y_row.addWidget(self.y_max_input)
        y_row.addWidget(QLabel("Step:")); y_row.addWidget(self.y_step_input)
        axis_form.addRow("Y-axis:", y_row)

        axis_group.setLayout(axis_form)
        layout.addWidget(axis_group)

        group.setLayout(form_layout)
        layout.addWidget(group)
        layout.addStretch(1)
        data_tab.setLayout(layout)
        return data_tab

    def create_plot_controls(self):
        """Tab: plot selection, transition, grid/titles (NO fit-line controls)."""
        plot_tab = QWidget()
        layout = QVBoxLayout()

        # Plot selection
        plot_type_groupbox = QGroupBox("Select Plot to Display")
        plot_type_layout = QVBoxLayout()
        self.radio_abs = QRadioButton("Absorbance Spectrum")
        self.radio_trans = QRadioButton("Transmittance Spectrum")
        self.radio_tauc = QRadioButton("Tauc Plot")
        self.plot_type_group = QButtonGroup()
        self.plot_type_group.addButton(self.radio_abs, 1)
        self.plot_type_group.addButton(self.radio_trans, 2)
        self.plot_type_group.addButton(self.radio_tauc, 3)
        self.radio_tauc.setChecked(True)
        self.plot_type_group.buttonClicked.connect(self.update_plot)
        plot_type_layout.addWidget(self.radio_abs)
        plot_type_layout.addWidget(self.radio_trans)
        plot_type_layout.addWidget(self.radio_tauc)
        plot_type_groupbox.setLayout(plot_type_layout)
        layout.addWidget(plot_type_groupbox)

        # Transition + titles + grid
        settings_group = QGroupBox("Plot Styling")
        settings_layout = QVBoxLayout()

        mode_layout = QHBoxLayout()
        self.mode_box = QComboBox()
        self.mode_box.addItems(list(self.TRANSITION_MAP.keys()))
        self.mode_box.setCurrentText("Direct (2)")
        self.mode_box.currentTextChanged.connect(self.on_mode_changed)  # Changed to custom handler
        mode_layout.addWidget(QLabel("Transition Type:"))
        mode_layout.addWidget(self.mode_box)
        settings_layout.addLayout(mode_layout)

        # Editable titles
        title_edit_row1 = QHBoxLayout()
        self.abs_title_input = QLineEdit(self._abs_title_text)
        self.abs_title_input.setPlaceholderText("(Absorbance title)")
        self.abs_title_input.textChanged.connect(self._on_abs_title_changed)
        title_edit_row1.addWidget(QLabel("Absorbance Title:"))
        title_edit_row1.addWidget(self.abs_title_input)
        settings_layout.addLayout(title_edit_row1)

        title_edit_row2 = QHBoxLayout()
        self.trans_title_input = QLineEdit(self._trans_title_text)
        self.trans_title_input.setPlaceholderText("(Transmittance title)")
        self.trans_title_input.textChanged.connect(self._on_trans_title_changed)
        title_edit_row2.addWidget(QLabel("Transmittance Title:"))
        title_edit_row2.addWidget(self.trans_title_input)
        settings_layout.addLayout(title_edit_row2)

        # Y labels editors
        ylab_row1 = QHBoxLayout()
        self.abs_ylabel_input = QLineEdit(self._abs_ylabel_text)
        self.abs_ylabel_input.setPlaceholderText("Absorbance (a.u.)")
        self.abs_ylabel_input.textChanged.connect(self._on_abs_ylabel_changed)
        ylab_row1.addWidget(QLabel("Absorbance Y-Label:"))
        ylab_row1.addWidget(self.abs_ylabel_input)
        settings_layout.addLayout(ylab_row1)

        ylab_row2 = QHBoxLayout()
        self.trans_ylabel_input = QLineEdit(self._trans_ylabel_text)
        self.trans_ylabel_input.setPlaceholderText("Transmittance (%)")
        self.trans_ylabel_input.textChanged.connect(self._on_trans_ylabel_changed)
        ylab_row2.addWidget(QLabel("Transmittance Y-Label:"))
        ylab_row2.addWidget(self.trans_ylabel_input)
        settings_layout.addLayout(ylab_row2)

        self.hide_y_labels_checkbox = QCheckBox("Hide Y-Axis Labels"); self.hide_y_labels_checkbox.setChecked(False)
        self.hide_y_labels_checkbox.stateChanged.connect(self.update_plot)
        self.hide_abs_title_checkbox = QCheckBox("Hide Absorbance Title"); self.hide_abs_title_checkbox.setChecked(False)
        self.hide_abs_title_checkbox.stateChanged.connect(self.update_plot)
        self.hide_trans_title_checkbox = QCheckBox("Hide Transmittance Title"); self.hide_trans_title_checkbox.setChecked(False)
        self.hide_trans_title_checkbox.stateChanged.connect(self.update_plot)
        self.hide_tauc_title_checkbox = QCheckBox("Hide Tauc Plot Title"); self.hide_tauc_title_checkbox.setChecked(False)
        self.hide_tauc_title_checkbox.stateChanged.connect(self.update_plot)
        self.show_grid_checkbox = QCheckBox("Show Grid"); self.show_grid_checkbox.setChecked(False)
        self.show_grid_checkbox.stateChanged.connect(self.update_plot)

        settings_layout.addWidget(self.hide_y_labels_checkbox)
        settings_layout.addWidget(self.hide_abs_title_checkbox)
        settings_layout.addWidget(self.hide_trans_title_checkbox)
        settings_layout.addWidget(self.hide_tauc_title_checkbox)
        settings_layout.addWidget(self.show_grid_checkbox)

        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)

        layout.addStretch(1)
        plot_tab.setLayout(layout)
        return plot_tab

    def create_style_controls_numbers(self):
        style_tab = QWidget()
        layout = QVBoxLayout()

        # Line widths
        group_widths = QGroupBox("Line Widths (numbers)")
        form_layout_widths = QFormLayout()
        self.line_width_input = QLineEdit(str(self._line_width))
        self.fit_width_input = QLineEdit(str(self._fit_width))
        for w in (self.line_width_input, self.fit_width_input):
            w.setToolTip("Enter a positive number, e.g., 2")
            w.editingFinished.connect(self._update_number_styles)
        form_layout_widths.addRow("Line Width:", self.line_width_input)
        form_layout_widths.addRow("Fit Line Width:", self.fit_width_input)
        group_widths.setLayout(form_layout_widths)
        layout.addWidget(group_widths)

        # Font sizes
        group_fonts = QGroupBox("Font Sizes (numbers)")
        font_layout = QFormLayout()
        self.title_size_input = QLineEdit(str(self._title_size))
        self.label_size_input = QLineEdit(str(self._label_size))
        self.legend_size_input = QLineEdit(str(self._legend_size))
        self.tick_size_input = QLineEdit(str(self._tick_size))
        for w in (self.title_size_input, self.label_size_input, self.legend_size_input, self.tick_size_input):
            w.setToolTip("Enter a positive integer, e.g., 14")
            w.editingFinished.connect(self._update_number_styles)
        font_layout.addRow("Title size:", self.title_size_input)
        font_layout.addRow("Label size:", self.label_size_input)
        font_layout.addRow("Legend size:", self.legend_size_input)
        font_layout.addRow("Tick size:", self.tick_size_input)
        group_fonts.setLayout(font_layout)
        layout.addWidget(group_fonts)

        # Colors
        group_colors = QGroupBox("Colors")
        color_layout = QFormLayout()
        self.main_color_btn = QPushButton("Choose Main Plot Color")
        self.main_color_btn.clicked.connect(self.pick_main_color)
        color_layout.addRow(self.main_color_btn)
        self.fit_color_btn = QPushButton("Choose Fit Line Color")
        self.fit_color_btn.clicked.connect(self.pick_fit_color)
        color_layout.addRow(self.fit_color_btn)
        group_colors.setLayout(color_layout)
        layout.addWidget(group_colors)

        # Legend & markers
        legend_group = QGroupBox("Legend & Markers")
        legend_form = QFormLayout()
        self.legend_text_input = QLineEdit()
        self.legend_text_input.setPlaceholderText("Legend label (e.g., Sample A)")
        self.legend_text_input.textChanged.connect(self._on_legend_text_changed)
        legend_form.addRow("Legend Label:", self.legend_text_input)

        self.marker_box = QComboBox()
        self.marker_box.addItems(["None", "Square", "Triangle Up", "Circle (filled)", "Circle (hollow)", "Diamond"])
        self.marker_box.currentTextChanged.connect(self._on_marker_changed)
        legend_form.addRow("Marker Style:", self.marker_box)

        legend_group.setLayout(legend_form)
        layout.addWidget(legend_group)

        layout.addStretch(1)
        style_tab.setLayout(layout)
        return style_tab

    def create_tick_controls(self):
        tick_tab = QWidget()
        layout = QVBoxLayout()

        group = QGroupBox("Major/Minor Tick Settings (Journal-ready)")
        form = QFormLayout()

        x_major_row = QHBoxLayout()
        self.x_major_input_tick = QLineEdit(); self.x_major_input_tick.setPlaceholderText("auto")
        x_major_row.addWidget(QLabel("Δx (major):")); x_major_row.addWidget(self.x_major_input_tick)

        x_minor_row = QHBoxLayout()
        self.x_minor_input_tick = QLineEdit(); self.x_minor_input_tick.setPlaceholderText("auto")
        x_minor_row.addWidget(QLabel("Δx (minor):")); x_minor_row.addWidget(self.x_minor_input_tick)

        y_major_row = QHBoxLayout()
        self.y_major_input_tick = QLineEdit(); self.y_major_input_tick.setPlaceholderText("auto")
        y_major_row.addWidget(QLabel("Δy (major):")); y_major_row.addWidget(self.y_major_input_tick)

        y_minor_row = QHBoxLayout()
        self.y_minor_input_tick = QLineEdit(); self.y_minor_input_tick.setPlaceholderText("auto")
        y_minor_row.addWidget(QLabel("Δy (minor):")); y_minor_row.addWidget(self.y_minor_input_tick)

        form.addRow("X-axis:", x_major_row)
        form.addRow("", x_minor_row)
        form.addRow("Y-axis:", y_major_row)
        form.addRow("", y_minor_row)

        btn_row = QHBoxLayout()
        apply_btn = QPushButton("Apply Tick Settings"); apply_btn.clicked.connect(self.apply_tick_settings)
        reset_btn = QPushButton("Reset Ticks"); reset_btn.clicked.connect(self.reset_tick_settings)
        btn_row.addWidget(apply_btn); btn_row.addWidget(reset_btn)

        group.setLayout(form)
        layout.addWidget(group)
        layout.addLayout(btn_row)
        layout.addStretch(1)
        tick_tab.setLayout(layout)
        return tick_tab

    def create_export_controls(self):
        export_tab = QWidget()
        layout = QVBoxLayout()

        group = QGroupBox("Export Plot")
        export_layout = QVBoxLayout()

        format_layout = QHBoxLayout()
        self.format_box = QComboBox()
        self.format_box.addItems(["png", "jpg", "jpeg", "pdf", "svg", "eps", "tiff"])
        format_layout.addWidget(QLabel("Select Format:"))
        format_layout.addWidget(self.format_box)
        export_layout.addLayout(format_layout)

        self.save_plot_btn = QPushButton("Save Current Plot")
        self.save_plot_btn.clicked.connect(self.export_plot)
        export_layout.addWidget(self.save_plot_btn)

        group.setLayout(export_layout)
        layout.addWidget(group)
        layout.addStretch(1)
        export_tab.setLayout(layout)
        return export_tab

    def create_tauc_data_export_controls(self):
        data_export_tab = QWidget()
        layout = QVBoxLayout()

        group = QGroupBox("Export Tauc Plot Data")
        export_layout = QVBoxLayout()

        self.export_tauc_data_btn = QPushButton("Export Tauc Data to CSV")
        self.export_tauc_data_btn.clicked.connect(self.export_tauc_data)
        export_layout.addWidget(self.export_tauc_data_btn)

        group.setLayout(export_layout)
        layout.addWidget(group)
        layout.addStretch(1)
        data_export_tab.setLayout(layout)
        return data_export_tab

    # ------------------ Helpers / parsing ------------------
    def _parse_positive_number(self, widget, default):
        text = (widget.text() if widget else "").strip()
        try:
            val = float(text)
            return val if np.isfinite(val) and val > 0 else default
        except Exception:
            return default

    def _parse_positive_int(self, widget, default):
        text = (widget.text() if widget else "").strip()
        try:
            val = int(float(text))
            return val if val > 0 else default
        except Exception:
            return default

    def _update_number_styles(self):
        self._line_width = self._parse_positive_number(self.line_width_input, 2)
        self._fit_width  = self._parse_positive_number(self.fit_width_input, 2)
        self._title_size = self._parse_positive_int(self.title_size_input, 16)
        self._label_size = self._parse_positive_int(self.label_size_input, 14)
        self._legend_size= self._parse_positive_int(self.legend_size_input, 12)
        self._tick_size  = self._parse_positive_int(self.tick_size_input, 12)
        self.update_plot()

    # ------------------ Title handlers ------------------
    def _on_abs_title_changed(self, text):
        self._abs_title_text = text.strip()
        self.update_plot()

    def _on_trans_title_changed(self, text):
        self._trans_title_text = text.strip()
        self.update_plot()

    # Y-label handlers
    def _on_abs_ylabel_changed(self, text):
        self._abs_ylabel_text = text if text.strip() else "Absorbance (a.u.)"
        self.update_plot()

    def _on_trans_ylabel_changed(self, text):
        self._trans_ylabel_text = text if text.strip() else "Transmittance (%)"
        self.update_plot()

    # ------------------ Legend/marker helpers ------------------
    def _on_legend_text_changed(self, text: str):
        self._legend_label = text if text.strip() else self._legend_label_default
        self.update_plot()

    def _on_marker_changed(self, text: str):
        self._marker_choice = text
        self._marker_hollow = (text == "Circle (hollow)")
        self.update_plot()

    def _marker_kwargs(self, color_hex: str):
        mapping = {
            "None": (None, {}),
            "Square": ('s', {}),
            "Triangle Up": ('^', {}),
            "Circle (filled)": ('o', {}),
            "Circle (hollow)": ('o', {"markerfacecolor": 'none'}),
            "Diamond": ('D', {}),
        }
        marker, extra = mapping.get(self._marker_choice, (None, {}))
        kwargs = {}
        if marker is not None:
            kwargs["marker"] = marker
            kwargs["markersize"] = 6
            if self._marker_hollow:
                kwargs["markerfacecolor"] = 'none'
                kwargs["markeredgewidth"] = 1.2
                kwargs["markeredgecolor"] = color_hex
            else:
                kwargs["markerfacecolor"] = color_hex
                kwargs["markeredgecolor"] = 'white'
                kwargs["markeredgewidth"] = 0.8
        kwargs.update(extra)
        return kwargs

    # ------------------ Labels ------------------
    def _tauc_ylabel(self, power: float) -> str:
        labels = {
            2.0: r"$\mathbf{(\alpha h\nu)^2}\; \mathbf{(cm^{2}\, eV^{-2})}$",
            0.5: r"$\mathbf{(\alpha h\nu)^{1/2}}\; \mathbf{(cm^{-1/2}\, eV^{1/2})}$",
        }
        return labels.get(power, r"$\mathbf{\alpha h\nu}$")

    # ------------------ Fit helpers ------------------
    def _compute_autofit(self):
        """Compute auto linear regression on top 20% of y; return (m, c) or (None, None)."""
        if self.E is None or self.y is None or len(self.E) < 2:
            return None, None
        try:
            threshold = np.nanpercentile(self.y, 80)
            mask = self.y > threshold
            E_fit = self.E[mask].reshape(-1, 1)
            y_fit = self.y[mask]
            if len(E_fit) > 1:
                model = LinearRegression().fit(E_fit, y_fit)
                m, c = float(model.coef_[0]), float(model.intercept_)
                return m, c
        except Exception:
            pass
        return None, None

    def _safe_tight_layout(self):
        # Manual margins only when canvas is actually sized
        try:
            w, h = self.canvas.get_width_height()
            if w >= 200 and h >= 150:
                self.canvas_figure.subplots_adjust(left=0.20, right=0.98, bottom=0.16, top=0.92)
        except Exception:
            pass

    def _ensure_valid_limits(self):
        try:
            x0, x1 = self.ax.get_xlim()
            if np.isfinite(x0) and np.isfinite(x1) and x0 == x1:
                eps = 1e-6 if x0 == 0 else abs(x0) * 1e-6
                self.ax.set_xlim(x0 - eps, x1 + eps)
        except Exception:
            pass
        try:
            y0, y1 = self.ax.get_ylim()
            if np.isfinite(y0) and np.isfinite(y1) and y0 == y1:
                eps = 1e-6 if y0 == 0 else abs(y0) * 1e-6
                self.ax.set_ylim(y0 - eps, y1 + eps)
        except Exception:
            pass

    # ------------------ Mode change handler ------------------
    def on_mode_changed(self, text):
        """Reset fit line data when transition type changes"""
        self.fit_line_data_x = None
        self.fit_line_data_y = None
        self.update_plot()

    # ------------------ Main update/draw ------------------
    def update_plot(self):
        if self.canvas.width() < 10 or self.canvas.height() < 10:
            return

        self.ax.clear()
        # IMPORTANT: recreate artists each draw (fixes missing ends after ax.clear())
        self.fit_line = None
        self.fit_pt_start = None
        self.fit_pt_end = None

        if self.wavelength is None:
            self.bandgap_label.setText("Load a CSV/TXT/XLSX file to begin.")
            self.bandgap_label.show()
            self._safe_tight_layout()
            self.canvas.draw_idle()
            return

        # Wavelength window
        try:
            min_wl = float(self.min_wl_input.text()) if self.min_wl_input.text() else float(np.nanmin(self.wavelength))
            max_wl = float(self.max_wl_input.text()) if self.max_wl_input.text() else float(np.nanmax(self.wavelength))
        except ValueError:
            self.bandgap_label.setText("Estimated Band Gap: Invalid Range")
            self.bandgap_label.show()
            self._safe_tight_layout()
            self.canvas.draw_idle()
            return

        mask = (self.wavelength >= min_wl) & (self.wavelength <= max_wl)
        wl = self.wavelength[mask]
        ab = self.absorbance[mask]
        tr = self.transmittance[mask]

        if len(wl) == 0:
            self.bandgap_label.setText("Estimated Band Gap: No Data")
            self.bandgap_label.show()
            self._safe_tight_layout()
            self.canvas.draw_idle()
            return

        # Tauc quantities
        d_cm = self._get_thickness_cm()
        self.E = 1241.0 / wl
        alpha = (2.303 * ab) / d_cm

        mode = self.mode_box.currentText()
        power = self.TRANSITION_MAP[mode]["power"]
        val = np.maximum(alpha * self.E, 0.0)
        self.y = val ** power

        # Styles
        self._line_width = self._parse_positive_number(self.line_width_input, self._line_width)
        self._fit_width  = self._parse_positive_number(self.fit_width_input, self._fit_width)
        self._title_size = self._parse_positive_int(self.title_size_input, self._title_size)
        self._label_size = self._parse_positive_int(self.label_size_input, self._label_size)
        self._legend_size= self._parse_positive_int(self.legend_size_input, self._legend_size)
        self._tick_size  = self._parse_positive_int(self.tick_size_input, self._tick_size)

        # Plot selection
        plot_type = self.plot_type_group.checkedId()

        if plot_type == 1:  # Absorbance
            self.bandgap_label.hide()
            self.ax.plot(wl, ab, color=self.abs_color, linewidth=self._line_width,
                         label=self.legend_text_input.text().strip() or "Absorbance",
                         **self._marker_kwargs(self.abs_color))
            self.ax.set_xlabel("Wavelength (nm)", fontsize=self._label_size)
            abs_title = "" if self.hide_abs_title_checkbox.isChecked() else (self._abs_title_text or "")
            self.ax.set_title(abs_title, fontsize=self._title_size)
            self.ax.set_ylabel(self._abs_ylabel_text, fontsize=self._label_size, fontweight='bold')

        elif plot_type == 2:  # Transmittance
            self.bandgap_label.hide()
            self.ax.plot(wl, tr, color=self.trans_color, linewidth=self._line_width,
                         label=self.legend_text_input.text().strip() or "Transmittance",
                         **self._marker_kwargs(self.trans_color))
            self.ax.set_xlabel("Wavelength (nm)", fontsize=self._label_size)
            trans_title = "" if self.hide_trans_title_checkbox.isChecked() else (self._trans_title_text or "")
            self.ax.set_title(trans_title, fontsize=self._title_size)
            self.ax.set_ylabel(self._trans_ylabel_text, fontsize=self._label_size, fontweight='bold')

        else:  # Tauc
            self.bandgap_label.show()
            self.ax.plot(self.E, self.y, color=self.tauc_color, linewidth=self._line_width,
                         label=self.legend_text_input.text().strip() or self._legend_label,
                         **self._marker_kwargs(self.tauc_color))
            self.ax.set_xlabel(r"$\mathbf{h\nu}\; \mathbf{(eV)}$", fontsize=self._label_size)
            self.ax.set_ylabel(self._tauc_ylabel(power), fontsize=self._label_size, fontweight='bold')
            title = "" if self.hide_tauc_title_checkbox.isChecked() else "Tauc Plot"
            self.ax.set_title(title, fontsize=self._title_size)

        # Legend
        handles, labels = self.ax.get_legend_handles_labels()
        if handles:
            self.ax.legend(fontsize=self._legend_size)

        # Common styling
        self.ax.grid(self.show_grid_checkbox.isChecked())
        if self.hide_y_labels_checkbox.isChecked():
            self.ax.set_yticklabels([])
        else:
            self.ax.tick_params(axis='y', which='both', left=True, labelleft=True)

        self.ax.set_facecolor('#f7f7f7')
        for spine in self.ax.spines.values():
            spine.set_edgecolor('#555555')
        self.ax.tick_params(colors='#2b2b2b', labelsize=self._tick_size)
        self.ax.xaxis.label.set_color('#2b2b2b')
        self.ax.yaxis.label.set_color('#2b2b2b')
        self.ax.title.set_color('#2b2b2b')

        # Axis limits/steps (no forced zero)
        try:
            x_min = float(self.x_min_input.text()) if self.x_min_input and self.x_min_input.text() else None
            x_max = float(self.x_max_input.text()) if self.x_max_input and self.x_max_input.text() else None
            y_min = float(self.y_min_input.text()) if self.y_min_input and self.y_min_input.text() else None
            y_max = float(self.y_max_input.text()) if self.y_max_input and self.y_max_input.text() else None
            x_step = float(self.x_step_input.text()) if self.x_step_input and self.x_step_input.text() else None
            y_step = float(self.y_step_input.text()) if self.y_step_input and self.y_step_input.text() else None
        except ValueError:
            x_min = x_max = y_min = y_max = x_step = y_step = None

        self.ax.set_xlim(left=x_min, right=x_max)
        self.ax.set_ylim(bottom=y_min, top=y_max)

        if x_step and x_step > 0:
            self.ax.xaxis.set_major_locator(MultipleLocator(x_step))
        if y_step and y_step > 0:
            self.ax.yaxis.set_major_locator(MultipleLocator(y_step))

        self._apply_current_tick_config()
        self._ensure_valid_limits()

        # ---- Sticky fit line (Tauc only) ----
        if plot_type == 3:
            if self.fit_line_data_x is None or self.fit_line_data_y is None:
                # Initialize once with auto-fit (first time only)
                m, c = self._compute_autofit()
                if m is not None and c is not None:
                    xmin, xmax = self.ax.get_xlim()
                    if not (np.isfinite(xmin) and np.isfinite(xmax) and xmax > xmin):
                        xmin, xmax = float(np.nanmin(self.E)), float(np.nanmax(self.E))
                    Eg_try = -c / m if m != 0 else xmin
                    x1 = max(xmin, Eg_try) if np.isfinite(Eg_try) else xmin
                    x2 = xmax
                    y1 = m * x1 + c
                    y2 = m * x2 + c
                    self.fit_line_data_x = np.array([x1, x2], dtype=float)
                    self.fit_line_data_y = np.array([y1, y2], dtype=float)
                    self._fit_m, self._fit_c = m, c
                    self.Eg = -c / m if m != 0 else np.nan
                else:
                    self.Eg = np.nan

            # Draw stored line and explicit endpoints (always recreate artists)
            if self.fit_line_data_x is not None and self.fit_line_data_y is not None:
                # Line
                self.fit_line, = self.ax.plot(
                    self.fit_line_data_x, self.fit_line_data_y,
                    linestyle='--', color=self.fit_color,
                    linewidth=self._fit_width,
                    label="Adjustable Fit Line", zorder=5, clip_on=False
                )
                # Endpoints
                x1, x2 = self.fit_line_data_x
                y1, y2 = self.fit_line_data_y
                self.fit_pt_start, = self.ax.plot([x1], [y1],
                    marker='o', markersize=10, markerfacecolor=self.fit_color,
                    markeredgecolor='white', markeredgewidth=1.5,
                    linestyle='None', zorder=6, clip_on=False, label='_nolegend_')
                self.fit_pt_end, = self.ax.plot([x2], [y2],
                    marker='o', markersize=10, markerfacecolor=self.fit_color,
                    markeredgecolor='white', markeredgewidth=1.5,
                    linestyle='None', zorder=6, clip_on=False, label='_nolegend_')

                # Bandgap from current endpoints
                if x2 != x1:
                    m_cur = (y2 - y1) / (x2 - x1)
                    c_cur = y1 - m_cur * x1
                    self.Eg = -c_cur / m_cur if m_cur != 0 else np.nan
                if np.isfinite(self.Eg):
                    self.bandgap_label.setText(f"Estimated Band Gap: <b>{self.Eg:.2f} eV</b>")
                else:
                    self.bandgap_label.setText("Estimated Band Gap: Fit Unavailable")

        # Apply margins safely and draw
        self._safe_tight_layout()
        self.apply_bold_font()
        self.canvas.draw_idle()

    # ------------------ Mouse (drag) handlers ------------------
    def on_click(self, event):
        # Only care on Tauc tab
        if self.plot_type_group.checkedId() != 3:
            self.dragging = False
            self.dragged_point = None
            return
        if self.fit_line_data_x is None or self.fit_line_data_y is None:
            return

        tolerance = 20  # pixels
        start_disp = self.ax.transData.transform((self.fit_line_data_x[0], self.fit_line_data_y[0]))
        end_disp   = self.ax.transData.transform((self.fit_line_data_x[1], self.fit_line_data_y[1]))
        click_disp = (event.x, event.y)

        dist_start = np.hypot(click_disp[0] - start_disp[0], click_disp[1] - start_disp[1])
        dist_end   = np.hypot(click_disp[0] - end_disp[0],   click_disp[1] - end_disp[1])

        if dist_start <= tolerance:
            self.dragging = True; self.dragged_point = 'start'
        elif dist_end <= tolerance:
            self.dragging = True; self.dragged_point = 'end'
        else:
            self.dragging = False; self.dragged_point = None

    def on_drag(self, event):
        if not self.dragging or self.dragged_point is None:
            return
        if self.fit_line_data_x is None or self.fit_line_data_y is None:
            return

        if event.xdata is not None and event.ydata is not None:
            xd, yd = event.xdata, event.ydata
        else:
            xd, yd = self.ax.transData.inverted().transform((event.x, event.y))

        if self.dragged_point == 'start':
            self.fit_line_data_x[0] = float(xd); self.fit_line_data_y[0] = float(yd)
        else:
            self.fit_line_data_x[1] = float(xd); self.fit_line_data_y[1] = float(yd)

        # Update artists
        if self.fit_line is not None:
            self.fit_line.set_data(self.fit_line_data_x, self.fit_line_data_y)
        if self.fit_pt_start is not None:
            self.fit_pt_start.set_data([self.fit_line_data_x[0]], [self.fit_line_data_y[0]])
        if self.fit_pt_end is not None:
            self.fit_pt_end.set_data([self.fit_line_data_x[1]], [self.fit_line_data_y[1]])

        self.canvas.draw_idle()

    def on_release(self, event):
        if self.dragging:
            self.dragging = False
            self.dragged_point = None
            if self.fit_line_data_x is not None:
                x1, x2 = self.fit_line_data_x
                y1, y2 = self.fit_line_data_y
                if x2 != x1:
                    m = (y2 - y1) / (x2 - x1)
                    c = y1 - m * x1
                    self.Eg = -c / m if m != 0 else np.nan
                    if np.isfinite(self.Eg):
                        self.bandgap_label.setText(f"Estimated Band Gap: <b>{self.Eg:.2f} eV</b>")

    # ------------------ Export / misc ------------------
    def export_tauc_data(self):
        if self.E is None or self.y is None:
            QMessageBox.warning(self, "Export Error", "No Tauc plot data to export. Please load data first.")
            return
        mode = self.mode_box.currentText()
        power = self.TRANSITION_MAP[mode]["power"]
        file_name = "Tauc_Plot_Data.csv"
        path, _ = QFileDialog.getSaveFileName(self, "Save Tauc Data as CSV", file_name, "CSV Files (*.csv)")
        if path:
            try:
                df_to_export = pd.DataFrame({
                    "Photon Energy (eV)": self.E,
                    f"(alpha*h*nu)^{power}": self.y
                })
                df_to_export.to_csv(path, index=False)
                QMessageBox.information(self, "Export Successful", f"Tauc data successfully exported to:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to save Tauc data: {e}")

    def pick_main_color(self):
        if hasattr(self, "radio_abs") and self.radio_abs.isChecked():
            current = self.abs_color
        elif hasattr(self, "radio_trans") and self.radio_trans.isChecked():
            current = self.trans_color
        else:
            current = self.tauc_color
        color = QColorDialog.getColor(QColor(current), self, "Choose Main Plot Color")
        if color.isValid():
            if hasattr(self, "radio_abs") and self.radio_abs.isChecked():
                self.abs_color = color.name()
            elif hasattr(self, "radio_trans") and self.radio_trans.isChecked():
                self.trans_color = color.name()
            else:
                self.tauc_color = color.name()
            self.update_plot()

    def pick_fit_color(self):
        color = QColorDialog.getColor(QColor(self.fit_color), self, "Choose Fit Line Color")
        if color.isValid():
            self.fit_color = color.name()
            self.update_plot()

    # ---------- Data load ----------
    def load_data(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Open UV-Vis Data Files",
            "",
            "Data Files (*.csv *.txt *.xlsx);;CSV (*.csv);;Text (*.txt);;Excel (*.xlsx);;All Files (*)"
        )
        if not paths:
            return

        frames = []
        errors = []
        for p in paths:
            try:
                df = self._read_two_col_file(p)
                if df is None or df.shape[1] < 2:
                    raise ValueError("File does not have at least 2 columns.")
                frames.append(df.iloc[:, :2].copy())
            except Exception as e:
                errors.append(f"{os.path.basename(p)}: {e}")

        if not frames:
            QMessageBox.critical(self, "Load Error", "No valid files were loaded.\n" + "\n".join(errors))
            return

        big = pd.concat(frames, axis=0, ignore_index=True)
        big = big.rename(columns={big.columns[0]: "wavelength_nm", big.columns[1]: "absorbance"})
        big = big.apply(pd.to_numeric, errors='coerce').dropna()
        big = big.sort_values("wavelength_nm")

        self.wavelength = big["wavelength_nm"].values
        self.absorbance = big["absorbance"].values
        self.transmittance = np.exp(-2.303 * self.absorbance) * 100

        info = f"Loaded {len(frames)} file(s), {len(big)} rows."
        if errors:
            info += f"  Skipped {len(errors)} file(s): " + "; ".join(errors[:3]) + (" ..." if len(errors) > 3 else "")
        self.loaded_info_label.setText(info)

        # Data changed: reset fit line
        self.fit_line_data_x = None
        self.fit_line_data_y = None
        self.update_plot()

    def _read_two_col_file(self, path: str) -> pd.DataFrame:
        ext = os.path.splitext(path)[1].lower()
        if ext == ".csv":
            try:
                return pd.read_csv(path, header=0)
            except Exception:
                return pd.read_csv(path, header=0, sep=';')
        elif ext == ".txt":
            try:
                return pd.read_csv(path, header=0)
            except Exception:
                return pd.read_csv(path, header=0, delim_whitespace=True)
        elif ext == ".xlsx":
            return pd.read_excel(path, header=0)
        else:
            return pd.read_csv(path, header=0)

    def _get_thickness_cm(self):
        text = self.thickness_input.text().strip()
        try:
            val = float(text) if text else 1.0
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Invalid thickness value. Using 1.0 cm.")
            return 1.0
        if val <= 0:
            QMessageBox.warning(self, "Input Error", "Thickness must be positive. Using 1.0 cm.")
            return 1.0
        unit = self.thickness_unit_box.currentText()
        factors_to_cm = {"cm": 1.0, "mm": 0.1, "µm": 1e-4, "nm": 1e-7}
        return val * factors_to_cm.get(unit, 1.0)

    # ---- Tick helpers & handlers ----
    def _parse_float_or_none(self, text):
        text = (text or "").strip()
        if text == "" or text.lower() == "auto":
            return None
        try:
            val = float(text)
            return val if np.isfinite(val) and val > 0 else None
        except Exception:
            return None

    def _apply_current_tick_config(self):
        self.ax.minorticks_on()
        if self._tick_cfg.get("x_major") is not None:
            self.ax.xaxis.set_major_locator(MultipleLocator(self._tick_cfg["x_major"]))
        if self._tick_cfg.get("x_minor") is not None:
            self.ax.xaxis.set_minor_locator(MultipleLocator(self._tick_cfg["x_minor"]))
        else:
            self.ax.xaxis.set_minor_locator(AutoMinorLocator(n=2))
        if self._tick_cfg.get("y_major") is not None:
            self.ax.yaxis.set_major_locator(MultipleLocator(self._tick_cfg["y_major"]))
        if self._tick_cfg.get("y_minor") is not None:
            self.ax.yaxis.set_minor_locator(MultipleLocator(self._tick_cfg["y_minor"]))
        else:
            self.ax.yaxis.set_minor_locator(AutoMinorLocator(n=2))
        self.apply_bold_font()

    def apply_tick_settings(self):
        x_major = self._parse_float_or_none(self.x_major_input_tick.text() if hasattr(self, "x_major_input_tick") else None)
        x_minor = self._parse_float_or_none(self.x_minor_input_tick.text() if hasattr(self, "x_minor_input_tick") else None)
        y_major = self._parse_float_or_none(self.y_major_input_tick.text() if hasattr(self, "y_major_input_tick") else None)
        y_minor = self._parse_float_or_none(self.y_minor_input_tick.text() if hasattr(self, "y_minor_input_tick") else None)
        self._tick_cfg = {"x_major": x_major, "x_minor": x_minor, "y_major": y_major, "y_minor": y_minor}
        self.update_plot()

    def reset_tick_settings(self):
        self._tick_cfg = {"x_major": None, "x_minor": None, "y_major": None, "y_minor": None}
        if hasattr(self, "x_major_input_tick"): self.x_major_input_tick.clear()
        if hasattr(self, "x_minor_input_tick"): self.x_minor_input_tick.clear()
        if hasattr(self, "y_major_input_tick"): self.y_major_input_tick.clear()
        if hasattr(self, "y_minor_input_tick"): self.y_minor_input_tick.clear()
        self.radio_tauc.setChecked(True)
        self.update_plot()

    # ------------------ Export ------------------
    def export_plot(self):
        if self.wavelength is None:
            QMessageBox.warning(self, "Export Error", "No plot to export. Please load data first.")
            return

        file_format = self.format_box.currentText()
        plot_type_id = self.plot_type_group.checkedId()

        if plot_type_id == 1:
            file_name = "Absorbance_Plot"
            title = "" if self.hide_abs_title_checkbox.isChecked() else (self._abs_title_text or "")
        elif plot_type_id == 2:
            file_name = "Transmittance_Plot"
            title = "" if self.hide_trans_title_checkbox.isChecked() else (self._trans_title_text or "")
        else:
            file_name = "Tauc_Plot"
            title = "" if self.hide_tauc_title_checkbox.isChecked() else "Tauc Plot"

        temp_fig = Figure(figsize=(8, 6), dpi=120)
        temp_ax = temp_fig.add_subplot(111)

        # Copy lines (includes endpoints since they are Line2D too)
        for line in self.ax.get_lines():
            temp_ax.plot(
                line.get_xdata(), line.get_ydata(),
                color=line.get_color(),
                linestyle=line.get_linestyle(),
                linewidth=line.get_linewidth(),
                marker=line.get_marker(), markersize=line.get_markersize(),
                markerfacecolor=line.get_markerfacecolor(), markeredgecolor=line.get_markeredgecolor()
            )

        temp_ax.set_xlabel(self.ax.get_xlabel(), fontsize=self._label_size, fontweight='bold')
        temp_ax.set_ylabel(self.ax.get_ylabel(), fontsize=self._label_size, fontweight='bold')
        temp_ax.set_title(title, fontsize=self._title_size)

        handles, labels = self.ax.get_legend_handles_labels()
        if handles:
            temp_ax.legend(handles, labels, fontsize=self._legend_size)

        temp_ax.set_facecolor(self.ax.get_facecolor())
        temp_ax.set_ylim(self.ax.get_ylim())
        temp_ax.set_xlim(self.ax.get_xlim())
        temp_ax.grid(self.show_grid_checkbox.isChecked())

        try:
            x_step = float(self.x_step_input.text()) if self.x_step_input and self.x_step_input.text() else None
            y_step = float(self.y_step_input.text()) if self.y_step_input and self.y_step_input.text() else None
        except ValueError:
            x_step = y_step = None
        if x_step and x_step > 0:
            temp_ax.xaxis.set_major_locator(MultipleLocator(x_step))
        else:
            temp_ax.xaxis.set_minor_locator(AutoMinorLocator(n=2))
        if y_step and y_step > 0:
            temp_ax.yaxis.set_major_locator(MultipleLocator(y_step))
        else:
            temp_ax.yaxis.set_minor_locator(AutoMinorLocator(n=2))

        try:
            temp_fig.subplots_adjust(left=0.20, right=0.98, bottom=0.16, top=0.92)
        except Exception:
            pass

        for tick in temp_ax.get_xticklabels():
            tick.set_fontweight('bold')
        for tick in temp_ax.get_yticklabels():
            tick.set_fontweight('bold')

        if self.hide_y_labels_checkbox.isChecked():
            temp_ax.set_yticklabels([])

        path, _ = QFileDialog.getSaveFileName(
            self, f"Save {file_name} as .{file_format}", f"{file_name}.{file_format}", f"Images (*.{file_format})"
        )
        if path:
            try:
                temp_fig.savefig(path, format=file_format, dpi=300)
                QMessageBox.information(self, "Export Successful", f"Plot successfully exported to:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to save plot: {e}")

        plt.close(temp_fig)

    # ------------------ Font weight ------------------
    def apply_bold_font(self):
        try:
            self.ax.xaxis.label.set_fontweight('bold')
            self.ax.yaxis.label.set_fontweight('bold')
            for tick in self.ax.get_xticklabels():
                tick.set_fontweight('bold')
            for tick in self.ax.get_yticklabels():
                tick.set_fontweight('bold')
        except Exception:
            pass


def main():
    app = QApplication(sys.argv)
    gui = TaucPlotGUI()
    gui.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()