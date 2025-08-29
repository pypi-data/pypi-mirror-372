#!/usr/bin/env python3
"""
测试Java注释处理功能的修改
验证注释精简和格式转换是否正常工作
"""

import tempfile
import os
from pathlib import Path
import tree_sitter_java as tsjava
from tree_sitter import Language, Parser

# 添加项目根目录到Python路径
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from kengine.code.skeleton.languages.java_handler import JavaHandler


def test_comment_processing():
    """测试注释处理功能"""
    
    # 创建测试用的Java代码，包含各种注释格式
    test_java_code = '''
package com.example.test;

/**
 * 这是一个测试类
 * @author John Doe
 * @date 2024-01-15
 * @version 1.0
 * 用于演示注释处理功能
 * Created by: Developer
 * Last modified: 2024-01-20
 */
public class TestClass {
    
    /**
     * 这是一个测试字段
     * @since 1.0
     * 存储用户名信息
     */
    private String username;
    
    /**
     * 这是一个测试方法
     * @param name 用户名参数
     * @return 返回处理结果
     * @author Jane Smith
     * 执行用户名处理逻辑
     */
    public String processName(String name) {
        return name.toUpperCase();
    }
}
'''
    
    # 设置tree-sitter解析器
    JAVA_LANGUAGE = Language(tsjava.language())
    parser = Parser(JAVA_LANGUAGE)
    
    # 创建JavaHandler实例
    handler = JavaHandler(JAVA_LANGUAGE)
    
    # 解析代码
    tree = parser.parse(bytes(test_java_code, "utf8"))
    
    # 生成骨架
    skeleton = handler.generate_skeleton(tree, test_java_code)
    
    print("生成的Java代码骨架:")
    print("=" * 50)
    print(skeleton)
    print("=" * 50)
    
    # 验证结果
    lines = skeleton.split('\n')
    
    # 检查是否使用了单行注释格式 //
    single_line_comments = [line for line in lines if line.strip().startswith('//')]
    multi_line_comments = [line for line in lines if '/**' in line or '*/' in line]
    
    print(f"\n发现的单行注释数量: {len(single_line_comments)}")
    print(f"发现的多行注释数量: {len(multi_line_comments)}")
    
    # 打印找到的注释
    if single_line_comments:
        print("\n单行注释内容:")
        for comment in single_line_comments:
            print(f"  {comment.strip()}")
    
    if multi_line_comments:
        print("\n多行注释内容:")
        for comment in multi_line_comments:
            print(f"  {comment.strip()}")
    
    # 验证注释是否被正确精简（不应包含@author, @date等标签）
    skeleton_lower = skeleton.lower()
    unwanted_keywords = ['@author', '@date', '@version', 'created by', 'last modified']
    
    found_unwanted = []
    for keyword in unwanted_keywords:
        if keyword in skeleton_lower:
            found_unwanted.append(keyword)
    
    print(f"\n检查是否包含不需要的关键词: {found_unwanted}")
    
    # 验证是否包含有用的描述性文本
    useful_content = ['测试类', '测试字段', '测试方法', '用户名', '处理']
    found_useful = []
    for content in useful_content:
        if content in skeleton:
            found_useful.append(content)
    
    print(f"检查是否保留了有用的描述: {found_useful}")
    
    # 总结测试结果
    print(f"\n测试结果总结:")
    print(f"✓ 使用单行注释格式: {'是' if len(single_line_comments) > 0 else '否'}")
    print(f"✓ 避免多行注释格式: {'是' if len(multi_line_comments) == 0 else '否'}")
    print(f"✓ 过滤不需要的标签: {'是' if len(found_unwanted) == 0 else '否'}")
    print(f"✓ 保留有用的描述: {'是' if len(found_useful) > 0 else '否'}")
    
    return skeleton


if __name__ == "__main__":
    test_comment_processing()