using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class PositionFeatureVisualizer : FeatureVisualizer
{
    [SerializeField] float lerpSpeed = 0.9f;
    [SerializeField] Vector3 offsetAtMax = Vector3.zero;
    Vector3 maxPosition;
    Vector3 minPosition;
    Vector3 targetPosition;

    [SerializeField] Material blackMaterial;
    [SerializeField] Material colorMaterial;
    Renderer rendr;
    float targetValue = 0;

    public override void UpdateFeature(float value)
    {
        targetPosition = Vector3.Lerp(minPosition, maxPosition, value);
    }

    void Awake()
    {
        minPosition = transform.position;
        maxPosition = minPosition + offsetAtMax;
        targetPosition = minPosition;

        rendr = GetComponent<Renderer>();
    }

    void Update()
    {
        if (targetValue <= 0.65)
        {
            UpdateMaterial(targetValue);
        }
        transform.position = Vector3.Lerp(transform.position, targetPosition, lerpSpeed);
        
    }

    void UpdateMaterial(float value)
    {
        if (rendr != null)
        {
            print(value);
            if (value <= 0.2f)
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
