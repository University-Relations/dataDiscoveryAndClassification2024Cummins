import React, { useState } from 'react';
import LocalScan from './pages/LocalScan';
import S3Scan from './pages/S3Scan';
import { Home, Scan, Cloud } from 'lucide-react';
import './App.css';

function App() {
  // Set up state for the current view
  const [currentView, setCurrentView] = useState('home');

  // Render content based on the current view
  const renderContent = () => {
    switch(currentView) {
      case 'local-scan':
        return <LocalScan />;
      case 's3-scan':
        return <S3Scan />;
      default:
        return (
          <div className="text-center p-10 ">
            {/* <h2 className="text-4xl font-semibold mb-6 text-blue-600">PII Detector</h2> */}
            <p className="text-1xl text-gray-600 mb-8 max-w-xl mx-auto">
              Detect and analyze Personally Identifiable Information (PII) in your documents and images. 
              Choose a scanning method below to get started.
            </p>
          </div>
        );
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="container mx-auto max-w-5xl">
        {/* Navbar */}
        <nav className="mb-8 bg-white rounded-lg shadow-lg">
          <div className="flex justify-between items-center p-6">
            <div className="flex items-center space-x-4">
              <span className="text-2xl font-bold text-blue-600">PII Detector</span>
            </div>
            <div className="flex space-x-6">
              {/* Navbar buttons to switch views */}
              <button 
                onClick={() => setCurrentView('home')} 
                className="flex items-center space-x-2 text-gray-700 hover:text-blue-600 transition-colors"
              >
                <Home className="w-6 h-6" />
                <span className="text-lg">Home</span>
              </button>
              <button 
                onClick={() => setCurrentView('local-scan')} 
                className="flex items-center space-x-2 text-gray-700 hover:text-blue-600 transition-colors"
              >
                <Scan className="w-6 h-6" />
                <span className="text-lg">Local Scan</span>
              </button>
              <button 
                onClick={() => setCurrentView('s3-scan')} 
                className="flex items-center space-x-2 text-gray-700 hover:text-blue-600 transition-colors"
              >
                <Cloud className="w-6 h-6" />
                <span className="text-lg">S3 Scan</span>
              </button>
            </div>
          </div>
        </nav>

        {/* Main Content Area */}
        <main>
          {renderContent()}
        </main>
      </div>
    </div>
  );
}

export default App;
