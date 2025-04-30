using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class Progress_bar : MonoBehaviour
{
    private FeaturePlayback featurePlayback;
    [SerializeField] private Transform child;
    private float lastTimestamp; //here the last timestamp in json should be stored
    private int featureCount;
    private Image childImage;

    [SerializeField] private LineRenderer amplitudeLine;
    [SerializeField] private Vector2 lineSize = new Vector2(5f, 1f); // width, height of the line
    private List<float> amplitudes; // amplitude history from featureData
    private Vector3[] fullLinePositions; // stored waveform data


    // Start is called before the first frame update
    void Start()
    {
        featurePlayback = FindObjectOfType<FeaturePlayback>();

        if (featurePlayback != null)
        {
            /*
            lastTimestamp = featurePlayback.GetLastTimestamp();

            // uses last time stamp to scale the bar in x
            Vector3 newScale = transform.localScale;
            newScale.x = lastTimestamp /100f;  // optional multiplier
            transform.localScale = newScale;
            */
            featureCount = Mathf.Max(1, featurePlayback.GetLastTimestamp()); // avoid divide by zero

            if (child != null)
            {
                childImage = child.GetComponent<Image>();
            }
            // Get amplitudes from featurePlayback
            amplitudes = featurePlayback.GetAmplitudes();
            SetupAmplitudeLine();
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
        if (float.TryParse(message, out float currentIndexFloat))
        {
            // Unity can't parse the alignment step messages as ints so we need to get them into a float first
            int currentIndex = (int)currentIndexFloat;
            UpdateProgress(currentIndex);
        }
        else
        {
            Debug.LogWarning($"Could not parse step index from message: {message}");
        }
    }

    //Here the updating happens
    private void UpdateProgress(int currentIndex)
    {
        if (childImage == null || featureCount <= 1)
            return;

        float progress = Mathf.Clamp01((float)currentIndex / (featureCount - 1));
        childImage.fillAmount = progress;

        // Draw the amplitude line up to current index
        if (amplitudeLine != null && fullLinePositions != null && currentIndex < fullLinePositions.Length)
        {
            amplitudeLine.positionCount = currentIndex + 1;
            for (int i = 0; i <= currentIndex; i++)
            {
                amplitudeLine.SetPosition(i, fullLinePositions[i]);
            }
        }
    }
    void SetupAmplitudeLine()
    {
        if (amplitudeLine == null || amplitudes == null || amplitudes.Count == 0)
            return;

        fullLinePositions = new Vector3[amplitudes.Count];

        for (int i = 0; i < amplitudes.Count; i++)
        {
            float x = ((float)i / (amplitudes.Count - 1)) * lineSize.x;
            float y = amplitudes[i] * lineSize.y;
            fullLinePositions[i] = new Vector3(x, y, 0);
        }

        // Start with just one point
        amplitudeLine.positionCount = 1;
        amplitudeLine.SetPosition(0, fullLinePositions[0]);
    }

}
