using UnityEngine;

public class CirclePosVisualizer : FeatureVisualizer
{
    [SerializeField] private float rotationAngle = 0f;
    [SerializeField] private float lerpSpeed = 0.2f;
    [SerializeField] private float minDistance = 0.5f;
    [SerializeField] private float offsetAtMax = 2f;

    [SerializeField] Material blackMaterial;
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
            if (value >= 0.4)
            {
                rendr.material = blackMaterial;
            }
            else
            {
                rendr.material.Lerp(blackMaterial, colorMaterial, value);
            }
        }
    }

    void Update()
    {
        transform.localPosition = Vector3.Lerp(transform.localPosition, targetPosition, lerpSpeed * Time.deltaTime);

        UpdateMaterial(targetValue);
    }
}