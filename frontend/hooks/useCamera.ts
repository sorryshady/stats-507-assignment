"use client";

import { useEffect, useRef, useState, useCallback } from "react";

export function useCamera() {
  const [isActive, setIsActive] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasPermission, setHasPermission] = useState<boolean | null>(null);
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  const startCamera = useCallback(async () => {
    try {
      setError(null);
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: "user",
        },
      });

      streamRef.current = stream;
      setHasPermission(true);
      setIsActive(true);
      // Note: Stream will be attached in useEffect when video element is ready
    } catch (err) {
      console.error("Camera error:", err);
      setHasPermission(false);
      setIsActive(false);
      
      if (err instanceof DOMException) {
        if (err.name === "NotAllowedError" || err.code === DOMException.NOT_ALLOWED_ERR) {
          setError("Camera permission denied. Please allow camera access in your browser settings.");
        } else if (err.name === "NotFoundError" || err.code === DOMException.NOT_FOUND_ERR) {
          setError("No camera found. Please connect a camera.");
        } else if (err.name === "NotReadableError" || err.code === DOMException.NOT_READABLE_ERR) {
          setError("Camera is already in use by another application.");
        } else if (err.name === "OverconstrainedError") {
          setError("Camera doesn't support the requested constraints. Trying with default settings...");
          // Retry with simpler constraints
          try {
            const fallbackStream = await navigator.mediaDevices.getUserMedia({ video: true });
            streamRef.current = fallbackStream;
            setHasPermission(true);
            setIsActive(true);
            if (videoRef.current) {
              videoRef.current.srcObject = fallbackStream;
              videoRef.current.play();
            }
            return;
          } catch (fallbackErr) {
            setError(`Camera error: ${err.message}`);
          }
        } else {
          setError(`Camera error: ${err.name} - ${err.message}`);
        }
      } else if (err instanceof Error) {
        setError(`Camera error: ${err.message}`);
      } else {
        setError("Failed to access camera. Please check your browser permissions.");
      }
    }
  }, []);

  const stopCamera = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    setIsActive(false);
    
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
  }, []);

  const captureFrame = useCallback((): string | null => {
    if (!videoRef.current || !isActive) {
      return null;
    }

    const video = videoRef.current;
    
    // Check if video is ready (HAVE_ENOUGH_DATA = 4)
    // readyState values: 0=HAVE_NOTHING, 1=HAVE_METADATA, 2=HAVE_CURRENT_DATA, 3=HAVE_FUTURE_DATA, 4=HAVE_ENOUGH_DATA
    if (video.readyState < 2) {
      return null;
    }

    // Check if video has valid dimensions
    if (video.videoWidth === 0 || video.videoHeight === 0) {
      return null;
    }

    const canvas = canvasRef.current || document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext("2d");
    if (!ctx) {
      return null;
    }

    ctx.drawImage(video, 0, 0);
    // Return base64 string without data URL prefix
    return canvas.toDataURL("image/jpeg", 0.8).split(",")[1];
  }, [isActive]);

  // Attach stream to video element when both are ready
  useEffect(() => {
    if (isActive && streamRef.current) {
      let retryCount = 0;
      const maxRetries = 40; // 2 seconds total (40 * 50ms)
      
      const checkAndAttach = () => {
        const video = videoRef.current;
        const stream = streamRef.current;
        
        if (video && stream) {
          console.log("✅ Video element and stream ready, attaching...");
          
          // Only attach if not already attached
          if (video.srcObject !== stream) {
            video.srcObject = stream;
          }
          
          const playPromise = video.play();
          if (playPromise !== undefined) {
            playPromise
              .then(() => {
                console.log("✅ Video playing successfully, readyState:", video.readyState);
              })
              .catch((playError) => {
                console.error("❌ Error playing video:", playError);
                setError(`Video playback error: ${playError.message}`);
              });
          }
        } else if (isActive && retryCount < maxRetries) {
          retryCount++;
          if (retryCount % 5 === 0) {
            console.log(`⏳ Waiting for video element... (attempt ${retryCount}/${maxRetries})`);
          }
          setTimeout(checkAndAttach, 50);
        } else if (retryCount >= maxRetries) {
          console.error("❌ Video element not available after", maxRetries, "attempts");
          console.error("Debug info:", {
            isActive,
            hasStream: !!streamRef.current,
            hasVideoRef: !!videoRef.current,
            videoRefValue: videoRef.current,
          });
        }
      };
      
      checkAndAttach();
    }
  }, [isActive]); // Re-run when isActive changes

  useEffect(() => {
    // Create canvas element for frame capture
    const canvas = document.createElement("canvas");
    canvasRef.current = canvas;

    return () => {
      stopCamera();
    };
  }, [stopCamera]);

  return {
    isActive,
    hasPermission,
    error,
    videoRef,
    startCamera,
    stopCamera,
    captureFrame,
  };
}

