import React from 'react';

export const Footer = () => {
    return (
        <footer className="bg-white py-6 border-t">
            <div className="container mx-auto px-6">
                <div className="flex flex-col md:flex-row justify-between items-center">
                    <div className="flex items-center space-x-2">
                        
                        <span className="text-lg font-medium text-indigo-800">PROFit</span>
                    </div>
                    <div className="mt-4 md:mt-0 text-sm text-gray-500">
                        &copy; {new Date().getFullYear()} PROFit. All rights reserved.
                    </div>
                </div>
            </div>
        </footer>
    );
};