"""
AI 瑜珈教練系統 - 資料庫模組
使用 MongoDB 儲存 session 與姿勢資料
"""

from pymongo import MongoClient, DESCENDING
from datetime import datetime
from typing import List, Dict, Optional
import logging

from config import MONGODB_URL, DATABASE_NAME, COLLECTION_SESSIONS

# 設定日誌
logger = logging.getLogger(__name__)


class Database:
    """MongoDB 資料庫管理類別"""
    
    def __init__(self, connection_string=MONGODB_URL, db_name=DATABASE_NAME):
        """
        初始化資料庫連接
        
        Args:
            connection_string: MongoDB 連接字串
            db_name: 資料庫名稱
        """
        try:
            self.client = MongoClient(connection_string)
            self.db = self.client[db_name]
            self.sessions = self.db[COLLECTION_SESSIONS]
            
            # 建立索引（提升查詢效能）
            self.sessions.create_index([("session_id", 1)], unique=True)
            self.sessions.create_index([("user_id", 1)])
            self.sessions.create_index([("start_time", DESCENDING)])
            
            logger.info(f"資料庫連接成功：{db_name}")
            
        except Exception as e:
            logger.error(f"資料庫連接失敗：{e}")
            raise
    
    def save_session(self, session_data: Dict) -> bool:
        """
        儲存 session 資料
        
        Args:
            session_data: Session 資料字典
        
        Returns:
            bool: 是否成功儲存
        """
        try:
            # 檢查必要欄位
            required_fields = ['session_id', 'user_id', 'start_time']
            for field in required_fields:
                if field not in session_data:
                    logger.error(f"缺少必要欄位：{field}")
                    return False
            
            # 使用 upsert 模式（如果存在則更新，否則插入）
            result = self.sessions.update_one(
                {'session_id': session_data['session_id']},
                {'$set': session_data},
                upsert=True
            )
            
            logger.info(f"Session 已儲存：{session_data['session_id']}")
            return True
            
        except Exception as e:
            logger.error(f"儲存 session 失敗：{e}")
            return False
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """
        取得單一 session 資料
        
        Args:
            session_id: Session ID
        
        Returns:
            Dict: Session 資料或 None
        """
        try:
            session = self.sessions.find_one(
                {'session_id': session_id},
                {'_id': 0}  # 不回傳 MongoDB 的 _id
            )
            return session
            
        except Exception as e:
            logger.error(f"取得 session 失敗：{e}")
            return None
    
    def get_user_history(self, user_id: str, limit: int = 20, skip: int = 0) -> List[Dict]:
        """
        取得使用者歷史記錄
        
        Args:
            user_id: 使用者 ID
            limit: 回傳筆數限制
            skip: 跳過筆數（分頁用）
        
        Returns:
            List[Dict]: Session 列表
        """
        try:
            sessions = list(
                self.sessions.find(
                    {'user_id': user_id},
                    {'_id': 0}
                )
                .sort('start_time', DESCENDING)
                .skip(skip)
                .limit(limit)
            )
            
            logger.info(f"取得使用者 {user_id} 的 {len(sessions)} 筆歷史記錄")
            return sessions
            
        except Exception as e:
            logger.error(f"取得歷史記錄失敗：{e}")
            return []
    
    def get_total_sessions_count(self, user_id: str) -> int:
        """
        取得使用者總 session 數量
        
        Args:
            user_id: 使用者 ID
        
        Returns:
            int: 總數量
        """
        try:
            count = self.sessions.count_documents({'user_id': user_id})
            return count
        except Exception as e:
            logger.error(f"取得總數失敗：{e}")
            return 0
    
    def update_session_poses(self, session_id: str, pose_data: Dict) -> bool:
        """
        更新 session 的姿勢資料（新增一個姿勢片段）
        
        Args:
            session_id: Session ID
            pose_data: 姿勢資料
        
        Returns:
            bool: 是否成功更新
        """
        try:
            result = self.sessions.update_one(
                {'session_id': session_id},
                {'$push': {'poses': pose_data}}
            )
            
            if result.modified_count > 0:
                logger.info(f"Session {session_id} 已新增姿勢資料")
                return True
            else:
                logger.warning(f"Session {session_id} 未找到或未更新")
                return False
                
        except Exception as e:
            logger.error(f"更新姿勢資料失敗：{e}")
            return False
    
    def update_session_final_info(self, session_id: str, duration_seconds: int, 
                                  avg_score: float, video_path: str) -> bool:
        """
        更新 session 最終資訊（練習結束後）
        
        Args:
            session_id: Session ID
            duration_seconds: 練習總時長（秒）
            avg_score: 平均分數
            video_path: 影片路徑
        
        Returns:
            bool: 是否成功更新
        """
        try:
            result = self.sessions.update_one(
                {'session_id': session_id},
                {'$set': {
                    'duration_seconds': duration_seconds,
                    'avg_score': avg_score,
                    'final_video_path': video_path,
                    'end_time': datetime.utcnow().isoformat()
                }}
            )
            
            if result.modified_count > 0:
                logger.info(f"Session {session_id} 最終資訊已更新")
                return True
            else:
                logger.warning(f"Session {session_id} 未找到或未更新")
                return False
                
        except Exception as e:
            logger.error(f"更新最終資訊失敗：{e}")
            return False
    
    def delete_session(self, session_id: str) -> bool:
        """
        刪除 session
        
        Args:
            session_id: Session ID
        
        Returns:
            bool: 是否成功刪除
        """
        try:
            result = self.sessions.delete_one({'session_id': session_id})
            
            if result.deleted_count > 0:
                logger.info(f"Session {session_id} 已刪除")
                return True
            else:
                logger.warning(f"Session {session_id} 未找到")
                return False
                
        except Exception as e:
            logger.error(f"刪除 session 失敗：{e}")
            return False
    
    def close(self):
        """關閉資料庫連接"""
        if self.client:
            self.client.close()
            logger.info("資料庫連接已關閉")


# 全域資料庫實例（單例模式）
_db_instance = None

def get_database() -> Database:
    """
    取得資料庫實例（單例模式）
    
    Returns:
        Database: 資料庫實例
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance


if __name__ == "__main__":
    # 測試資料庫連接
    logging.basicConfig(level=logging.INFO)
    
    db = Database()
    
    # 測試儲存 session
    test_session = {
        'session_id': 'test_20260114_163000',
        'user_id': 'test_user',
        'start_time': datetime.utcnow().isoformat(),
        'poses': [],
        'avg_score': 0,
        'duration_seconds': 0
    }
    
    if db.save_session(test_session):
        print("測試 session 儲存成功")
        
        # 測試取得 session
        retrieved = db.get_session('test_20260114_163000')
        if retrieved:
            print(f"取得 session：{retrieved['session_id']}")
        
        # 測試新增姿勢
        pose_data = {
            'segment_id': 1,
            'pose_name': 'Warrior II',
            'score': 85,
            'correct': True,
            'feedback': '很好！'
        }
        
        db.update_session_poses('test_20260114_163000', pose_data)
        
        # 測試取得歷史
        history = db.get_user_history('test_user', limit=5)
        print(f"歷史記錄數：{len(history)}")
        
        # 刪除測試 session
        db.delete_session('test_20260114_163000')
        print("測試 session 已刪除")
    
    db.close()
