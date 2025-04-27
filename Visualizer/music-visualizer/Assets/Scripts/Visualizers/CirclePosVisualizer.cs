using UnityEngine;

public class CirclePosVisualizer : FeatureVisualizer
{
    [SerializeField] private float rotationAngle = 0f;
    [SerializeField] private float lerpSpeed = 0.2f;
    [SerializeField] private float minDistance = 0.5f;
    [SerializeField] private float offsetAtMax = 2f;

    
    [SerializeField] Material colorMaterial;

    private Renderer rendr;

    private Vector3 initialPosition;
    private Vector3 targetPosition;
    private float targetValue = 0;

    void Awake()
    {
        // Calculate initial position based on the rotation angle
        float radians = rotationAngle * Mathf.Deg2Rad;
        initialPosition = new Vector3(Mathf.Cos(radians), Mathf.Sin(radians), 0);
        transform.localPosition = initialPosition * minDistance;
        targetPosition = initialPosition * minDistance;
        rendr = GetComponent<Renderer>();
    }

    public override void UpdateFeature(float value)
    {
        targetValue = value;
        // Move outward by scaling the initial position between minDistance and maxDistance
        float distance = Mathf.Lerp(minDistance, offsetAtMax, value);
        targetPosition = initialPosition * distance;
    }
    void UpdateMaterial(float value)
    {
        if (rendr != null)
        {
            Color orgColor = rendr.material.color;
            // material converted to hsv so we can manipulate brightness later
            Color.RGBToHSV(orgColor, out float h, out float s, out float v);

            //here the value is changed depending on the value
            float newSaturation = Mathf.Lerp(0f, 1f, value); // 0 = grayscale, 1 = full color

            //converted back to RGB to be used as the color yay
            Color newColor = Color.HSVToRGB(h, newSaturation, v);

            rendr.material.color = newColor;
        }
    }

    void Update()
    {
        transform.localPosition = Vector3.Lerp(transform.localPosition, targetPosition, lerpSpeed * Time.deltaTime);

        UpdateMaterial(targetValue);
    }
}