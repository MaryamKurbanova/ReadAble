"use client";

import { useState, useRef } from "react";
import { ReactComponent as PdfIcon } from "./assets/icons/pdf-icon.svg";
import "./App.css";

function App() {
  const [inputText, setInputText] = useState("");
  const [selectedFont, setSelectedFont] = useState("OpenDyslexic");
  const [previewText, setPreviewText] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  const handlePdfUpload = () => {
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setIsDragging(false);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const files = e.dataTransfer.files;
    handleFiles(files);
  };

  const onFileSelect = (e) => {
    const files = e.target.files;
    handleFiles(files);
  };

  const handleFiles = async (files) => {
    if (files.length > 0) {
      const file = files[0];
      if (file.type === "application/pdf" || file.type === "text/plain") {
        const formData = new FormData();
        formData.append("file", file);

        try {
          const response = await fetch("http://localhost:5000/api/upload", {
            method: "POST",
            body: formData,
          });

          if (response.ok) {
            const data = await response.json();
            setInputText(data.text);
            setPreviewText(data.text);
            setShowModal(false);
          } else {
            const errorData = await response.json();
            alert(`Error: ${errorData.error}`);
          }
        } catch (error) {
          console.error("Error uploading file:", error);
          alert("An error occurred while uploading the file.");
        }
      } else {
        alert("Please upload a PDF or TXT file");
      }
    }
  };

  const applyFontStyle = (e) => {
    setInputText(e.target.value);
    setPreviewText(e.target.value);
  };

  const generateSpeechFromText = () => {
    // TO DO: Implement speech generation logic
  };

  return (
    <div className="App">
      <h1>Dyslexify</h1>

      <button className="import-button" onClick={handlePdfUpload}>
        Import PDF/TXT
      </button>
      <div className="input-section">
        <label>Enter text here:</label>
        <textarea
          value={inputText}
          onChange={applyFontStyle}
          placeholder="Enter your text here..."
        ></textarea>
      </div>

      <div className="font-selection-section">
        <label>Select Font:</label>
        <select
          value={selectedFont}
          onChange={(e) => setSelectedFont(e.target.value)}
        >
          <option value="OpenDyslexic">OpenDyslexic (Default)</option>
          <option value="Sylexiad Sans Spaced">Sylexiad Sans Spaced</option>
          <option value="Sylexiad Serif Spaced">Sylexiad Serif Spaced</option>
        </select>
      </div>

      <div className="preview-section">
        <div style={{ fontFamily: selectedFont }}>{previewText}</div>
      </div>

      <button
        className="speech-generate-button"
        onClick={generateSpeechFromText}
      >
        Generate Speech
      </button>

      {showModal && (
        <div className="modal-overlay" onClick={closeModal}>
          <div
            className={`modal-content ${isDragging ? "dragging" : ""}`}
            onClick={(e) => e.stopPropagation()}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <button className="close-button" onClick={closeModal}>
              ×
            </button>
            <div className="pdf-icon">
              <PdfIcon />
            </div>
            <p>Drag and drop a PDF or TXT file</p>
            <button
              className="select-file-button"
              onClick={() => fileInputRef.current.click()}
            >
              Select a file
            </button>
            <input
              type="file"
              ref={fileInputRef}
              onChange={onFileSelect}
              accept=".pdf,.txt"
              style={{ display: "none" }}
            />
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
