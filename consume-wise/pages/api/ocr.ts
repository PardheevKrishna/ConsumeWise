// pages/api/ocr.ts
import type { NextApiRequest, NextApiResponse } from "next";

// This is a placeholder. You should integrate with an actual OCR API.
const OCR_API_URL = "https://api.example.com/ocr";

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method === "POST") {
    try {
      const { image } = req.body;

      // Send the image to the OCR API
      const response = await fetch(OCR_API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          // Include any necessary authentication headers
        },
        body: JSON.stringify({ image }),
      });

      const data = await response.json();

      if (!response.ok) {
        return res
          .status(response.status)
          .json({ error: data.error || "OCR failed" });
      }

      return res.status(200).json({ text: data.text });
    } catch (error) {
      return res.status(500).json({ error: "Internal Server Error" });
    }
  } else {
    res.setHeader("Allow", ["POST"]);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}
