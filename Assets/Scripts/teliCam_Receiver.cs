using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Threading;
using UnityEngine;
using UnityEngine.UI;

public class teliCam_Receiver : MonoBehaviour
{
    Thread receiveThread;
    TcpClient client;
    TcpListener listener;
    int port;
    float timer = 0.0f;
    int seconds;
    int fps = 0;

    public RawImage img;
    byte[] imageDatas = new byte[0];
    Texture2D tex;
    // Start is called before the first frame update
    public void Start()
    {
        InitTcp();
        tex = new Texture2D(720, 540);
    }

    void InitTcp()
    {
        port = 5066;
        print("TCP Initialized");
        IPEndPoint anyIP = new IPEndPoint(IPAddress.Parse("127.0.0.1"), port);
        listener = new TcpListener(anyIP);
        listener.Start();

        receiveThread = new Thread(new ThreadStart(ReceiveData));
        receiveThread.IsBackground = true;
        receiveThread.Start();
    }

    private void OnDestroy()
    {
        receiveThread.Abort();
    }

    private void ReceiveData()
    {
        while(true)
        {
           // print("received somting...");
            fps++;
            try
            {
                client = listener.AcceptTcpClient();
                NetworkStream stream = new NetworkStream(client.Client);
                StreamReader sr = new StreamReader(stream);

                string jsonData = sr.ReadLine();

                Data _imgData = JsonUtility.FromJson<Data>(jsonData);
                imageDatas = _imgData.image;
            }
            catch(Exception e)
            {
                print(e);
            }
        }
    }

    public class Data
    {
        public byte[] image;
    }
    // Update is called once per frame
    // private void FixedUpdate()
    private void Update()
    {
        timer += Time.deltaTime;
        if (timer >= 1f)
        {
            timer = timer % 1f ;
            print(fps);
            fps = 0;
        }
        tex.LoadImage(imageDatas);
        img.texture = tex;
    }
}
