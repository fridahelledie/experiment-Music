using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class BandwithOpacity : FeatureVisualizer
{
    [SerializeField] private Material mat;
    private Renderer rendr;

    private float targetValue = 1f; // Chromatic strength driving opacity - Has to be changed to the more than 2 chromatic shit
                                    
    void Awake()
    {
        //Getting material
        rendr = GetComponent<Renderer>();
        mat = rendr.material; 
        EnableTransparency();
    }

    public override void UpdateFeature(float value)
    {
        targetValue = value; // has to be changed to if statement
    }



    void Update()
    {
        if (mat != null)
        {
            Color color = mat.color;
            color.a = Mathf.Lerp(0f, 1f, targetValue); // Fade alpha based on chroma value, has to be changed 
            mat.color = color;
        }
    }

    void EnableTransparency()
    {
        if (mat != null)
        {
            mat.SetFloat("_Mode", 3); // Set Standard Shader mode to Transparent
            mat.SetInt("_SrcBlend", (int)UnityEngine.Rendering.BlendMode.SrcAlpha);
            mat.SetInt("_DstBlend", (int)UnityEngine.Rendering.BlendMode.OneMinusSrcAlpha);
            mat.SetInt("_ZWrite", 0);
            mat.DisableKeyword("_ALPHATEST_ON");
            mat.EnableKeyword("_ALPHABLEND_ON");
            mat.DisableKeyword("_ALPHAPREMULTIPLY_ON");
            mat.renderQueue = 3000;
        }
    }
}
