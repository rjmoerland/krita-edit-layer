import krita
from .edit_layer_externally import EditLayerExternally

# And add the extension to Krita's list of extensions:
app = krita.Krita.instance()
# Instantiate the plugin:
extension = EditLayerExternally(parent=app)
app.addExtension(extension)
