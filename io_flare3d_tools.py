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

import bpy, zlib, time, struct, zipfile, io
from struct import unpack, pack, calcsize
from bpy.props import *
from xml.etree import ElementTree as ET

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
	
	surfaces,maps,materials,nodes = [],[],[],[]
	
	data = file.read()	
	
	if zipfile.is_zipfile(Config.FilePath):	
		zf = zipfile.ZipFile(Config.FilePath, 'r')
		print(zf.namelist())
		#print(zf.infolist())
		mainxml = zf.read("main.xml")
		
		surfaces,maps,materials,nodes = parseMainXML(mainxml,Config)
		
		#open .vertex file
		vertex0 = zf.read("0.vertex")
		#file = open(vertex0,'rb')
		#file.seek(0)
		b = io.BytesIO(vertex0)
		bdata = b.getvalue()
		#print(b.read1(4))
		#view = b.getbuffer()
		#print(b.getvalue())
		
		
		verts = []
		faces = []
		uvs = []
		norms = []
		
		inputs = {}
		inputs["POSITION"] = []
		inputs["NORMAL"] = []
		inputs["UV0"] = []
		inputs["UV1"] = []
		
		for xs in surfaces:
		
			numflts = 0
			for att in xs._inputs:
				if att == "POSITION":
					#position
					numflts = numflts + 3
				if att == "NORMAL":
					#normal
					numflts = numflts + 3
				if att == "UV0":
					#tangent
					numflts = numflts + 2
				if att == "UV1":
					#joint
					numflts = numflts + 2
			flcount = int(len(bdata)/4)
			points = int(flcount/numflts)
			
			print(flcount)
			print(numflts)
			print(points)
			
			i = 0
			for p in range(points):
				for att in xs._inputs:
					if att == "POSITION":
						x = unpack(">f",b.read1(4))[0]
						y = unpack(">f",b.read1(4))[0]
						z = unpack(">f",b.read1(4))[0]
						verts.append((x, y, z))
						#faces.append((i,i+1,i+2))
						#i = i + 1
					if att == "NORMAL":
						b.read1(4)
						b.read1(4)
						b.read1(4)
					if att == "UV0":
						b.read1(4)
						b.read1(4)
					if att == "UV1":
						b.read1(4)
						b.read1(4)
				
		#print(faces)
		#print(verts)
		
		# create a new mesh  
		me = bpy.data.meshes.new("Mesh") 
		
		# create an object with that mesh
		ob = bpy.data.objects.new("Mesh", me)  
		
		# position object at 3d-cursor
		ob.location = bpy.context.scene.cursor_location
		
		# Link object to scene
		bpy.context.scene.objects.link(ob)  
		
		# edges or faces should be [], or you ask for problems
		me.from_pydata(verts,[],faces)
		
	else:
		print("Error the file selected isn't recognized as zip compression")

	file.close()
	
	return {'FINISHED'}

def format2Byte(fmt,b):
	ret = None
	if fmt == "float3":
		ret = unpack(">fff",b.read1(12))[0]
	elif fmt == "float2":
		ret = unpack(">ff",b.read1(8))[0]
	else:
		print("Unrecognised format")
	return ret
	
def parseMainXML(xml,Config):
	root = ET.XML(xml)
	#print(root)
	#print(list(root))
	
	surfaces = []
	maps = []
	materials = []
	nodes = []
	
	elem_surfaces,elem_maps,elem_materials,elem_nodes = list(root)
	
	for x in range(len(elem_surfaces)):
		xs = XMLSurface(Config)
		surfaces.append(xs.read(elem_surfaces[x]))
		
	#for x in range(len(elem_maps)):
	#	xmp = XMLMap(Config)
	#	maps.append(xmp.read(elem_maps[x]))
		
	#for x in range(len(elem_materials)):
	#	xmt = XMLMaterial(Config)
	#	materials.append(xmt.read(elem_materials[x]))
		
	#for x in range(len(elem_nodes)):
	#	xno = XMLNode(Config)
	#	nodes.append(xno.read(elem_nodes[x]))
	
	return surfaces,maps,materials,nodes

			
class XMLSurface:
	def __init__(self,Config):
		self._id = 0
		self._source = None
		self._sizePerVertex = 0
		self._inputs = []
		self._formats = []
		self.Config = Config
	
	def read(self,elem):
		#print(elem[x].tag)
		#print(elem[x].items())
		#print(elem[x].get("id"))
		#print(elem[x].get("sizePerVertex"))
		#print(elem[x].get("inputs"))
		#print(elem[x].get("formats"))
		self._id = elem.get("id")
		self._sizePerVertex = elem.get("sizePerVertex")
		self._inputs = elem.get("inputs").split(",")
		self._formats = elem.get("formats").split(",")
		return self
		
class XMLMap:
	def __init__(self,Config):
		self._id = 0
		self._type = None
		self._channel = 0
		self._source = []
		self._uvOffset = []
		self._uvRepeat = []
		self.Config = Config
	
	def read(self,elem):
		self._id = elem.get("id")
		self._type = elem.get("type")
		self._channel = elem.get("channel")
		self._source = elem.get("source")
		#self._uvOffset = elem[x].get("formats")
		#self._uvRepeat = elem[x].get("formats")
		return self
		
class XMLMaterial:
	def __init__(self,Config):
		self._id = 0
		self._name = ""
		self._twoSided = true
		self._opacity = 100
		self._diffuse = []
		self._specular = []
		self.Config = Config
	
	def read(self,elem):
		self._id = elem.get("id")
		self._name = elem.get("name")
		self._twoSided = elem.get("twoSided")
		self._opacity = elem.get("opacity")
		#self._diffuse = elem[x].get("formats")
		#self._specular = elem[x].get("formats")
		return self
		
class XMLMeshNode:
	def __init__(self,Config):
		self._id = 0
		self._name = ""
		self._type = true
		self._surfaces = 100
		self._materials = []
		self._min = []
		self._max = []
		self._center = []
		self._radius = []
		self._transform = []
		self.Config = Config
	
	def read(self,elem):
		self._id = elem.get("id")
		self._name = elem.get("name")
		self._twoSided = elem.get("twoSided")
		self._opacity = elem.get("opacity")
		#self._diffuse = elem[x].get("formats")
		#self._specular = elem[x].get("formats")
		return self
		
class XMLCameraNode:
	def __init__(self,Config):
		self._id = 0
		self._name = ""
		self._type = true
		self._class = 100
		self._fov = []
		self._nearclip = []
		self._farclip = []
		self._active = []
		self._transform = []
		self.Config = Config
	
	def read(self,elem):
		self._id = elem.get("id")
		self._name = elem.get("name")
		self._twoSided = elem.get("twoSided")
		self._opacity = elem.get("opacity")
		#self._diffuse = elem[x].get("formats")
		#self._specular = elem[x].get("formats")
		return self
			
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
			print(".zf3d export time: %.2f" % (time.clock() - time1))
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