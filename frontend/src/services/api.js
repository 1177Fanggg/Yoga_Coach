// API 服務層 - 封裝所有後端 API 呼叫
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

// 建立 axios 實例
const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// API 服務物件
export const apiService = {
    /**
     * 開始新的練習 session
     * @param {string} userId - 使用者 ID
     * @returns {Promise} session 資料
     */
    async startSession(userId = 'default_user') {
        const response = await apiClient.post('/start_session', {
            user_id: userId,
        });
        return response.data;
    },

    /**
     * 姿勢分析
     * @param {string} sessionId - Session ID
     * @param {Array} landmarks - 33 個 MediaPipe landmarks
     * @param {string} poseHint - 姿勢提示（可選）
     * @returns {Promise} 分析結果
     */
    async analyzePose(sessionId, landmarks, poseHint = null) {
        const response = await apiClient.post('/pose_analysis', {
            session_id: sessionId,
            landmarks: landmarks,
            timestamp: Math.floor(Date.now() / 1000),
            pose_hint: poseHint,
        });
        return response.data;
    },

    /**
     * 結束姿勢片段
     * @param {string} sessionId - Session ID
     * @param {string} poseName - 姿勢名稱
     * @param {number} avgScore - 平均分數
     * @param {number} duration - 持續時間（秒）
     * @returns {Promise} 片段資料
     */
    async endSegment(sessionId, poseName, avgScore, duration) {
        const response = await apiClient.post('/end_segment', {
            session_id: sessionId,
            pose_name: poseName,
            avg_score: avgScore,
            duration_seconds: duration,
        });
        return response.data;
    },

    /**
     * 合併影片並匯出
     * @param {string} sessionId - Session ID
     * @returns {Promise} 影片資料
     */
    async mergeAndExport(sessionId) {
        const response = await apiClient.post('/merge_and_export', {
            session_id: sessionId,
        });
        return response.data;
    },

    /**
     * 取得使用者歷史記錄
     * @param {string} userId - 使用者 ID
     * @param {number} limit - 回傳筆數限制
     * @param {number} skip - 跳過筆數
     * @returns {Promise} 歷史記錄
     */
    async getUserHistory(userId = 'default_user', limit = 20, skip = 0) {
        const response = await apiClient.get('/user_history', {
            params: { user_id: userId, limit, skip },
        });
        return response.data;
    },

    /**
     * 取得 session 詳細資訊
     * @param {string} sessionId - Session ID
     * @returns {Promise} Session 詳情
     */
    async getSessionDetail(sessionId) {
        const response = await apiClient.get('/session_detail', {
            params: { session_id: sessionId },
        });
        return response.data;
    },

    /**
     * 文字轉語音
     * @param {string} text - 文字內容
     * @returns {Promise} 音訊檔案資訊
     */
    async generateTTS(text) {
        const response = await apiClient.post('/tts_feedback', {
            text: text,
            language: 'zh-TW',
        });
        return response.data;
    },
};

export default apiService;
