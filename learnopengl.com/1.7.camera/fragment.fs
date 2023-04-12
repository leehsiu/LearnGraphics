#version 330 core

out vec4 FragColor;
in vec2 fTexCoord;

uniform sampler2D texture0;
uniform sampler2D texture1;


void main()
{
	FragColor = mix(
		texture(texture0, fTexCoord), 
		texture(texture1, vec2(fTexCoord.x,1.0 - fTexCoord.y)), 0.2);
}