import sys
import glfw
import glfw.GLFW as GLFW
import OpenGL.GL as gl

# orignal CPP code: https://learnopengl.com/code_viewer_gh.php?
# code=src/1.getting_started/1.2.hello_window_clear/hello_window_clear.cpp


def init_glfw(width, height, title="window"):
    glfw.init()
    
    # setup OpenGL context
    glfw.window_hint(GLFW.GLFW_CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(GLFW.GLFW_CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(GLFW.GLFW_OPENGL_PROFILE, GLFW.GLFW_OPENGL_CORE_PROFILE)
    
    if sys.platform == "darwin":
        glfw.window_hint(GLFW.GLFW_OPENGL_FORWARD_COMPAT, GLFW.GLFW_TRUE)
    
    window = glfw.create_window(width, height, title, None, None)
    
    glfw.make_context_current(window)
    info = """
        Vendor: {0}
        Renderer: {1}
        OpenGL Version: {2}
        Shader Version: {3}
    """.format(
        gl.glGetString(gl.GL_VENDOR),
        gl.glGetString(gl.GL_RENDERER),
        gl.glGetString(gl.GL_VERSION),
        gl.glGetString(gl.GL_SHADING_LANGUAGE_VERSION)
    )
    print(info)

    return window


class App:
    def __init__(self, window):
        # initialise opengl
        self.window = window
        glfw.set_framebuffer_size_callback(window,self.resize)
        
        self.mainloop()

    def resize(self,window, width,height):
        gl.glViewport(0,0, width, height)
        

    def process_input(self):
        if glfw.get_key(self.window, GLFW.GLFW_KEY_ESCAPE) == GLFW.GLFW_PRESS:
            glfw.set_window_should_close(self.window, True)

    def mainloop(self):
        while not glfw.window_should_close(self.window):
            
            self.process_input()
            # main drawing
            gl.glClearColor(0.8, 0.2, 0.2, 1)
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)

            glfw.swap_buffers(self.window)
            glfw.poll_events()
        self.quit()

    def quit(self):
        glfw.terminate()


if __name__ == "__main__":
    window = init_glfw(640, 480)
    app = App(window)
