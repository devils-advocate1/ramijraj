export interface Point {
  x: number;
  y: number;
}

export interface Rectangle {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface TextElement {
  id: string;
  x: number;
  y: number;
  text: string;
  fontSize: number;
  fontFamily: string;
  color: string;
  rotation: number;
  isSelected: boolean;
}

export interface EraseArea {
  id: string;
  points: Point[];
  isSelected: boolean;
}

export interface EditHistory {
  id: string;
  type: 'text' | 'erase' | 'draw';
  data: any;
  timestamp: number;
}

export type ToolType = 'select' | 'text' | 'erase' | 'draw' | 'move';

export interface CanvasState {
  image: HTMLImageElement | null;
  textElements: TextElement[];
  eraseAreas: EraseArea[];
  selectedTool: ToolType;
  brushSize: number;
  history: EditHistory[];
  historyIndex: number;
  isProcessing: boolean;
}

export interface OCRResult {
  text: string;
  confidence: number;
  bounds: Rectangle;
}

export interface FontMatch {
  fontFamily: string;
  confidence: number;
  sampleText: string;
}

export interface InpaintingResult {
  success: boolean;
  imageData?: string;
  error?: string;
}