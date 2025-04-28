using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Progress_bar : MonoBehaviour
{
    private FeaturePlayback featurePlayback;
    [SerializeField] private Transform child;
    private float lastTimestamp; //here the last timestamp in json should be stored

    // Start is called before the first frame update
    void Start()
    {
        featurePlayback = FindObjectOfType<FeaturePlayback>();

        if (featurePlayback != null)
        {
            float lastTimestamp = featurePlayback.GetLastTimestamp();

            // uses last time stamp to scale the bar in x
            Vector3 newScale = transform.localScale;
            newScale.x = lastTimestamp /100f;  // optional multiplier
            transform.localScale = newScale;
        }
    }

    private void OnEnable()
    {
        //sub to the python event
        playbackInitializer.instance.onPythonMessageReceived.AddListener(OnAlignmentStepReceived);
    }

    private void OnDisable()
    {
        playbackInitializer.instance.onPythonMessageReceived.RemoveListener(OnAlignmentStepReceived);
    }

    //current timestamp is parse into a float toupdate the progress bar over time
    private void OnAlignmentStepReceived(string message)
    {
        if (float.TryParse(message, out float currentTimestamp))
        {
            UpdateProgress(currentTimestamp);
        }
    }

    //Here the updating happens
    private void UpdateProgress(float currentTimestamp)
    {
        if (child == null || lastTimestamp <= 0)
            return;

        float progress = Mathf.Clamp01(currentTimestamp / lastTimestamp);

        Vector3 scale = child.localScale;
        scale.x = progress;
        child.localScale = scale;
    }
}
