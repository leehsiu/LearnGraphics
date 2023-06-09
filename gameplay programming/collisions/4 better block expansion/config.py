import glfw
import glfw.GLFW as GLFW_CONSTANTS
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
import numpy as np
import pyrr
import ctypes
from PIL import Image, ImageOps

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

def createShader(vertexFilepath, fragmentFilepath):

        with open(vertexFilepath,'r') as f:
            vertex_src = f.readlines()

        with open(fragmentFilepath,'r') as f:
            fragment_src = f.readlines()
        
        shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                                compileShader(fragment_src, GL_FRAGMENT_SHADER))
        
        return shader

def load_model_from_file(folderpath, filename):

    v = []
    vt = []
    vn = []
    vertices = []

    with open(f"{folderpath}/{filename}",'r') as f:
        line = f.readline()
        while line:
            firstSpace = line.find(" ")
            flag = line[0:firstSpace]
            if flag=="mtllib":
                #declaration of material file
                pass
            elif flag=="v":
                #vertex
                line = line.replace("v ","")
                line = line.split(" ")
                l = [float(x) for x in line]
                v.append(l)
                #print(v)
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
                #face, four vertices in v/vt/vn form
                line = line.replace("f ","")
                line = line.replace("\n","")
                line = line.split(" ")
                theseVertices = []
                theseTextures = []
                theseNormals = []
                for vertex in line:
                    l = vertex.split("/")
                    position = int(l[0]) - 1
                    theseVertices.append(v[position])
                    texture = int(l[1]) - 1
                    theseTextures.append(vt[texture])
                    normal = int(l[2]) - 1
                    theseNormals.append(vn[normal])
                # obj file uses triangle fan format for each face individually.
                # unpack each face
                triangles_in_face = len(line) - 2

                vertex_order = []
                for i in range(triangles_in_face):
                    vertex_order.append(0)
                    vertex_order.append(i+1)
                    vertex_order.append(i+2)
                for i in vertex_order:
                    for x in theseVertices[i]:
                        vertices.append(x)
                    for x in theseTextures[i]:
                        vertices.append(x)
                    for x in theseNormals[i]:
                        vertices.append(x)
                
            line = f.readline()
    
    return vertices

###############################################################################