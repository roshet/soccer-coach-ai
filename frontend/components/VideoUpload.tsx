"use client";
import { useRef, useState } from "react";

interface Props {
  onFileSelect: (file: File) => void;
  selectedFile: File | null;
}

const MAX_SIZE_BYTES = 50 * 1024 * 1024; // 50MB — mirrors the backend limit
const MAX_DURATION_SECONDS = 30;

// Read a video file's duration by probing its metadata off-DOM.
function getVideoDuration(file: File): Promise<number> {
  return new Promise((resolve, reject) => {
    const video = document.createElement("video");
    video.preload = "metadata";
    const url = URL.createObjectURL(file);
    video.onloadedmetadata = () => {
      URL.revokeObjectURL(url);
      resolve(video.duration);
    };
    video.onerror = () => {
      URL.revokeObjectURL(url);
      reject(new Error("Could not read video metadata"));
    };
    video.src = url;
  });
}

export default function VideoUpload({ onFileSelect, selectedFile }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragOver, setDragOver] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Validate type/size/duration up front so the user isn't made to wait through a full
  // upload only for the backend to reject it (the backend still enforces these as a backstop).
  const validateAndSelect = async (file: File) => {
    setError(null);
    if (!file.type.startsWith("video/")) {
      setError("Please choose a video file (MP4, MOV, or AVI).");
      return;
    }
    if (file.size > MAX_SIZE_BYTES) {
      setError(`Video is ${(file.size / 1024 / 1024).toFixed(0)}MB — must be under 50MB.`);
      return;
    }
    try {
      const duration = await getVideoDuration(file);
      if (duration > MAX_DURATION_SECONDS) {
        setError(`Video is ${duration.toFixed(0)}s long — must be 30 seconds or less.`);
        return;
      }
    } catch {
      // Metadata unreadable in this browser — let the backend enforce duration rather than block.
    }
    onFileSelect(file);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) {
      void validateAndSelect(file);
    }
  };

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-300">Video</label>
      <div
        onClick={() => inputRef.current?.click()}
        onDrop={handleDrop}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-colors ${
          dragOver
            ? "border-green-400 bg-green-900/20"
            : "border-gray-700 hover:border-gray-500"
        }`}
      >
        {selectedFile ? (
          <div className="space-y-1">
            <p className="text-green-400 font-medium">{selectedFile.name}</p>
            <p className="text-sm text-gray-400">
              {(selectedFile.size / 1024 / 1024).toFixed(1)} MB
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            <p className="text-gray-300">Drag and drop your video here</p>
            <p className="text-sm text-gray-500">or click to browse</p>
            <p className="text-xs text-gray-600 mt-3">MP4, MOV, AVI · Max 50MB · Max 30 seconds</p>
          </div>
        )}
      </div>
      <input
        ref={inputRef}
        type="file"
        accept="video/*"
        className="hidden"
        onChange={(e) => {
          const f = e.target.files?.[0];
          if (f) void validateAndSelect(f);
        }}
      />
      {error && (
        <p className="text-sm text-red-400">{error}</p>
      )}
      <p className="text-xs text-gray-500">
        Tip: Film from a 45° angle at waist height with good lighting for best results.
      </p>
    </div>
  );
}
