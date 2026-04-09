import React, { useRef, useEffect, useState } from 'react';

const CAPTURE_INTERVAL = 1000; // ms

export default function LiveFaceDetect() {
    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const [isActive, setIsActive] = useState(false);
    const [result, setResult] = useState(null);
    const [croppedFaceUrl, setCroppedFaceUrl] = useState(null);
    const [error, setError] = useState(null);
    const [processing, setProcessing] = useState(false);

    useEffect(() => {
        let intervalId;

        if (isActive) {
            startCamera();
            intervalId = setInterval(captureAndProcess, CAPTURE_INTERVAL);
        } else {
            stopCamera();
            if (intervalId) clearInterval(intervalId);
        }

        return () => {
            stopCamera();
            if (intervalId) clearInterval(intervalId);
        };
    }, [isActive]);

    const startCamera = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });
            if (videoRef.current) {
                videoRef.current.srcObject = stream;
            }
            setError(null);
        } catch (err) {
            console.error("Error accessing camera:", err);
            setError("Failed to access camera. Please ensure permissions are granted.");
            setIsActive(false);
        }
    };

    const stopCamera = () => {
        if (videoRef.current && videoRef.current.srcObject) {
            const tracks = videoRef.current.srcObject.getTracks();
            tracks.forEach(track => track.stop());
            videoRef.current.srcObject = null;
        }
    };

    const captureAndProcess = async () => {
        if (!videoRef.current || !canvasRef.current || processing) return;

        const video = videoRef.current;
        const canvas = canvasRef.current;

        // Set canvas dimensions to match video
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

        canvas.toBlob(async (blob) => {
            if (!blob) return;

            setProcessing(true);
            const formData = new FormData();
            formData.append('file', blob, 'frame.jpg');

            try {
                const response = await fetch('http://localhost:5000/face-detect', {
                    method: 'POST',
                    body: formData,
                });
                const data = await response.json();
                setResult(data.message);
                if (data.cropped_face_base64) {
                    setCroppedFaceUrl(data.cropped_face_base64);
                }
            } catch (err) {
                console.error("Error processing frame:", err);
            } finally {
                setProcessing(false);
            }
        }, 'image/jpeg', 0.8);
    };

    return (
        <div className="live-face-detect">
            <div style={{ marginBottom: '1.5rem', textAlign: 'center' }}>
                <div className={`status-badge ${isActive ? 'status-online' : 'status-offline'}`}>
                    {isActive ? '● Live Feed Online' : '○ System Standby'}
                </div>
                <div style={{ display: 'flex', justifyContent: 'center', gap: '12px' }}>
                    {!isActive ? (
                        <button onClick={() => setIsActive(true)} className="btn-primary">
                            Start Live Detection
                        </button>
                    ) : (
                        <button onClick={() => setIsActive(false)} className="btn-secondary">
                            Stop Detection
                        </button>
                    )}
                </div>
            </div>

            {error && (
                <div style={{
                    background: 'rgba(255, 68, 68, 0.1)',
                    border: '1px solid rgba(255, 68, 68, 0.3)',
                    color: '#ff6b6b',
                    padding: '12px',
                    borderRadius: '8px',
                    marginBottom: '1.5rem',
                    fontSize: '0.9rem',
                    textAlign: 'center'
                }}>
                    ⚠️ {error}
                </div>
            )}

            <div style={{
                display: 'flex',
                gap: '30px',
                flexWrap: 'wrap',
                justifyContent: 'center',
                alignItems: 'start'
            }}>
                {/* Video Feed Section */}
                <div style={{
                    position: 'relative',
                    borderRadius: '16px',
                    overflow: 'hidden',
                    border: '1px solid var(--doc-border)',
                    background: '#000',
                    boxShadow: isActive ? '0 0 30px rgba(108, 92, 231, 0.2)' : 'none',
                    transition: 'all 0.5s ease'
                }}>
                    <video
                        ref={videoRef}
                        autoPlay
                        playsInline
                        muted
                        style={{
                            width: '100%',
                            maxWidth: '480px',
                            aspectRatio: '4/3',
                            display: isActive ? 'block' : 'none',
                            objectFit: 'cover'
                        }}
                    />
                    {!isActive && (
                        <div style={{
                            width: '480px',
                            maxWidth: '100%',
                            aspectRatio: '4/3',
                            background: 'linear-gradient(45deg, #12121a, #1a1a26)',
                            display: 'flex',
                            flexDirection: 'column',
                            alignItems: 'center',
                            justifyContent: 'center',
                            color: 'var(--doc-text-muted)'
                        }}>
                            <div style={{ fontSize: '3rem', marginBottom: '1rem', opacity: 0.3 }}>📷</div>
                            <p style={{ fontSize: '0.9rem' }}>Camera Stream Offline</p>
                        </div>
                    )}
                    {processing && (
                        <div style={{
                            position: 'absolute',
                            bottom: 20,
                            left: '50%',
                            transform: 'translateX(-50%)',
                            background: 'rgba(0,0,0,0.7)',
                            backdropFilter: 'blur(4px)',
                            color: '#fff',
                            padding: '6px 16px',
                            borderRadius: '100px',
                            fontSize: '11px',
                            fontFamily: 'JetBrains Mono',
                            letterSpacing: '1px',
                            border: '1px solid rgba(255,255,255,0.1)'
                        }}>
                            ANALYZING FRAME...
                        </div>
                    )}
                </div>

                {/* Results Section */}
                <div style={{
                    width: '240px',
                    background: 'var(--doc-surface-2)',
                    padding: '24px',
                    borderRadius: '16px',
                    border: '1px solid var(--doc-border)',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center'
                }}>
                    <h4 style={{ margin: '0 0 16px', fontSize: '0.9rem', color: 'var(--doc-accent-2)' }}>Detection Results</h4>

                    <div style={{
                        marginBottom: '20px',
                        fontSize: '1.2rem',
                        fontWeight: '700',
                        color: result?.includes('1') ? '#00ff00' : 'var(--doc-text)',
                        textAlign: 'center'
                    }}>
                        {result ? result.split('.')[0] : "Standby"}
                    </div>

                    <div style={{
                        width: '180px',
                        height: '180px',
                        border: '2px solid var(--doc-border)',
                        borderRadius: '12px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        overflow: 'hidden',
                        background: 'var(--doc-bg)',
                        position: 'relative'
                    }}>
                        {croppedFaceUrl ? (
                            <img src={croppedFaceUrl} alt="Detected Face" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                        ) : (
                            <div style={{ textAlign: 'center', padding: '20px' }}>
                                <div style={{ fontSize: '1.5rem', opacity: 0.2, marginBottom: '8px' }}>👤</div>
                                <span style={{ fontSize: '10px', color: 'var(--doc-text-muted)', textTransform: 'uppercase', letterSpacing: '1px' }}>
                                    Awaiting Detection
                                </span>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            <canvas ref={canvasRef} style={{ display: 'none' }} />
        </div>
    );
}
