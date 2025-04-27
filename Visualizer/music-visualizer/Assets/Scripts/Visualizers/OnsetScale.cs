using System.Collections;
using System.Collections.Generic;
using UnityEngine;


public class OnsetScale : FeatureVisualizer
{
    
    [SerializeField] Vector3 scaleMax;
    private Vector3 scaleMin;
    private Vector3 targetScale;
    [SerializeField] float lerpSpeed = 0.2f;
   

    private void Awake()
    {

        scaleMin = transform.localScale;
        targetScale = scaleMin;
    }

    public override void UpdateFeature(float value)
    {

        targetScale = Vector3.Lerp(scaleMin, scaleMax, value);
    }
    void Start()
    {
        
    }

    void Update()
    {
        transform.localScale = Vector3.Lerp(transform.localScale, targetScale, lerpSpeed * Time.deltaTime);
    }
}
