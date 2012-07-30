bl_info = {
	'name': 'Export: Flare3D Tools',
	'author': 'David E Jones, http://davidejones.com',
	'version': (1, 0, 0),
	'blender': (2, 6, 3),
	'location': 'File > Import/Export;',
	'description': 'Importer and exporter for Flare3D engine. Supports ZF3D files"',
	'warning': '',
	'wiki_url': '',
	'tracker_url': 'http://davidejones.com',
	'category': 'Import-Export'}

import bpy, zlib, time, struct, zipfile
from bpy.props import *

#==================================
# Common Functions 
#==================================

def checkBMesh():
	a,b,c = bpy.app.version
	return (int(b) >= 63)
	
#==================================
# ZF3D IMPORTER
#==================================

class ZF3DImporterSettings:
	def __init__(self,FilePath=""):
		self.FilePath = str(FilePath)

class ZF3DImporter(bpy.types.Operator):
	bl_idname = "ops.zf3dimporter"
	bl_label = "Import ZF3D (Flare3D)"
	bl_description = "Import ZF3D (Flare3D)"
	
	filepath= StringProperty(name="File Path", description="Filepath used for importing the ZF3D file", maxlen=1024, default="")

	def execute(self, context):
		time1 = time.clock()
		
		file = open(self.filepath,'rb')
		file.seek(0)
		Config = ZF3DImporterSettings(FilePath=self.filepath)
		ZF3DImport(file,Config)
		file.close()
		
		print(".zf3d import time: %.2f" % (time.clock() - time1))
		return {'FINISHED'}
	def invoke (self, context, event):
		wm = context.window_manager
		wm.fileselect_add(self)
		return {'RUNNING_MODAL'}

def ZF3DImport(file,Config):
	print("coming soon")
	
	data = file.read()	
	if zipfile.is_zipfile(Config.FilePath):	
		zf = zipfile.ZipFile(Config.FilePath, 'r')
		print(zf.namelist())
		#print(zf.infolist())
		mainxml = zf.read("main.xml")

	file.close()
	
	return {'FINISHED'}
	
class ZF3DExporterSettings:
	def __init__(self,filePath=""):
		self.filePath = filePath

class ZF3DExporter(bpy.types.Operator):
	bl_idname = "ops.zf3dexporter"
	bl_label = "Export ZF3D (Flare3D)"
	bl_description = "Export ZF3D (Flare3D)"
	
	filepath = bpy.props.StringProperty()
	
	def execute(self, context):
		filePath = self.properties.filepath
		fp = self.properties.filepath
		if not filePath.lower().endswith('.zf3d'):
			filePath += '.zf3d'
		try:
			time1 = time.clock()
			print('Output file : %s' %filePath)
			file = open(filePath, 'wb')
			file.close()
			Config = ZF3DExporterSettings(fp)
			file = open(filePath, 'ab')
			
			ZF3DExport(file,Config)
			
			file.close()
			print(".a3d export time: %.2f" % (time.clock() - time1))
		except Exception as e:
			print(e)
			file.close()
		return {'FINISHED'}
	def invoke (self, context, event):		
		context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}
	
def menu_func_import(self, context):
	self.layout.operator(ZF3DImporter.bl_idname, text='Flare3D (.zf3d)')

def menu_func_export(self, context):
	zf3d_path = bpy.data.filepath.replace('.blend', '.zf3d')
	self.layout.operator(ZF3DExporter.bl_idname, text='Flare3D (.zf3d)').filepath = zf3d_path

def register():
	bpy.utils.register_module(__name__)
	bpy.types.INFO_MT_file_import.append(menu_func_import)
	bpy.types.INFO_MT_file_export.append(menu_func_export)
	
def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.INFO_MT_file_import.remove(menu_func_import)
	bpy.types.INFO_MT_file_export.remove(menu_func_export)
	
if __name__ == '__main__':
	register()