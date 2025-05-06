using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public abstract class FeatureVisualizer : MonoBehaviour
{
    public abstract void UpdateFeature(float value);
    public virtual void UpdateFeature(float[] values) { }

}
