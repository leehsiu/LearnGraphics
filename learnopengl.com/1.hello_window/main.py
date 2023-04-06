import glfw
import glfw.GLFW as GLFW
import OpenGL.GL as gl

# orignal CPP code: https://learnopengl.com/code_viewer_gh.php?
# code=src/1.getting_started/1.2.hello_window_clear/hello_window_clear.cpp


def init_glfw(width, height, title="window"):
    glfw.init()
    
    # Follow are required on macOS to use OpenGL 4.1 
    glfw.window_hint(GLFW.GLFW_CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(GLFW.GLFW_CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(GLFW.GLFW_OPENGL_PROFILE, GLFW.GLFW_OPENGL_CORE_PROFILE)
    glfw.window_hint(GLFW.GLFW_OPENGL_FORWARD_COMPAT, GLFW.GLFW_TRUE)
    # glfw.window_hint(GLFW.GLFW_DOUBLEBUFFER, gl.GL_FALSE)
    window = glfw.create_window(width, height, title, None, None)
    glfw.make_context_current(window)
    glfw.set_framebuffer_size_callback(window, framebuffer_size_callback)
    gl.glEnable(gl.GL_PROGRAM_POINT_SIZE)
    print(gl.glGetString(gl.GL_VERSION))
    return window


def framebuffer_size_callback(window, width, height):
    gl.glViewport(0, 0, width, height)


class App:
    def __init__(self, window):
        # initialise opengl
        self.window = window
        self.mainLoop()

    def process_input(self):
        if glfw.get_key(self.window, GLFW.GLFW_KEY_ESCAPE) == GLFW.GLFW_PRESS:
            glfw.set_window_should_close(self.window, True)

    def mainLoop(self):
        running = True
        while (running):
            if glfw.window_should_close(self.window):
                running = False
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
    myApp = App(window)
