from config import *
import sphere
import camera
import plane
import light

class Scene:
    """
        Holds pointers to all objects in the scene
    """


    def __init__(self):
        """
            Set up scene objects.
        """
        
        self.spheres = [
            sphere.Sphere(
                center = [
                    np.random.uniform(low = -2.0, high = 2.0),
                    np.random.uniform(low = -2.0, high = 2.0),
                    np.random.uniform(low = 0.0, high = 3.0)
                ],
                radius = np.random.uniform(low = 0.3, high = 1.0),
                color = [
                    np.random.uniform(low = 0.3, high = 1.0),
                    np.random.uniform(low = 0.3, high = 1.0),
                    np.random.uniform(low = 0.3, high = 1.0)
                ],
                roughness = np.random.uniform(low = 0.3, high = 0.8)
            ) for i in range(5)
        ]
        
        self.planes = [
            plane.Plane(
                normal = [0, 0, 1],
                tangent = [1, 0, 0],
                bitangent = [0, 1, 0],
                uMin = -3,
                uMax = 3,
                vMin = -3,
                vMax = 3,
                center = [0, 0, -1],
                material_index = 1
            ),
        ]

        self.lights = []

        for i in range(4):

            theta = np.random.uniform(low = 0.0, high = 2 * np.pi)
            phi = np.random.uniform(low = 0.0, high = 2 * np.pi)

            self.lights.append(light.Light(
                position = [
                    np.random.uniform(low = -4.0, high = 4.0),
                    np.random.uniform(low = -4.0, high = 4.0),
                    np.random.uniform(low =  0.0, high = 4.0)
                ],
                strength = np.random.uniform(low = 1.0, high = 3.0),
                color = [
                    abs(np.cos(theta, dtype = np.float32) * np.cos(phi, dtype = np.float32)),
                    abs(np.sin(theta, dtype = np.float32) * np.cos(phi, dtype = np.float32)),
                    abs(np.sin(phi, dtype = np.float32))
                ],
            ))
        
        self.camera = camera.Camera(
            position = [-1, 0, 0]
        )

        self.outDated = True
    
    def move_player(self, forwardsSpeed, rightSpeed):
        """
        attempt to move the player with the given speed
        """
        
        dPos = forwardsSpeed * self.camera.forwards + rightSpeed * self.camera.right
        
        self.camera.position[0] += dPos[0]
        self.camera.position[1] += dPos[1]
    
    def spin_player(self, dAngle):
        """
            shift the player's direction by the given amount, in degrees
        """
        self.camera.theta += dAngle[0]
        if (self.camera.theta < 0):
            self.camera.theta += 360
        elif (self.camera.theta > 360):
            self.camera.theta -= 360
        
        self.camera.phi += dAngle[1]
        if (self.camera.phi < -89):
            self.camera.phi = -89
        elif (self.camera.phi > 89):
            self.camera.phi = 89
        
        self.camera.recalculateVectors()