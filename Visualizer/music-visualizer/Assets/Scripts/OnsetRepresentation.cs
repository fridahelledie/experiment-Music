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
        if (onsetFeature.Detected)
        {
            Instantiate(particlePrefab, particleLocation.position, particleLocation.rotation);
        }
    }
}
