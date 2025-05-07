using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class OnsetRepresentation : MonoBehaviour
{
    public Transform particleLocation;
    public GameObject particlePrefab;
    public float activationThreshold = 0.5f;

    private void Start()
    {
        FeaturePlayback.OnsetFeatureRecieved += OnsetReceived;
    }

    public void OnsetReceived(OnsetFeatures onsetFeature)
    {
        Debug.Log($"Onset: {onsetFeature.Strenght}");
        if (onsetFeature.Strenght >  activationThreshold)
        {
            Instantiate(particlePrefab, particleLocation.position, particleLocation.rotation);
        }
    }
}
