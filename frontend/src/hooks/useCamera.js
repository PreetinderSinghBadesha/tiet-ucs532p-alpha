/**
 * useCamera.js — Webcam access and image capture hook.
 */

import { useRef, useState, useCallback, useEffect } from "react";

/**
 * @returns {{
 *   videoRef: React.MutableRefObject,
 *   canvasRef: React.MutableRefObject,
 *   stream: MediaStream|null,
 *   error: string|null,
 *   isReady: boolean,
 *   startCamera: () => Promise<void>,
 *   stopCamera: () => void,
 *   captureImage: () => string|null   // returns base64 data URL or null
 * }}
 */
export function useCamera() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);

  const [stream, setStream] = useState(null);
  const [error, setError] = useState(null);
  const [isReady, setIsReady] = useState(false);

  const startCamera = useCallback(async () => {
    setError(null);
    setIsReady(false);
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "user", width: { ideal: 1280 }, height: { ideal: 720 } },
        audio: false,
      });
      streamRef.current = mediaStream;
      setStream(mediaStream);

      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
        await new Promise((resolve) => {
          videoRef.current.onloadedmetadata = resolve;
        });
        videoRef.current.play();
        setIsReady(true);
      }
    } catch (err) {
      console.error("Camera error:", err);
      if (err.name === "NotAllowedError" || err.name === "PermissionDeniedError") {
        setError("Camera permission was denied. Please allow camera access and try again.");
      } else if (err.name === "NotFoundError") {
        setError("No camera found on this device. Please use the file upload option.");
      } else {
        setError(`Camera error: ${err.message}`);
      }
    }
  }, []);

  const stopCamera = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
      setStream(null);
      setIsReady(false);
      if (videoRef.current) {
        videoRef.current.srcObject = null;
      }
    }
  }, []);

  const captureImage = useCallback(() => {
    if (!videoRef.current || !canvasRef.current || !isReady) return null;
    const video = videoRef.current;
    const canvas = canvasRef.current;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    // Mirror the image horizontally (selfie-style)
    ctx.translate(canvas.width, 0);
    ctx.scale(-1, 1);
    ctx.drawImage(video, 0, 0);
    return canvas.toDataURL("image/jpeg", 0.92);
  }, [isReady]);

  // Cleanup on unmount
  useEffect(() => {
    return () => stopCamera();
  }, [stopCamera]);

  return { videoRef, canvasRef, stream, error, isReady, startCamera, stopCamera, captureImage };
}
