import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import VideoPlayer from '../components/VideoPlayer';
import apiService from '../services/api';

const SessionDetailPage = () => {
    const { sessionId } = useParams();
    const navigate = useNavigate();
    const [session, setSession] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchDetail = async () => {
            try {
                setLoading(true);
                const data = await apiService.getSessionDetail(sessionId);
                setSession(data);
            } catch (error) {
                console.error('載入詳情失敗:', error);
                alert('無法載入 Session 資料');
                navigate('/history');
            } finally {
                setLoading(false);
            }
        };

        if (sessionId) fetchDetail();
    }, [sessionId, navigate]);

    if (loading) {
        return (
            <div className="h-screen flex items-center justify-center">
                <div className="spinner mr-3"></div>
                <span className="text-lg text-gray-600">載入中...</span>
            </div>
        );
    }

    if (!session) return null;

    const { start_time, duration_seconds, avg_score, video_url, poses, stats } = session;

    return (
        <div className="container py-8 animate-fade-in">
            {/* 導航 */}
            <button
                className="btn btn-secondary mb-6 text-sm"
                onClick={() => navigate('/history')}
            >
                ← 返回歷史記錄
            </button>

            {/* 標頭資訊 */}
            <div className="flex flex-col lg:flex-row justify-between items-start lg:items-end mb-8 gap-4">
                <div>
                    <div className="text-sm text-gray-500 mb-1">SESSION DETAIL</div>
                    <h1 className="text-3xl font-bold text-gray-900 mb-2">
                        {new Date(start_time).toLocaleString('zh-TW')}
                    </h1>
                    <div className="flex gap-4 text-sm text-gray-600">
                        <span>⏱ 時長: {Math.floor(duration_seconds / 60)}分 {duration_seconds % 60}秒</span>
                        <span>⭐ 平均分數: {avg_score}</span>
                    </div>
                </div>

                <div className="flex gap-3">
                    {video_url && (
                        <a
                            href={`http://localhost:8000${video_url}`}
                            download
                            className="btn btn-secondary"
                            target="_blank" rel="noreferrer"
                        >
                            📥 下載影片
                        </a>
                    )}
                    <button
                        className="btn btn-primary"
                        onClick={() => navigate('/')}
                    >
                        🔄 重新練習
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* 左側：影片播放器 */}
                <div className="lg:col-span-2 space-y-6">
                    <div className="card p-0 overflow-hidden bg-black">
                        {video_url ? (
                            <VideoPlayer src={`http://localhost:8000${video_url}`} />
                        ) : (
                            <div className="aspect-video flex items-center justify-center text-gray-400">
                                <p>此練習未建立影片檔案</p>
                            </div>
                        )}
                    </div>

                    {/* 統計卡片 */}
                    <div className="grid grid-cols-3 gap-4">
                        <div className="card bg-gray-50 text-center py-4">
                            <div className="text-xs text-gray-500 uppercase">總姿勢數</div>
                            <div className="text-2xl font-bold">{stats.total_poses}</div>
                        </div>
                        <div className="card bg-gray-50 text-center py-4">
                            <div className="text-xs text-gray-500 uppercase">正確次數</div>
                            <div className="text-2xl font-bold text-green-600">{stats.correct_poses}</div>
                        </div>
                        <div className="card bg-gray-50 text-center py-4">
                            <div className="text-xs text-gray-500 uppercase">正確率</div>
                            <div className="text-2xl font-bold">{Math.round(stats.accuracy_rate)}%</div>
                        </div>
                    </div>
                </div>

                {/* 右側：姿勢列表 */}
                <div className="space-y-4">
                    <h2 className="text-xl font-bold text-gray-900">姿勢詳情</h2>
                    <div className="space-y-4 max-h-[600px] overflow-y-auto pr-2">
                        {poses.map((pose, index) => (
                            <div key={index} className="card p-4 hover:shadow-md transition bg-white">
                                <div className="flex justify-between items-center mb-2">
                                    <h3 className="font-bold text-gray-900">{pose.pose_name}</h3>
                                    <span className={`text-lg font-bold ${pose.score >= 80 ? 'text-green-600' : 'text-gray-700'}`}>
                                        {pose.score}
                                    </span>
                                </div>

                                <div className="text-xs text-gray-400 mb-2">
                                    {pose.correct ? (
                                        <span className="badge badge-success mr-2">✓ 正確</span>
                                    ) : (
                                        <span className="badge badge-warning mr-2">! 需調整</span>
                                    )}
                                    {Math.floor(pose.duration_seconds)} 秒
                                </div>

                                <p className="text-sm text-gray-600 bg-gray-50 p-2 rounded">
                                    {pose.feedback}
                                </p>
                            </div>
                        ))}

                        {poses.length === 0 && (
                            <p className="text-gray-500 text-center py-4">無詳細姿勢記錄</p>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default SessionDetailPage;
