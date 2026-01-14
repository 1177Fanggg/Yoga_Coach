import React, { useState, useEffect, useRef } from 'react';
import CameraComponent from '../components/Camera';
import FeedbackPanel from '../components/FeedbackPanel';
import apiService from '../services/api';
import websocketService from '../services/websocket';

const LivePracticePage = () => {
    const [sessionId, setSessionId] = useState(null);
    const [isRecording, setIsRecording] = useState(false);
    const [feedback, setFeedback] = useState(null);
    const [duration, setDuration] = useState(0);
    const [selectedPose, setSelectedPose] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const timerRef = useRef(null);

    // 姿勢列表
    const POSES = [
        { id: 'Warrior II', name: 'Warrior II (戰士二式)' },
        { id: 'Tree Pose', name: 'Tree Pose (樹式)' },
        { id: 'Downward Dog', name: 'Downward Dog (下犬式)' }
    ];

    useEffect(() => {
        return () => {
            // Cleanup
            if (timerRef.current) clearInterval(timerRef.current);
            if (sessionId) {
                websocketService.disconnect();
                // 嘗試合併影片（如果意外退出）
                // apiService.mergeAndExport(sessionId).catch(console.error);
            }
        };
    }, [sessionId]);

    const handleStartSession = async () => {
        try {
            setIsLoading(true);
            const data = await apiService.startSession();
            setSessionId(data.session_id);
            setIsRecording(true);

            // 連接 WebSocket
            websocketService.connect(data.session_id);
            websocketService.addListener(handleWebSocketMessage);

            // 開始計時
            timerRef.current = setInterval(() => {
                setDuration(prev => prev + 1);
            }, 1000);

        } catch (error) {
            console.error('開始練習失敗:', error);
            alert('無法開始練習，請確認後端服務是否啟動');
        } finally {
            setIsLoading(false);
        }
    };

    const handleEndSession = async () => {
        if (!sessionId) return;

        try {
            setIsLoading(true);
            // 停止錄製並合併影片
            await apiService.mergeAndExport(sessionId);

            setIsRecording(false);
            websocketService.disconnect();
            if (timerRef.current) clearInterval(timerRef.current);

            alert('練習結束！影片已儲存');
            // 可以導航到詳情頁或重置狀態
            window.location.href = '/history';

        } catch (error) {
            console.error('結束練習失敗:', error);
            alert('結束練習時發生錯誤');
        } finally {
            setIsLoading(false);
        }
    };

    const handleWebSocketMessage = (message) => {
        if (message.type === 'pose_feedback') {
            setFeedback(message.data);
        }
    };

    const handlePoseResults = async (landmarks) => {
        if (!sessionId || !isRecording) return;

        // 每隔幾幀發送一次以減輕負載 (前端 MediaPipe 很即時，但後端不需要每幀都分析全部)
        // 這裡我們簡單地每次都發，但建議加上 throttle
        // 為簡化，直接發送

        try {
            // 透過 WebSocket 發送還是 HTTP？
            // 原設計是用 HTTP POST /pose_analysis，WebSocket 負責接收回饋
            // 但頻繁 HTTP POST 效能較差。若後端有 WebSocket 接收會更好。
            // 目前實作計畫是：前端偵測 -> HTTP POST -> WebSocket 回傳結果
            // 為了效能，我們限制發送頻率 (例如每 200ms)

            const now = Date.now();
            if (!handlePoseResults.lastTime || now - handlePoseResults.lastTime > 200) {
                handlePoseResults.lastTime = now;

                // 這裡我們不等待回應，避免阻塞 UI
                apiService.analyzePose(sessionId, landmarks, selectedPose || null).catch(err => console.error(err));
            }
        } catch (error) {
            console.error('分析失敗:', error);
        }
    };

    const handlePlayAudio = async (text) => {
        if (!text) return;
        try {
            const data = await apiService.generateTTS(text);
            if (data.audio_url) {
                const audio = new Audio(`http://localhost:8000${data.audio_url}`);
                audio.play();
            }
        } catch (error) {
            console.error('TTS 播放失敗:', error);
        }
    };

    const formatDuration = (sec) => {
        const m = Math.floor(sec / 60).toString().padStart(2, '0');
        const s = (sec % 60).toString().padStart(2, '0');
        return `${m}:${s}`;
    };

    return (
        <div className="container py-6 h-screen flex flex-col">
            <header className="flex justify-between items-center mb-6">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">即時練習</h1>
                    <p className="text-gray-500">AI 瑜珈教練輔助系統</p>
                </div>
                <div className="flex items-center gap-4">
                    <div className="text-xl font-mono bg-gray-100 px-3 py-1 rounded">
                        ⏱ {formatDuration(duration)}
                    </div>
                    <button
                        className="btn btn-secondary text-sm"
                        onClick={() => window.location.href = '/history'}
                    >
                        查看歷史
                    </button>
                </div>
            </header>

            {/* 主要內容區 */}
            <div className="flex-1 grid grid-cols-1 lg:grid-cols-3 gap-6 min-h-0 overflow-hidden">
                {/* 左側：相機畫面 (佔 2/3) */}
                <div className="lg:col-span-2 bg-black rounded-2xl overflow-hidden relative shadow-lg flex items-center justify-center">
                    <CameraComponent
                        onResults={handlePoseResults}
                        isRecording={isRecording}
                    />
                </div>

                {/* 右側：回饋與姿勢選擇 (佔 1/3) */}
                <div className="flex flex-col gap-6 min-h-0 overflow-y-auto pr-2">
                    {/* 即時回饋面板 */}
                    <div className="flex-1 min-h-[300px]">
                        <FeedbackPanel
                            feedback={feedback}
                            onPlayAudio={handlePlayAudio}
                        />
                    </div>

                    {/* 姿勢選擇 (移到底部或側邊) */}
                    <div className="card">
                        <h3 className="text-sm font-semibold text-gray-700 mb-3">選擇目標姿勢</h3>
                        <div className="grid grid-cols-1 gap-2">
                            <button
                                className={`btn text-left justify-start ${selectedPose === '' ? 'btn-primary' : 'btn-secondary'}`}
                                onClick={() => setSelectedPose('')}
                            >
                                🤖 自動偵測
                            </button>
                            {POSES.map(pose => (
                                <button
                                    key={pose.id}
                                    className={`btn text-left justify-start ${selectedPose === pose.id ? 'btn-primary' : 'btn-secondary'}`}
                                    onClick={() => setSelectedPose(pose.id)}
                                >
                                    🧘 {pose.name}
                                </button>
                            ))}
                        </div>
                    </div>
                </div>
            </div>

            {/* 底部控制面板 */}
            <div className="mt-6 bg-white border border-gray-200 rounded-xl p-4 shadow-sm flex justify-between items-center">
                <div className="flex items-center gap-4">
                    <div className="text-sm text-gray-500">
                        狀態: <span className={`font-bold ${isRecording ? 'text-green-600' : 'text-gray-400'}`}>
                            {isRecording ? '● 練習中' : '○ 準備就緒'}
                        </span>
                    </div>
                    {isRecording && (
                        <div className="text-xl font-mono bg-gray-100 px-3 py-1 rounded">
                            ⏱ {formatDuration(duration)}
                        </div>
                    )}
                </div>

                <div className="flex gap-4">
                    {!isRecording ? (
                        <button
                            onClick={handleStartSession}
                            disabled={isLoading}
                            className="btn btn-primary btn-lg rounded-full px-8 shadow-lg hover:shadow-xl transform transition hover:-translate-y-1"
                        >
                            ▶ 開始練習
                        </button>
                    ) : (
                        <button
                            onClick={handleEndSession}
                            disabled={isLoading}
                            className="btn btn-error btn-lg rounded-full px-8 shadow-lg hover:shadow-xl transform transition hover:-translate-y-1"
                        >
                            ■ 結束練習
                        </button>
                    )}
                </div>

                <div className="text-sm text-gray-400">
                    目前姿勢: {selectedPose ? POSES.find(p => p.id === selectedPose)?.name : '自動偵測'}
                </div>
            </div>
        </div>
    );
};

export default LivePracticePage;
