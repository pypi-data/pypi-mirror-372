class MenuOptions:
    """
    MenuOptions class provides methods to control various menu-related settings
    for the trading chart interface.
    """

    def __init__(self, trader):
        self.instance = trader.instance
        self.trader_id = trader.id

    def show_chart_title_input(self, show_input: bool):
        """Shows or hides the chart title input in the menu.

        Args:
            show_input (bool): Set True to show the chart title input, False to hide it.
        """
        self.instance.send(self.trader_id, 'showChartTitleInput', {'showInput': show_input})
        return self

    def show_currency_input(self, show_input: bool):
        """Shows or hides the currency input in the menu.

        Args:
            show_input (bool): Set True to show the currency input, False to hide it.
        """
        self.instance.send(self.trader_id, 'showCurrencyInput', {'showInput': show_input})
        return self

    def show_watermark_text_input(self, show_input: bool):
        """Shows or hides the watermark text input in the menu.

        Args:
            show_input (bool): Set True to show the watermark text input, False to hide it.
        """
        self.instance.send(self.trader_id, 'showWatermarkTextInput', {'showInput': show_input})
        return self

    def show_axis_on_right_checkbox(self, show_checkbox: bool):
        """Shows or hides the axis on right checkbox in the menu.

        Args:
            show_checkbox (bool): Set True to show the checkbox, False to hide it.
        """
        self.instance.send(self.trader_id, 'showAxisOnRightCheckbox', {'showCheckbox': show_checkbox})
        return self

    def show_percent_scale_checkbox(self, show_checkbox: bool):
        """Shows or hides the percent scale checkbox in the menu.

        Args:
            show_checkbox (bool): Set True to show the checkbox, False to hide it.
        """
        self.instance.send(self.trader_id, 'showPercentScaleCheckbox', {'showCheckbox': show_checkbox})
        return self

    def show_data_packing_checkbox(self, show_checkbox: bool):
        """Shows or hides the data packing checkbox in the menu.

        Args:
            show_checkbox (bool): Set True to show the checkbox, False to hide it.
        """
        self.instance.send(self.trader_id, 'showDataPackingCheckbox', {'showCheckbox': show_checkbox})
        return self

    def show_zoom_band_checkbox(self, show_checkbox: bool):
        """Shows or hides the zoom band checkbox in the menu.

        Args:
            show_checkbox (bool): Set True to show the checkbox, False to hide it.
        """
        self.instance.send(self.trader_id, 'showZoomBandCheckbox', {'showCheckbox': show_checkbox})
        return self

    def show_show_title_checkbox(self, show_checkbox: bool):
        """Shows or hides the show title checkbox in the menu.

        Args:
            show_checkbox (bool): Set True to show the checkbox, False to hide it.
        """
        self.instance.send(self.trader_id, 'showShowTitleCheckbox', {'showCheckbox': show_checkbox})
        return self

    def show_show_splitters_checkbox(self, show_checkbox: bool):
        """Shows or hides the show splitters checkbox in the menu.

        Args:
            show_checkbox (bool): Set True to show the checkbox, False to hide it.
        """
        self.instance.send(self.trader_id, 'showShowSplittersCheckbox', {'showCheckbox': show_checkbox})
        return self

    def show_show_search_checkbox(self, show_checkbox: bool):
        """Shows or hides the show search checkbox in the menu.

        Args:
            show_checkbox (bool): Set True to show the checkbox, False to hide it.
        """
        self.instance.send(self.trader_id, 'showShowSearchCheckbox', {'showCheckbox': show_checkbox})
        return self

    def show_show_file_selection_checkbox(self, show_checkbox: bool):
        """Shows or hides the show file selection checkbox in the menu.

        Args:
            show_checkbox (bool): Set True to show the checkbox, False to hide it.
        """
        self.instance.send(self.trader_id, 'showShowFileSelectionCheckbox', {'showCheckbox': show_checkbox})
        return self

    def show_allow_hide_toolbar_checkbox(self, show_checkbox: bool):
        """Shows or hides the allow hide toolbar checkbox in the menu.

        Args:
            show_checkbox (bool): Set True to show the checkbox, False to hide it.
        """
        self.instance.send(self.trader_id, 'showAllowHideToolbarCheckbox', {'showCheckbox': show_checkbox})
        return self

    def show_show_watermark_checkbox(self, show_checkbox: bool):
        """Shows or hides the show watermark checkbox in the menu.

        Args:
            show_checkbox (bool): Set True to show the checkbox, False to hide it.
        """
        self.instance.send(self.trader_id, 'showShowWatermarkCheckbox', {'showCheckbox': show_checkbox})
        return self

    def show_horizontal_line_checkbox(self, show_checkbox: bool):
        """Shows or hides the horizontal line checkbox in the menu.

        Args:
            show_checkbox (bool): Set True to show the checkbox, False to hide it.
        """
        self.instance.send(self.trader_id, 'showHorizontalLineCheckbox', {'showCheckbox': show_checkbox})
        return self

    def show_vertical_line_checkbox(self, show_checkbox: bool):
        """Shows or hides the vertical line checkbox in the menu.

        Args:
            show_checkbox (bool): Set True to show the checkbox, False to hide it.
        """
        self.instance.send(self.trader_id, 'showVerticalLineCheckbox', {'showCheckbox': show_checkbox})
        return self

    def show_vertical_zoom_checkbox(self, show_checkbox: bool):
        """Shows or hides the vertical zoom checkbox in the menu.

        Args:
            show_checkbox (bool): Set True to show the checkbox, False to hide it.
        """
        self.instance.send(self.trader_id, 'showVerticalZoomCheckbox', {'showCheckbox': show_checkbox})
        return self

    def show_vertical_pan_checkbox(self, show_checkbox: bool):
        """Shows or hides the vertical pan checkbox in the menu.

        Args:
            show_checkbox (bool): Set True to show the checkbox, False to hide it.
        """
        self.instance.send(self.trader_id, 'showVerticalPanCheckbox', {'showCheckbox': show_checkbox})
        return self

    def show_restrict_x_checkbox(self, show_checkbox: bool):
        """Shows or hides the restrict X checkbox in the menu.

        Args:
            show_checkbox (bool): Set True to show the checkbox, False to hide it.
        """
        self.instance.send(self.trader_id, 'showRestrictXCheckbox', {'showCheckbox': show_checkbox})
        return self

    def show_restrict_y_checkbox(self, show_checkbox: bool):
        """Shows or hides the restrict Y checkbox in the menu.

        Args:
            show_checkbox (bool): Set True to show the checkbox, False to hide it.
        """
        self.instance.send(self.trader_id, 'showRestrictYCheckbox', {'showCheckbox': show_checkbox})
        return self

    def show_cursor_tracking_dropdown(self, show_dropdown: bool):
        """Shows or hides the cursor tracking dropdown in the menu.

        Args:
            show_dropdown (bool): Set True to show the dropdown, False to hide it.
        """
        self.instance.send(self.trader_id, 'showCursorTrackingDropdown', {'showDropdown': show_dropdown})
        return self

    def show_result_table_dropdown(self, show_dropdown: bool):
        """Shows or hides the result table dropdown in the menu.

        Args:
            show_dropdown (bool): Set True to show the dropdown, False to hide it.
        """
        self.instance.send(self.trader_id, 'showResultTableDropdown', {'showDropdown': show_dropdown})
        return self

    def show_wheel_zoom_dropdown(self, show_dropdown: bool):
        """Shows or hides the wheel zoom dropdown in the menu.

        Args:
            show_dropdown (bool): Set True to show the dropdown, False to hide it.
        """
        self.instance.send(self.trader_id, 'showWheelZoomDropdown', {'showDropdown': show_dropdown})
        return self

    def show_rectangle_zoom_dropdown(self, show_dropdown: bool):
        """Shows or hides the rectangle zoom dropdown in the menu.

        Args:
            show_dropdown (bool): Set True to show the dropdown, False to hide it.
        """
        self.instance.send(self.trader_id, 'showRectangleZoomDropdown', {'showDropdown': show_dropdown})
        return self

    def show_panning_dropdown(self, show_dropdown: bool):
        """Shows or hides the panning dropdown in the menu.

        Args:
            show_dropdown (bool): Set True to show the dropdown, False to hide it.
        """
        self.instance.send(self.trader_id, 'showPanningDropdown', {'showDropdown': show_dropdown})
        return self

    def show_theme_dropdown(self, show_dropdown: bool):
        """Shows or hides the theme dropdown in the menu.

        Args:
            show_dropdown (bool): Set True to show the dropdown, False to hide it.
        """
        self.instance.send(self.trader_id, 'showThemeDropdown', {'showDropdown': show_dropdown})
        return self

    def show_fill_style_dropdown(self, show_dropdown: bool):
        """Shows or hides the fill style dropdown in the menu.

        Args:
            show_dropdown (bool): Set True to show the dropdown, False to hide it.
        """
        self.instance.send(self.trader_id, 'showFillStyleDropdown', {'showDropdown': show_dropdown})
        return self

    def show_positive_body_input(self, show_input: bool):
        """Shows or hides the positive body color input in the menu.

        Args:
            show_input (bool): Set True to show the input, False to hide it.
        """
        self.instance.send(self.trader_id, 'showPositiveBodyInput', {'showInput': show_input})
        return self

    def show_positive_wick_input(self, show_input: bool):
        """Shows or hides the positive wick color input in the menu.

        Args:
            show_input (bool): Set True to show the input, False to hide it.
        """
        self.instance.send(self.trader_id, 'showPositiveWickInput', {'showInput': show_input})
        return self

    def show_negative_body_input(self, show_input: bool):
        """Shows or hides the negative body color input in the menu.

        Args:
            show_input (bool): Set True to show the input, False to hide it.
        """
        self.instance.send(self.trader_id, 'showNegativeBodyInput', {'showInput': show_input})
        return self

    def show_negative_wick_input(self, show_input: bool):
        """Shows or hides the negative wick color input in the menu.

        Args:
            show_input (bool): Set True to show the input, False to hide it.
        """
        self.instance.send(self.trader_id, 'showNegativeWickInput', {'showInput': show_input})
        return self

    def show_line_color_input(self, show_input: bool):
        """Shows or hides the line color input in the menu.

        Args:
            show_input (bool): Set True to show the input, False to hide it.
        """
        self.instance.send(self.trader_id, 'showLineColorInput', {'showInput': show_input})
        return self

    def show_background_color_input(self, show_input: bool):
        """Shows or hides the background color input in the menu.

        Args:
            show_input (bool): Set True to show the input, False to hide it.
        """
        self.instance.send(self.trader_id, 'showBackgroundColorInput', {'showInput': show_input})
        return self

    def show_series_color_input(self, show_input: bool):
        """Shows or hides the series color input in the menu.

        Args:
            show_input (bool): Set True to show the input, False to hide it.
        """
        self.instance.send(self.trader_id, 'showSeriesColorInput', {'showInput': show_input})
        return self

    def show_gradient_color_input(self, show_input: bool):
        """Shows or hides the gradient color input in the menu.

        Args:
            show_input (bool): Set True to show the input, False to hide it.
        """
        self.instance.send(self.trader_id, 'showGradientColorInput', {'showInput': show_input})
        return self

    def show_mountain_gradient_checkbox(self, show_checkbox: bool):
        """Shows or hides the mountain gradient checkbox in the menu.

        Args:
            show_checkbox (bool): Set True to show the checkbox, False to hide it.
        """
        self.instance.send(self.trader_id, 'showMountainGradientCheckbox', {'showCheckbox': show_checkbox})
        return self

    def show_shadow_glow_checkbox(self, show_checkbox: bool):
        """Shows or hides the shadow glow checkbox in the menu.

        Args:
            show_checkbox (bool): Set True to show the checkbox, False to hide it.
        """
        self.instance.send(self.trader_id, 'showShadowGlowCheckbox', {'showCheckbox': show_checkbox})
        return self

    def show_show_image_checkbox(self, show_checkbox: bool):
        """Shows or hides the show image checkbox in the menu.

        Args:
            show_checkbox (bool): Set True to show the checkbox, False to hide it.
        """
        self.instance.send(self.trader_id, 'showShowImageCheckbox', {'showCheckbox': show_checkbox})
        return self

    def show_angle_input(self, show_input: bool):
        """Shows or hides the angle input in the menu.

        Args:
            show_input (bool): Set True to show the input, False to hide it.
        """
        self.instance.send(self.trader_id, 'showAngleInput', {'showInput': show_input})
        return self

    def show_gradient_speed_input(self, show_input: bool):
        """Shows or hides the gradient speed input in the menu.

        Args:
            show_input (bool): Set True to show the input, False to hide it.
        """
        self.instance.send(self.trader_id, 'showGradientSpeedInput', {'showInput': show_input})
        return self

    def show_radial_x_input(self, show_input: bool):
        """Shows or hides the radial X input in the menu.

        Args:
            show_input (bool): Set True to show the input, False to hide it.
        """
        self.instance.send(self.trader_id, 'showRadialXInput', {'showInput': show_input})
        return self

    def show_radial_y_input(self, show_input: bool):
        """Shows or hides the radial Y input in the menu.

        Args:
            show_input (bool): Set True to show the input, False to hide it.
        """
        self.instance.send(self.trader_id, 'showRadialYInput', {'showInput': show_input})
        return self
