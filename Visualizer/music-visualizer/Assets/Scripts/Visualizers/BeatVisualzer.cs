using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class BeatVisualzer : MonoBehaviour
{
   
    public float rotationAngle = 45f; // Rotate 90 each beat
    void Start()
    {
        // Subscribe to the OnBeatDetected event
        FeaturePlayback.OnBeatDetected += TriggerBeatEffect;
    }


    public void TriggerBeatEffect()
    {
        // Debug log to confirm if the method is called
        Debug.Log("Beat found yay");

        // Instantly rotate the object by the specified angle around the Y axis
        transform.Rotate(0, 0, rotationAngle);
    }
}