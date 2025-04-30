using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class BandwithOpacity : FeatureVisualizer
{
    [SerializeField] private float lerpSpeed = 5f;

    private Renderer rendr;
    private Material instanceMaterial;

    private float targetValue = 0f;
    private float currentBump = 0f;
    void Awake()
    {
        rendr = GetComponent<Renderer>();

        if (rendr != null)
        {
            // Create instance material
            instanceMaterial = new Material(rendr.material);
            rendr.material = instanceMaterial;
        }
    }

    public override void UpdateFeature(float value)
    {
        
        targetValue = value;
    }


    void Update()
    {
        if (instanceMaterial == null) return;

        // If chroma max is 2 or more, bumpStrength should be 1, else 0
        float targetBump = (targetValue >= 2f) ? 1f : 0f;

        // Smooth transition (optional)
        currentBump = Mathf.Lerp(currentBump, targetBump, lerpSpeed * Time.deltaTime);
        instanceMaterial.SetFloat("_BumpScale", currentBump);
    }


}
