import re


def fix_mermaid(markdown: str) -> str: 
    """
    Fixes mermaid code blocks in markdown.
    mermaid语法错误有如下几种
    mermaid语法问题： 
问题1： 中文需要添加双引号， 避免被错误解析
错误案例：
```mermaid 
erDiagram
    SHIPMENT_ORDER ||--o{ DELIVERY : 包含
    DELIVERY ||--o{ DELIVERY_DETAIL : 包含
    DELIVERY_DETAIL }o--|| CARTON : 关联
    SHIPMENT_ORDER ||--o{ ORDER_LINE : 包含
    CARTON ||--o{ CARTON_DETAIL : 包含
    SHIPMENT_ORDER ||--o{ PACKAGE : 自动打包
```
正确的应该是：

```mermaid
erDiagram
    SHIPMENT_ORDER ||--o{ DELIVERY : "包含"
    DELIVERY ||--o{ DELIVERY_DETAIL : "包含"
    DELIVERY_DETAIL }o--|| CARTON : "关联"
    SHIPMENT_ORDER ||--o{ ORDER_LINE : "包含"
    CARTON ||--o{ CARTON_DETAIL : "包含"
    SHIPMENT_ORDER ||--o{ PACKAGE : "自动打包"
```

问题2： 省略号问题， 在mermaid中出现省略号，导致语法错误

错误案例：
```mermaid
erDiagram
    LaneDensityList ||--o{ LaneDensity : "包含"
    LaneDensity {
        String warehouseNo
        String laneNo
        String pickerNo
        Integer densityValue
        Integer operateStatusEnum
        ...
    }
```
应该修复为:
erDiagram
    LaneDensityList ||--o{ LaneDensity : "包含"
    LaneDensity {
        String warehouseNo
        String laneNo
        String pickerNo
        Integer densityValue
        Integer operateStatusEnum
    }
```

问题3： 正常的字段展示， 出现了 类似java单行注释的内容 //
错误案例： 
```mermaid
erDiagram
    LaneDensityList ||--o{ LaneDensity : "包含"
    LaneDensity {
        String warehouseNo
        String laneNo
        String pickerNo
        Integer densityValue
        Integer operateStatusEnum
        // 参考xx
    }
```
应该去掉注释一行的内容修复为：
```mermaid
erDiagram
    LaneDensityList ||--o{ LaneDensity : "包含"
    LaneDensity {
        String warehouseNo
        String laneNo
        String pickerNo
        Integer densityValue
        Integer operateStatusEnum
    }
```
    :param markdown 输入的markdown文本
    :return 修复后的markdown文件
    """
    if not markdown:
        return markdown
    
    # 使用正则表达式匹配所有mermaid代码块
    mermaid_pattern = r'```mermaid\n(.*?)\n```'
    
    def fix_mermaid_block(match):
        """修复单个mermaid代码块的内容"""
        mermaid_content = match.group(1)
        
        # 按行处理mermaid内容
        lines = mermaid_content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # 问题3：移除Java单行注释 - 以//开头的行（忽略前导空格）
            if re.match(r'^\s*//.*', line):
                # 跳过注释行，不添加到结果中
                continue
            
            # 问题2：移除包含省略号的行
            if '...' in line:
                # 跳过包含省略号的行
                continue
            
            # 问题1：为中文关系标签添加双引号
            # 匹配ER图关系语法：实体1 关系符号 实体2 : 中文标签
            chinese_relation_pattern = r'(\s*\w+\s+[|}{o\-]+\s+\w+\s*:\s*)([^"\s][^"]*[^\s"])(\s*)$'
            match_relation = re.match(chinese_relation_pattern, line)
            
            if match_relation:
                prefix = match_relation.group(1)  # 关系前缀部分
                label = match_relation.group(2)   # 中文标签
                suffix = match_relation.group(3)  # 后缀空格
                
                # 检查标签是否包含中文字符且未被双引号包围
                if re.search(r'[\u4e00-\u9fff]', label) and not (label.startswith('"') and label.endswith('"')):
                    # 为中文标签添加双引号
                    line = f'{prefix}"{label}"{suffix}'
            
            fixed_lines.append(line)
        
        # 重新组装修复后的mermaid代码块
        fixed_content = '\n'.join(fixed_lines)
        return f'```mermaid\n{fixed_content}\n```'
    
    # 使用re.DOTALL标志使.匹配换行符
    fixed_markdown = re.sub(mermaid_pattern, fix_mermaid_block, markdown, flags=re.DOTALL)
    
    return fixed_markdown