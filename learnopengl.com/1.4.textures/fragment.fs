#version 330 core
out vec4 FragColor;

in vec3 fColor;
in vec2 fTexCoord;

// texture sampler
uniform sampler2D texture0;

void main()
{
	FragColor = texture(texture0, fTexCoord) * vec4(fColor, 1.0);
}