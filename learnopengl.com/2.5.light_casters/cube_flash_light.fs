#version 330 core

out vec4 FragColor;

in vec3 fNormal;
in vec3 fPos;
in vec2 fTexCoord;


struct Material {
    sampler2D diffuse;
    sampler2D specular;
    float shininess;
};

struct Light {
    vec3 position;
    vec3 direction;

    vec3 ambient;
    vec3 diffuse;
    vec3 specular;

    float cutoff;
    float outerCufoff;
    float constant;
    float linear;
    float quadratic;
};

uniform Material material;
uniform Light light;
uniform vec3 viewPos;



void main()
{
    
    vec3 ambient = light.ambient * texture(material.diffuse, fTexCoord).rgb;
        
    vec3 lightDir = normalize(light.position - fPos);
    float theta = dot(lightDir, normalize(-light.direction));
    vec3 result;

    if(theta > light.cutoff) 
    {    
        // ambient
        // diffuse 
        vec3 norm = normalize(fNormal);
        float diff = max(dot(norm, lightDir), 0.0);
        vec3 diffuse = light.diffuse * diff * texture(material.diffuse, fTexCoord).rgb;  
        
        // specular
        vec3 viewDir = normalize(viewPos - fPos);
        vec3 reflectDir = reflect(-lightDir, norm);  
        float spec = pow(max(dot(viewDir, reflectDir), 0.0), material.shininess);
        vec3 specular = light.specular * spec * texture(material.specular, fTexCoord).rgb;  
        
        // attenuation
        float dist  = length(light.position - fPos);
        float attenuation = 1.0 / (light.constant + light.linear * dist + light.quadratic * (dist * dist));    

        diffuse   *= attenuation;
        specular *= attenuation;   
        
        result = ambient + diffuse + specular;
    
    }
    else 
    {
        // vec3 result = ambient;
        // FragColor = vec4(ambient, 1.0);
        result = ambient;
    }
        FragColor = vec4(result, 1.0);

}