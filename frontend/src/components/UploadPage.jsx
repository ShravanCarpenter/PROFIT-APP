import React, { useState, useRef, useEffect } from 'react';
import {
    Upload, Image, Video, X, Check, Clock, Award, Play, Pause, AlertCircle,
    Target, Heart, AlertTriangle, Settings, Star
} from 'lucide-react';
import yogaApiService from '../services/yogaApiService'; 

export const UploadPage = () => {
    const [file, setFile] = useState(null);
    const [fileType, setFileType] = useState(null);
    const [isProcessing, setIsProcessing] = useState(false);
    const [isAnalyzed, setIsAnalyzed] = useState(false);
    const [isPlaying, setIsPlaying] = useState(false);
    const [currentTime, setCurrentTime] = useState(0);
    const [duration, setDuration] = useState(0);
    const [error, setError] = useState(null);

    const [poseResults, setPoseResults] = useState({
        poseName: '',
        accuracy: 0,
        confidence: 0,
        feedback: {
            description: '',
            alignment_cues: [],
            benefits: [],
            common_mistakes: [],
            modifications: '',
            difficulty: ''
        }
    });

    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const fileInputRef = useRef(null);

    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        if (!selectedFile) return;

        if (selectedFile.size > 100 * 1024 * 1024) {
            setError('File size must be less than 100MB');
            e.target.value = null;
            return;
        }

        resetAnalysisState();

        if (selectedFile.type.startsWith('image/')) {
            setFileType('image');
            setFile(selectedFile);
        } else if (selectedFile.type.startsWith('video/')) {
            setFileType('video');
            setFile(selectedFile);
        } else {
            setError('Please upload an image or video file');
            e.target.value = null;
        }
    };

    const resetAnalysisState = () => {
        setIsAnalyzed(false);
        setError(null);
        setPoseResults({
            poseName: '',
            accuracy: 0,
            feedback: {},
            keypoints: [],
            confidence: 0
        });
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        const droppedFile = e.dataTransfer.files[0];
        if (!droppedFile) return;

        if (droppedFile.size > 100 * 1024 * 1024) {
            setError('File size must be less than 100MB');
            return;
        }

        resetAnalysisState();

        if (droppedFile.type.startsWith('image/')) {
            setFileType('image');
            setFile(droppedFile);
        } else if (droppedFile.type.startsWith('video/')) {
            setFileType('video');
            setFile(droppedFile);
        } else {
            setError('Please upload an image or video file');
        }
    };

    const handleDragOver = (e) => {
        e.preventDefault();
        e.stopPropagation();
    };

    const processFile = async () => {
        if (!file) return;

        setIsProcessing(true);
        setError(null);

        try {
            const response = await yogaApiService.analyzeImage(file); // Correct usage

            const formattedResults = {
                poseName: response.pose_name || response.predicted_pose || response.predicted_class || 'Unknown Pose',
                accuracy: Math.round(response.accuracy || response.confidence || response.score * 100 || 0),
                confidence: response.confidence || response.score || 0,
                feedback: response.feedback || response.suggestions || {},
                keypoints: response.landmarks || []
            };

            setPoseResults(formattedResults);
            setIsAnalyzed(true);

            if (fileType === 'image' && formattedResults.keypoints?.length > 0) {
                drawKeypointsOnImage(formattedResults.keypoints);
            }

        } catch (error) {
            console.error('Analysis failed:', error);

            let errorMessage = 'Analysis failed. Please try again.';
            if (error.response) {
                errorMessage = `Server error: ${error.response.data?.message || error.response.statusText}`;
            } else if (error.request) {
                errorMessage = 'No response from server. Check your backend or CORS.';
            } else {
                errorMessage = `Error: ${error.message}`;
            }

            setError(errorMessage);
        } finally {
            setIsProcessing(false);
        }
    };

    const toBase64 = (file) => {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.readAsDataURL(file);
            reader.onload = () => resolve(reader.result);
            reader.onerror = (error) => reject(error);
        });
    };

    const drawKeypointsOnImage = (keypoints) => {
        if (!canvasRef.current || !keypoints || keypoints.length === 0) return;

        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');
        const img = canvas.previousElementSibling;

        canvas.width = img.naturalWidth;
        canvas.height = img.naturalHeight;
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        ctx.strokeStyle = '#4f46e5';
        ctx.lineWidth = 3;
        ctx.fillStyle = '#c7d2fe';

        keypoints.forEach((point) => {
            const x = point.x || point[0];
            const y = point.y || point[1];
            const visibility = point.visibility || point[2] || 1;
            if (visibility > 0.5) {
                ctx.beginPath();
                ctx.arc(x, y, 5, 0, Math.PI * 2);
                ctx.fill();
                ctx.stroke();
            }
        });
    };

    const togglePlayPause = () => {
        if (videoRef.current) {
            if (isPlaying) {
                videoRef.current.pause();
            } else {
                videoRef.current.play();
            }
            setIsPlaying(!isPlaying);
        }
    };

    const updateTime = () => {
        if (videoRef.current) {
            setCurrentTime(videoRef.current.currentTime);
        }
    };

    const formatTime = (time) => {
        const minutes = Math.floor(time / 60);
        const seconds = Math.floor(time % 60);
        return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    };

    const getDifficultyColor = (difficulty) => {
        const lower = difficulty?.toLowerCase() || '';
        if (lower.includes('beginner') || lower.includes('easy')) return 'text-green-600 bg-green-50 border-green-200';
        if (lower.includes('intermediate') || lower.includes('medium')) return 'text-yellow-600 bg-yellow-50 border-yellow-200';
        if (lower.includes('advanced') || lower.includes('hard')) return 'text-red-600 bg-red-50 border-red-200';
        return 'text-gray-600 bg-gray-50 border-gray-200';
    };

    useEffect(() => {
        if (videoRef.current && fileType === 'video' && file) {
            videoRef.current.onloadedmetadata = () => {
                setDuration(videoRef.current.duration);
            };
        }
    }, [file, fileType]);

    return (
        <div className="container mx-auto px-4 py-8">
            <h1 className="text-3xl font-bold text-center mb-8 text-indigo-800">Upload & Analyze Yoga Poses</h1>

            {/* Error message */}
            {error && (
                <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center">
                    <AlertCircle size={20} className="mr-2" />
                    <span>{error}</span>
                    <button
                        onClick={() => setError(null)}
                        className="ml-auto text-red-500 hover:text-red-700"
                    >
                        <X size={16} />
                    </button>
                </div>
            )}

            <div className="grid lg:grid-cols-2 gap-6">
                {/* Upload section */}
                <div className="bg-white rounded-xl shadow-lg p-6">
                    {!file ? (
                        <div
                            className="border-2 border-dashed border-gray-300 rounded-lg p-8 flex flex-col items-center justify-center text-center min-h-80 hover:border-indigo-300 transition-colors"
                            onDrop={handleDrop}
                            onDragOver={handleDragOver}
                        >
                            <Upload size={48} className="text-gray-400 mb-4" />
                            <h3 className="text-xl font-medium text-gray-700 mb-2">Upload your yoga practice</h3>
                            <p className="text-gray-500 mb-6">Drag and drop an image or video file here, or click to browse</p>
                            <button
                                onClick={() => fileInputRef.current.click()}
                                className="bg-indigo-600 text-white px-6 py-3 rounded-lg flex items-center space-x-2 hover:bg-indigo-700 transition-colors"
                            >
                                <span>Select File</span>
                            </button>
                            <input
                                type="file"
                                ref={fileInputRef}
                                onChange={handleFileChange}
                                accept="image/*,video/*"
                                className="hidden"
                            />
                            <p className="text-gray-400 text-sm mt-4">
                                Supported formats: JPG, PNG, MP4, MOV (max. 100MB)
                            </p>
                        </div>
                    ) : (
                        <div className="relative">
                            {/* Media preview */}
                            {fileType === 'image' ? (
                                <div className="relative">
                                    <img
                                        src={URL.createObjectURL(file)}
                                        alt="Uploaded yoga pose"
                                        className="w-full max-w-md mx-auto h-auto rounded-lg shadow-md"
                                        onLoad={() => {
                                            // Resize canvas to match image after it loads
                                            if (canvasRef.current) {
                                                const img = canvasRef.current.previousElementSibling;
                                                canvasRef.current.width = img.naturalWidth;
                                                canvasRef.current.height = img.naturalHeight;
                                            }
                                        }}
                                    />
                                    <canvas
                                        ref={canvasRef}
                                        className="absolute top-0 left-0 w-full h-full pointer-events-none max-w-md mx-auto"
                                        style={{ maxWidth: '100%', height: 'auto' }}
                                    />
                                </div>
                            ) : (
                                <div className="relative">
                                    <video
                                        ref={videoRef}
                                        src={URL.createObjectURL(file)}
                                        className="w-full max-w-md mx-auto h-auto rounded-lg shadow-md"
                                        onTimeUpdate={updateTime}
                                        onEnded={() => setIsPlaying(false)}
                                    />

                                    {/* Video controls */}
                                    {fileType === 'video' && (
                                        <div className="mt-4">
                                            <div className="flex items-center justify-between mb-2">
                                                <button
                                                    onClick={togglePlayPause}
                                                    className="bg-indigo-600 text-white p-2 rounded-full hover:bg-indigo-700 transition-colors"
                                                >
                                                    {isPlaying ? <Pause size={20} /> : <Play size={20} />}
                                                </button>
                                                <div className="flex items-center space-x-2 text-sm">
                                                    <span>{formatTime(currentTime)}</span>
                                                    <span>/</span>
                                                    <span>{formatTime(duration)}</span>
                                                </div>
                                            </div>
                                            <div className="w-full bg-gray-200 rounded-full h-1.5">
                                                <div
                                                    className="bg-indigo-600 h-1.5 rounded-full transition-all"
                                                    style={{ width: `${duration > 0 ? (currentTime / duration) * 100 : 0}%` }}
                                                ></div>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            )}

                            {/* File info and actions */}
                            <div className="mt-4 flex justify-between items-center">
                                <div className="flex items-center">
                                    {fileType === 'image' ?
                                        <Image size={20} className="text-indigo-600 mr-2" /> :
                                        <Video size={20} className="text-indigo-600 mr-2" />
                                    }
                                    <span className="text-gray-700 truncate">{file.name}</span>
                                </div>

                                <button
                                    onClick={() => {
                                        setFile(null);
                                        setFileType(null);
                                        resetAnalysisState();
                                        if (fileInputRef.current) {
                                            fileInputRef.current.value = '';
                                        }
                                    }}
                                    className="p-2 text-red-500 hover:text-red-700 transition-colors"
                                >
                                    <X size={20} />
                                </button>
                            </div>

                            {/* Analysis button */}
                            {!isAnalyzed && !isProcessing && (
                                <button
                                    onClick={processFile}
                                    className="mt-4 w-full bg-indigo-600 text-white py-3 rounded-lg flex items-center justify-center space-x-2 hover:bg-indigo-700 transition-colors"
                                >
                                    <span>Analyze Pose</span>
                                </button>
                            )}

                            {/* Processing indicator */}
                            {isProcessing && (
                                <div className="mt-4 w-full bg-indigo-100 text-indigo-700 py-3 rounded-lg flex items-center justify-center">
                                    <div className="w-5 h-5 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin mr-2"></div>
                                    <span>Analyzing with AI model...</span>
                                </div>
                            )}

                            {/* Re-analyze button */}
                            {isAnalyzed && (
                                <button
                                    onClick={processFile}
                                    disabled={isProcessing}
                                    className="mt-4 w-full bg-gray-600 text-white py-3 rounded-lg flex items-center justify-center space-x-2 hover:bg-gray-700 transition-colors disabled:opacity-50"
                                >
                                    <span>Re-analyze</span>
                                </button>
                            )}
                        </div>
                    )}
                </div>

                {/* Results panel */}
                <div className="bg-white rounded-xl shadow-lg p-6 max-h-screen overflow-y-auto">
                    <h2 className="text-xl font-semibold text-indigo-800 mb-6 flex items-center sticky top-0 bg-white pb-2 border-b border-gray-100">
                        <Star className="mr-2" size={20} />
                        Analysis Results
                    </h2>

                    {isAnalyzed ? (
                        <div className="space-y-4">
                            {/* Detected Pose */}
                            <div className="bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-100 rounded-xl p-4">
                                <h3 className="text-base font-semibold text-indigo-800 mb-2 flex items-center">
                                    <Target className="mr-2" size={16} />
                                    Detected Pose
                                </h3>
                                <p className="text-lg font-bold text-indigo-700 mb-2">{poseResults.poseName}</p>
                                {poseResults.confidence > 0 && (
                                    <div className="flex items-center">
                                        <div className="bg-white rounded-full px-2 py-1 text-xs font-medium text-indigo-600 border border-indigo-200">
                                            Confidence: {Math.round(poseResults.confidence * 100)}%
                                        </div>
                                    </div>
                                )}
                            </div>

                            {/* Accuracy Score */}
                            <div className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm">
                                <div className="flex justify-between items-center mb-3">
                                    <h3 className="text-base font-semibold text-gray-800 flex items-center">
                                        <Award className="mr-2 text-yellow-500" size={16} />
                                        Accuracy Score
                                    </h3>
                                    <span className={`text-xl font-bold ${poseResults.accuracy >= 80 ? 'text-green-600' :
                                            poseResults.accuracy >= 60 ? 'text-yellow-600' : 'text-red-600'
                                        }`}>
                                        {poseResults.accuracy}%
                                    </span>
                                </div>
                                <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                                    <div
                                        className={`h-full rounded-full transition-all duration-500 ${poseResults.accuracy >= 80 ? 'bg-gradient-to-r from-green-400 to-green-600' :
                                                poseResults.accuracy >= 60 ? 'bg-gradient-to-r from-yellow-400 to-yellow-600' :
                                                    'bg-gradient-to-r from-red-400 to-red-600'
                                            }`}
                                        style={{ width: `${poseResults.accuracy}%` }}
                                    ></div>
                                </div>
                                <p className="text-xs text-gray-600 mt-2">
                                    {poseResults.accuracy >= 80 ? 'Excellent form!' :
                                        poseResults.accuracy >= 60 ? 'Good, with room for improvement' :
                                            'Needs improvement'}
                                </p>
                            </div>

                            {/* Pose Feedback */}
                            <div className="bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden">
                                <div className="bg-gradient-to-r from-indigo-500 to-purple-600 px-4 py-2">
                                    <h3 className="text-base font-semibold text-white flex items-center">
                                        <Heart className="mr-2" size={16} />
                                        Detailed Feedback
                                    </h3>
                                </div>

                                {poseResults.feedback && poseResults.feedback.description ? (
                                    <div className="p-3 space-y-3">
                                        {/* Description */}
                                        <div className="bg-blue-50 border-l-4 border-blue-400 p-3 rounded-r-lg">
                                            <h4 className="font-semibold text-blue-800 mb-1 flex items-center text-sm">
                                                <div className="w-1.5 h-1.5 bg-blue-400 rounded-full mr-2"></div>
                                                Description
                                            </h4>
                                            <p className="text-blue-700 leading-relaxed text-sm">{poseResults.feedback.description}</p>
                                        </div>

                                        {/* Alignment Cues */}
                                        {poseResults.feedback.alignment_cues?.length > 0 && (
                                            <div className="bg-indigo-50 border-l-4 border-indigo-400 p-3 rounded-r-lg">
                                                <h4 className="font-semibold text-indigo-800 mb-2 flex items-center text-sm">
                                                    <Target className="mr-2" size={14} />
                                                    Alignment Cues
                                                </h4>
                                                <ul className="space-y-1">
                                                    {poseResults.feedback.alignment_cues.map((cue, index) => (
                                                        <li key={index} className="flex items-start">
                                                            <div className="w-1 h-1 bg-indigo-400 rounded-full mt-1.5 mr-2 flex-shrink-0"></div>
                                                            <span className="text-indigo-700 text-xs leading-relaxed">{cue}</span>
                                                        </li>
                                                    ))}
                                                </ul>
                                            </div>
                                        )}

                                        {/* Benefits */}
                                        {poseResults.feedback.benefits?.length > 0 && (
                                            <div className="bg-green-50 border-l-4 border-green-400 p-3 rounded-r-lg">
                                                <h4 className="font-semibold text-green-800 mb-2 flex items-center text-sm">
                                                    <Heart className="mr-2" size={14} />
                                                    Benefits
                                                </h4>
                                                <ul className="space-y-1">
                                                    {poseResults.feedback.benefits.map((benefit, index) => (
                                                        <li key={index} className="flex items-start">
                                                            <div className="w-1 h-1 bg-green-400 rounded-full mt-1.5 mr-2 flex-shrink-0"></div>
                                                            <span className="text-green-700 text-xs leading-relaxed">{benefit}</span>
                                                        </li>
                                                    ))}
                                                </ul>
                                            </div>
                                        )}

                                        {/* Common Mistakes */}
                                        {poseResults.feedback.common_mistakes?.length > 0 && (
                                            <div className="bg-red-50 border-l-4 border-red-400 p-3 rounded-r-lg">
                                                <h4 className="font-semibold text-red-800 mb-2 flex items-center text-sm">
                                                    <AlertTriangle className="mr-2" size={14} />
                                                    Common Mistakes to Avoid
                                                </h4>
                                                <ul className="space-y-1">
                                                    {poseResults.feedback.common_mistakes.map((mistake, index) => (
                                                        <li key={index} className="flex items-start">
                                                            <div className="w-1 h-1 bg-red-400 rounded-full mt-1.5 mr-2 flex-shrink-0"></div>
                                                            <span className="text-red-700 text-xs leading-relaxed">{mistake}</span>
                                                        </li>
                                                    ))}
                                                </ul>
                                            </div>
                                        )}

                                        {/* Modifications & Difficulty */}
                                        <div className="grid gap-3">
                                            {poseResults.feedback.modifications && (
                                                <div className="bg-purple-50 border-l-4 border-purple-400 p-3 rounded-r-lg">
                                                    <h4 className="font-semibold text-purple-800 mb-1 flex items-center text-sm">
                                                        <Settings className="mr-2" size={14} />
                                                        Modifications
                                                    </h4>
                                                    <p className="text-purple-700 text-xs leading-relaxed">{poseResults.feedback.modifications}</p>
                                                </div>
                                            )}

                                            {poseResults.feedback.difficulty && (
                                                <div className="bg-orange-50 border-l-4 border-orange-400 p-3 rounded-r-lg">
                                                    <h4 className="font-semibold text-orange-800 mb-2 flex items-center text-sm">
                                                        <Star className="mr-2" size={14} />
                                                        Difficulty Level
                                                    </h4>
                                                    <div className={`inline-block px-2 py-1 rounded-full text-xs font-medium border ${getDifficultyColor(poseResults.feedback.difficulty)}`}>
                                                        {poseResults.feedback.difficulty}
                                                    </div>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                ) : (
                                    <div className="p-3 bg-green-50 border border-green-200 rounded-lg flex items-center">
                                        <Check size={16} className="text-green-600 mr-2 flex-shrink-0" />
                                        <div>
                                            <p className="text-green-800 font-medium text-sm">Excellent Form!</p>
                                            <p className="text-green-600 text-xs">Your pose alignment looks great. Keep up the excellent work!</p>
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>
                    ) : (
                        <div className="flex flex-col items-center justify-center h-48 text-center p-4">
                            {file ? (
                                isProcessing ? (
                                    <>
                                        <div className="w-12 h-12 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mb-4"></div>
                                        <p className="text-gray-600 font-medium">Analyzing your yoga pose...</p>
                                        <p className="text-gray-400 text-sm mt-2">Using trained AI model to detect pose and provide feedback</p>
                                    </>
                                ) : (
                                    <>
                                        <div className="bg-indigo-100 rounded-full p-4 mb-4">
                                            <Target className="w-8 h-8 text-indigo-600" />
                                        </div>
                                        <p className="text-gray-600 mb-4 font-medium">
                                            Ready to analyze your pose!
                                        </p>
                                        <p className="text-gray-400 text-sm">
                                            Click "Analyze Pose" to get AI-powered feedback on your yoga practice
                                        </p>
                                        <p className="text-gray-400 text-xs mt-2">
                                            Our model recognizes 84 different yoga poses
                                        </p>
                                    </>
                                )
                            ) : (
                                <>
                                    <div className="bg-gray-100 rounded-full p-4 mb-4">
                                        <Upload className="w-8 h-8 text-gray-400" />
                                    </div>
                                    <p className="text-gray-500">
                                        Upload an image or video to receive AI-powered feedback on your yoga practice
                                    </p>
                                </>
                            )}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};