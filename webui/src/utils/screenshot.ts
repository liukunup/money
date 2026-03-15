import html2canvas from 'html2canvas';

export interface ScreenshotOptions {
  scale?: number;
  backgroundColor?: string | null;
  logging?: boolean;
  useCORS?: boolean;
}

export async function captureElement(
  element: HTMLElement,
  options: ScreenshotOptions = {}
): Promise<Blob> {
  const {
    scale = 2,
    backgroundColor = null,
    logging = false,
    useCORS = true,
  } = options;

  try {
    const canvas = await html2canvas(element, {
      scale,
      backgroundColor,
      logging,
      useCORS,
      allowTaint: true,
    });

    return new Promise((resolve, reject) => {
      canvas.toBlob(
        (blob) => {
          if (blob) {
            resolve(blob);
          } else {
            reject(new Error('Failed to capture screenshot'));
          }
        },
        'image/png',
        1.0
      );
    });
  } catch (error) {
    console.error('Screenshot capture failed:', error);
    throw error;
  }
}

export function downloadBlob(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

export async function shareImage(blob: Blob, title: string, text?: string): Promise<boolean> {
  if (!navigator.share) {
    console.warn('Web Share API not supported');
    return false;
  }

  const file = new File([blob], 'money-dashboard.png', { type: 'image/png' });

  try {
    const shareData: ShareData = {
      title,
      text,
      files: [file],
    };

    if (!navigator.canShare(shareData)) {
      return false;
    }

    await navigator.share(shareData);
    return true;
  } catch (error) {
    // User cancelled or share failed
    if ((error as Error).name !== 'AbortError') {
      console.error('Share failed:', error);
    }
    return false;
  }
}

export async function captureAndDownload(
  element: HTMLElement,
  filename: string = 'money-dashboard.png'
): Promise<void> {
  const blob = await captureElement(element);
  downloadBlob(blob, filename);
}

export async function captureAndShare(
  element: HTMLElement,
  title: string = 'Money Dashboard',
  text?: string
): Promise<boolean> {
  const blob = await captureElement(element);
  return shareImage(blob, title, text);
}
