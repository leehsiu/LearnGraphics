import os.path
import numpy as np
import OpenGL.GL as gl
import ctypes

class BufferGeometry(object):
    def __init__(self,position, color_0, normal, texcoord):
        self.vertex_attr = np.hstack([position,color_0,normal,texcoord])
        self.count = self.vertex_attr.shape[0]
        self._vao = None
        self._vbo = None
        self.upload()

    def upload(self):

        self._vao = gl.glGenVertexArrays(1)
        self._vbo = gl.glGenBuffers(1)

        gl.glBindVertexArray(self._vao)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices,
            gl.GL_STATIC_DRAW)
        gl.glVertexAttribPointer(
            0, 3, gl.GL_FLOAT, gl.GL_FALSE,  11 * ctypes.sizeof(ctypes.c_float),
            ctypes.c_void_p(0))
        gl.glEnableVertexAttribArray(0)
        
        gl.glVertexAttribPointer(
            1, 3, gl.GL_FLOAT, gl.GL_FALSE, 11 * ctypes.sizeof(ctypes.c_float),
            ctypes.c_void_p(3 * ctypes.sizeof(ctypes.c_float)))
        gl.glEnableVertexAttribArray(1)
        
        gl.glVertexAttribPointer(
            2, 3, gl.GL_FLOAT, gl.GL_FALSE, 11 * ctypes.sizeof(ctypes.c_float),
            ctypes.c_void_p(6 * ctypes.sizeof(ctypes.c_float)))
        gl.glEnableVertexAttribArray(2)
        
        gl.glVertexAttribPointer(
            3, 2, gl.GL_FLOAT, gl.GL_FALSE, 11 * ctypes.sizeof(ctypes.c_float),
            ctypes.c_void_p(9 * ctypes.sizeof(ctypes.c_float)))
        gl.glEnableVertexAttribArray(3)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        gl.glBindVertexArray(0)

    def draw(self):
        gl.glBindVertexArray(self._vao)
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, self.count)
        gl.glBindVertexArray(0)

    def dispose(self):
        gl.glDeleteVertexArrays(1, self._vao)
        gl.glDeleteBuffers(1, self._vbo)

class Material(object):
    def __init__(self,Ka,Kd,Ks,Ns,map_Ka,map_Kd,map_Ks,map_Ns):
    
    def use(shader):
        
        
  
class Mesh(object):
    def __init__(self, geometry, material) -> None:
        self.geometry = geometry
        self.material = material
    
    def draw(self,shader):
        self.material.use(shader)
        self.geometry.draw()
    
    def dispose(self):
        self.geometry.dispose()
    
class Model(object):
    def __init__(self,meshes,textures):
        self.meshes = meshes
        self.textures = textures
    
    @classmethod
    def load_OBJ(cls,path):
        objs,mtls = load_OBJ(path)
        texture_files = []
        for mtl in mtls:
            for attr in ['map_Ka','map_Kd','map_Ks']:
                if getattr(mtl,attr) is not None:
                    texture_files.append(getattr(mtl,attr))
        texture_files = set(texture_files)
        # build map from name to ID
        
       




class MTLContent:
    def __init__(self, name):
        self.name = name
        self.Ka = None # ambient
        self.Kd = None # diffuse
        self.Ks = None # specular
        self.Ns = None # Expontional
        self.d = None # transparency
        self.Ni = None # index of refraction
        self.map_Ka = None
        self.map_Kd = None
        self.map_Ks = None
        self.map_Ns = None
        

class OBJContent:
    def __init__(self,name) -> None:
        self.name = name
        self.v = []
        self.vc = []
        self.vn = []
        self.vt = []
        
        self.mtl = None
        
    def add_face(self,indices,_v,_vc,_vn,_vt):
        indices = [self.parse_index(x) for x in indices]
        a,ua,na = indices[0]
        
        for i in range(1,len(indices)-1):
            b,ub,nb = indices[i]
            c,uc,nc = indices[i+1]
            
            # add vertex
            self.v.append(_v[a])
            self.v.append(_v[b])
            self.v.append(_v[c])
            self.vc.append(_vc[a])
            self.vc.append(_vc[b])
            self.vc.append(_vc[c])
            
            
            # add normal
            if na is None:
                vec_ab = np.array(_v[b]) - np.array(_v[a])
                vec_bc = np.array(_v[c]) - np.array(_v[b])
                vec_norm = np.cross(vec_ab,vec_bc)
                vec_norm = vec_norm / np.linalg.norm(vec_norm)
                vec_norm = vec_norm.tolist()
                self.vn.append(vec_norm)
                self.vn.append(vec_norm)
                self.vn.append(vec_norm)
            else:
                self.vn.append(_vn[na])
                self.vn.append(_vn[nb])
                self.vn.append(_vn[nc])
                
            
            if ua is None:
                self.vt.append([0.,0.])
                self.vt.append([0.,0.])
                self.vt.append([0.,0.])
            else:
                self.vt.append(_vt[ua])
                self.vt.append(_vt[ub])
                self.vt.append(_vt[uc])
                
    @staticmethod
    def parse_index(index):
        indices = index.split('/')
        v_idx = int(indices[0]) - 1
        
        vt_idx = None
        vn_idx = None
        if len(indices) == 2:
            vt_idx = int(indices[1]) - 1
        elif len(indices) == 3:
            vt_idx = int(indices[1]) - 1 if indices[1] else None
            vn_idx = int(indices[2]) - 1
        return v_idx, vt_idx, vn_idx
            
            


def load_MTL(path):
    with open(path, 'r') as f:
        text = f.read()
    lines = text.splitlines()
    mtls = []
    _mtl = None
    for line in lines:
        if not line:
            continue
        if line.startswith("#"):
            continue
        elems = line.split()
        prop = elems[0].lower()
        values = elems[1:]
        if prop == "newmtl":
            if _mtl is not None:
                mtls.append(_mtl)
            _mtl = MTLContent(line.split()[1])
                
        elif prop == "ka":
            _mtl.Ka = [float(val) for val in values]
        elif prop == "kd":
            _mtl.Kd = [float(val) for val in values]
        elif prop == "ks":
            _mtl.Ks = [float(val) for val in values]
        elif prop == "map_ka":
            _mtl.map_Ka = values
        elif prop == "map_kd":
            _mtl.map_Ka = values
        elif prop == "map_ks":
            _mtl.map_Ka = values

    return mtls
        
    
    


def load_OBJ(path):
    with open(path, 'r') as f:
        text = f.read()
    lines = text.splitlines()
    mtl_array = []
    obj_array = []
    
    _v = []
    _vt = []
    _vn = []
    _vc = []
    
    
    _object = OBJContent("")
    for line in lines:
        if not line: # empty line
            continue
        elif line.startswith("#"): # comment line
            continue
        elif line.startswith("mtllib"):
            mtl_file_name = line.split()[1]
            mtl_path = os.path.join(
                os.path.dirname(path),mtl_file_name)
            mtl_array.extend(load_MTL(mtl_path))
        elif line.startswith("o") or line.startswith("g"):
            name = line.split()[1]
            if not _object.v:
                _object.name = name
            else:
                obj_array.append(_object)
                _object = OBJContent(name)
        elif line.startswith("v "):
            v = line.split()
            v = [float(x) for x in v[1:]]
            _v.append(v[:3])
            if len(v) == 6:
                _vc.append(v[3:])
            else:
                _vc.append([1.0,1.0,1.0])
        elif line.startswith("vn "):
            vn = line.split()
            vn = [float(x) for x in vn[1:]]
            _vn.append(vn)
        elif line.startswith("vt "):
            vt = line.split()
            vt = [float(x) for x in vt[1:]]
            _vt.append(vt)
        elif line.startswith("f "):
            indices = line.split()[1:]
            _object.add_face(indices, _v, _vc, _vn, _vt)
        elif line.startswith("usemtl "):
            mtl = line.split()[1]
            _object.mtl = mtl
    obj_array.append(_object)
    return obj_array,mtl_array
    
if __name__=="__main__":
    file = '../../assets/objects/lego/lego.obj'
    #file = '../../assets/objects/backpack/backpack.obj'
    objs,mtls = load_OBJ(file)
    for o in objs:
        print(o.name,o.mtl)
    
    for mtl in mtls:
        print(mtl.name)