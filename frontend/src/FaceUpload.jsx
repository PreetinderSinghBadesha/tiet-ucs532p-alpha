import React, { useState } from 'react';

export default function FaceUpload() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [result, setResult] = useState(null);
  const [croppedFaceUrl, setCroppedFaceUrl] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]);
    setResult(null);
    setCroppedFaceUrl(null);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    setLoading(true);
    const formData = new FormData();
    formData.append('file', selectedFile);
    try {
      const response = await fetch('http://localhost:5000/face-detect', {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      setResult(data.message);
      if (data.cropped_face_url) {
        setCroppedFaceUrl(data.cropped_face_url);
      }
    } catch (err) {
      setResult('Error processing image.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ margin: '2rem 0' }}>
      <h3>Face Detection Demo</h3>
      <input type="file" accept="image/*" onChange={handleFileChange} />
      <button onClick={handleUpload} disabled={!selectedFile || loading} style={{ marginLeft: 8 }}>
        {loading ? 'Processing...' : 'Upload & Detect'}
      </button>
      {result && <div style={{ marginTop: 16 }}>{result}</div>}
      {croppedFaceUrl && (
        <div style={{ marginTop: 16 }}>
          <img src={croppedFaceUrl} alt="Cropped Face" style={{ maxWidth: 200, border: '2px solid #0c0' }} />
        </div>
      )}
    </div>
  );
}
