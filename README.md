# Edit Layer Externally
A Krita plug-in that runs an external application on a single paint layer.

As an Adobe refugee, I've moved to Krita for my photo editing. The only thing I missed was the option to run Photoshop plug-ins on a Krita paint later. Often, they can be used as stand-alone programs, but I quickly got tired of exporting a layer from Krita, starting the plug-in, edit, saving the file, and importing the modified layer into Krita again. That's where this little plug-in comes in handy.

After installing the plugin,you can find the script in the `Tools/Scripts/Edit Layer Externally` menu. On first use, the plug-in should ask you if you want to configure it. In case it doesn’t, or if you would like to reconfigure the external editor, use the `Tools/Scripts/Configure Edit Layer Externally` menu item. 

## Installing 

Press the button labeled "Code" on this page and download the ZIP file. Then continue the installation by following the instructions located [here](https://docs.krita.org/en/user_manual/python_scripting/install_custom_python_plugin.html).

## Configuring

First run the menu action Tools/Scripts/Configure Edit Layer Externally. Browse to an executable file with the file dialog that opens. If the executable needs any command line parameters or switches, you can add them in the dialog that opens after selecting a file. You can leave the box empty if no switches are required. Close the command line switch dialog with OK and the plugin is configured. You can reconfigure at any time by choosing Tools/Scripts/Configure Edit Layer Externally again.

**Note:** it is probably wise to not choose Krita itself as external editor, as that resulted in Krita hanging (on my Windows machine). Also, doesn’t make a lot of sense to choose Krita as external editor, I guess.

## Use
- Select a paint layer
- Go to Tools/Scripts/Edit Layer Externally
- Export the layer according to what your external editor needs
- The external editor is opened. Modify what you need
- Save over the temporary file
- Close the external editor

Krita will load the external layer, and incorporate it in the document as a new layer above the source.
 
## Requirements

Tested with Krita 2.5.3 on Windows 10, and images in the RGB format with 8 and 16 bit integers per pixel.
