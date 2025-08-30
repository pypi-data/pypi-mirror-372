from PyInstaller.utils.hooks import get_package_paths
import os.path

(_, root) = get_package_paths('aspose')

datas = [(os.path.join(root, 'assemblies', 'barcode'), os.path.join('aspose', 'assemblies', 'barcode'))]

hiddenimports = [ 'aspose', 'aspose.pyreflection', 'aspose.pydrawing', 'aspose.pygc', 'aspose.pycore' ]

