import React, { useState, useEffect } from 'react';
import PoseCard from '../components/PoseCard';
import apiService from '../services/api';

const HistoryPage = () => {
    const [sessions, setSessions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [stats, setStats] = useState({ total_sessions: 0 });

    useEffect(() => {
        fetchHistory();
    }, []);

    const fetchHistory = async () => {
        try {
            setLoading(true);
            const data = await apiService.getUserHistory();
            setSessions(data.sessions);
            setStats({ total_sessions: data.total });
        } catch (error) {
            console.error('載入歷史失敗:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container py-8">
            {/* 標頭 */}
            <div className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900 mb-2">練習歷史</h1>
                    <p className="text-gray-500">檢視您過去的練習記錄與進步歷程</p>
                </div>
                <button
                    className="btn btn-primary"
                    onClick={() => window.location.href = '/'}
                >
                    + 開始新練習
                </button>
            </div>

            {/* 統計概覽 */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="card bg-gray-900 text-white">
                    <div className="text-gray-400 text-sm mb-1 uppercase tracking-wider">總練習次數</div>
                    <div className="text-4xl font-bold">{stats.total_sessions}</div>
                </div>
                {/* 可以擴充更多統計 */}
                <div className="card">
                    <div className="text-gray-500 text-sm mb-1 uppercase tracking-wider">最近練習</div>
                    <div className="text-2xl font-bold text-gray-900">
                        {sessions.length > 0 ? new Date(sessions[0].date).toLocaleDateString() : '-'}
                    </div>
                </div>
                <div className="card">
                    <div className="text-gray-500 text-sm mb-1 uppercase tracking-wider">平均分數</div>
                    <div className="text-2xl font-bold text-gray-900">
                        {sessions.length > 0 ? Math.round(sessions.reduce((acc, curr) => acc + curr.avg_score, 0) / sessions.length) : '-'}
                    </div>
                </div>
            </div>

            {/* 列表 */}
            <div>
                <h2 className="text-xl font-bold text-gray-900 mb-4">最近記錄</h2>

                {loading ? (
                    <div className="text-center py-12">
                        <div className="spinner mb-4"></div>
                        <p className="text-gray-500">載入中...</p>
                    </div>
                ) : sessions.length === 0 ? (
                    <div className="text-center py-16 bg-gray-50 rounded-lg border border-gray-200">
                        <p className="text-xl text-gray-600 mb-4">尚無練習記錄</p>
                        <button
                            className="btn btn-primary"
                            onClick={() => window.location.href = '/'}
                        >
                            開始第一次練習
                        </button>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {sessions.map(session => (
                            <PoseCard key={session.session_id} data={session} />
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default HistoryPage;
