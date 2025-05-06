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
using UnityEngine.SceneManagement;
using System.Threading;
using UnityEngine.Networking;

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
    public string songFiletype = "None"; // we should probably automate this instead of having to manually type it
    bool readyToPlay = false;
    public AudioSource audioSource;


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
        if (readyToPlay && Input.GetKeyDown(KeyCode.Space))     
        {
            readyToPlay = false;
            SendToPython("START");
            audioSource.Play();
        }
    }
    public void StartPlayback()
    {
        //StartCoroutine(loadAudio());

        SceneManager.LoadScene("FinalScene");
        // Start the thread for receiving data
        ThreadStart ts = new ThreadStart(GetInfo);
        mThread = new Thread(ts);
        mThread.Start();

        //Run songProcessor to generate a visualization if one does not already exist; otherwise, run the alignment script & start playback
        bool generateVisualization = !doesVisualizationExist(selectedSong);

        if (generateVisualization)
        {
            StartPythonProcess("songProcessor", selectedSong + songFiletype); //when json file with name of selected song not present
        }
        else
        {
            FeaturePlayback bruh = FindObjectOfType<FeaturePlayback>();
            bruh.StartLivePlayback(selectedSong);
            bruh.startSteppingWithAlignmentFile();

            // StartPythonProcess("OLTW-aligner", selectedSong + songFiletype);
            // Note for future: Start FeaturePlayback, reading the selectedSong and stepping visualization based on python messages sent by oltw script
        }

    }
    private void OnApplicationQuit()
    {
        CancelProcessing();
    }
    IEnumerator loadAudio()
    {
        string filePath = System.IO.Path.Combine(Application.streamingAssetsPath, "audio", selectedSong + songFiletype);
        string url = "file://" + filePath;
        using (UnityWebRequest www = UnityWebRequestMultimedia.GetAudioClip(url, AudioType.UNKNOWN))
        {
            yield return www.SendWebRequest();

            if (www.result != UnityWebRequest.Result.Success)
            {
                UnityEngine.Debug.LogError("Failed to load audio: " + www.error);
                UnityEngine.Debug.LogError(url);

            }
            else
            {
                AudioClip clip = DownloadHandlerAudioClip.GetContent(www);
                audioSource.clip = clip;
            }
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
                    string pythonScriptPath = $"\"{Application.dataPath}/StreamingAssets/{scriptName}.py\"";

                    // Chain environment activation and script execution
                    sw.WriteLine($"call conda activate {condaEnvName} && python {pythonScriptPath} {songName}");
                    sw.WriteLine("exit"); // Exit cmd after running the command (unsure if this is necessary?)
                }
            }

            // Additional message reading for when I need to debug
            
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
        if (message == "READY")
        {
            readyToPlay = true;
        }

    }
    public void CancelProcessing()
    {
        if (pythonProcess != null && !pythonProcess.HasExited)
        {
            try
            {
                int pid = pythonProcess.Id;

                // Kill the cmd.exe AND its children (like python.exe)
                Process killer = new Process();
                killer.StartInfo.FileName = "taskkill";
                killer.StartInfo.Arguments = $"/PID {pid} /T /F";
                killer.StartInfo.CreateNoWindow = true;
                killer.StartInfo.UseShellExecute = false;
                killer.Start();
                killer.WaitForExit();

                UnityEngine.Debug.Log("Successfully killed Python process tree.");
            }
            catch (Exception ex)
            {
                UnityEngine.Debug.LogError($"Error killing process tree: {ex.Message}");
            }
            finally
            {
                pythonProcess = null;
            }
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
    void SendToPython(string message)
    {
        if (client != null && client.Connected)
        {
            try
            {
                NetworkStream nwStream = client.GetStream();
                byte[] buffer = Encoding.UTF8.GetBytes(message);
                nwStream.Write(buffer, 0, buffer.Length);
                nwStream.Flush();
            }
            catch (Exception ex)
            {
                UnityEngine.Debug.LogError($"Error sending message to Python: {ex.Message}");
            }
        }
    }

    #endregion Python functions
    bool doesVisualizationExist(string fileName)
    {
        string path = Path.Combine(Application.streamingAssetsPath, "jsonVisualizations", fileName + ".json");
        print("looking for: " + path);
        return File.Exists(path);
    }
}
