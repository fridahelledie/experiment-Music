using System.Collections.Generic;
using UnityEngine;
using System.IO;
using Newtonsoft.Json;
using System.Globalization;

public class FeaturePlayback : MonoBehaviour
{
    private List<FeatureEntry> featureData;
    private int lastStepIndex = -1;

    public delegate void ChromaFeatureRecieved(ChromaFeature chromaFeature);
    public static ChromaFeatureRecieved onChromaFeatureRecieved;

    public delegate void OnsetFeaturesRecieved(OnsetFeatures onsetFeatures);
    public static OnsetFeaturesRecieved OnsetFeatureRecieved;

    public delegate void AmplitudeFeaturesRecieved(AmplitudeFeature amplitudeFeature);
    public static AmplitudeFeaturesRecieved AmplitudeFeatureRecieved;

    public delegate void BeatDetected();
    public static BeatDetected OnBeatDetected;

    [System.Serializable]
    public class FeatureEntry
    {
        public float timestamp;
        public float onset;
        public float amplitude;
        public float[] chroma;
        public float? beat_times;
    }

    // Called externally to start live-aligned visualization
    public void StartLivePlayback(string songName)
    {
        string jsonPath = Path.Combine(Application.streamingAssetsPath, "jsonVisualizations", Path.ChangeExtension(songName, ".json"));
        if (File.Exists(jsonPath))
        {
            string json = File.ReadAllText(jsonPath);
            featureData = JsonConvert.DeserializeObject<List<FeatureEntry>>(json);
            Debug.Log("Live feature data loaded.");
        }
        else
        {
            Debug.LogError("Feature JSON file not found for: " + songName);
            return;
        }

        // Register listener for Python alignment updates
        playbackInitializer.instance.onPythonMessageReceived.AddListener(OnAlignmentStepReceived);
    }

    // Called each time OLTW-aligner sends a new alignment step
    private void OnAlignmentStepReceived(string message)
    {
        Debug.Log("Received message from Python: " + message);
        if (float.TryParse(message, NumberStyles.Float, CultureInfo.InvariantCulture, out float stepFloat))
        {
            int stepIndex = Mathf.FloorToInt(stepFloat);
            Debug.Log($"Parsed step index: {stepIndex} (last was {lastStepIndex})");
            if (stepIndex != lastStepIndex && stepIndex >= 0 && stepIndex < featureData.Count)
            {
                lastStepIndex = stepIndex;
                ApplyFeatureStep(featureData[stepIndex]);
            }
            else
            {
                Debug.LogWarning("Failed to parse message from Python: " + message);
            }
        }
    }

    private void ApplyFeatureStep(FeatureEntry entry)
    {
        ChromaFeature chromaFeature = new ChromaFeature(
            entry.chroma[9], entry.chroma[10], entry.chroma[11], entry.chroma[0], entry.chroma[1],
            entry.chroma[2], entry.chroma[3], entry.chroma[4], entry.chroma[5], entry.chroma[6],
            entry.chroma[7], entry.chroma[8]
        );
        print("chroma features");
        OnsetFeatures onsetFeature = new OnsetFeatures(entry.onset);
        AmplitudeFeature amplitudeFeature = new AmplitudeFeature(entry.amplitude);
        if (IsBeatDetected(entry.beat_times))
        {
            OnBeatDetected?.Invoke();
        }

        onChromaFeatureRecieved?.Invoke(chromaFeature);
        if (entry.onset > 0.3f) OnsetFeatureRecieved?.Invoke(onsetFeature);
        AmplitudeFeatureRecieved?.Invoke(amplitudeFeature);
    }

    private bool IsBeatDetected(float? beatTime)
    {
        return beatTime.HasValue;
    }

    public float GetLastTimestamp()
    {
        if (featureData != null && featureData.Count > 0)
        {
            return featureData[featureData.Count - 1].timestamp;
        }
        return 0f;
    }
}
