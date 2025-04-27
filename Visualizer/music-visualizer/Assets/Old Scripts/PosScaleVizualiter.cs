using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class PosScaleVizualiter : FeatureVisualizer
{
    public enum FeatureType { Position, Scale }
    [SerializeField] FeatureType featureType;

    [SerializeField] float lerpSpeed = 0.2f;
    [SerializeField] Vector3 offsetAtMax = Vector3.zero;
    

    //FOR CENTROID 
    [SerializeField] Material colorMaterial;

    private Vector3 minPosition;
    private Vector3 maxPosition;
    private Vector3 targetPosition;
    
    private float targetValue = 0;

    private Renderer rendr;

    void Awake()
    {
        // Store initial values
        minPosition = transform.position;
        maxPosition = minPosition + offsetAtMax;
        targetPosition = minPosition;
        

        rendr = GetComponent<Renderer>();
    }

    public override void UpdateFeature(float value)
    {
        targetValue = value;

        if (featureType == FeatureType.Position)
        {
            targetPosition = Vector3.Lerp(minPosition, maxPosition, value);
        }
       
    }

    void Update()
    {
        if (featureType == FeatureType.Position)
        {
            transform.position = Vector3.Lerp(transform.position, targetPosition, lerpSpeed * Time.deltaTime);
        }
       
        UpdateMaterial(targetValue);
    }

    //FOR CENTROID
    void UpdateMaterial(float value)
    {
        if (rendr != null)
        {
            Color orgColor = rendr.material.color;
            // material converted to hsv so we can manipulate brightness later
            Color.RGBToHSV(orgColor, out float h, out float s, out float v);

            //here the value is changed depending on the value
            float newSaturation = Mathf.Lerp(0f, 1f, value); // 0 = grayscale, 1 = full color

            //converted back to RGB to be used as the color yay
            Color newColor = Color.HSVToRGB(h, newSaturation, v);

            rendr.material.color = newColor;
        }
    }
}

