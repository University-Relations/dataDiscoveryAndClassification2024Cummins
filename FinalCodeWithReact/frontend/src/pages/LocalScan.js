import React, { useState } from "react";
import { Download, Eye, FileText, Loader2 } from "lucide-react";
import "./styles/LocalScan.css";

function LocalScan() {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [reportUrl, setReportUrl] = useState(null);
  const [previewContent, setPreviewContent] = useState(null);

  const handleFileChange = (e) => {
    setFiles(Array.from(e.target.files)); // Set selected files to state
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (files.length === 0) return;

    const formData = new FormData();
    files.forEach((file) => formData.append("files", file)); // Append all files under 'files' key

    setLoading(true);
    try {
      // Send files to backend for processing
      const response = await fetch("http://localhost:5000/api/process-local-files", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Network response was not ok");
      }

      const data = await response.json();
      const reportFilename = data.report;

      // Fetch and generate report download link
      const reportResponse = await fetch(`http://localhost:5000/download-report/${reportFilename}`);
      const reportBlob = await reportResponse.blob();
      const url = window.URL.createObjectURL(reportBlob);
      setReportUrl(url);

      setPreviewContent({
        totalImages: data.totalImages || files.length,
        piiDetected: data.piiDetected || 0,
        files: files.map((file) => file.name), // Display file names in preview
      });
    } catch (error) {
      console.error("Error processing files:", error);
      alert("Failed to process files. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (reportUrl) {
      const link = document.createElement("a");
      link.href = reportUrl;
      link.download = "PII_Report.pdf";
      link.click();
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-semibold text-blue-800">Local Scan</h2>
      <form onSubmit={handleSubmit} className="mb-6">
        <div className="flex items-center space-x-4">
          <input
            type="file"
            multiple
            webkitdirectory="true" // Allow directory selection
            onChange={handleFileChange}
            className="flex-grow file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
          />
          <button
            type="submit"
            disabled={loading || files.length === 0}
            className={`flex items-center space-x-2 px-4 py-2 rounded-full transition-colors ${
              loading || files.length === 0
                ? "bg-gray-300 text-gray-500 cursor-not-allowed"
                : "bg-blue-600 text-white hover:bg-blue-700"
            }`}
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin mr-2" />
                Processing...
              </>
            ) : (
              "Scan Files"
            )}
          </button>
        </div>
      </form>

      {previewContent && (
        <div className="bg-blue-50 rounded-lg p-4 mb-6">
          <div className="flex items-center mb-4">
            <Eye className="w-6 h-6 text-blue-600 mr-2" />
            <h3 className="text-lg font-semibold text-blue-800">Scan Preview</h3>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-gray-600">Total Images Scanned:</p>
              <p className="font-bold text-blue-800">{previewContent.totalImages}</p>
            </div>
          </div>
          <div className="mt-4">
            <p className="text-gray-600">Scanned Files:</p>
            <ul className="list-disc list-inside text-sm text-gray-700">
              {previewContent.files.map((filename, index) => (
                <li key={index}>{filename}</li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {reportUrl && (
        <div className="flex space-x-4">
          <button
            onClick={handleDownload}
            className="flex items-center space-x-2 bg-green-500 text-white px-4 py-2 rounded-full hover:bg-green-600 transition-colors"
          >
            <Download className="w-5 h-5" />
            <span>Download Report</span>
          </button>
          <a
            href={reportUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center space-x-2 bg-blue-500 text-white px-4 py-2 rounded-full hover:bg-blue-600 transition-colors"
          >
            <Eye className="w-5 h-5" />
            <span>Preview Report</span>
          </a>
        </div>
      )}
    </div>
  );
}

export default LocalScan;
