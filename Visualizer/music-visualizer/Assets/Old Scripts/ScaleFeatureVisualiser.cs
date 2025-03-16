using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class ScaleFeatureVisualiser : FeatureVisualizer
{
    Vector3 targetScale;
    Vector3 scaleMin;
    [SerializeField] Vector3 scaleMax;

    //Vector3 maxPosition;
    //Vector3 minPosition;
    //Vector3 targetPosition;

    [SerializeField] float lerpSpeed = 0.2f;
    //[SerializeField] Vector3 offsetAtMax = Vector3.zero;

    [SerializeField] Material blackMaterial;
    [SerializeField] Material colorMaterial;
    Renderer rendr;

    float targetValue = 0; 

    public override void UpdateFeature(float value)
    {
        
        targetValue = value;

        //targetPosition = Vector3.Lerp(minPosition, maxPosition, value);
        targetScale = Vector3.Lerp(scaleMin, scaleMax, value);
    }

    void Awake()
    {
        /*minPosition = transform.position;
        maxPosition = minPosition + offsetAtMax;
        targetPosition = minPosition;*/

        scaleMin = transform.localScale;
        targetScale = scaleMin;

        rendr = GetComponent<Renderer>();
    }

    void Update()
    {
        if (targetValue == 0.3)
        {
            transform.localScale = scaleMin;
            //transform.position = minPosition;
        }
        else
        {
            transform.localScale = Vector3.Lerp(transform.localScale, targetScale, lerpSpeed * Time.deltaTime);

            //transform.position = Vector3.Lerp(transform.position, targetPosition, lerpSpeed * Time.deltaTime);

        }


        UpdateMaterial(targetValue);
    }

    void UpdateMaterial(float value)
    {
        if (rendr != null)
        {
            print(value);
            if (value <= 0.65f)
            {
                rendr.material = blackMaterial;
            }
            else
            {
                rendr.material.Lerp(colorMaterial, blackMaterial, value);
            }
        }
    }
}
