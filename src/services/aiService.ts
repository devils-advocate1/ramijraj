import { InpaintingResult, OCRResult } from '../types';

// Cleanup.pictures API for AI inpainting
export const performInpainting = async (
  imageData: string,
  maskData: string
): Promise<InpaintingResult> => {
  try {
    // Using Cleanup.pictures API (you'll need to get an API key)
    const response = await fetch('https://api.cleanup.pictures/v1/remove', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.REACT_APP_CLEANUP_API_KEY || 'demo'}`,
      },
      body: JSON.stringify({
        image: imageData,
        mask: maskData,
      }),
    });

    if (!response.ok) {
      throw new Error('Inpainting failed');
    }

    const result = await response.json();
    return {
      success: true,
      imageData: result.image,
    };
  } catch (error) {
    console.error('Inpainting error:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }
};

// Tesseract.js for OCR
export const performOCR = async (imageData: string): Promise<OCRResult[]> => {
  try {
    const { createWorker } = await import('tesseract.js');
    const worker = await createWorker('eng');
    
    const result = await worker.recognize(imageData);
    await worker.terminate();

    return result.data.words.map((word: any) => ({
      text: word.text,
      confidence: word.confidence,
      bounds: {
        x: word.bbox.x0,
        y: word.bbox.y0,
        width: word.bbox.x1 - word.bbox.x0,
        height: word.bbox.y1 - word.bbox.y0,
      },
    }));
  } catch (error) {
    console.error('OCR error:', error);
    return [];
  }
};

// Font matching service
export const matchFont = async (sampleText: string): Promise<string> => {
  // Simple font matching - in production, you'd use a more sophisticated service
  const commonFonts = [
    'Arial', 'Helvetica', 'Times New Roman', 'Georgia', 
    'Verdana', 'Tahoma', 'Courier New', 'Impact'
  ];
  
  // For demo purposes, return a random font
  // In production, you'd analyze the text characteristics
  return commonFonts[Math.floor(Math.random() * commonFonts.length)];
};