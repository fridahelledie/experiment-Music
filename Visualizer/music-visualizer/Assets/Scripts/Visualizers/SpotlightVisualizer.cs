using UnityEngine;

public class SpotlightVisualizer : FeatureVisualizer
{
    [SerializeField] private Light spotLight;

    // Bandwidth - Spot Angle control
    [SerializeField] private float minBandwidth = 400f;
    [SerializeField] private float maxBandwidth = 1800f;
    [SerializeField] private float minSpotAngle = 15f;
    [SerializeField] private float maxSpotAngle = 80f;

    // Centroid - Color + Rotation control
    [SerializeField] private float minCentroid = 400f;
    [SerializeField] private float maxCentroid = 1800f;
    [SerializeField] private Color lowCentroidColor = Color.blue;
    [SerializeField] private Color highCentroidColor = Color.red;
    [SerializeField] private float minRotationY = 0f;
    [SerializeField] private float maxRotationY = 180f;

    [SerializeField] private float lerpSpeed = 5f;

    private float targetSpotAngle;
    private Color targetColor;
    private float targetRotationY;

    void Awake()
    {
        if (spotLight == null)
        {
            Debug.LogError("SpotlightVisualizer: Please assign a spotLight.");
            enabled = false;
            return;
        }

        targetSpotAngle = spotLight.spotAngle;
        targetColor = spotLight.color;
        targetRotationY = transform.eulerAngles.y;
    }

    // Expects float[2]: [bandwidth, centroid]
    public override void UpdateFeature(float[] features)
    {
        if (features.Length != 2)
        {
            Debug.LogWarning("Spotlightvisualizer expects exactly 2 feature values [bandwidth, centroid].");
            return;
        }

        float bandwidth = features[0];
        float centroid = features[1];

        // Normalize bandwidth (0–1)
        float bwNorm = Mathf.InverseLerp(minBandwidth, maxBandwidth, bandwidth);
        bwNorm = Mathf.Clamp01(bwNorm);

        // Normalize centroid (0–1)
        float centNorm = Mathf.InverseLerp(minCentroid, maxCentroid, centroid);
        centNorm = Mathf.Clamp01(centNorm);

        // Map to spot angle
        targetSpotAngle = Mathf.Lerp(minSpotAngle, maxSpotAngle, bwNorm);

        // Map to color
        targetColor = Color.Lerp(lowCentroidColor, highCentroidColor, centNorm);

        // Map to Y rotation
        targetRotationY = Mathf.Lerp(minRotationY, maxRotationY, centNorm);
    }
    public override void UpdateFeature(float input)
    {
        Debug.LogWarning("Use the other UpdateFeature for SpotlightVisualizer");
    }
    void Update()
    {
        // Smoothly update spotlight properties
        spotLight.spotAngle = Mathf.Lerp(spotLight.spotAngle, targetSpotAngle, lerpSpeed * Time.deltaTime);
        spotLight.color = Color.Lerp(spotLight.color, targetColor, lerpSpeed * Time.deltaTime);

        // Smoothly update rotation
        Vector3 currentEuler = transform.eulerAngles;
        float newY = Mathf.LerpAngle(currentEuler.y, targetRotationY, lerpSpeed * Time.deltaTime);
        transform.eulerAngles = new Vector3(currentEuler.x, newY, currentEuler.z);
    }
}
