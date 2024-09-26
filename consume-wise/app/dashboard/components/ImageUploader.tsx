// app/dashboard/components/ImageUploader.tsx
"use client";

import React, { useState } from "react";
import Button from "../../../components/Common/Button";

const ImageUploader = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [analysis, setAnalysis] = useState<any>(null);
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
      // Convert image to base64
      const base64 = await toBase64(selectedFile);

      // Send to OCR API
      const ocrResponse = await fetch("/api/ocr", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ image: base64 }),
      });

      const ocrData = await ocrResponse.json();

      if (!ocrResponse.ok) {
        throw new Error(ocrData.error || "OCR failed");
      }

      const extractedText = ocrData.text;

      // Send extracted text to AI Analysis API
      const analyzeResponse = await fetch("/api/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text: extractedText }),
      });

      const analyzeData = await analyzeResponse.json();

      if (!analyzeResponse.ok) {
        throw new Error(analyzeData.error || "Analysis failed");
      }

      setAnalysis(analyzeData.analysis);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const toBase64 = (file: File) =>
    new Promise<string>((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => {
        if (typeof reader.result === "string") resolve(reader.result);
        else reject("Failed to convert image to base64");
      };
      reader.onerror = (error) => reject(error);
    });

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
      {analysis && (
        <div className="mt-6">
          {/* Render analysis components here */}
          {/* Example: */}
          {/* <HealthScore score={analysis.healthScore} /> */}
          {/* <NutrientAnalysis data={analysis.NutritionalAnalysis} /> */}
        </div>
      )}
    </div>
  );
};

export default ImageUploader;
