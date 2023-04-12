#version 330 core
out vec4 FragColor;

in vec3 fColor;
in vec2 fTexCoord;

uniform sampler2D texture0;
uniform sampler2D texture1;

uniform float mixValue;

void main()
{
	FragColor = mix(
		texture(texture0, fTexCoord), 
		texture(texture1, vec2(fTexCoord.x,1.0 - fTexCoord.y)), mixValue);
}