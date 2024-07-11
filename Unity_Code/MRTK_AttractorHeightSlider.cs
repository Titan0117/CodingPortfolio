using Microsoft.MixedReality.Toolkit.UI;
using System.Collections;
using System.Collections.Generic;
using TMPro;
using UnityEngine;
using Microsoft.MixedReality.Toolkit.Experimental;
using System.Reflection;
using UnityEngine.UIElements;
using System;
using FFCore;
using mixpanel;
using Unity.Mathematics;

public class MRTK_AttractorHeightSlider : MonoBehaviour
{
    public PinchSlider _redHeightSlider = null;
    public PinchSlider _yellowHeightSlider = null;
    public PinchSlider _greenHeightSlider = null;
    public PinchSlider _redSizeSlider = null;
    public PinchSlider _yellowSizeSlider = null;
    public PinchSlider _greenSizeSlider = null;
    public float _heightMax;
    public float _heightMed;
    public float _heightMin;
    public float _sizeMax;
    public float _sizeMid;
    public float _sizeMin;
    private Camera _user;
    public GameObject[] _gem;
    private float _distance;
    private float _gemHeight, _gemSize;
    public float _distanceMax, _distanceMid, _distanceMin;
    private float time = 0.0f;
    public float interpolationPeriod = 0.1f;
    private float b1, b2, m1, m2;
    private float _GreenYellowHeightLerp;
    private float _MinMedDistLerp;
    private float _MinMedHeightLerp;
    private float _MinMedSizeLerp;
    private float smoothTime;
    private Vector3 _currentVelocity;
    private float _lastGemTime;
    private float _MedMaxDistLerp;
    private float _MedMaxHeightLerp;
    private float _MedMaxSizeLerp;
    private PinchSlider _activeHeightSlider, _activeSizeSlider;
    private Color _MinMedLerpedColor;
    private Color _MedMaxLerpedColor;

    [AddComponentMenu("Scripts/MRTK/Examples/ShowSliderValue")]


    private void Start()
    {
        _lastGemTime = Time.time;
        _user = Camera.main;
        SliderUpdate();
        adjustGem();
    }

    private void SliderUpdate()
    {
        print("updatingSlider");   

    }

    private void Update()
    {
        //set an update/refresh period
        time += Time.deltaTime;

        if (time >= interpolationPeriod)
        {
            time = 0.0f;
            adjustGem();
        }
    }

    public void adjustGem()
    {

        //Add Slider Value to Height values

        foreach (GameObject _piece in _gem)
        {

            //get position of the piece and declare y as 0
            Vector3 _piecePosition = _piece.transform.position;
            _piecePosition.y = 0;
            // _piecePosition.z = 0;
            //Math.Round(_piecePosition.x, 4); 

            //get camera position and declare y value as 0
            Vector3 playerPosition = _user.transform.position;
            playerPosition.y = 0;
            //playerPosition.z = 0;
            //Math.Round(playerPosition.x, 4);

            //get the distance between the piece and the user
            _distance = Vector3.Distance(playerPosition, _piecePosition);
            _distance = (float)Math.Round(_distance, 2);
            print("I got the distance" + _distance);
            var _pieceRenderer = _piece.GetComponent<Renderer>();


            if (_distance < _distanceMid)
            {   
                _MinMedDistLerp = Mathf.InverseLerp(_distanceMid, _distanceMin, _distance);

                _MinMedHeightLerp = Mathf.SmoothStep(_heightMed + _yellowHeightSlider.SliderValue, (_heightMin + _greenHeightSlider.SliderValue), _MinMedDistLerp);
                _MinMedSizeLerp = Mathf.SmoothStep(_sizeMid + _yellowSizeSlider.SliderValue, _sizeMin + _greenSizeSlider.SliderValue,_MinMedDistLerp);
               
                _piece.transform.position = Vector3.SmoothDamp(_piece.transform.position,
                    new Vector3(_piece.transform.position.x, _MinMedHeightLerp, _piece.transform.position.z),
                    ref _currentVelocity,
                    1f,
                    1f,
                    Time.time - _lastGemTime);
                
                _piece.transform.localScale = Vector3.SmoothDamp(_piece.transform.localScale,
                    new Vector3(_MinMedSizeLerp, _MinMedSizeLerp, _MinMedSizeLerp),
                    ref _currentVelocity,
                    1f,
                    1f,
                    Time.time - _lastGemTime);
              


                _MinMedLerpedColor = Color.Lerp(Color.yellow, Color.green, _MinMedDistLerp);
                _pieceRenderer.material.SetColor("_Color", _MinMedLerpedColor);
            }
            if (_distance >= _distanceMid)
            {
                _MedMaxDistLerp = Mathf.InverseLerp(_distanceMax, _distanceMid, _distance);

                _MedMaxHeightLerp = Mathf.SmoothStep(_heightMax + _redHeightSlider.SliderValue, _heightMed + _yellowHeightSlider.SliderValue, _MedMaxDistLerp);
                _MedMaxSizeLerp = Mathf.SmoothStep(_sizeMax + _redSizeSlider.SliderValue, _sizeMid + _yellowSizeSlider.SliderValue, _MedMaxDistLerp);
                _piece.transform.position = Vector3.SmoothDamp(_piece.transform.position,
                    new Vector3(_piece.transform.position.x, _MedMaxHeightLerp, _piece.transform.position.z),
                    ref _currentVelocity,
                    1f,
                    1f,
                    Time.time - _lastGemTime);

                _piece.transform.localScale = Vector3.SmoothDamp(_piece.transform.localScale,
                    new Vector3(_MedMaxSizeLerp, _MedMaxSizeLerp, _MedMaxSizeLerp),
                    ref _currentVelocity,
                    1f,
                    1f,
                    Time.time - _lastGemTime);
                _MedMaxLerpedColor = Color.Lerp(Color.red, Color.yellow, _MedMaxDistLerp);
                _pieceRenderer.material.SetColor("_Color", _MedMaxLerpedColor);
            }
        }   
        _lastGemTime = Time.deltaTime;
    }
}
