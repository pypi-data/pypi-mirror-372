from PyInstaller.utils.hooks import get_package_paths
import os.path

(_, root) = get_package_paths('aspose')

datas = [(os.path.join(root, 'assemblies', 'threed'), os.path.join('aspose', 'assemblies', 'threed'))]

hiddenimports = [ 'aspose', 'aspose.pyreflection', 'aspose.pygc', 'aspose.pycore' ]

