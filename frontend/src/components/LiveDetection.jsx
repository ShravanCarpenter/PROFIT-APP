import React, { useState, useRef, useEffect } from 'react';
import { Camera, Play, Square, Clock, Award, Info, AlertTriangle } from 'lucide-react';
import axios from 'axios';

const API_URL = 'http://localhost:5000';

export const LiveDetection = () => {
    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const [isStreaming, setIsStreaming] = useState(false);
    const [sessionTime, setSessionTime] = useState(0);
    const [detectedPose, setDetectedPose] = useState(null);
    const [feedback, setFeedback] = useState([]);
    const [accuracy, setAccuracy] = useState(0);
    const [showInfo, setShowInfo] = useState(false);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [error, setError] = useState(null);
    const [detectionHistory, setDetectionHistory] = useState([]);

    const timerRef = useRef(null);
    const detectionIntervalRef = useRef(null);

    const yogaApiService = {
        analyzeImage: (file) => {
            const formData = new FormData();
            formData.append('image', file);

            return axios.post(`${API_URL}/predict`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
                timeout: 10000
            }).then(res => res.data);
        }
    };

    const captureFrame = () => {
        if (!videoRef.current || !canvasRef.current) return null;
        const video = videoRef.current;
        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');
        canvas.width = video.videoWidth || 640;
        canvas.height = video.videoHeight || 480;
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        return canvas.toDataURL('image/jpeg', 0.8);
    };

    const startStream = async () => {
        try {
            setError(null);
            const stream = await navigator.mediaDevices.getUserMedia({
                video: { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: 'user' },
                audio: false,
            });

            if (videoRef.current) {
                videoRef.current.srcObject = stream;
                setIsStreaming(true);
                timerRef.current = setInterval(() => setSessionTime(t => t + 1), 1000);
                videoRef.current.onloadedmetadata = () => startLivePoseDetection();
            }
        } catch (err) {
            setError("Could not access webcam. Please ensure you have given permission and try again.");
        }
    };

    const stopStream = () => {
        if (videoRef.current?.srcObject) {
            videoRef.current.srcObject.getTracks().forEach(track => track.stop());
            videoRef.current.srcObject = null;
        }
        clearInterval(timerRef.current);
        clearInterval(detectionIntervalRef.current);
        setIsStreaming(false);
        setDetectedPose(null);
        setFeedback([]);
        setAccuracy(0);
        setSessionTime(0);
        setIsAnalyzing(false);
        setError(null);
    };

    const startLivePoseDetection = () => {
        detectionIntervalRef.current = setInterval(async () => {
            if (!isStreaming || isAnalyzing) return;
            try {
                setIsAnalyzing(true);
                const frameData = captureFrame();
                if (frameData) {
                    const blob = await fetch(frameData).then(res => res.blob());
                    const result = await yogaApiService.analyzeImage(blob);
                    processDetectionResult(result);
                }
            } catch (err) {
                setError("Error analyzing pose. Please check your backend connection.");
            } finally {
                setIsAnalyzing(false);
            }
        }, 2000);
    };

    const processDetectionResult = (result) => {
        if (!result?.predicted_pose) return;
        const pose = result.predicted_pose;
        const confidence = Math.round(result.confidence || 75);
        setDetectedPose(pose);
        setAccuracy(confidence);
        setDetectionHistory(prev => [...prev.slice(-4), { pose, confidence, timestamp: Date.now() }]);

        if (typeof result.feedback === 'object') {
            const feedbackList = [];
            if (Array.isArray(result.feedback.suggestions)) feedbackList.push(...result.feedback.suggestions);
            else if (Array.isArray(result.feedback.tips)) feedbackList.push(...result.feedback.tips);
            else if (Array.isArray(result.feedback.corrections)) feedbackList.push(...result.feedback.corrections);
            else Object.values(result.feedback).forEach(v => Array.isArray(v) ? feedbackList.push(...v) : feedbackList.push(v));
            setFeedback(feedbackList.slice(0, 3));
        } else if (Array.isArray(result.feedback)) {
            setFeedback(result.feedback.slice(0, 3));
        } else {
            generateFallbackFeedback(pose, confidence);
        }

        if (canvasRef.current && videoRef.current) {
            const canvas = canvasRef.current;
            const ctx = canvas.getContext('2d');
            const video = videoRef.current;
            canvas.width = video.videoWidth || 640;
            canvas.height = video.videoHeight || 480;
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        }

        if (Array.isArray(result.keypoints)) drawPoseKeypoints(result.keypoints);
        else drawPoseOverlay(pose, confidence);
    };

    const drawPoseKeypoints = (keypoints) => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.strokeStyle = '#4f46e5';
        ctx.lineWidth = 3;
        ctx.fillStyle = '#c7d2fe';

        const connections = [[0, 1], [1, 2], [2, 3], [3, 4], [1, 5], [5, 6], [6, 7], [1, 8], [8, 9], [9, 10], [1, 11], [11, 12], [11, 13], [13, 14], [14, 15], [12, 16], [16, 17], [17, 18]];
        connections.forEach(([i, j]) => {
            if (keypoints[i] && keypoints[j]) {
                ctx.beginPath();
                ctx.moveTo(keypoints[i].x, keypoints[i].y);
                ctx.lineTo(keypoints[j].x, keypoints[j].y);
                ctx.stroke();
            }
        });

        keypoints.forEach(point => {
            if (point?.x && point?.y) {
                ctx.beginPath();
                ctx.arc(point.x, point.y, 6, 0, Math.PI * 2);
                ctx.fill();
                ctx.stroke();
            }
        });
    };

    const drawPoseOverlay = (pose, confidence) => {
        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = 'rgba(79, 70, 229, 0.9)';
        ctx.fillRect(10, 10, 200, 60);
        ctx.fillStyle = 'white';
        ctx.font = 'bold 16px Arial';
        ctx.fillText(pose, 20, 35);
        ctx.font = '14px Arial';
        ctx.fillText(`${confidence}% accuracy`, 20, 55);
    };

    const formatTime = (seconds) => {
        const mins = Math.floor(seconds / 60).toString().padStart(2, '0');
        const secs = (seconds % 60).toString().padStart(2, '0');
        return `${mins}:${secs}`;
    };

    useEffect(() => {
        return () => stopStream();
    }, []);

    return (
        <div className="container mx-auto px-4 py-8">
            <h1 className="text-3xl font-bold text-center mb-8 text-indigo-800">Live Yoga Pose Detection</h1>

            {error && (
                <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4 flex items-center">
                    <AlertTriangle className="text-red-500 mr-3" size={20} />
                    <span className="text-red-700">{error}</span>
                </div>
            )}

            <div className="grid md:grid-cols-3 gap-6">
                {/* Video feed and controls */}
                <div className="md:col-span-2 bg-white rounded-xl shadow-lg p-6">
                    <div className="relative">
                        <video
                            ref={videoRef}
                            className="w-full h-auto rounded-lg bg-gray-100"
                            autoPlay
                            playsInline
                            muted
                            style={{ display: isStreaming ? 'block' : 'none' }}
                        />
                        <canvas
                            ref={canvasRef}
                            className="absolute top-0 left-0 w-full h-full pointer-events-none"
                            width="640"
                            height="480"
                            style={{ display: isStreaming ? 'block' : 'none' }}
                        />

                        {!isStreaming && (
                            <div className="bg-gray-100 rounded-lg flex flex-col items-center justify-center p-12 min-h-96">
                                <Camera size={64} className="text-gray-400 mb-4" />
                                <p className="text-gray-500 text-center mb-6">
                                    Click start to begin your yoga session with live pose detection
                                </p>
                                <button
                                    onClick={startStream}
                                    className="bg-indigo-600 text-white px-6 py-3 rounded-lg flex items-center space-x-2 hover:bg-indigo-700 transition-colors"
                                >
                                    <Play size={20} />
                                    <span>Start Session</span>
                                </button>
                            </div>
                        )}

                        {/* Analysis indicator */}
                        {isAnalyzing && (
                            <div className="absolute top-4 right-4 bg-blue-500 text-white px-3 py-1 rounded-full text-sm flex items-center">
                                <div className="w-2 h-2 bg-white rounded-full mr-2 animate-pulse"></div>
                                Analyzing...
                            </div>
                        )}
                    </div>

                    {/* Controls */}
                    <div className="mt-4 flex justify-between items-center">
                        <div className="flex items-center space-x-4">
                            <div className="flex items-center space-x-2">
                                <Clock size={20} className="text-indigo-600" />
                                <span className="font-mono text-lg">{formatTime(sessionTime)}</span>
                            </div>

                            {detectionHistory.length > 0 && (
                                <div className="text-sm text-gray-600">
                                    Poses detected: {detectionHistory.length}
                                </div>
                            )}
                        </div>

                        {isStreaming && (
                            <button
                                onClick={stopStream}
                                className="bg-red-500 text-white px-4 py-2 rounded-lg flex items-center space-x-2 hover:bg-red-600 transition-colors"
                            >
                                <Square size={18} />
                                <span>End Session</span>
                            </button>
                        )}
                    </div>
                </div>

                {/* Feedback panel */}
                <div className="bg-white rounded-xl shadow-lg p-6">
                    <div className="flex justify-between items-center mb-6">
                        <h2 className="text-xl font-semibold text-indigo-800">Pose Analysis</h2>
                        <button
                            onClick={() => setShowInfo(!showInfo)}
                            className="text-indigo-600 hover:text-indigo-800"
                        >
                            <Info size={20} />
                        </button>
                    </div>

                    {showInfo && (
                        <div className="bg-indigo-50 p-4 rounded-lg mb-6">
                            <p className="text-sm text-indigo-700">
                                Our AI analyzes your pose in real-time using your trained model and provides
                                personalized feedback to help you improve. The accuracy score shows how well
                                your pose matches the ideal form.
                            </p>
                        </div>
                    )}

                    {isStreaming ? (
                        <>
                            {detectedPose ? (
                                <>
                                    <div className="mb-6">
                                        <h3 className="text-lg font-medium mb-2">Detected Pose</h3>
                                        <div className="bg-indigo-100 p-4 rounded-lg">
                                            <p className="text-xl font-semibold text-indigo-700">{detectedPose}</p>
                                        </div>
                                    </div>

                                    <div className="mb-6">
                                        <div className="flex justify-between mb-2">
                                            <h3 className="text-lg font-medium">Accuracy</h3>
                                            <div className="flex items-center">
                                                <Award size={18} className="text-yellow-500 mr-1" />
                                                <span className={`font-semibold ${accuracy >= 80 ? 'text-green-600' :
                                                    accuracy >= 60 ? 'text-yellow-600' : 'text-red-600'
                                                    }`}>
                                                    {accuracy}%
                                                </span>
                                            </div>
                                        </div>
                                        <div className="w-full bg-gray-200 rounded-full h-2.5">
                                            <div
                                                className={`h-2.5 rounded-full transition-all duration-300 ${accuracy >= 80 ? 'bg-green-500' :
                                                    accuracy >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                                                    }`}
                                                style={{ width: `${accuracy}%` }}
                                            ></div>
                                        </div>
                                    </div>

                                    <div>
                                        <h3 className="text-lg font-medium mb-3">Feedback</h3>
                                        {feedback.length > 0 ? (
                                            <ul className="space-y-2">
                                                {feedback.map((item, index) => (
                                                    <li key={index} className="flex items-start">
                                                        <span className="inline-flex items-center justify-center bg-indigo-100 text-indigo-800 w-6 h-6 rounded-full text-sm mr-2 mt-0.5">
                                                            {index + 1}
                                                        </span>
                                                        <span className="text-sm">{item}</span>
                                                    </li>
                                                ))}
                                            </ul>
                                        ) : (
                                            <p className="text-gray-500 italic">Great form! Keep it up.</p>
                                        )}
                                    </div>

                                    {/* Detection History */}
                                    {detectionHistory.length > 1 && (
                                        <div className="mt-6 pt-4 border-t">
                                            <h3 className="text-sm font-medium mb-2 text-gray-600">Recent Poses</h3>
                                            <div className="flex flex-wrap gap-2">
                                                {detectionHistory.slice(-3).map((detection, index) => (
                                                    <span key={index} className="text-xs bg-gray-100 px-2 py-1 rounded">
                                                        {detection.pose} ({detection.confidence}%)
                                                    </span>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </>
                            ) : (
                                <div className="flex flex-col items-center justify-center h-64">
                                    <div className="w-12 h-12 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mb-4"></div>
                                    <p className="text-gray-600">Detecting your pose...</p>
                                    <p className="text-sm text-gray-500 mt-2">Make sure you're visible in the camera</p>
                                </div>
                            )}
                        </>
                    ) : (
                        <div className="flex flex-col items-center justify-center h-64 text-center">
                            <p className="text-gray-500 mb-2">
                                Start a session to receive real-time feedback on your yoga poses using your trained AI model
                            </p>
                            <p className="text-sm text-gray-400">
                                Make sure your Flask backend is running on localhost:5000
                            </p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );

};