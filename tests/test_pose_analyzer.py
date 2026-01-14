"""
AI 瑜珈教練系統 - 姿勢分析單元測試
"""

import pytest
import sys
from pathlib import Path

# 將 backend 目錄加入路徑
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from pose_analyzer import calculate_angle, check_warrior_ii, check_tree_pose, check_downward_dog, analyze_pose


def test_calculate_angle():
    """測試角度計算函數"""
    # 測試 90 度角
    a = {'x': 0.0, 'y': 0.0, 'z': 0.0, 'visibility': 1.0}
    b = {'x': 0.0, 'y': 1.0, 'z': 0.0, 'visibility': 1.0}
    c = {'x': 1.0, 'y': 1.0, 'z': 0.0, 'visibility': 1.0}
    
    angle = calculate_angle(a, b, c)
    assert 89 <= angle <= 91, f"90度角計算錯誤：{angle}"
    
    # 測試 180 度角（直線）
    a = {'x': 0.0, 'y': 0.0, 'z': 0.0, 'visibility': 1.0}
    b = {' x': 0.5, 'y': 0.0, 'z': 0.0, 'visibility': 1.0}
    c = {'x': 1.0, 'y': 0.0, 'z': 0.0, 'visibility': 1.0}
    
    angle = calculate_angle(a, b, c)
    assert 179 <= angle <= 180, f"180度角計算錯誤：{angle}"
    
    print("✓ 角度計算測試通過")


def test_analyze_pose():
    """測試姿勢分析功能"""
    # 建立測試用的 33 個 landmarks（正常站立姿勢）
    landmarks = []
    for i in range(33):
        landmarks.append({
            'x': 0.5,
            'y': float(i) / 33.0,
            'z': 0.0,
            'visibility': 0.9
        })
    
    # 測試分析
    result = analyze_pose(landmarks)
    
    assert 'pose_name' in result
    assert 'correct' in result
    assert 'score' in result
    assert 'feedback' in result
    assert 'details' in result
    
    assert isinstance(result['score'], int)
    assert 0 <= result['score'] <= 100
    assert isinstance(result['correct'], bool)
    
    print(f"✓ 姿勢分析測試通過：{result['pose_name']}, 分數：{result['score']}")


def test_landmarks_validation():
    """測試 landmarks 驗證"""
    # 測試錯誤數量的 landmarks
    invalid_landmarks = [{'x': 0.5, 'y': 0.5, 'z': 0.0, 'visibility': 1.0}] * 10
    
    result = analyze_pose(invalid_landmarks)
    
    assert result['pose_name'] == 'Unknown'
    assert result['score'] == 0
    assert not result['correct']
    
    print("✓ Landmarks 驗證測試通過")


if __name__ == "__main__":
    print("開始執行姿勢分析測試...\n")
    
    try:
        test_calculate_angle()
        test_analyze_pose()
        test_landmarks_validation()
        
        print("\n所有測試通過！✓")
    except AssertionError as e:
        print(f"\n測試失敗：{e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n測試錯誤：{e}")
        sys.exit(1)
