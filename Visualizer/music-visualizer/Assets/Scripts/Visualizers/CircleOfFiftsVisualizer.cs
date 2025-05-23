using UnityEngine;

public class CircleOfFifthsVisualizer : FeatureVisualizer
{
    [SerializeField] private Transform[] wedges;
    [SerializeField] private float minScale = 0.5f;
    [SerializeField] private float maxScale = 1.5f;
    [SerializeField] private Color baseColor = Color.gray;
    [SerializeField] private float lerpSpeed = 5f;

    private Vector3[] targetScales;
    private Color[] targetColors;
    private Color[] originalColors;
    private Renderer[] renderers;

    void Awake()
    {
        if (wedges.Length != 12)
        {
            Debug.LogError("CircleOfFifthsVisualizer: Please assign exactly 12 wedges.");
            enabled = false;
            return;
        }

        targetScales = new Vector3[12];
        targetColors = new Color[12];
        originalColors = new Color[12];
        renderers = new Renderer[12];

        for (int i = 0; i < 12; i++)
        {
            targetScales[i] = Vector3.one * minScale;
            renderers[i] = wedges[i].GetComponent<Renderer>();
            if (renderers[i] != null)
            {
                // Instance material so we don�t affect shared one
                renderers[i].material = new Material(renderers[i].material);
                // Store original color from material as max (highlight) color
                originalColors[i] = renderers[i].material.color;
                // Initialize target color as baseColor
                targetColors[i] = baseColor;
            }
        }
    }

    public override void UpdateFeature(float[] chromaValues)
    {
        if (chromaValues.Length != 12)
        {
            Debug.LogWarning("UpdateFeature expects 12 chroma values.");
            return;
        }

        for (int i = 0; i < 12; i++)
        {
            float value = Mathf.Clamp01(chromaValues[i]);
            float scale = Mathf.Lerp(minScale, maxScale, value);
            targetScales[i] = Vector3.one * scale;

            // Lerp between baseColor and originalColor of this wedge
            targetColors[i] = Color.Lerp(baseColor, originalColors[i], value);
        }
    }
    public override void UpdateFeature(float input)
    {
        Debug.LogWarning("Use the other UpdateFeature for CircleOfFiftsVisualizer");
    }
    void Update()
    {
        for (int i = 0; i < 12; i++)
        {
            // Smooth scale transition
            wedges[i].localScale = Vector3.Lerp(wedges[i].localScale, targetScales[i], lerpSpeed * Time.deltaTime);

            // Smooth color transition
            if (renderers[i] != null)
            {
                Color currentColor = renderers[i].material.color;
                Color newColor = Color.Lerp(currentColor, targetColors[i], lerpSpeed * Time.deltaTime);
                renderers[i].material.color = newColor;
            }
        }
    }
}
