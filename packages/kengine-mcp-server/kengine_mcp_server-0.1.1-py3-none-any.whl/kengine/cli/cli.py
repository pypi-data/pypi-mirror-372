"""
增强的CLI控制器

提供更丰富的命令行参数控制功能，支持多种子命令和向后兼容模式
"""

import argparse
import logging
import sys
from typing import Dict, Any, Optional
from pathlib import Path

from ..core import KnowledgeService
from ..core.types import KnowledgeGenerationRequest
from ..core.enums import ExecuteStep


class EnhancedCLIController:
    """增强的CLI控制器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.knowledge_service = KnowledgeService()
    
    def create_parser(self) -> argparse.ArgumentParser:
        """创建参数解析器"""
        parser = argparse.ArgumentParser(
            description="知识工程系统 - 代码仓库分析与文档生成工具",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        parser.add_argument("--repo_group", required=True, help="代码仓库组名")
        parser.add_argument("--repo_name", required=True, help="代码仓库名称")
        parser.add_argument("--model_name", default="gpt-4.1", help="LLM模型名称")
        parser.add_argument("--prompt_version", help="提示词版本")
        parser.add_argument("--branch", default="master", help="Git分支")
        parser.add_argument("--force_project_type", help="强制指定项目类型")
        parser.add_argument("--execute_step", default="full", help=f"制定执行步骤, 有效值： {ExecuteStep.steps()}")
        parser.add_argument("--specify_document_path", default="", help="指定文档路径")
        
        return parser
    
    
    def validate_project_path(self, path: str) -> bool:
        """验证项目路径，返回布尔值而不是抛出异常"""
        try:
            project_path = Path(path)
            if not project_path.exists():
                return False
            if not project_path.is_dir():
                return False
            return True
        except Exception:
            return False
    
    def _display_success_message(self, args: argparse.Namespace):
        """显示成功消息"""
        print("\n" + "="*60)
        print("🎉 知识工程流程完成！")
        print(f"📁 项目: {args.repo_group}/{args.repo_name}")
        print(f"🔍 查看文档: cd web && npm run dev")
        print(f"🌐 访问地址: http://localhost:3000")
        print("="*60)
    
    def _display_failure_message(self):
        """显示失败消息"""
        print("\n" + "="*60)
        print("❌ 知识工程流程失败")
        print("请查看日志获取详细错误信息")
        print("="*60)
    
    
    def execute_command(self, args: argparse.Namespace) -> int:
        """执行概览生成命令"""
        try:
            # 1. 验证execute_step参数
            if not ExecuteStep.is_valid(args.execute_step):
                valid_steps = ExecuteStep.steps()
                print(f'❌ execute_step参数必须为{valid_steps}中的一个，当前值: {args.execute_step}')
                return 1
            
            # 转换为枚举值
            execute_step_enum = ExecuteStep.from_string(args.execute_step)
            
            # 2. 验证repo_group和repo_name
            if not args.repo_group or not args.repo_name:
                print("❌ repo_group和repo_name参数不能为空")
                return 1
            
            print(f"🚀 开始生成项目概览...")
            print(f"📁 仓库: {args.repo_group}/{args.repo_name}")
            print(f"🤖 使用模型: {args.model_name}")
            if args.prompt_version:
                print(f"🏷️  提示词版本: {args.prompt_version}")
            if args.branch != "master":
                print(f"🌿 Git分支: {args.branch}")
            if args.force_project_type:
                print(f"🎯 强制项目类型: {args.force_project_type}")
            
            
            request = KnowledgeGenerationRequest(
                repo_group=args.repo_group,
                repo_name=args.repo_name,
                model_name=args.model_name,
                prompt_version=args.prompt_version,
                branch=args.branch,
                force_project_type=args.force_project_type,
                execute_step=execute_step_enum,
                specify_document_path=args.specify_document_path
            )
            
            result = self.knowledge_service.generate_knowledge(request)
            
            # 4. 处理结果
            if result.success:
                print(f"\n✅ 项目概览生成成功!")
                print(f"📁 输出路径: {result.output_path}")
                
                # 显示项目信息
                if result.project_type:
                    print(f"🏷️  项目类型: {result.project_type}")
                if result.strategy_used:
                    print(f"⚙️  使用策略: {result.strategy_used}")
                
                # 显示分类结果（如果有）
                if result.classification_result:
                    classification = result.classification_result
                    confidence = classification.get('confidence', 0)
                    print(f"🎯 分类置信度: {confidence}")
                
                # 显示RAG构建结果
                if result.rag_built:
                    print(f"🔍 RAG知识库构建完成")
                
                # 显示概览结果详情
                if result.overview_result and result.overview_result.success:
                    print(f"📊 概览生成完成")
                    if result.overview_result.metadata:
                        metadata = result.overview_result.metadata
                        if 'execution_time' in metadata:
                            print(f"⏱️  生成耗时: {metadata['execution_time']:.2f}秒")
                
                return 0
            else:
                print(f"\n❌ 项目概览生成失败")
                if result.error:
                    print(f"错误信息: {result.error}")
                if result.generate_stage:
                    print(f"失败阶段: {result.generate_stage}")
                
                # 显示警告信息
                if result.warnings:
                    print("\n⚠️  警告信息:")
                    for warning in result.warnings:
                        print(f"  - {warning}")
                
                return 1
                
        except Exception as e:
            self.logger.error(f"执行概览生成命令失败: {e}")
            print(f"\n❌ 概览生成失败: {e}")
            import traceback
            self.logger.error("错误详情:")
            self.logger.error(traceback.format_exc())
            return 1
    
    def run(self, args: Optional[list] = None) -> int:
        """运行CLI控制器"""
        parser = self.create_parser()
        parsed_args = parser.parse_args(args)
        
        # 执行对应的命令
        return self.execute_command(parsed_args)


def main():
    """CLI入口点"""
    controller = EnhancedCLIController()
    sys.exit(controller.run())


if __name__ == "__main__":
    main()