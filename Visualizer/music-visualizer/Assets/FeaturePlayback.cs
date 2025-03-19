using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.IO;
using Newtonsoft.Json;

public class FeaturePlayback : MonoBehaviour
{
    private List<FeatureEntry> featureData;
    private float startTime;

    public delegate void ChromaFeatureRecieved(ChromaFeature chromaFeature);
    public static ChromaFeatureRecieved onChromaFeatureRecieved;

    public delegate void OnsetFeaturesRecieved(OnsetFeatures onsetFeatures);
    public static OnsetFeaturesRecieved OnsetFeatureRecieved;

    [System.Serializable] // matches the data structure of the saves json files
    public class FeatureEntry
    {
        public float timestamp;
        public float onset;
        public float[] chroma;
    }

    void Start()
    {
        LoadFeatureData();
        StartCoroutine(PlayFeatures());
    }

    void LoadFeatureData()
    {
        string filePath = Path.Combine(Application.streamingAssetsPath, "audio_features.json");
        if (File.Exists(filePath))
        {
            string json = File.ReadAllText(filePath);
            featureData = JsonConvert.DeserializeObject<List<FeatureEntry>>(json);
            Debug.Log("Feature data loaded.");
        }
        else
        {
            Debug.LogError("Feature file not found!");
        }
    }

    IEnumerator PlayFeatures()
    {
        startTime = Time.time;

        foreach (var entry in featureData)
        {
            // Wait till timestamp of entry before processing data (We'll need to replace this with time stepping logic from OLTW algorithm)
            float waitTime = entry.timestamp - (Time.time - startTime);
            if (waitTime > 0) yield return new WaitForSeconds(waitTime);

            // Convert json data to ChromaFeature and OnsetFeatures objects
            ChromaFeature chromaFeature = new ChromaFeature(
                entry.chroma[0], entry.chroma[1], entry.chroma[2], entry.chroma[3], entry.chroma[4],
                entry.chroma[5], entry.chroma[6], entry.chroma[7], entry.chroma[8], entry.chroma[9],
                entry.chroma[10], entry.chroma[11]
            );

            OnsetFeatures onsetFeature = new OnsetFeatures(entry.onset);

            // Call delegate functions
            onChromaFeatureRecieved?.Invoke(chromaFeature);
            if (entry.onset > 0.3f) OnsetFeatureRecieved?.Invoke(onsetFeature); // Have to use same threshold as python to prevent invoking function with null data
        }
    }
}
