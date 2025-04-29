using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class OnsetScale : FeatureVisualizer
{
    [SerializeField] float lowZScale = 1f;   // Z scale when value is below 0.5
    [SerializeField] float highZScale = 3f;  // Z scale when value is 0.5 or above

    public override void UpdateFeature(float value)
    {
        float targetZ = (value >= 0.5f) ? highZScale : lowZScale;
        Vector3 currentScale = transform.localScale;
        transform.localScale = new Vector3(currentScale.x, currentScale.y, targetZ);
    }
}
