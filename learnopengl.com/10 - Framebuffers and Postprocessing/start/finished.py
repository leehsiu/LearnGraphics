import glfw
import glfw.GLFW as GLFW_CONSTANTS
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
import numpy as np
import pyrr
import ctypes
from PIL import Image, ImageOps
import math

############################## Constants ######################################

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

RETURN_ACTION_CONTINUE = 0
RETURN_ACTION_EXIT = 1

#0: debug, 1: production
GAME_MODE = 0

############################## helper functions ###############################

def initialize_glfw():

    glfw.init()
    glfw.window_hint(GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MAJOR,3)
    glfw.window_hint(GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MINOR,3)
    glfw.window_hint(GLFW_CONSTANTS.GLFW_OPENGL_PROFILE, GLFW_CONSTANTS.GLFW_OPENGL_CORE_PROFILE)
    glfw.window_hint(GLFW_CONSTANTS.GLFW_OPENGL_FORWARD_COMPAT, GLFW_CONSTANTS.GLFW_TRUE)
    #for uncapped framerate
    glfw.window_hint(GLFW_CONSTANTS.GLFW_DOUBLEBUFFER,GL_FALSE) 
    window = glfw.create_window(SCREEN_WIDTH, SCREEN_HEIGHT, "Title", None, None)
    glfw.make_context_current(window)
    
    #glViewport(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
    
    glEnable(GL_PROGRAM_POINT_SIZE)
    glClearColor(0.1, 0.1, 0.1, 1)

    return window

###############################################################################

class SimpleComponent:


    def __init__(self, position, eulers):

        self.position = np.array(position, dtype=np.float32)
        self.eulers = np.array(eulers, dtype=np.float32)
        self.modelTransform = pyrr.matrix44.create_identity(dtype=np.float32)
    
    def update(self, rate):

        self.eulers[1] += 0.25 * rate
        if self.eulers[1] > 360:
            self.eulers[1] -= 360
        
        self.modelTransform = pyrr.matrix44.create_identity(dtype=np.float32)
        self.modelTransform = pyrr.matrix44.multiply(
            m1=self.modelTransform, 
            m2=pyrr.matrix44.create_from_eulers(
                eulers=np.radians(self.eulers), dtype=np.float32
            )
        )
        self.modelTransform = pyrr.matrix44.multiply(
            m1=self.modelTransform, 
            m2=pyrr.matrix44.create_from_translation(
                vec=np.array(self.position),dtype=np.float32
            )
        )
        
class BillBoardComponent:

    def __init__(self, position):

        self.position = np.array(position, dtype=np.float32)
        self.modelTransform = pyrr.matrix44.create_identity(dtype=np.float32)
    
    def update(self, playerPosition):
        
        directionFromPlayer = self.position - playerPosition
        angle1 = np.arctan2(-directionFromPlayer[1],directionFromPlayer[0])
        dist2d = math.sqrt(directionFromPlayer[0] ** 2 + directionFromPlayer[1] ** 2)
        angle2 = np.arctan2(directionFromPlayer[2],dist2d)

        self.modelTransform = pyrr.matrix44.create_identity(dtype=np.float32)
        self.modelTransform = pyrr.matrix44.multiply(
            self.modelTransform,
            pyrr.matrix44.create_from_y_rotation(theta=angle2, dtype=np.float32)
        )
        self.modelTransform = pyrr.matrix44.multiply(
           self.modelTransform,
            pyrr.matrix44.create_from_z_rotation(theta=angle1, dtype=np.float32)
        )
        self.modelTransform = pyrr.matrix44.multiply(
            self.modelTransform,
            pyrr.matrix44.create_from_translation(self.position,dtype=np.float32)
        )

class BrightBillboard:


    def __init__(self, position, color, strength):

        self.position = np.array(position, dtype=np.float32)
        self.modelTransform = pyrr.matrix44.create_identity(dtype=np.float32)
        self.color = np.array(color, dtype=np.float32)
        self.strength = strength
    
    def update(self, playerPosition):
        
        directionFromPlayer = self.position - playerPosition
        angle1 = np.arctan2(-directionFromPlayer[1],directionFromPlayer[0])
        dist2d = math.sqrt(directionFromPlayer[0] ** 2 + directionFromPlayer[1] ** 2)
        angle2 = np.arctan2(directionFromPlayer[2],dist2d)

        self.modelTransform = pyrr.matrix44.create_identity(dtype=np.float32)
        self.modelTransform = pyrr.matrix44.multiply(
            self.modelTransform,
            pyrr.matrix44.create_from_y_rotation(theta=angle2, dtype=np.float32)
        )
        self.modelTransform = pyrr.matrix44.multiply(
           self.modelTransform,
            pyrr.matrix44.create_from_z_rotation(theta=angle1, dtype=np.float32)
        )
        self.modelTransform = pyrr.matrix44.multiply(
            self.modelTransform,
            pyrr.matrix44.create_from_translation(self.position,dtype=np.float32)
        )

class Player:


    def __init__(self, position):

        self.position = np.array(position, dtype = np.float32)
        self.theta = 0
        self.phi = 0
        self.update_vectors()
    
    def update_vectors(self):

        self.forwards = np.array(
            [
                np.cos(np.deg2rad(self.theta)) * np.cos(np.deg2rad(self.phi)),
                np.sin(np.deg2rad(self.theta)) * np.cos(np.deg2rad(self.phi)),
                np.sin(np.deg2rad(self.phi))
            ],
            dtype = np.float32
        )

        globalUp = np.array([0,0,1], dtype=np.float32)

        self.right = np.cross(self.forwards, globalUp)

        self.up = np.cross(self.right, self.forwards)

        self.viewTransform = pyrr.matrix44.create_look_at(
            eye = self.position,
            target = self.position + self.forwards,
            up = self.up, 
            dtype = np.float32
        )

class Scene:


    def __init__(self):

        self.cubes = [
            SimpleComponent(
                position = [6,0,1],
                eulers = [0,0,0]
            ),
        ]

        self.medkits = [
            BillBoardComponent(
                position = [3,0,0.5]
            )
        ]

        self.lights = [
            BrightBillboard(
                position = [
                    4.0, 
                    -4.0 + i, 
                    1.0
                ],
                color = [
                    np.random.uniform(low=0.0, high=1.0), 
                    np.random.uniform(low=0.0, high=1.0), 
                    np.random.uniform(low=0.0, high=1.0)
                ],
                strength = 3
            )
            for i in range(8)
        ]

        self.player = Player(
            position = [0,0,2]
        )

    def update(self, rate):

        for cube in self.cubes:
            cube.update(rate)
        
        for medkit in self.medkits:
            medkit.update(self.player.position)

        for light in self.lights:
            light.update(self.player.position)
        
        self.player.update_vectors()
    
    def move_player(self, dPos):

        dPos = np.array(dPos, dtype = np.float32)
        self.player.position += dPos
    
    def spin_player(self, dTheta, dPhi):

        self.player.theta += dTheta
        if self.player.theta > 360:
            self.player.theta -= 360
        elif self.player.theta < 0:
            self.player.theta += 360
        
        self.player.phi = min(
            89, max(-89, self.player.phi + dPhi)
        )

class App:


    def __init__(self, window):

        self.window = window

        self.renderer = GraphicsEngine()

        self.scene = Scene()

        self.lastTime = glfw.get_time()
        self.currentTime = 0
        self.numFrames = 0
        self.frameTime = 0

        self.mainLoop()

    def mainLoop(self):
        running = True
        while (running):
            #check events
            if glfw.window_should_close(self.window) \
                or glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_ESCAPE) == GLFW_CONSTANTS.GLFW_PRESS:
                running = False
            
            self.handleKeys()
            self.handleMouse()

            glfw.poll_events()

            self.scene.update(self.frameTime / 16.67)
            
            self.renderer.render(self.scene)

            #timing
            self.calculateFramerate()
        self.quit()

    def handleKeys(self):

        combo = 0
        directionModifier = 0
        """
        w: 1 -> 0 degrees
        a: 2 -> 90 degrees
        w & a: 3 -> 45 degrees
        s: 4 -> 180 degrees
        w & s: 5 -> x
        a & s: 6 -> 135 degrees
        w & a & s: 7 -> 90 degrees
        d: 8 -> 270 degrees
        w & d: 9 -> 315 degrees
        a & d: 10 -> x
        w & a & d: 11 -> 0 degrees
        s & d: 12 -> 225 degrees
        w & s & d: 13 -> 270 degrees
        a & s & d: 14 -> 180 degrees
        w & a & s & d: 15 -> x
        """

        if glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_W) == GLFW_CONSTANTS.GLFW_PRESS:
            combo += 1
        if glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_A) == GLFW_CONSTANTS.GLFW_PRESS:
            combo += 2
        if glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_S) == GLFW_CONSTANTS.GLFW_PRESS:
            combo += 4
        if glfw.get_key(self.window, GLFW_CONSTANTS.GLFW_KEY_D) == GLFW_CONSTANTS.GLFW_PRESS:
            combo += 8
        
        if combo > 0:
            if combo == 3:
                directionModifier = 45
            elif combo == 2 or combo == 7:
                directionModifier = 90
            elif combo == 6:
                directionModifier = 135
            elif combo == 4 or combo == 14:
                directionModifier = 180
            elif combo == 12:
                directionModifier = 225
            elif combo == 8 or combo == 13:
                directionModifier = 270
            elif combo == 9:
                directionModifier = 315
            
            dPos = [
                self.frameTime * 0.025 * np.cos(np.deg2rad(self.scene.player.theta + directionModifier)),
                self.frameTime * 0.025 * np.sin(np.deg2rad(self.scene.player.theta + directionModifier)),
                0
            ]

            self.scene.move_player(dPos)

    def handleMouse(self):

        (x,y) = glfw.get_cursor_pos(self.window)
        rate = self.frameTime / 16.67
        theta_increment = rate * ((SCREEN_WIDTH / 2) - x)
        phi_increment = rate * ((SCREEN_HEIGHT / 2) - y)
        self.scene.spin_player(theta_increment, phi_increment)
        glfw.set_cursor_pos(self.window, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

    def calculateFramerate(self):

        self.currentTime = glfw.get_time()
        delta = self.currentTime - self.lastTime
        if (delta >= 1):
            framerate = max(1,int(self.numFrames/delta))
            glfw.set_window_title(self.window, f"Running at {framerate} fps.")
            self.lastTime = self.currentTime
            self.numFrames = -1
            self.frameTime = float(1000.0 / max(1,framerate))
        self.numFrames += 1

    def quit(self):
        
        self.renderer.destroy()

class GraphicsEngine:


    def __init__(self):

        #initialise opengl
        glClearColor(0.0, 0.0, 0.0, 1)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self.create_assets()

        self.setup_shaders()

        self.query_shader_locations()
    
    def setup_shaders(self):

        projection_transform = pyrr.matrix44.create_perspective_projection(
            fovy = 45, aspect = SCREEN_WIDTH/SCREEN_HEIGHT, 
            near = 0.1, far = 50, dtype=np.float32
        )

        self.lighting_shader = self.createShader("shaders/vertex.txt", "shaders/fragment.txt")
        glUseProgram(self.lighting_shader)
        glUniformMatrix4fv(
            glGetUniformLocation(self.lighting_shader,"projection"),
            1, GL_FALSE, projection_transform
        )
        glUniform1i(glGetUniformLocation(self.lighting_shader, "material.albedo"), 0)
        glUniform1i(glGetUniformLocation(self.lighting_shader, "material.ao"), 1)
        glUniform1i(glGetUniformLocation(self.lighting_shader, "material.specular"), 2)
        glUniform1i(glGetUniformLocation(self.lighting_shader, "material.normal"), 3)

        self.unlit_shader = self.createShader("shaders/vertex_light.txt", "shaders/fragment_light.txt")
        glUseProgram(self.unlit_shader)
        glUniformMatrix4fv(
            glGetUniformLocation(self.unlit_shader,"projection"),
            1, GL_FALSE, projection_transform
        )

    def query_shader_locations(self):

        #attributes shared by both shaders
        self.modelMatrixLocation = {}
        self.viewMatrixLocation = {}

        glUseProgram(self.lighting_shader)
        self.modelMatrixLocation["lit"] = glGetUniformLocation(self.lighting_shader, "model")
        self.viewMatrixLocation["lit"] = glGetUniformLocation(self.lighting_shader, "view")
        self.lightLocation = {
            "position": [
                glGetUniformLocation(self.lighting_shader, f"lightPos[{i}]")
                for i in range(8)
            ],
            "color": [
                glGetUniformLocation(self.lighting_shader, f"lights[{i}].color")
                for i in range(8)
            ],
            "strength": [
                glGetUniformLocation(self.lighting_shader, f"lights[{i}].strength")
                for i in range(8)
            ]
        }
        self.cameraPosLoc = glGetUniformLocation(self.lighting_shader, "viewPos")

        glUseProgram(self.unlit_shader)
        self.modelMatrixLocation["unlit"] = glGetUniformLocation(self.unlit_shader, "model")
        self.viewMatrixLocation["unlit"] = glGetUniformLocation(self.unlit_shader, "view")
        self.tintLoc = glGetUniformLocation(self.unlit_shader, "tint")

    def create_assets(self):

        self.wood_texture = AdvancedMaterial("wood")
        self.cube_mesh = Mesh("models/cube.obj")
        self.medkit_texture = AdvancedMaterial("medkit")
        self.medkit_billboard = BillBoard(w = 0.6, h = 0.5)

        self.light_texture = Material("gfx/greenlight.png")
        self.light_billboard = BillBoard(w = 0.2, h = 0.1)
    
    def createShader(self, vertexFilepath, fragmentFilepath):

        with open(vertexFilepath,'r') as f:
            vertex_src = f.readlines()

        with open(fragmentFilepath,'r') as f:
            fragment_src = f.readlines()
        
        shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                                compileShader(fragment_src, GL_FRAGMENT_SHADER))
        
        return shader

    def render(self, scene):

        #refresh screen
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        #lit shader
        glUseProgram(self.lighting_shader)

        glUniformMatrix4fv(self.viewMatrixLocation["lit"], 1, GL_FALSE, scene.player.viewTransform)

        glUniform3fv(self.cameraPosLoc, 1, scene.player.position)

        for i,light in enumerate(scene.lights):
            glUniform3fv(self.lightLocation["position"][i], 1, light.position)
            glUniform3fv(self.lightLocation["color"][i], 1, light.color)
            glUniform1f(self.lightLocation["strength"][i], light.strength)

        self.wood_texture.use()
        glBindVertexArray(self.cube_mesh.vao)
        for cube in scene.cubes:
            glUniformMatrix4fv(self.modelMatrixLocation["lit"],1,GL_FALSE,cube.modelTransform)
            glDrawArrays(GL_TRIANGLES, 0, self.cube_mesh.vertex_count)
        
        self.medkit_texture.use()
        glBindVertexArray(self.medkit_billboard.vao)
        for medkit in scene.medkits:
            glUniformMatrix4fv(self.modelMatrixLocation["lit"],1,GL_FALSE,medkit.modelTransform)
            glDrawArrays(GL_TRIANGLES, 0, self.medkit_billboard.vertexCount)

        #unlit shader
        glUseProgram(self.unlit_shader)

        glUniformMatrix4fv(self.viewMatrixLocation["unlit"], 1, GL_FALSE, scene.player.viewTransform)

        self.light_texture.use()
        glBindVertexArray(self.light_billboard.vao)
        for i,light in enumerate(scene.lights):

            glUniform3fv(self.tintLoc, 1, light.color)
            glUniformMatrix4fv(self.modelMatrixLocation["unlit"],1,GL_FALSE,light.modelTransform)
            glDrawArrays(GL_TRIANGLES, 0, self.light_billboard.vertexCount)

        glFlush()

    def destroy(self):

        self.cube_mesh.destroy()
        self.wood_texture.destroy()
        self.medkit_billboard.destroy()
        self.medkit_texture.destroy()
        self.light_billboard.destroy()
        self.light_texture.destroy()
        glDeleteProgram(self.lighting_shader)
        glDeleteProgram(self.unlit_shader)

class Mesh:


    def __init__(self, filename):
        # x, y, z, s, t, nx, ny, nz, tx, ty, tz, bx, by, bz
        self.vertices = self.loadMesh(filename)
        self.vertex_count = len(self.vertices)//14
        self.vertices = np.array(self.vertices, dtype=np.float32)

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        offset = 0
        #position
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 56, ctypes.c_void_p(offset))
        offset += 12
        #texture
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 56, ctypes.c_void_p(offset))
        offset += 8
        #normal
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 56, ctypes.c_void_p(offset))
        offset += 12
        #tangent
        glEnableVertexAttribArray(3)
        glVertexAttribPointer(3, 3, GL_FLOAT, GL_FALSE, 56, ctypes.c_void_p(offset))
        offset += 12
        #bitangent
        glEnableVertexAttribArray(4)
        glVertexAttribPointer(4, 3, GL_FLOAT, GL_FALSE, 56, ctypes.c_void_p(offset))
        offset += 12
    
    def loadMesh(self, filename):

        #raw, unassembled data
        v = []
        vt = []
        vn = []
        
        #final, assembled and packed result
        vertices = []

        #open the obj file and read the data
        with open(filename,'r') as f:
            line = f.readline()
            while line:
                firstSpace = line.find(" ")
                flag = line[0:firstSpace]
                if flag=="v":
                    #vertex
                    line = line.replace("v ","")
                    line = line.split(" ")
                    l = [float(x) for x in line]
                    v.append(l)
                elif flag=="vt":
                    #texture coordinate
                    line = line.replace("vt ","")
                    line = line.split(" ")
                    l = [float(x) for x in line]
                    vt.append(l)
                elif flag=="vn":
                    #normal
                    line = line.replace("vn ","")
                    line = line.split(" ")
                    l = [float(x) for x in line]
                    vn.append(l)
                elif flag=="f":
                    #face, three or more vertices in v/vt/vn form
                    line = line.replace("f ","")
                    line = line.replace("\n","")
                    #get the individual vertices for each line
                    line = line.split(" ")
                    faceVertices = []
                    faceTextures = []
                    faceNormals = []
                    for vertex in line:
                        #break out into [v,vt,vn],
                        #correct for 0 based indexing.
                        l = vertex.split("/")
                        position = int(l[0]) - 1
                        faceVertices.append(v[position])
                        texture = int(l[1]) - 1
                        faceTextures.append(vt[texture])
                        normal = int(l[2]) - 1
                        faceNormals.append(vn[normal])
                    # obj file uses triangle fan format for each face individually.
                    # unpack each face
                    triangles_in_face = len(line) - 2

                    vertex_order = []
                    """
                        eg. 0,1,2,3 unpacks to vertices: [0,1,2,0,2,3]
                    """
                    for i in range(triangles_in_face):
                        vertex_order.append(0)
                        vertex_order.append(i+1)
                        vertex_order.append(i+2)
                    # calculate tangent and bitangent for point
                    # how do model positions relate to texture positions?
                    point1 = faceVertices[vertex_order[0]]
                    point2 = faceVertices[vertex_order[1]]
                    point3 = faceVertices[vertex_order[2]]
                    uv1 = faceTextures[vertex_order[0]]
                    uv2 = faceTextures[vertex_order[1]]
                    uv3 = faceTextures[vertex_order[2]]
                    #direction vectors
                    deltaPos1 = [point2[i] - point1[i] for i in range(3)]
                    deltaPos2 = [point3[i] - point1[i] for i in range(3)]
                    deltaUV1 = [uv2[i] - uv1[i] for i in range(2)]
                    deltaUV2 = [uv3[i] - uv1[i] for i in range(2)]
                    # calculate
                    den = 1 / (deltaUV1[0] * deltaUV2[1] - deltaUV2[0] * deltaUV1[1])
                    tangent = []
                    #tangent x
                    tangent.append(den * (deltaUV2[1] * deltaPos1[0] - deltaUV1[1] * deltaPos2[0]))
                    #tangent y
                    tangent.append(den * (deltaUV2[1] * deltaPos1[1] - deltaUV1[1] * deltaPos2[1]))
                    #tangent z
                    tangent.append(den * (deltaUV2[1] * deltaPos1[2] - deltaUV1[1] * deltaPos2[2]))
                    bitangent = []
                    #bitangent x
                    bitangent.append(den * (-deltaUV2[0] * deltaPos1[0] + deltaUV1[0] * deltaPos2[0]))
                    #bitangent y
                    bitangent.append(den * (-deltaUV2[0] * deltaPos1[1] + deltaUV1[0] * deltaPos2[1]))
                    #bitangent z
                    bitangent.append(den * (-deltaUV2[0] * deltaPos1[2] + deltaUV1[0] * deltaPos2[2]))
                    for i in vertex_order:
                        for x in faceVertices[i]:
                            vertices.append(x)
                        for x in faceTextures[i]:
                            vertices.append(x)
                        for x in faceNormals[i]:
                            vertices.append(x)
                        for x in tangent:
                            vertices.append(x)
                        for x in bitangent:
                            vertices.append(x)
                line = f.readline()
        return vertices
    
    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1,(self.vbo,))

class Material:

    
    def __init__(self, filepath):
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        with Image.open(filepath, mode = "r") as img:
            image_width,image_height = img.size
            img = img.convert("RGBA")
            img_data = bytes(img.tobytes())
            glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,image_width,image_height,0,GL_RGBA,GL_UNSIGNED_BYTE,img_data)
        glGenerateMipmap(GL_TEXTURE_2D)

    def use(self):
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D,self.texture)

    def destroy(self):
        glDeleteTextures(1, (self.texture,))

class AdvancedMaterial:

    
    def __init__(self, fileroot):

        #albedo
        self.albedoTexture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.albedoTexture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        with Image.open(f"gfx/{fileroot}_albedo.png", mode = "r") as img:
            image_width,image_height = img.size
            img = img.convert("RGBA")
            img_data = bytes(img.tobytes())
            glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,image_width,image_height,0,GL_RGBA,GL_UNSIGNED_BYTE,img_data)
        glGenerateMipmap(GL_TEXTURE_2D)

        #ambient occlusion
        self.ambientOcclusionTexture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.ambientOcclusionTexture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        with Image.open(f"gfx/{fileroot}_ao.png", mode = "r") as img:
            image_width,image_height = img.size
            img = img.convert("RGBA")
            img_data = bytes(img.tobytes())
            glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,image_width,image_height,0,GL_RGBA,GL_UNSIGNED_BYTE,img_data)
        glGenerateMipmap(GL_TEXTURE_2D)

        #glossmap
        self.glossmapTexture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.glossmapTexture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        with Image.open(f"gfx/{fileroot}_glossmap.png", mode = "r") as img:
            image_width,image_height = img.size
            img = img.convert("RGBA")
            img_data = bytes(img.tobytes())
            glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,image_width,image_height,0,GL_RGBA,GL_UNSIGNED_BYTE,img_data)
        glGenerateMipmap(GL_TEXTURE_2D)

        #normal
        self.normalTexture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.normalTexture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        with Image.open(f"gfx/{fileroot}_normal.png", mode = "r") as img:
            image_width,image_height = img.size
            img = img.convert("RGBA")
            img_data = bytes(img.tobytes())
            glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,image_width,image_height,0,GL_RGBA,GL_UNSIGNED_BYTE,img_data)
        glGenerateMipmap(GL_TEXTURE_2D)

        #handy list
        self.textures = [
            self.albedoTexture, self.ambientOcclusionTexture, self.glossmapTexture, self.normalTexture
        ]

    def use(self):

        for i,texture in enumerate(self.textures):
            glActiveTexture(GL_TEXTURE0 + i)
            glBindTexture(GL_TEXTURE_2D, texture)

    def destroy(self):
        glDeleteTextures(len(self.textures), self.textures)

class BillBoard:


    def __init__(self, w, h):

        #x,y,z, s,t, normal, tangent, bitangent

        self.vertices = (
            0, -w/2,  h/2, 0, 0, -1, 0, 0, 0, 0, 1, 0, 1, 0,
            0, -w/2, -h/2, 0, 1, -1, 0, 0, 0, 0, 1, 0, 1, 0,
            0,  w/2, -h/2, 1, 1, -1, 0, 0, 0, 0, 1, 0, 1, 0,

            0, -w/2,  h/2, 0, 0, -1, 0, 0, 0, 0, 1, 0, 1, 0,
            0,  w/2, -h/2, 1, 1, -1, 0, 0, 0, 0, 1, 0, 1, 0,
            0,  w/2,  h/2, 1, 0, -1, 0, 0, 0, 0, 1, 0, 1, 0
        )
        self.vertices = np.array(self.vertices, dtype=np.float32)
        self.vertexCount = 6
        
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        offset = 0
        #position
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 56, ctypes.c_void_p(offset))
        offset += 12
        #texture
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 56, ctypes.c_void_p(offset))
        offset += 8
        #normal
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 56, ctypes.c_void_p(offset))
        offset += 12
        #tangent
        glEnableVertexAttribArray(3)
        glVertexAttribPointer(3, 3, GL_FLOAT, GL_FALSE, 56, ctypes.c_void_p(offset))
        offset += 12
        #bitangent
        glEnableVertexAttribArray(4)
        glVertexAttribPointer(4, 3, GL_FLOAT, GL_FALSE, 56, ctypes.c_void_p(offset))
        offset += 12
    
    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))

window = initialize_glfw()
myApp = App(window)