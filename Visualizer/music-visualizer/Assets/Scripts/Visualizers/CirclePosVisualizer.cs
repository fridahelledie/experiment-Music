using UnityEngine;

public class CirclePosVisualizer : FeatureVisualizer
{
    [SerializeField] private float rotationAngle = 0f;
    [SerializeField] private float lerpSpeed = 0.2f;
    [SerializeField] private float minDistance = 0.5f;
    [SerializeField] private float offsetAtMax = 2f;


    private Renderer rendr;
    private Material instanceMaterial;
    private Color originalColor;

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
        if (rendr != null)
        {
            // Create an instance of the material so we don�t modify the shared one
            instanceMaterial = new Material(rendr.material);
            rendr.material = instanceMaterial;
            originalColor = instanceMaterial.color;
        }

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
        if (instanceMaterial != null)
        {
            // Lerp between gray and original color based on value
            Color newColor = Color.Lerp(Color.gray, originalColor, value);
            instanceMaterial.color = newColor;
        }
    }

    void Update()
    {
        transform.localPosition = Vector3.Lerp(transform.localPosition, targetPosition, lerpSpeed * Time.deltaTime);

        UpdateMaterial(targetValue);
    }
}