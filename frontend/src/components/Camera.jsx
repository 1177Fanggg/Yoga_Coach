import React, { useEffect, useRef, useState } from 'react';
import { Pose, POSE_CONNECTIONS } from '@mediapipe/pose';
import { Camera } from '@mediapipe/camera_utils';
import { drawConnectors, drawLandmarks } from '@mediapipe/drawing_utils';

const CameraComponent = ({ onResults, isRecording }) => {
    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const [error, setError] = useState(null);

    useEffect(() => {
        const videoElement = videoRef.current;
        const canvasElement = canvasRef.current;

        if (!videoElement || !canvasElement) return;

        const canvasCtx = canvasElement.getContext('2d');

        const onResultsCallback = (results) => {
            // 設定 Canvas 尺寸與影片一致
            canvasElement.width = videoElement.videoWidth;
            canvasElement.height = videoElement.videoHeight;

            canvasCtx.save();
            canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);

            // 繪製骨架 - 使用簡潔的白色與灰色線條
            if (results.poseLandmarks) {
                drawConnectors(canvasCtx, results.poseLandmarks, POSE_CONNECTIONS, {
                    color: '#ffffff', // 白色連結線
                    lineWidth: 2
                });
                drawLandmarks(canvasCtx, results.poseLandmarks, {
                    color: '#d1d5db', // 淺灰色節點
                    lineWidth: 1,
                    radius: 3
                });
            }
            canvasCtx.restore();

            // 將 landmarks 回傳給父元件
            if (onResults && results.poseLandmarks) {
                onResults(results.poseLandmarks);
            }
        };

        // 初始化 MediaPipe Pose
        const pose = new Pose({
            locateFile: (file) => {
                return `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`;
            }
        });

        pose.setOptions({
            modelComplexity: 1,
            smoothLandmarks: true,
            enableSegmentation: false,
            smoothSegmentation: false,
            minDetectionConfidence: 0.5,
            minTrackingConfidence: 0.5
        });

        pose.onResults(onResultsCallback);

        // 初始化 Camera
        const camera = new Camera(videoElement, {
            onFrame: async () => {
                await pose.send({ image: videoElement });
            },
            width: 1280,
            height: 720
        });

        camera.start()
            .then(() => {
                console.log('相機已啟動');
            })
            .catch(err => {
                console.error('相機啟動失敗:', err);
                setError('無法存取相機，請檢查權限');
            });

        return () => {
            // 清理資源 (Camera class doesn't have a stop method exposed easily in this version, 
            // but cleaning up references helps)
            /* 
             注意：MediaPipe Camera Utils 的 stop 方法有時不穩定，
             這裡依賴組件卸載來停止更新
            */
        };
    }, [onResults]);

    return (
        <div className="relative w-full h-full bg-black rounded-lg overflow-hidden flex items-center justify-center">
            {error && (
                <div className="absolute z-10 text-white bg-red-500 px-4 py-2 rounded">
                    {error}
                </div>
            )}

            {/* 原始影片元素 (隱藏，只用於擷取) */}
            <video
                ref={videoRef}
                className="absolute w-full h-full object-cover opacity-50"
                style={{ display: 'none' }} // 隱藏原始 video，改為畫在 canvas 如果需要，或者直接顯示 video 並疊加 canvas
            // 這裡我們顯示 video 並疊加 canvas
            />

            {/* 為了顯示錄影畫面，我們還是顯示 video 元素，但在上面疊加 canvas */}
            <video
                ref={videoRef}
                className="absolute w-full h-full object-contain"
                autoPlay
                playsInline
                muted
            />

            <canvas
                ref={canvasRef}
                className="absolute w-full h-full object-contain pointer-events-none"
            />

            {isRecording && (
                <div className="absolute top-4 right-4 flex items-center gap-2 bg-red-600 text-white px-3 py-1 rounded-full animate-pulse">
                    <div className="w-3 h-3 bg-white rounded-full"></div>
                    <span className="text-sm font-medium">REC</span>
                </div>
            )}
        </div>
    );
};

export default CameraComponent;
