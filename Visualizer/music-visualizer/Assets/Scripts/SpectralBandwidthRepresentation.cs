using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class SpectralBandwidthRepresentation : MonoBehaviour
{
    public FeatureVisualizer[] visualizers;
    public float MaxFrequency = 20000f;

    private void Start()
    {
        FeaturePlayback.OnSpectralBandwidthRecieved += OnBandwidthRecieved;
    }

    void OnBandwidthRecieved(float bandwidth)
    {
        foreach(FeatureVisualizer visualizer in visualizers)
        {
            visualizer.UpdateFeature(bandwidth / MaxFrequency);
        }
    }
}
