// app/dashboard/components/ImageUploader.tsx
"use client";

import React, { useState } from "react";
import Button from "../../../components/Common/Button";

interface ImageUploaderProps {
  onAnalysis: (analysis: any, highlightedImage: string) => void;
}

const ImageUploader: React.FC<ImageUploaderProps> = ({ onAnalysis }) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append("file", selectedFile);

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/analyze`,
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Analysis failed.");
      }

      onAnalysis(
        data.analysis,
        `data:image/jpeg;base64,${data.highlighted_image}`
      );
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4 bg-white rounded shadow">
      <h2 className="text-xl font-semibold mb-4">Upload Product Image</h2>
      <input
        type="file"
        accept="image/*"
        onChange={handleFileChange}
        className="mb-4"
      />
      <Button onClick={handleUpload} disabled={!selectedFile || loading}>
        {loading ? "Analyzing..." : "Analyze"}
      </Button>
      {error && <p className="text-red-600 mt-4">{error}</p>}
    </div>
  );
};

export default ImageUploader;
