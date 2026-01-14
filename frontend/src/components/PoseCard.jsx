import React from 'react';
import { useNavigate } from 'react-router-dom';

const PoseCard = ({ data }) => {
    const navigate = useNavigate();
    const { session_id, start_time, duration_seconds, avg_score, poses_count, video_available } = data;

    // 格式化日期
    const date = new Date(start_time).toLocaleString('zh-TW', {
        dateStyle: 'medium',
        timeStyle: 'short'
    });

    // 格式化時長
    const formatDuration = (seconds) => {
        const min = Math.floor(seconds / 60);
        const sec = Math.floor(seconds % 60);
        return `${min.toString().padStart(2, '0')}:${sec.toString().padStart(2, '0')}`;
    };

    return (
        <div className="card hover:shadow-lg transition-shadow cursor-pointer" onClick={() => navigate(`/session/${session_id}`)}>
            <div className="flex justify-between items-start mb-4">
                <div>
                    <div className="text-xs text-gray-500 mb-1">SESSION ID: {session_id}</div>
                    <div className="text-lg font-bold text-gray-900">{date}</div>
                </div>
                {video_available && (
                    <span className="badge bg-gray-100 text-gray-600 border border-gray-200">
                        🎬 已錄製
                    </span>
                )}
            </div>

            <div className="grid grid-cols-3 gap-4 mb-4">
                <div className="text-center p-2 bg-gray-50 rounded border border-gray-100">
                    <div className="text-xs text-gray-500 mb-1">分數</div>
                    <div className={`text-xl font-bold ${avg_score >= 80 ? 'text-green-600' : 'text-gray-900'}`}>
                        {Math.round(avg_score)}
                    </div>
                </div>
                <div className="text-center p-2 bg-gray-50 rounded border border-gray-100">
                    <div className="text-xs text-gray-500 mb-1">時長</div>
                    <div className="text-xl font-bold text-gray-900">
                        {formatDuration(duration_seconds)}
                    </div>
                </div>
                <div className="text-center p-2 bg-gray-50 rounded border border-gray-100">
                    <div className="text-xs text-gray-500 mb-1">姿勢數</div>
                    <div className="text-xl font-bold text-gray-900">
                        {poses_count}
                    </div>
                </div>
            </div>

            <div className="flex justify-end">
                <span className="text-sm text-blue-600 font-medium hover:underline">
                    查看詳情 →
                </span>
            </div>
        </div>
    );
};

export default PoseCard;
