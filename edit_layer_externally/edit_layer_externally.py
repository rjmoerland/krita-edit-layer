# Extension skeleton based on BBD's Krita Script Starter Feb 2018

import os
import subprocess
from tempfile import TemporaryDirectory

from krita import Extension, InfoObject, Krita, QRect, qDebug
from PyQt5.Qt import QByteArray, QImage
from PyQt5.QtWidgets import QFileDialog, QInputDialog, QMessageBox

from .__about__ import __version__

EXE_EXTENSION_ID = "pykrita_edit_layer_externally"
DEFINE_EXTENSION_ID = "pykrita_config_edit_layer_externally"
EXE_MENU_ENTRY = "Edit Layer Externally"
DEFINE_MENU_ENTRY = "Configure Edit Layer Externally"


class EditLayerExternally(Extension):

    def __init__(self, parent):
        # Always initialise the superclass.
        # This is necessary to create the underlying C++ object
        self.msgBox = QMessageBox(None)
        super().__init__(parent)

    def _read_config(self, slot: int = 1):
        qDebug(f"_read_config: slot = {slot}")
        self.command = Krita.instance().readSetting("Edit Layer Externally", f"command_{slot}", "")
        self.parameters = Krita.instance().readSetting(
            "Edit Layer Externally", f"parameters_{slot}", ""
        )
        qDebug(f"_read_config: command = {self.command}")
        qDebug(f"_read_config: parameters = {self.parameters}")

    def _write_config(self, command: str, parameters: str, slot: int = 1):
        qDebug(f"_write_config: command = {command}")
        qDebug(f"_write_config: parameters = {parameters}")
        qDebug(f"_write_config: slot = {slot}")

        Krita.instance().writeSetting("Edit Layer Externally", f"command_{slot}", command)
        Krita.instance().writeSetting("Edit Layer Externally", f"parameters_{slot}", parameters)

    def setup(self):
        qDebug(f"Edit Layer Externally setup reporting version {__version__}")
        self._read_config()

    def verify_command(self, command_string: str):
        if not os.path.isfile(command_string):
            qDebug(f"verify_command returned False")
            return False
        return True

    def define_command(self):
        command = QFileDialog.getOpenFileName(None, "Browse to executable file")[0]
        qDebug(f"define_command: command = {command}")

        if command is None or command == "":
            return
        if not self.verify_command(command):
            self.msgBox.setText(
                f"Could not verify the validity of the command line given: {command}. "
                "Check if it is a valid path to an executable on your system."
            )
            self.msgBox.exec()
            return

        parameters, accept = QInputDialog().getText(
            None,
            "Edit Layer Externally",
            "Enter switches / run time options to add to the command line:",
        )
        if accept:
            qDebug(f"define_command: storing config")

            self._write_config(command, parameters, 1)
            self._read_config()
            self.msgBox.setText("Plug-in configured successfully")
            self.msgBox.exec()

    def createActions(self, window):
        action = window.createAction(EXE_EXTENSION_ID, EXE_MENU_ENTRY, "tools/scripts")
        action.triggered.connect(self.action_triggered)
        action = window.createAction(DEFINE_EXTENSION_ID, DEFINE_MENU_ENTRY, "tools/scripts")
        action.triggered.connect(self.define_command)

    def action_triggered(self):
        qDebug(f"Running Edit Layer Externally version {__version__}")
        # Get the current document and the active node (layer)
        if self.command == "":  # No command set up
            self.msgBox.setText("No command defined yet")
            self.msgBox.setInformativeText("Would you like to do that now?")
            self.msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            self.msgBox.setDefaultButton(QMessageBox.Yes)
            if self.msgBox.exec() == QMessageBox.Yes:
                self.define_command()
            return

        doc = Krita.instance().activeDocument()
        if not doc:
            self.msgBox.setText("No active document found")
            self.msgBox.exec()
            return

        node = doc.activeNode()
        if not node or not node.type() == "paintlayer":
            self.msgBox.setText("Please select a paint layer.")
            self.msgBox.exec()
            return

        width, height = doc.width(), doc.height()
        colorDepth = node.colorDepth()
        colorModel = node.colorModel()
        qDebug(
            f"action_trigged: reported document width, height, color depth and color model: {width} x {height}: {colorDepth} {colorModel}"
        )

        ext = "tiff" if colorDepth in ("F16", "F32") else "png"
        # Define a temporary file path
        with TemporaryDirectory(prefix="krita_layer_") as tmpdir:
            temp_filename = os.path.join(tmpdir, f"layer.{ext}")

            # Not sure this is necessary
            if temp_filename.find(" ") != -1:
                temp_filename = f'"{temp_filename}"'
            qDebug(f"action_triggered: temp_filename = {temp_filename}")

            # Save the layer as an image
            qDebug(f"Saving layer with dimensions (w x h): {width} x {height}")
            node.save(temp_filename, 72.0, 72.0, InfoObject(), QRect(0, 0, width, height))
            # Workaround: node.save() should return True or False, but seems to
            # always return False? Therefore, check that the file exists before
            # continuing, as the user may have pressed the cancel button in the
            # export dialog.
            if not os.path.isfile(temp_filename):
                qDebug(f"action_triggered: action cancelled, temporary file not detected after node.save()")
                return
            clone = node.duplicate()
            clone.setName(f"Edited - {node.name()}")
            parent = node.parentNode()
            parent.addChildNode(clone, node)
            qDebug(f"action_triggered: duplicated source node")

            # Open the image in an external editor (e.g., GIMP)
            try:
                qDebug(
                    f"action_triggered: running {self.command} {temp_filename} {self.parameters}"
                )
                subprocess.run([self.command, temp_filename, self.parameters])
            except FileNotFoundError:
                self.msgBox.setText("External editor not found.")
                self.msgBox.exec()
                return

            # Reload the image after editing
            if os.path.exists(temp_filename):
                qDebug("action_triggered: retrieving modified file")
                image = QImage()
                success = image.load(temp_filename)
                if not success:
                    self.msgBox.setText(f"Edited layer file could not be loaded successfully.")
                    self.msgBox.exec()
                    return
                rect = image.rect()
                qDebug(f"Retrieved image has dimensions (w x h): {rect.width()} x {rect.height()}")

                if (rect.width() != width) or (rect.height() != height):
                    self.msgBox.setText(
                        f"The dimensions of the layer file mismatch with the document."
                    )
                    self.msgBox.exec()
                    return

                # Based on limited testing, U8 images do not need to have their bytes swapped, but U16 do need it.
                # No idea about floating point formats however.
                if colorDepth == "U16" and colorModel == "RGBA":
                    qDebug("U16 color format, swapping RGB data to BGR")
                    image = image.rgbSwapped()
                pixel_data = image.bits()
                pixel_data.setsize(image.byteCount())

                # Update the Krita layer with the new image
                clone.setPixelData(QByteArray(pixel_data.asstring()), 0, 0, width, height)
                doc.refreshProjection()
                qDebug("action_triggered: done")
            else:
                self.msgBox.setText(f"Could not find edited layer file '{temp_filename}'.")
                self.msgBox.exec()
                return
