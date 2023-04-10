import OpenGL.GL as gl
import PIL.Image

__all__ = [
    'Texture',
]
class Texture:
    def __init__(self, filepath):
        self.texture = gl.glGenTextures(1)
        
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture)

        gl.glTexParameteri(
            gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
        gl.glTexParameteri(
            gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)
        gl.glTexParameteri(
            gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER,
            gl.GL_LINEAR_MIPMAP_LINEAR)
        gl.glTexParameteri(
            gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)

        # load image, create texture and generate mipmaps
        img = PIL.Image.open(filepath)
        img_data = img.convert("RGB").tobytes()

        gl.glTexImage2D(
            gl.GL_TEXTURE_2D, 0, gl.GL_RGB, img.size[0], img.size[1], 0,
            gl.GL_RGB, gl.GL_UNSIGNED_BYTE, img_data)
        gl.glGenerateMipmap(gl.GL_TEXTURE_2D)

    def use(self):
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture)

    def dispose(self):
        gl.glDeleteTextures(1, self.texture)
