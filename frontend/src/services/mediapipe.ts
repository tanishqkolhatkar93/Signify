import { FilesetResolver, HandLandmarker, type HandLandmarkerResult } from "@mediapipe/tasks-vision";
import type { HandLandmarks } from "../types";

let handLandmarker: HandLandmarker | null = null;
let isInitializing = false;

export async function getHandLandmarker(): Promise<HandLandmarker | null> {
  if (handLandmarker) return handLandmarker;
  if (isInitializing) {
    while (isInitializing) {
      await new Promise((r) => setTimeout(r, 100));
    }
    return handLandmarker;
  }

  isInitializing = true;
  try {
    const vision = await FilesetResolver.forVisionTasks(
      "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.18/wasm"
    );
    handLandmarker = await HandLandmarker.createFromOptions(vision, {
      baseOptions: {
        modelAssetPath:
          "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task",
        delegate: "GPU"
      },
      runningMode: "VIDEO",
      numHands: 2
    });
    return handLandmarker;
  } catch (err) {
    console.warn("MediaPipe GPU delegate init failed, retrying with CPU delegate:", err);
    try {
      const vision = await FilesetResolver.forVisionTasks(
        "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.18/wasm"
      );
      handLandmarker = await HandLandmarker.createFromOptions(vision, {
        baseOptions: {
          modelAssetPath:
            "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task",
          delegate: "CPU"
        },
        runningMode: "VIDEO",
        numHands: 2
      });
      return handLandmarker;
    } catch (e2) {
      console.error("Critical: Could not initialize MediaPipe HandLandmarker:", e2);
      return null;
    }
  } finally {
    isInitializing = false;
  }
}

export const HAND_CONNECTIONS = [
  { start: 0, end: 1 },
  { start: 1, end: 2 },
  { start: 2, end: 3 },
  { start: 3, end: 4 },
  { start: 0, end: 5 },
  { start: 5, end: 6 },
  { start: 6, end: 7 },
  { start: 7, end: 8 },
  { start: 5, end: 9 },
  { start: 9, end: 10 },
  { start: 10, end: 11 },
  { start: 11, end: 12 },
  { start: 9, end: 13 },
  { start: 13, end: 14 },
  { start: 14, end: 15 },
  { start: 15, end: 16 },
  { start: 13, end: 17 },
  { start: 0, end: 17 },
  { start: 17, end: 18 },
  { start: 18, end: 19 },
  { start: 19, end: 20 }
];

export function convertToAppHandLandmarks(result: HandLandmarkerResult): HandLandmarks[] {
  if (!result || !result.landmarks || result.landmarks.length === 0) return [];
  return result.landmarks.map((landmarks, idx) => {
    let handedness = "Right";
    if (result.handedness && result.handedness[idx] && result.handedness[idx][0]) {
      handedness = result.handedness[idx][0].categoryName || "Right";
    }
    return {
      handedness,
      landmarks: landmarks.map((pt) => ({ x: pt.x, y: pt.y, z: pt.z ?? 0 }))
    };
  });
}
