#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aNormal;

out vec3 FragPos;
out vec3 FragNormal;

uniform mat4 projection;
uniform mat4 view;
uniform mat4 model;
uniform mat3 modelNormal;


void main()
{
	FragPos = vec3(model * vec4(aPos, 1.0));
	FragNormal = modelNormal * aNormal;
	// FragNormal = mat3(transpose(inverse(model))) * aNormal;  
	gl_Position = projection * view * vec4(FragPos,1.0);
}