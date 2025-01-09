import React, { useRef, useState } from 'react';
import { FolderOpen, Upload, Loader2 } from 'lucide-react';

function FileUpload({ onFileProcessing }) {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const directoryInputRef = useRef(null);

  // Handle the directory or file selection change
  const handleDirectoryChange = (e) => {
    const selectedFiles = Array.from(e.target.files);
    setFiles(selectedFiles); // Store selected files in the state
  };

  // Trigger the directory input when the user clicks "Select Directory"
  const triggerDirectoryInput = () => {
    directoryInputRef.current.click();
  };

  // Handle the form submission and call the processing function
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (files.length === 0) return; // Don't submit if no files are selected

    setLoading(true); // Show loading state
    try {
      // Call the function passed from the parent component to process files
      await onFileProcessing(files);
    } catch (error) {
      console.error('Error in file processing:', error);
      alert('Failed to process files');
    } finally {
      setLoading(false); // Reset loading state after processing
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <input 
        type="file" 
        ref={directoryInputRef}
        webkitdirectory="true" // Allow directory selection
        multiple // Allow multiple files
        accept="*/*" // Allow all file types, adjust if needed for specific files
        onChange={handleDirectoryChange} 
        className="hidden"
      />
      
      <div className="flex items-center space-x-4">
        <button 
          type="button"
          onClick={triggerDirectoryInput}
          className="flex items-center space-x-2 bg-blue-50 text-blue-700 px-4 py-2 rounded-full hover:bg-blue-100 transition-colors"
        >
          <FolderOpen className="w-5 h-5" />
          <span>Select Directory</span>
        </button>
        
        {files.length > 0 && (
          <div className="text-gray-600">
            {files.length} file(s) selected
          </div>
        )}
      </div>

      <div className="mt-4">
        {/* Display the list of selected files */}
        {files.length > 0 && (
          <div className="space-y-2">
            {files.map((file, index) => (
              <div key={index} className="text-gray-600">
                <span>{file.name}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      <button 
        type="submit" 
        disabled={loading || files.length === 0}
        className={`w-full flex items-center justify-center space-x-2 p-3 rounded-lg transition-colors ${
          loading || files.length === 0 
            ? 'bg-gray-300 text-gray-500 cursor-not-allowed' 
            : 'bg-blue-600 text-white hover:bg-blue-700'
        }`}
      >
        {loading ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin mr-2" />
            Processing...
          </>
        ) : (
          <>
            <Upload className="w-5 h-5 mr-2" />
            Scan Selected Files
          </>
        )}
      </button>
    </form>
  );
}

export default FileUpload;
