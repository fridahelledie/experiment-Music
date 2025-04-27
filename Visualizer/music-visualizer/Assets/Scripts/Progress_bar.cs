using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Progress_bar : MonoBehaviour
{
    private FeaturePlayback featurePlayback;
    

    // Start is called before the first frame update
    void Start()
    {
        featurePlayback = FindObjectOfType<FeaturePlayback>();

        if (featurePlayback != null)
        {
            float lastTimestamp = featurePlayback.GetLastTimestamp();

            // uses last time stamp to scale the bar in x
            Vector3 newScale = transform.localScale;
            newScale.x = lastTimestamp * 0.1f;  // optional multiplier
            transform.localScale = newScale;
        }
    }

    // Update is called once per frame
    void Update()
    {
        
    }
}
