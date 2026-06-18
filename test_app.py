import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_import():
    """测试导入是否正常"""
    try:
        from ai_floating_ball import TraeFloatingBall
        print("✅ 导入成功")
        return True
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return False

def test_paths():
    """测试 Trae 路径搜索"""
    trae_paths = [
        r"C:\Program Files\Trae\Trae.exe",
        r"C:\Program Files (x86)\Trae\Trae.exe",
        os.path.join(os.environ.get('APPDATA', ''), 'Trae', 'Trae.exe'),
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Trae', 'Trae.exe'),
        r"C:\Program Files\TraeCN\TraeCN.exe",
        r"C:\Program Files (x86)\TraeCN\TraeCN.exe",
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'TraeCN', 'TraeCN.exe')
    ]
    
    found_paths = []
    for path in trae_paths:
        if os.path.exists(path):
            found_paths.append(path)
    
    if found_paths:
        print(f"✅ 找到 {len(found_paths)} 个 Trae 安装路径:")
        for p in found_paths:
            print(f"   - {p}")
    else:
        print("⚠️ 未找到 Trae 安装路径（运行时可手动选择）")
    
    return len(found_paths) > 0

def test_chat_response():
    """测试聊天响应生成"""
    try:
        from ai_floating_ball import TraeFloatingBall
        
        test_messages = [
            "帮我审查代码",
            "我遇到了一个错误",
            "生成一个Python函数",
            "Python列表怎么用"
        ]
        
        print("\n✅ 测试聊天响应:")
        for msg in test_messages:
            # 创建一个临时实例来测试响应
            ball = TraeFloatingBall.__new__(TraeFloatingBall)
            ball.knowledge_base = {
                "python": {
                    "list": "Python列表操作",
                    "dict": "Python字典操作"
                }
            }
            response = ball.generate_response(msg)
            print(f"   问题: {msg}")
            print(f"   响应类型: {'代码' if response.get('code') else '文本'}")
            print()
        
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def main():
    print("🚀 Trae 悬浮球测试套件")
    print("=" * 40)
    
    results = []
    
    print("\n1. 测试导入功能:")
    results.append(test_import())
    
    print("\n2. 测试路径搜索:")
    results.append(test_paths())
    
    print("\n3. 测试聊天响应:")
    results.append(test_chat_response())
    
    print("\n" + "=" * 40)
    passed = sum(results)
    total = len(results)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！")
    else:
        print("⚠️ 部分测试未通过，请检查问题")

if __name__ == "__main__":https://github.com/fgyhk642-arch/trae-floating-ball
    main()