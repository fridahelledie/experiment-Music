using UnityEngine;

public class LightControlVisualizer : FeatureVisualizer
{
    [SerializeField] private Vector3 startRotation;
    [SerializeField] private Vector3 endRotation;
    [SerializeField] private float lerpSpeed = 0.2f;
    [SerializeField] private float minIntensity = 0.5f;
    [SerializeField] private float maxIntensity = 2.0f;

    private Light lightComponent;
    private Quaternion targetRotation;
    private float targetIntensity;

    void Awake()
    {
        lightComponent = GetComponent<Light>();
        targetRotation = Quaternion.Euler(startRotation);
        targetIntensity = minIntensity;
    }

    public override void UpdateFeature(float value)
    {
        float boostedValue = Mathf.Clamp01(value * 50f);
        // Interpolate between start and end rotation
        targetRotation = Quaternion.Euler(Vector3.Lerp(startRotation, endRotation, value));

        // Interpolate light intensity
        targetIntensity = Mathf.Lerp(minIntensity, maxIntensity, value);
    }

    void Update()
    {
        transform.rotation = Quaternion.Lerp(transform.rotation, targetRotation, lerpSpeed * Time.deltaTime);
        if (lightComponent != null)
        {
            lightComponent.intensity = Mathf.Lerp(lightComponent.intensity, targetIntensity, lerpSpeed * Time.deltaTime);
        }
    }
}