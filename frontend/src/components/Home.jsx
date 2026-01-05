import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Camera, Upload, ChevronRight, Star, CheckCircle } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext'; // Adjust the import path as needed

export const Home = () => {
    const { isAuthenticated } = useAuth();
    const navigate = useNavigate();

    const handleProtectedNavigation = (path) => {
        if (isAuthenticated()) {
            navigate(path);
        } else {
            navigate('/'); // Redirect to login page
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-b from-indigo-50 to-white">
            {/* Hero Section */}
            <div className="container mx-auto px-4 pt-16 pb-20">
                <div className="max-w-4xl mx-auto text-center">
                    <div className="inline-block px-3 py-1 bg-indigo-100 rounded-full text-indigo-800 text-sm font-medium mb-6">
                        AI-Powered Yoga Assistant
                    </div>
                    <h1 className="text-4xl md:text-6xl font-bold mb-6 text-indigo-900 leading-tight">
                        Perfect Your <span className="text-indigo-600">Yoga Practice</span> With AI
                    </h1>
                    <p className="text-xl text-gray-600 mb-10 max-w-2xl mx-auto">
                        Get real-time pose detection and personalized corrections to improve your form and deepen your practice
                    </p>

                    <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
                        <button
                            onClick={() => handleProtectedNavigation('/live')}
                            className="px-8 py-3 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 transition-colors flex items-center justify-center group"
                        >
                            Try Live Detection
                            <ChevronRight size={18} className="ml-1 transform group-hover:translate-x-1 transition-transform" />
                        </button>
                        <button
                            onClick={() => handleProtectedNavigation('/upload')}
                            className="px-8 py-3 bg-white text-indigo-600 border border-indigo-200 rounded-lg font-medium hover:bg-indigo-50 transition-colors flex items-center justify-center"
                        >
                            Upload Practice
                        </button>
                    </div>
                </div>

                {/* Feature Cards */}
                <div className="grid md:grid-cols-2 gap-6 lg:gap-8 max-w-5xl mx-auto mb-24">
                    <div
                        onClick={() => handleProtectedNavigation('/live')}
                        className="group bg-white rounded-2xl shadow-md hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 overflow-hidden cursor-pointer"
                    >
                        <div className="p-8">
                            <div className="bg-indigo-100 p-4 rounded-full mb-6 w-16 h-16 flex items-center justify-center group-hover:bg-indigo-600 transition-colors">
                                <Camera size={32} className="text-indigo-600 group-hover:text-white transition-colors" />
                            </div>
                            <h2 className="text-2xl font-semibold text-indigo-900 mb-3">Live Detection</h2>
                            <p className="text-gray-600 mb-4">
                                Get instant feedback on your poses using your webcam with real-time AI analysis
                                {!isAuthenticated() && (
                                    <span className="block text-sm text-amber-600 mt-2 font-medium">
                                        🔒 Login required to access this feature
                                    </span>
                                )}
                            </p>
                            <div className="flex flex-wrap gap-2 mb-4">
                                <span className="px-3 py-1 bg-indigo-50 text-indigo-700 rounded-full text-sm">Real-time</span>
                                <span className="px-3 py-1 bg-indigo-50 text-indigo-700 rounded-full text-sm">Instant feedback</span>
                                <span className="px-3 py-1 bg-indigo-50 text-indigo-700 rounded-full text-sm">Pose tracking</span>
                            </div>
                            <div className="flex items-center text-indigo-600 font-medium group-hover:text-indigo-700">
                                {isAuthenticated() ? 'Start now' : 'Login to start'} <ChevronRight size={16} className="ml-1" />
                            </div>
                        </div>
                    </div>

                    <div
                        onClick={() => handleProtectedNavigation('/upload')}
                        className="group bg-white rounded-2xl shadow-md hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 overflow-hidden cursor-pointer"
                    >
                        <div className="p-8">
                            <div className="bg-indigo-100 p-4 rounded-full mb-6 w-16 h-16 flex items-center justify-center group-hover:bg-indigo-600 transition-colors">
                                <Upload size={32} className="text-indigo-600 group-hover:text-white transition-colors" />
                            </div>
                            <h2 className="text-2xl font-semibold text-indigo-900 mb-3">Upload Practice</h2>
                            <p className="text-gray-600 mb-4">
                                Upload videos or images of your practice for detailed analysis and personalized recommendations
                                {!isAuthenticated() && (
                                    <span className="block text-sm text-amber-600 mt-2 font-medium">
                                        🔒 Login required to access this feature
                                    </span>
                                )}
                            </p>
                            <div className="flex flex-wrap gap-2 mb-4">
                                <span className="px-3 py-1 bg-indigo-50 text-indigo-700 rounded-full text-sm">Detailed analysis</span>
                                <span className="px-3 py-1 bg-indigo-50 text-indigo-700 rounded-full text-sm">Progress tracking</span>
                                <span className="px-3 py-1 bg-indigo-50 text-indigo-700 rounded-full text-sm">Form correction</span>
                            </div>
                            <div className="flex items-center text-indigo-600 font-medium group-hover:text-indigo-700">
                                {isAuthenticated() ? 'Upload practice' : 'Login to upload'} <ChevronRight size={16} className="ml-1" />
                            </div>
                        </div>
                    </div>
                </div>

                {/* How It Works */}
                <div className="bg-white p-10 rounded-2xl shadow-md max-w-5xl mx-auto mb-24">
                    <h3 className="text-2xl md:text-3xl font-semibold text-indigo-900 mb-8 text-center">How PROFit Works</h3>
                    <div className="grid md:grid-cols-3 gap-8">
                        <div className="flex flex-col items-center relative">
                            <div className="bg-indigo-600 text-white p-4 rounded-full mb-6 w-14 h-14 flex items-center justify-center font-bold z-10">
                                1
                            </div>
                            {/* Line connecting steps (hidden on mobile) */}
                            <div className="hidden md:block absolute top-7 left-1/2 h-0.5 w-full bg-indigo-100"></div>
                            <h4 className="font-semibold text-lg mb-3 text-indigo-900">Select Mode</h4>
                            <p className="text-gray-600 text-center">Choose between live detection or upload your yoga practice</p>
                        </div>
                        <div className="flex flex-col items-center relative">
                            <div className="bg-indigo-600 text-white p-4 rounded-full mb-6 w-14 h-14 flex items-center justify-center font-bold z-10">
                                2
                            </div>
                            {/* Line connecting steps (hidden on mobile) */}
                            <div className="hidden md:block absolute top-7 left-1/2 h-0.5 w-full bg-indigo-100"></div>
                            <h4 className="font-semibold text-lg mb-3 text-indigo-900">Perform Your Poses</h4>
                            <p className="text-gray-600 text-center">Our advanced AI analyzes your form and alignment in real-time</p>
                        </div>
                        <div className="flex flex-col items-center">
                            <div className="bg-indigo-600 text-white p-4 rounded-full mb-6 w-14 h-14 flex items-center justify-center font-bold">
                                3
                            </div>
                            <h4 className="font-semibold text-lg mb-3 text-indigo-900">Get Feedback</h4>
                            <p className="text-gray-600 text-center">Receive personalized corrections to improve your practice safely</p>
                        </div>
                    </div>
                </div>

                {/* Benefits */}
                <div className="max-w-5xl mx-auto bg-indigo-600 rounded-2xl overflow-hidden">
                    <div className="grid md:grid-cols-2">
                        <div className="p-10 flex flex-col justify-center">
                            <h3 className="text-2xl md:text-3xl font-semibold text-white mb-6">Benefits of YogaAI</h3>
                            <ul className="space-y-4">
                                <li className="flex items-start">
                                    <CheckCircle size={22} className="text-indigo-200 mr-3 mt-1 flex-shrink-0" />
                                    <span className="text-white">Prevent injuries with proper form guidance</span>
                                </li>
                                <li className="flex items-start">
                                    <CheckCircle size={22} className="text-indigo-200 mr-3 mt-1 flex-shrink-0" />
                                    <span className="text-white">Track your progress over time</span>
                                </li>
                                <li className="flex items-start">
                                    <CheckCircle size={22} className="text-indigo-200 mr-3 mt-1 flex-shrink-0" />
                                    <span className="text-white">Practice with confidence at your own pace</span>
                                </li>
                                <li className="flex items-start">
                                    <CheckCircle size={22} className="text-indigo-200 mr-3 mt-1 flex-shrink-0" />
                                    <span className="text-white">Personalized recommendations for improvement</span>
                                </li>
                            </ul>
                            <div className="mt-8">
                                <button
                                    onClick={() => handleProtectedNavigation('/live')}
                                    className="px-6 py-3 bg-white text-indigo-600 rounded-lg font-medium hover:bg-indigo-50 transition-colors inline-flex items-center"
                                >
                                    {isAuthenticated() ? 'Get Started Free' : 'Login to Get Started'}
                                    <ChevronRight size={18} className="ml-1" />
                                </button>
                            </div>
                        </div>
                        <div className="bg-indigo-700 p-10 hidden md:flex items-center justify-center">
                            {/* This is where you could add an illustration or image */}
                            <div className="text-center">
                                <div className="text-5xl font-bold text-white mb-3">20+</div>
                                <div className="text-indigo-200 text-lg">Yoga poses detected</div>
                                <div className="h-px w-20 bg-indigo-400 my-6 mx-auto"></div>
                                <div className="text-5xl font-bold text-white mb-3">98%</div>
                                <div className="text-indigo-200 text-lg">Detection accuracy</div>
                                <div className="h-px w-20 bg-indigo-400 my-6 mx-auto"></div>
                                <div className="text-5xl font-bold text-white mb-3">5000+</div>
                                <div className="text-indigo-200 text-lg">Active users</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};