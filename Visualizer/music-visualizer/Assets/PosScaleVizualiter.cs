using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class PosScaleVizualiter : FeatureVisualizer
{
    public enum FeatureType { Position, Scale }
    [SerializeField] FeatureType featureType;

    [SerializeField] float lerpSpeed = 0.2f;
    [SerializeField] Vector3 offsetAtMax = Vector3.zero;
    [SerializeField] Vector3 scaleMax;

    [SerializeField] Material blackMaterial;
    [SerializeField] Material colorMaterial;

    private Vector3 minPosition;
    private Vector3 maxPosition;
    private Vector3 scaleMin;
    private Vector3 targetPosition;
    private Vector3 targetScale;
    private float targetValue = 0;

    private Renderer rendr;

    void Awake()
    {
        // Store initial values
        minPosition = transform.position;
        maxPosition = minPosition + offsetAtMax;

        scaleMin = transform.localScale;
        targetPosition = minPosition;
        targetScale = scaleMin;

        rendr = GetComponent<Renderer>();
    }

    public override void UpdateFeature(float value)
    {
        targetValue = value;

        if (featureType == FeatureType.Position)
        {
            targetPosition = Vector3.Lerp(minPosition, maxPosition, value);
        }
        else if (featureType == FeatureType.Scale)
        {
            targetScale = Vector3.Lerp(scaleMin, scaleMax, value);
        }
    }

    void Update()
    {
        if (featureType == FeatureType.Position)
        {
            transform.position = Vector3.Lerp(transform.position, targetPosition, lerpSpeed * Time.deltaTime);
        }
        else if (featureType == FeatureType.Scale)
        {
            transform.localScale = Vector3.Lerp(transform.localScale, targetScale, lerpSpeed * Time.deltaTime);
        }

        UpdateMaterial(targetValue);
    }

    void UpdateMaterial(float value)
    {
        if (rendr != null)
        {
            if (value >= 0.4)
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

