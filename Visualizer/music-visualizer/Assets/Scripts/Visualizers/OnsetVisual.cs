using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class OnsetVisual : MonoBehaviour
{
    public float scale = 5f;
    public object particle;
    // Start is called before the first frame update
    void Start()
    {
        //FeaturePlayback.OnsetFeatureRecieved += scaleEffect;
    }

    public void scaleEffect()
    {
        //particle = transform.localScale(0,0,scale);
    }
}
