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

    public float maxDuration = 1f;
    public float currentTime = 0f;


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
    

    public void SetMaxDuration(float max)
    {
        maxDuration = Mathf.Max(1f, max); // prevent divide by zero
    }

    public void UpdateProgress(float current)
    {
        currentTime = Mathf.Clamp(current, 0f, maxDuration);
        float fillAmount = currentTime / maxDuration;
        mask.fillAmount = fillAmount;

        Debug.Log($"ProgressBar: {currentTime:F2}/{maxDuration:F2} ({fillAmount:P0})");
    }


}
