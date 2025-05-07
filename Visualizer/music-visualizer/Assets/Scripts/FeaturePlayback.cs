using System.Collections.Generic;
using UnityEngine;
using System.IO;
using Newtonsoft.Json;
using System.Globalization;
using System.Linq;
using Unity.VisualScripting;
using static UnityEngine.EventSystems.EventTrigger;
using System.Collections;
using UnityEngine.UIElements;

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

    public delegate void MaxChromaRecieved(float maxChroma);
    public static MaxChromaRecieved OnMaxChromaRecieved;

    public delegate void SpectralCentroidRecieved(float spectralCentroid);
    public static SpectralCentroidRecieved OnSpectralCentroidRecieved;

    public delegate void SpectralBandwidthRecieved(float spectralBandwidth);
    public static SpectralBandwidthRecieved OnSpectralBandwidthRecieved;

    Progress_bar progressBar;
    public AudioSource audio;

    [System.Serializable]
    public class FeatureEntry
    {
        public float timestamp;
        public float onset;
        public float amplitude;
        public float[] chroma;
        public float? beat_times;
        public float spectral_centroid;
        public float spectral_bandwidth;
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
        //Debug.Log("Received message from Python: " + message);
        if (float.TryParse(message, NumberStyles.Float, CultureInfo.InvariantCulture, out float stepFloat))
        {
            int stepIndex = Mathf.FloorToInt(stepFloat);
            //Debug.Log($"Parsed step index: {stepIndex} (last was {lastStepIndex})");
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
    public void startSteppingWithAlignmentFile()
    {
        StartCoroutine(StepWithAlignmentFile());
    }

    IEnumerator StepWithAlignmentFile()
    {
        yield return new WaitForSeconds(5);
        progressBar = FindObjectOfType<Progress_bar>();


        string filePath = Path.Combine(Application.streamingAssetsPath, "alignment-path.txt");
        string fileDump = File.ReadAllText(filePath);

        string[] alignmentPath = fileDump.Split("\n");

        Queue<alignmentEntry> entries = new Queue<alignmentEntry>();


        alignmentEntry lastEntry = new alignmentEntry("1,1");


        for (int i = 0; i < alignmentPath.Length; i++) 
        {
            alignmentEntry newEntry = new alignmentEntry(alignmentPath[i]);

            entries.Enqueue(newEntry);
            lastEntry = newEntry;
        }


        float secondsPerI = 354f / lastEntry.i;
        audio.Play();

        while (entries.Count > 0)
        {
            alignmentEntry currentI = entries.Dequeue();

            Queue<alignmentEntry> currentIQueue = new Queue<alignmentEntry>();

            currentIQueue.Enqueue(currentI);

            while (entries.Count > 0 && entries.Peek().i == currentI.i)
            {
                currentIQueue.Enqueue(entries.Dequeue());
            }

            float timePerEntry = secondsPerI / (float)currentIQueue.Count;
            print("time per entry" + timePerEntry);


            foreach (alignmentEntry pathPoint in currentIQueue)
            {
                ApplyFeatureStep(featureData[pathPoint.j]);
                progressBar.UpdateProgress(pathPoint.j);
                yield return new WaitForSeconds(timePerEntry);
            }

        }
        yield return null;
    }

    public class alignmentEntry
    {
        public int i;
        public int j;

        public alignmentEntry(string input)
        {
            string[] inputArray = input.Split(",");
            int.TryParse(inputArray[0], out int i);
            int.TryParse(inputArray[1], out int j);

            this.i = i;
            this.j = j;
        }
    }

    private void ApplyFeatureStep(FeatureEntry entry)
    {
        ChromaFeature chromaFeature = new ChromaFeature(
            entry.chroma[9], entry.chroma[10], entry.chroma[11], entry.chroma[0], entry.chroma[1],
            entry.chroma[2], entry.chroma[3], entry.chroma[4], entry.chroma[5], entry.chroma[6],
            entry.chroma[7], entry.chroma[8]
        );
        //print("chroma features");
        OnsetFeatures onsetFeature = new OnsetFeatures(entry.onset);
        AmplitudeFeature amplitudeFeature = new AmplitudeFeature(entry.amplitude);
        if (IsBeatDetected(entry.beat_times))
        {
            OnBeatDetected?.Invoke();
        }

        onChromaFeatureRecieved?.Invoke(chromaFeature);
        if (entry.onset > 0.3f) OnsetFeatureRecieved?.Invoke(onsetFeature);
        AmplitudeFeatureRecieved?.Invoke(amplitudeFeature);

        float maxChroma = Mathf.Max(entry.chroma);
        OnMaxChromaRecieved?.Invoke(maxChroma);


        OnSpectralCentroidRecieved?.Invoke(entry.spectral_centroid);
        OnSpectralBandwidthRecieved?.Invoke(entry.spectral_bandwidth);
    }

    private bool IsBeatDetected(float? beatTime)
    {
        return beatTime.HasValue;
    }

    public int GetLastTimestamp()
    {
        if (featureData != null && featureData.Count > 0)
        {
            // return featureData[featureData.Count - 1].timestamp;
            return featureData.Count;
        }
        return 0;
    }
    public List<float> GetAmplitudes()
    {
        return featureData.Select(f => f.amplitude).ToList();
    }

}
