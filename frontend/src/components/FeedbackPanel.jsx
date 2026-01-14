import React, { useRef } from 'react';

const FeedbackPanel = ({ feedback, onPlayAudio }) => {
    if (!feedback) {
        return (
            <div className="card h-full flex items-center justify-center text-center">
                <div className="text-gray-500">
                    <p className="text-xl mb-2">等待姿勢偵測...</p>
                    <p className="text-sm">請站在相機前開始練習</p>
                </div>
            </div>
        );
    }

    const { pose_name, score, feedback: feedbackText, correct, details } = feedback;

    // 判斷分數顏色
    let scoreClass = "text-gray-900";
    if (score >= 90) scoreClass = "text-green-600";
    else if (score >= 70) scoreClass = "text-yellow-600";
    else scoreClass = "text-red-600";

    return (
        <div className="card h-full flex flex-col justify-between animate-fade-in">
            <div>
                <div className="flex justify-between items-start mb-6">
                    <div>
                        <h3 className="text-sm text-gray-500 uppercase tracking-wider mb-1">當前姿勢</h3>
                        <h2 className="text-3xl font-bold text-gray-900">{pose_name || '偵測中...'}</h2>
                    </div>
                    <div className="text-right">
                        <div className={`text-4xl font-bold ${scoreClass}`}>
                            {score || 0}
                            <span className="text-lg text-gray-400 font-normal">/100</span>
                        </div>
                        <div className="mt-1">
                            {correct ? (
                                <span className="badge badge-success">✓ 正確</span>
                            ) : (
                                <span className="badge badge-warning">! 需調整</span>
                            )}
                        </div>
                    </div>
                </div>

                <div className="mb-6">
                    <h4 className="text-sm font-semibold text-gray-700 mb-2">建議與回饋</h4>
                    <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                        <p className="text-lg leading-relaxed text-gray-800">
                            {feedbackText || '保持姿勢...'}
                        </p>
                    </div>
                </div>

                {details && Object.keys(details).length > 0 && (
                    <div className="mb-6">
                        <h4 className="text-sm font-semibold text-gray-700 mb-3">詳細數據</h4>
                        <div className="grid grid-cols-2 gap-3 text-sm">
                            {Object.entries(details).map(([key, value]) => (
                                <div key={key} className="flex justify-between items-center bg-white p-2 border rounded">
                                    <span className="text-gray-500 capitalize">{key.replace(/_/g, ' ')}</span>
                                    <span className="font-mono font-medium">{value}°</span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>

            <div className="mt-4 pt-4 border-t border-gray-100">
                <button
                    onClick={() => onPlayAudio(feedbackText)}
                    className="btn btn-secondary w-full flex items-center justify-center gap-2"
                    disabled={!feedbackText}
                >
                    <span>🔊 播放語音回饋</span>
                </button>
            </div>
        </div>
    );
};

export default FeedbackPanel;
