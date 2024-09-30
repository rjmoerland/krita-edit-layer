# Edit Layer Externally

A Krita plug-in that runs an external application on a single paint/clone/group/file layer.

As an Adobe refugee, I've moved to Krita for my photo editing. The only thing I missed was the option to run Photoshop plug-ins on a Krita paint layer. Often, they can be used as stand-alone programs, but I quickly got tired of exporting a layer from Krita, starting the plug-in, edit, saving the file, and importing the modified layer into Krita again. That's where this little plug-in comes in handy.

After installing the plugin, you can find the script in the `Tools/Scripts/Edit Layer Externally` menu. On first use, the plug-in should ask you if you want to configure it. In case it doesn’t, or if you would like to reconfigure the external editor, use the `Tools/Scripts/Configure Edit Layer Externally` menu item. 


## Installing 

Press the button labeled "Code" on this page and download the ZIP file. Then continue the installation by following the instructions located [here](https://docs.krita.org/en/user_manual/python_scripting/install_custom_python_plugin.html).


## Configuring

First run the menu action Tools/Scripts/Configure Edit Layer Externally. Browse to an executable file with the file dialog that opens. If the executable needs any command line parameters or switches, you can add them in the dialog that opens after selecting a file. You can leave the box empty if no switches are required. Close the command line switch dialog with OK and the plugin is configured. You can reconfigure at any time by choosing Tools/Scripts/Configure Edit Layer Externally again.

**Note:** it is probably wise to not choose Krita itself as external editor, as that resulted in Krita hanging (on my Windows machine). Also, it doesn’t make a lot of sense to choose Krita as external editor, I guess.


## Use
- Select a Paint layer, Clone layer, Group layer or File layer
- Go to Tools/Scripts/Edit Layer Externally
- Export the layer according to what your external editor needs
- The external editor is opened. Modify what you need
- **Save over** the temporary file
- **Close the external editor** (Krita will not respond until you do!)

Krita will load the external layer, and incorporate it in the document as a new layer above the source.


## Notes

- The plugin requires the file type to remain unchanged between saving and loading of the layer. For example, when a layer is exported as PNG, it needs to stay a PNG. You can change the bit depth to whatever is supported by the file format, as long as it is supported by Krita.
    - Integer formats are exported as PNG.
    - Float formats are exported as TIFF.
- The dimensions of the layer (width x height) may change, but the layer size will change accordingly.
    - The top left point of the layer is the anchor


## Requirements

Tested with Krita 5.2.5 on Windows 10, and images in the RGB format with 8 and 16 bit integers per pixel. Floating point formats should work but have only been tested very lightly (read: once).

## Changelog

### v0.2.0
- Allow exporting File layers, Group layers and Clone layers
- Export Paint layers with Filter masks applied
- Use a Krita File layer to re-import the edited layer, instead of QImage
