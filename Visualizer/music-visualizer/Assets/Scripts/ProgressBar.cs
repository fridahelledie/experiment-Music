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
        if (max > 0)
            GetCurrentFill();
    }


    void GetCurrentFill()
    {
        float fillAmount = Mathf.Clamp01((float)current / max);
        mask.fillAmount = fillAmount;
    }

   

}
