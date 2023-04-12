import OpenGL.GL as gl
import PIL.Image
import numpy as np


__all__ = [
    'Texture',
]

class Texture:
    def __init__(self, img):
        self.texture = gl.glGenTextures(1)
        # all upcoming GL_TEXTURE_2D operations now have effect on this texture
        # object
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture)
        # set the texture wrapping parameters

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
        if isinstance(img, np.ndarray):
            img = PIL.Image.fromarray(img)
            
        img_data = img.convert("RGB").tobytes()

        gl.glTexImage2D(
            gl.GL_TEXTURE_2D, 0, gl.GL_RGB, img.size[0], img.size[1], 0,
            gl.GL_RGB, gl.GL_UNSIGNED_BYTE, img_data)
        gl.glGenerateMipmap(gl.GL_TEXTURE_2D)

    @classmethod
    def load(cls, path):
        img = PIL.Image.open(path)
        return cls(img)

    def use(self):
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture)

    def dispose(self):
        gl.glDeleteTextures(1, (self.texture,))
