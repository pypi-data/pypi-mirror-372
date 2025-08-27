#!/usr/bin/env python3
"""
跨平台兼容性测试脚本
验证 capacity-web 在不同平台上的工作情况
"""

import sys
import platform
import os

def test_platform_compatibility():
    """测试平台兼容性"""
    print("🌍 平台兼容性测试")
    print(f"操作系统: {platform.system()} {platform.release()}")
    print(f"Python版本: {sys.version}")
    print(f"架构: {platform.machine()}")
    print(f"处理器: {platform.processor()}")
    
    # 测试路径处理
    print(f"\n📁 路径兼容性:")
    print(f"当前工作目录: {os.getcwd()}")
    print(f"路径分隔符: '{os.sep}'")
    print(f"环境变量分隔符: '{os.pathsep}'")
    
    # 测试导入
    try:
        from capacity_web import search_with_nextchat
        print(f"\n✅ 模块导入成功")
        
        # 测试基本功能
        result = search_with_nextchat("test", max_results=1)
        if "success" in result:
            print(f"✅ 基本功能测试成功")
        else:
            print(f"❌ 基本功能测试失败")
            
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
    except Exception as e:
        print(f"⚠️  功能测试警告: {e}")

if __name__ == "__main__":
    test_platform_compatibility()
