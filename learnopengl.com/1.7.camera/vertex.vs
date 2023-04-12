#version 330 core
layout (location = 0) in vec3 vPos;
layout (location = 1) in vec2 vTexCoord;

out vec2 fTexCoord;

uniform mat4 ModelViewProjectionMatrix;

// ModelViewProjectionMatrix = projection * view * model
// pre-calculated on CPU to reduce overhead

void main()
{
	gl_Position = ModelViewProjectionMatrix * vec4(vPos, 1.0);
	fTexCoord = vTexCoord;
}