import Konva from 'konva';
import jsPDF from 'jspdf';
import { ExportOptions } from '@/components/Canvas/types';

/**
 * Export Konva stage to PNG/JPEG
 */
export async function exportToImage(
  stage: Konva.Stage,
  options: ExportOptions
): Promise<Blob> {
  return new Promise((resolve, reject) => {
    try {
      const scale = options.scale;
      const originalScale = stage.scaleX();
      const originalPosition = { x: stage.x(), y: stage.y() };

      // Temporarily adjust scale for export
      stage.scale({ x: scale, y: scale });
      stage.position({ x: 0, y: 0 });

      // Get data URL
      const dataUrl = stage.toDataURL({
        mimeType: options.format === 'jpg' ? 'image/jpeg' : 'image/png',
        quality: options.quality === 'high' ? 1 : options.quality === 'medium' ? 0.8 : 0.6,
        pixelRatio: 1,
      });

      // Restore original scale and position
      stage.scale({ x: originalScale, y: originalScale });
      stage.position(originalPosition);

      // Convert data URL to blob
      fetch(dataUrl)
        .then(res => res.blob())
        .then(resolve)
        .catch(reject);
    } catch (error) {
      reject(error);
    }
  });
}

/**
 * Export Konva stage to SVG
 */
export async function exportToSVG(
  stage: Konva.Stage,
  options: ExportOptions
): Promise<string> {
  return new Promise((resolve, reject) => {
    try {
      const serializer = new XMLSerializer();
      const stageNode = stage.content.cloneNode(true);
      const svgString = serializer.serializeToString(stageNode);
      
      // Add SVG wrapper with proper dimensions
      const width = stage.width() * options.scale;
      const height = stage.height() * options.scale;
      
      const svg = `<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg width="${width}px" height="${height}px" viewBox="0 0 ${width} ${height}"
     xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
  <rect width="100%" height="100%" fill="${options.backgroundColor}"/>
  ${svgString}
</svg>`;
      
      resolve(svg);
    } catch (error) {
      reject(error);
    }
  });
}

/**
 * Export Konva stage to PDF
 */
export async function exportToPDF(
  stage: Konva.Stage,
  options: ExportOptions
): Promise<Blob> {
  return new Promise(async (resolve, reject) => {
    try {
      // First export as image
      const imageBlob = await exportToImage(stage, {
        ...options,
        format: 'png',
        scale: options.scale,
      });
      
      const imageUrl = URL.createObjectURL(imageBlob);
      const img = new Image();
      
      img.onload = () => {
        const pdf = new jsPDF({
          orientation: img.width > img.height ? 'l' : 'p',
          unit: 'px',
          format: [img.width, img.height],
        });
        
        pdf.addImage(img, 'PNG', 0, 0, img.width, img.height);
        const pdfBlob = pdf.output('blob');
        URL.revokeObjectURL(imageUrl);
        resolve(pdfBlob);
      };
      
      img.onerror = reject;
      img.src = imageUrl;
    } catch (error) {
      reject(error);
    }
  });
}

/**
 * Download blob as file
 */
export function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

/**
 * Download SVG as file
 */
export function downloadSVG(svgString: string, filename: string) {
  const blob = new Blob([svgString], { type: 'image/svg+xml' });
  downloadBlob(blob, filename);
}