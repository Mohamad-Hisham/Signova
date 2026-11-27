import { useCallback, useEffect, useRef, useState } from "react";

export type CameraStatus = "off" | "requesting" | "ready" | "error";

function stopTracks(stream: MediaStream | null): void {
  stream?.getTracks().forEach(track => track.stop());
}

function cameraMessage(cause: unknown): string {
  if (cause instanceof DOMException) {
    switch (cause.name) {
      case "NotAllowedError":
      case "PermissionDeniedError":
        return "Camera access is blocked for this site. Allow camera permission, then try again.";
      case "NotFoundError":
        return "No camera was found. Connect a camera or use a device with a camera.";
      case "NotReadableError":
      case "TrackStartError":
        return "The camera could not start. Close other camera apps and try again.";
      case "OverconstrainedError":
        return "This camera cannot provide a supported video stream.";
      case "SecurityError":
        return "Camera access requires HTTPS, or localhost during development.";
    }
  }
  return "The camera could not start. Check browser permission and try again.";
}

export function useCamera() {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const ownedStream = useRef<MediaStream | null>(null);
  const generation = useRef(0);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [status, setStatus] = useState<CameraStatus>("off");
  const [error, setError] = useState<string | null>(null);

  const release = useCallback(() => {
    generation.current += 1;
    stopTracks(ownedStream.current);
    ownedStream.current = null;
    const video = videoRef.current;
    if (video) {
      video.pause();
      video.srcObject = null;
    }
  }, []);

  const stop = useCallback(() => {
    release();
    setStream(null);
    setStatus("off");
  }, [release]);

  const start = useCallback(async () => {
    release();
    const requestGeneration = generation.current;
    setError(null);
    setStatus("requesting");

    if (!navigator.mediaDevices?.getUserMedia) {
      const message = "This browser does not support camera access.";
      setError(message);
      setStatus("error");
      return null;
    }

    try {
      let next: MediaStream;
      try {
        next = await navigator.mediaDevices.getUserMedia({
          video: {
            facingMode: "user",
            width: { ideal: 640 },
            height: { ideal: 480 },
          },
          audio: false,
        });
      } catch (cause) {
        if (
          cause instanceof DOMException &&
          cause.name === "OverconstrainedError"
        ) {
          next = await navigator.mediaDevices.getUserMedia({
            video: true,
            audio: false,
          });
        } else {
          throw cause;
        }
      }

      if (requestGeneration !== generation.current) {
        stopTracks(next);
        return null;
      }

      const video = videoRef.current;
      if (!video) {
        stopTracks(next);
        throw new Error("CAMERA_VIDEO_ELEMENT_MISSING");
      }

      ownedStream.current = next;
      video.srcObject = next;
      video.muted = true;
      video.playsInline = true;
      await video.play();

      if (requestGeneration !== generation.current) {
        stopTracks(next);
        return null;
      }

      await new Promise<void>((resolve, reject) => {
        if (video.videoWidth > 0 && video.videoHeight > 0) {
          resolve();
          return;
        }
        const loaded = () => {
          window.clearTimeout(timer);
          video.removeEventListener("loadedmetadata", loaded);
          resolve();
        };
        const timer = window.setTimeout(() => {
          video.removeEventListener("loadedmetadata", loaded);
          reject(new Error("CAMERA_METADATA_TIMEOUT"));
        }, 5000);
        video.addEventListener("loadedmetadata", loaded, { once: true });
      });

      if (requestGeneration !== generation.current) {
        stopTracks(next);
        return null;
      }

      const primaryTrack = next.getVideoTracks()[0];
      primaryTrack?.addEventListener(
        "ended",
        () => {
          if (ownedStream.current === next) {
            release();
            setStream(null);
            setStatus("error");
            setError("The camera disconnected. Start it again to continue.");
          }
        },
        { once: true },
      );
      setStream(next);
      setStatus("ready");
      return next;
    } catch (cause) {
      if (requestGeneration === generation.current) {
        release();
        setStream(null);
        setError(
          cause instanceof Error && cause.message.startsWith("CAMERA_")
            ? "The camera did not provide a usable video stream. Try again."
            : cameraMessage(cause),
        );
        setStatus("error");
      }
      return null;
    }
  }, [release]);

  useEffect(() => {
    return () => {
      generation.current += 1;
      stopTracks(ownedStream.current);
      ownedStream.current = null;
      if (videoRef.current) videoRef.current.srcObject = null;
    };
  }, []);

  return { videoRef, stream, status, error, start, stop };
}
