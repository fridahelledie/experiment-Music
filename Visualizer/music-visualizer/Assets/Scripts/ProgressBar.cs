using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;


[ExecuteInEditMode()]
public class ProgressBar : MonoBehaviour
{
    public int max; //skal connectes med json
    public int current; // skal følges med timestamps
    public Image mask;


    // Start is called before the first frame update
    void Update()
    {
        Debug.Log("ProgressBar Update called");
        if (max > 0)
            GetCurrentFill();
    }


    void GetCurrentFill()
    {
        float fillAmount = Mathf.Clamp01((float)current / max);
        Debug.Log($"Current: {current}, Max: {max}, Fill: {fillAmount}");
        mask.fillAmount = fillAmount;
    }

   

}
