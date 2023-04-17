#version 330 core
layout (location = 0) in vec3 vPos;
layout (location = 1) in vec3 vColor;
layout (location = 2) in vec3 vNormal;
layout (location = 3) in vec2 vTexCoord;


out vec3 fPos;
out vec3 fColor;
out vec3 fNormal;
out vec2 fTexCoord;

uniform mat4 ModelMatrix;
uniform mat4 ModelViewProjectionMatrix;
uniform mat3 NormalMatrix;


void main()
{
	fPos = vec3(ModelMatrix * vec4(vPos,1.0));
	fNormal = NormalMatrix * vNormal;
	fColor = vColor;
	fTexCoord = vTexCoord;
	gl_Position = ModelViewProjectionMatrix * vec4(vPos,1.0);
}

// pre-compute MVP and normal matrix on CPU
// https://learnopengl.com/code_viewer_gh.php?code=src/2.lighting/
// 4.2.lighting_maps_specular_map/4.2.lighting_maps.vs
// uniform mat4 model;
// uniform mat4 view;
// uniform mat4 projection;

// void main()
// {
//     FragPos = vec3(model * vec4(aPos, 1.0));
//     Normal = mat3(transpose(inverse(model))) * aNormal;  
//     TexCoords = aTexCoords;
    
//     gl_Position = projection * view * vec4(FragPos, 1.0);
// }
