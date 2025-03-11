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

    public override void UpdateFeature(float value)
    {
        targetPosition = Vector3.Lerp(minPosition, maxPosition, value);
    }

    void Awake()
    {
        minPosition = transform.position;
        maxPosition = minPosition + offsetAtMax;
        targetPosition = minPosition;
    }

    void Update()
    {
        transform.position = Vector3.Lerp(transform.position, targetPosition, lerpSpeed);
    }
}
