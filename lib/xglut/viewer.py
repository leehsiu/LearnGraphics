import glfw
import glfw.GLFW as GLFW
import OpenGL.GL as gl

__all__ = [
    'GLFWViewer',
]
def init_glfw(width, height, title="window"):
    glfw.init()
    glfw.window_hint(GLFW.GLFW_CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(GLFW.GLFW_CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(GLFW.GLFW_OPENGL_PROFILE, GLFW.GLFW_OPENGL_CORE_PROFILE)
    glfw.window_hint(GLFW.GLFW_OPENGL_FORWARD_COMPAT, GLFW.GLFW_TRUE)
    
    window = glfw.create_window(width, height, title, None, None)
    glfw.make_context_current(window)

    return window


class GLFWViewer:
    def __init__(self, width, height, title="window"):
        
        # init opengl
        self.width = width
        self.height = height
        self.window = init_glfw(width, height, title)
        glfw.set_framebuffer_size_callback(self.window,self.resize)


    def resize(self,window,width,height):
        self.width = width
        self.height = height
        gl.glViewport(0, 0, width, height)

    def handle_input(self):
        if glfw.get_key(self.window, GLFW.GLFW_KEY_ESCAPE) == GLFW.GLFW_PRESS:
            glfw.set_window_should_close(self.window, True)

    def draw(self):
        pass
    
    def dispose(self):
        pass

    def view(self):
        
        while not glfw.window_should_close(self.window):
            
            self.handle_input()           
            self.draw()
            glfw.swap_buffers(self.window)
            glfw.poll_events()
            
        self.quit()

    def quit(self):
        self.dispose()
        glfw.terminate()


if __name__ == "__main__":
    viewer = GLFWViewer(640,480)
    viewer.view()
    