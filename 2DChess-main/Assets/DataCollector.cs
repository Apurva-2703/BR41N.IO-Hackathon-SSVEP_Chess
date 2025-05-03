using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class DataCollector : MonoBehaviour
{
    [SerializeField] public SSVEP_Blink stim1;
    [SerializeField] public SSVEP_Blink stim2;
    [SerializeField] public SSVEP_Blink stim3;
    [SerializeField] public SSVEP_Blink stim4;
    [SerializeField] public SSVEP_Blink stim5;
    [SerializeField] public SSVEP_Blink stim6;
    [SerializeField] public SSVEP_Blink stim7;
    [SerializeField] public SSVEP_Blink stim8;

    private float stimulusTime = 4;


    // Start is called before the first frame update
    void Start() {
        
    }


    // Update is called once per frame
    void Update() {
        if (Input.GetKeyDown(KeyCode.Space))
        {
            StartCoroutine(Selection());
        }
    }

    IEnumerator Selection() {
        stim1.StartBlink();
        stim2.StartBlink();
        stim3.StartBlink();
        stim4.StartBlink();
        stim5.StartBlink();
        stim6.StartBlink();
        stim7.StartBlink();
        stim8.StartBlink();

        yield return new WaitForSeconds(4);

        stim1.StopBlink();
        stim2.StopBlink();
        stim3.StopBlink();
        stim4.StopBlink();
        stim5.StopBlink();
        stim6.StopBlink();
        stim7.StopBlink();
        stim8.StopBlink();

        yield return new WaitForSeconds(4);
    }
}
