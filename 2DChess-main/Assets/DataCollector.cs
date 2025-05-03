using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class DataCollector : MonoBehaviour
{
    public SSVEP_Blink[] stims;
    [SerializeField] public Transform stimulii;

    public float stimulusTime = 4;
    public float restTime = 3;


    private float leftHandX = -5.5f;
    private float rightHandX = 3.9f;
    float[] verticalYPos = { 6.02f, 4.94f, 3.84f, 3.02f, 1.93f, 0.98f, -0.06f, -0.95f };

    private float topHandY = 7f;
    private float bottomHandY = -2.02f;
    float[] horizontalXPos = { -4.29f, -3.3f, -2.24f, -1.21f, -0.25f, 0.78f, 1.76f, 2.81f };


    public Button startButton;


    // Start is called before the first frame update
    void Start() {
        int count = 8;
        stims = new SSVEP_Blink[count];

        for (int i = 0; i < count; i++)
        {
            string name = "stim" + (i + 1); // stim1, stim2, ...
            stims[i] = stimulii.Find(name)?.gameObject.GetComponent<SSVEP_Blink>();

            if (stims[i] == null)
                Debug.LogWarning(name + " not found as a child!");
        }

        SetVerticalPositions();
    }


    // Update is called once per frame
    void Update() {
    }


    public void StartDataCollection() {
        startButton.interactable = false;
        startButton.gameObject.SetActive(false);
        StartCoroutine(Selection());
    }





    IEnumerator Selection() {

        // Set to vertical positions
        SetVerticalPositions();

        // Blink for rows
        StartBlink();
        yield return new WaitForSeconds(stimulusTime);
        StopBlink();

        // Rest
        yield return new WaitForSeconds(restTime);
        SetHorizontalPositions(); 
        yield return new WaitForSeconds(restTime);

        // Blink for columns
        StartBlink();
        yield return new WaitForSeconds(stimulusTime);
        StopBlink();

        SetVerticalPositions();
        startButton.interactable = true;
        startButton.gameObject.SetActive(true);
    }


    private void StartBlink() {
        for (int i = 0; i < 8; ++i) {
            stims[i].StartBlink();
        }
    }

    private void StopBlink() {
        for (int i = 0; i < 8; ++i) {
            stims[i].StopBlink();
        }
    }


    private void SetVerticalPositions() {
        for (int i = 0; i < 8; ++i) {
            float tempX = 0;
            if (i%2 == 0) {
                tempX = leftHandX;
            }
            else {
                tempX = rightHandX;
            }
            stims[i].gameObject.transform.localPosition = new Vector3(tempX, verticalYPos[i], 0f); // x=2, y=3, z=0
        }
    }

    private void SetHorizontalPositions() {
        for (int i = 0; i < 8; ++i) {
            float tempY = 0;
            if (i%2 == 0) {
                tempY = topHandY;
            }
            else {
                tempY = bottomHandY;
            }
            stims[i].gameObject.transform.localPosition = new Vector3(horizontalXPos[i], tempY, 0f); // x=2, y=3, z=0
        }
    }
}
