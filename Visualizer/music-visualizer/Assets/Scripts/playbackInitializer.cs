using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Net.Sockets;
using System.Net;
using System.Text;
using UnityEditor.MemoryProfiler;
using UnityEditor.PackageManager;
using UnityEngine;
using System.Collections.Concurrent;
using UnityEngine.Events;
using System.Threading;

public class playbackInitializer : MonoBehaviour
{
    public static playbackInitializer instance;

    Thread mThread;
    public string connectionIP = "127.0.0.1";
    public int connectionPort = 25001;
    IPAddress localAdd;
    TcpListener listener;
    TcpClient client;
    private Process pythonProcess;
    public class PythonMessageEvent : UnityEvent<string> { }
    public PythonMessageEvent onPythonMessageReceived;
    private ConcurrentQueue<string> messageQueue = new ConcurrentQueue<string>();
    bool running = false;
    bool processingComplete = false;

    public string selectedSong = "None";


    private void Start()
    {
        // Singleton pattern to preserve the instance
        if (instance != null && instance != this)
        {
            Destroy(gameObject);
            return;
        }

        instance = this;
        DontDestroyOnLoad(gameObject); // Preserve across scenes

        onPythonMessageReceived = new PythonMessageEvent();
    }

    private void Update()
    {
        // Process python messages added to the queue by showPythonMessage
        while (messageQueue.TryDequeue(out string message))
        {
            onPythonMessageReceived.Invoke(message);
        }

        if (processingComplete)
        {
            processingComplete = false;
            // Note for future: Add behaviour here for when playback is finished
        }
    }
    public void StartPlayback()
    {
        // Start the thread for receiving data
        ThreadStart ts = new ThreadStart(GetInfo);
        mThread = new Thread(ts);
        mThread.Start();

        //Run songProcessor to generate a visualization if one does not already exist; otherwise, run the alignment script & start playback
        bool generateVisualization = !doesVisualizationExist(selectedSong);

        if (generateVisualization)
        {
            StartPythonProcess("songProcessor", selectedSong); //when json file with name of selected song not present
        }
        else
        {
            StartPythonProcess("OLTW-aligner", selectedSong);
            // Note for future: Start FeaturePlayback, reading the selectedSong and stepping visualization based on python messages sent by oltw script
        }

    }
    #region Functions for starting, ending & communicating with python scripts
    void StartPythonProcess(string scriptName, string songName)
    {
        if (pythonProcess == null || pythonProcess.HasExited)
        {
            pythonProcess = new Process();
            pythonProcess.StartInfo.FileName = "cmd.exe";
            pythonProcess.StartInfo.RedirectStandardInput = true;
            pythonProcess.StartInfo.RedirectStandardOutput = true;
            pythonProcess.StartInfo.RedirectStandardError = true;
            pythonProcess.StartInfo.UseShellExecute = false;
            pythonProcess.StartInfo.CreateNoWindow = true;

            pythonProcess.Start();

            using (StreamWriter sw = pythonProcess.StandardInput)
            {
                if (sw.BaseStream.CanWrite)
                {
                    string condaEnvName = "SoundProcessing";
                    string pythonScriptPath = $"\"{Application.dataPath}/StreamingAssets/Python/{scriptName}.py\"";

                    // Chain environment activation and script execution
                    sw.WriteLine($"call conda activate {condaEnvName} && python {pythonScriptPath} {songName}");
                    sw.WriteLine("exit"); // Exit cmd after running the command (unsure if this is necessary?)
                }
            }

            // Additional message reading for when I need to debug
            /*
            pythonProcess.OutputDataReceived += (sender, e) =>
            {
                if (!string.IsNullOrEmpty(e.Data))
                {
                    showPythonMessage(e.Data);
                }
            };

            pythonProcess.ErrorDataReceived += (sender, e) =>
            {
                if (!string.IsNullOrEmpty(e.Data))
                {
                    UnityEngine.Debug.LogError($"Python error: {e.Data}");
                }
            };

            pythonProcess.BeginOutputReadLine();
            pythonProcess.BeginErrorReadLine();
            */

        }
        else
        {
            UnityEngine.Debug.LogWarning("Python process is already running.");
        }
    }
    void showPythonMessage(string message)
    {
        UnityEngine.Debug.Log($"Python Message: {message}");
        messageQueue.Enqueue(message); // Queue the message for processing on the main thread
    }
    public void CancelProcessing()
    {
        if (pythonProcess != null && !pythonProcess.HasExited)
        {
            pythonProcess.Kill();
            pythonProcess = null;
            UnityEngine.Debug.Log("Python process terminated.");
        }
    }

    void GetInfo()
    {
        localAdd = IPAddress.Parse(connectionIP);
        listener = new TcpListener(localAdd, connectionPort);
        listener.Start();
        client = listener.AcceptTcpClient();
        running = true;

        while (running)
        {
            SendAndReceiveData();
        }
        listener.Stop();
    }

    void SendAndReceiveData()
    {
        NetworkStream nwStream = client.GetStream();
        byte[] buffer = new byte[client.ReceiveBufferSize];

        try
        {
            int bytesRead = nwStream.Read(buffer, 0, client.ReceiveBufferSize);
            if (bytesRead == 0)
            {
                // Assume processing completed if the socket closes
                UnityEngine.Debug.Log("Socket closed by Python. Assuming processing completed.");
                processingComplete = true;
                running = false;
                return;
            }

            string dataReceived = Encoding.UTF8.GetString(buffer, 0, bytesRead).Trim();
            showPythonMessage(dataReceived);

        }
        catch (Exception ex)
        {
            UnityEngine.Debug.LogError($"Socket error: {ex.Message}");
            running = false;
        }
    }
    #endregion Python functions
    bool doesVisualizationExist(string fileName)
    {
        string path = Path.Combine(Application.streamingAssetsPath, "jsonVisualizations/" + fileName);
        return File.Exists(path);
    }
}
