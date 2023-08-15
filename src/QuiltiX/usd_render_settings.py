from Qt import QtWidgets, QtCore  # type: ignore
from NodeGraphQt.custom_widgets.properties_bin import node_property_widgets
from QuiltiX.constants import VALUE_DECIMALS

from pxr.Usdviewq.stageView import UsdImagingGL  # type: ignore

# Inherit from _PropertiesList so the layouts & styling are the same
class RenderSettingsWidget(node_property_widgets._PropertiesList):
    def __init__(self, stage_view, window_title="Render Settings"):
        super(RenderSettingsWidget, self).__init__()
        self.stage_view = stage_view

        # Imitate node_property_widgets._PropertiesContainer
        self._main_widget = QtWidgets.QWidget()
        self._main_grid_layout = QtWidgets.QGridLayout()
        self._main_grid_layout.setColumnStretch(1, 1)
        self._main_grid_layout.setSpacing(6)

        layout = QtWidgets.QVBoxLayout(self._main_widget)
        layout.setAlignment(QtCore.Qt.AlignTop)
        layout.addLayout(self._main_grid_layout)

        self.insertRow(0)
        self.setCellWidget(0, 0, self._main_widget)

    def on_renderer_changed(self):
        self._clear_widgets()
        self._populate_widgets()

    def _clear_widgets(self):
        for i in reversed(range(self._main_grid_layout.count())):
            item_to_remove = self._main_grid_layout.itemAt(i)
            if item_to_remove:
                widget_to_remove = item_to_remove.widget()
                if widget_to_remove:
                    self._main_grid_layout.removeWidget(widget_to_remove)
                    widget_to_remove.deleteLater()

    def _populate_widgets(self):
        settings = self.stage_view.GetRendererSettingsList()

        label_flags = QtCore.Qt.AlignCenter | QtCore.Qt.AlignRight

        for i, setting in enumerate(settings):
            label = f"{str(setting.key)}: "
            value = self.stage_view.GetRendererSetting(setting.key)
            self._main_grid_layout.addWidget(QtWidgets.QLabel(label), i, 0, label_flags)

            if setting.type == UsdImagingGL.RendererSettingType.FLAG:
                checkBox = QtWidgets.QCheckBox(self._main_widget)

                checkBox.setChecked(value)

                checkBox.toggled.connect(lambda v, setting=setting: self.stage_view.SetRendererSetting(setting.key, v))

                self._main_grid_layout.addWidget(checkBox, i, 1)

            elif setting.type == UsdImagingGL.RendererSettingType.INT:
                spinBox = QtWidgets.QSpinBox(self._main_widget)
                spinBox.wheelEvent = lambda _: None

                spinBox.setMinimum(-(2**31))
                spinBox.setMaximum(2**31 - 1)

                spinBox.setValue(self.stage_view.GetRendererSetting(setting.key))

                spinBox.valueChanged.connect(
                    lambda v, setting=setting: self.stage_view.SetRendererSetting(setting.key, v)
                )

                self._main_grid_layout.addWidget(QtWidgets.QLabel(label), i, 0, label_flags)
                self._main_grid_layout.addWidget(spinBox, i, 1)

            elif setting.type == UsdImagingGL.RendererSettingType.FLOAT:
                spinBox = QtWidgets.QDoubleSpinBox(self._main_widget)
                spinBox.wheelEvent = lambda _: None

                spinBox.setDecimals(VALUE_DECIMALS)
                spinBox.setMinimum(-(2**31))
                spinBox.setMaximum(2**31 - 1)

                spinBox.setValue(self.stage_view.GetRendererSetting(setting.key))

                spinBox.valueChanged.connect(
                    lambda v, setting=setting: self.stage_view.SetRendererSetting(setting.key, v)
                )

                self._main_grid_layout.addWidget(spinBox, i, 1)

            elif setting.type == UsdImagingGL.RendererSettingType.STRING:
                lineEdit = QtWidgets.QLineEdit(self._main_widget)

                lineEdit.setText(self.stage_view.GetRendererSetting(setting.key))

                lineEdit.textChanged.connect(
                    lambda v, setting=setting: self.stage_view.SetRendererSetting(setting.key, v)
                )

                self._main_grid_layout.addWidget(lineEdit, i, 1)

        # FIXME: make sure the widget renders. somehow the widget or its contents only render after resizing??
