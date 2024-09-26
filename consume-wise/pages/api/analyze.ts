// pages/api/analyze.ts
import type { NextApiRequest, NextApiResponse } from "next";

// Replace with your actual Generative AI API endpoint and key
const AI_API_URL = "https://api.example.com/generative-ai";
const AI_API_KEY = process.env.GENERATIVE_AI_API_KEY;

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method === "POST") {
    try {
      const { text } = req.body;

      // Send the text to the Generative AI API
      const response = await fetch(AI_API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${AI_API_KEY}`,
        },
        body: JSON.stringify({ prompt: text }),
      });

      const data = await response.json();

      if (!response.ok) {
        return res
          .status(response.status)
          .json({ error: data.error || "AI Analysis failed" });
      }

      return res.status(200).json({ analysis: data.analysis });
    } catch (error) {
      return res.status(500).json({ error: "Internal Server Error" });
    }
  } else {
    res.setHeader("Allow", ["POST"]);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}
