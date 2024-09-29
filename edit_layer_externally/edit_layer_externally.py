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
            qDebug("verify_command returned False")
            return False
        return True

    def define_command(self):
        command = QFileDialog.getOpenFileName(None, "Browse to executable file")[0]
        qDebug(f"define_command: command = {command}")

        if command is None or command == "":
            return
        if not self.verify_command(command):
            QMessageBox.critical(
                None,
                "Configure failed:",
                f"Could not verify the validity of the command line given: {command}. "
                "Check if it is a valid path to an executable on your system.",
            )
            return

        parameters, accept = QInputDialog().getText(
            None,
            EXE_MENU_ENTRY,
            "Enter switches / run time options to add to the command line:",
        )
        if accept:
            qDebug("define_command: storing config")

            self._write_config(command, parameters, 1)
            self._read_config()

            QMessageBox.information(None, EXE_MENU_ENTRY, "Plug-in configured successfully")

    def createActions(self, window):
        action = window.createAction(EXE_EXTENSION_ID, EXE_MENU_ENTRY, "tools/scripts")
        action.triggered.connect(self.action_triggered)
        action = window.createAction(DEFINE_EXTENSION_ID, DEFINE_MENU_ENTRY, "tools/scripts")
        action.triggered.connect(self.define_command)

    def action_triggered(self):
        qDebug(f"Running Edit Layer Externally version {__version__}")
        # Get the current document and the active node (layer)
        if self.command == "":  # No command set up
            msgBox = QMessageBox()
            msgBox.setText("No command defined yet")
            msgBox.setInformativeText("Would you like to do that now?")
            msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msgBox.setDefaultButton(QMessageBox.Yes)
            if msgBox.exec() == QMessageBox.Yes:
                self.define_command()
            return

        doc = Krita.instance().activeDocument()
        if not doc:
            QMessageBox.information(None, EXE_MENU_ENTRY, "No active document found")
            return

        node = doc.activeNode()
        if not node or node.type() not in ["paintlayer", "filelayer", "clonelayer", "grouplayer"]:
            QMessageBox.information(
                None,
                EXE_MENU_ENTRY,
                "Please select a Paint layer, File layer, Clone layer or Group layer.",
            )
            return

        source_rect = node.bounds()
        colorDepth = node.colorDepth()
        colorModel = node.colorModel()
        qDebug(
            "action_trigged: reported document width, height, color depth and color model:"
            f" {source_rect.width()} x {source_rect.height()}: {colorDepth} {colorModel}"
        )

        ext = "tiff" if colorDepth in ("F16", "F32") else "png"
        # Define a temporary file path
        with TemporaryDirectory(prefix="krita_layer_") as tmpdir:
            temp_filename = os.path.join(tmpdir, f"layer.{ext}")

            # Put the filename between quotes in case it contains a space. Not sure this is
            # necessary
            if temp_filename.find(" ") != -1:
                temp_filename = f'"{temp_filename}"'
            qDebug(f"action_triggered: temp_filename = {temp_filename}")

            # Save the layer as an image
            qDebug(
                f"Saving layer with dimensions (w x h): {source_rect.width()} x {source_rect.height()}"
            )
            node.save(temp_filename, 72.0, 72.0, InfoObject(), source_rect)
            # Workaround: node.save() should return True or False, but seems to
            # always return False? Therefore, check that the file exists before
            # continuing, as the user may have pressed the cancel button in the
            # export dialog.
            if not os.path.isfile(temp_filename):
                qDebug(
                    "action_triggered: action cancelled, temporary file not detected after node.save()"
                )
                return

            # Open the image in an external editor (e.g., GIMP)
            try:
                qDebug(
                    f"action_triggered: running {self.command} {temp_filename} {self.parameters}"
                )
                subprocess.run([self.command, temp_filename, self.parameters])
            except FileNotFoundError:
                QMessageBox.information(None, EXE_MENU_ENTRY, "External editor not found.")
                return

            # Reload the image after editing
            if os.path.exists(temp_filename):
                qDebug("action_triggered: retrieving modified file")
                file_node = doc.createFileLayer(
                    f"File Layer - {node.name()}", temp_filename, "ToImageSize", "Lanczos3"
                )

                file_rect = file_node.bounds()
                qDebug(
                    f"Retrieved image has dimensions (w x h): {file_rect.width()} x {file_rect.height()}"
                )
                pixel_data = file_node.projectionPixelData(
                    file_rect.left(), file_rect.top(), file_rect.width(), file_rect.height()
                )

                # Update the Krita layer with the new image
                target = doc.createNode(f"Edited - {node.name()}", "paintlayer")
                qDebug(f"action_triggered: created target node")
                target.setPixelData(pixel_data, 0, 0, file_rect.width(), file_rect.height())
                parent = node.parentNode()
                parent.addChildNode(target, node)
                doc.refreshProjection()
                qDebug("action_triggered: done")
            else:
                QMessageBox.critical(
                    None, EXE_MENU_ENTRY, f"Could not find edited layer file '{temp_filename}'."
                )
                return
