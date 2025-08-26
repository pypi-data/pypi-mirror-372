"""
StandardDomTree - 新的DOM树协议定义

这个模块定义了新的标准化DOM树结构，用于统一文档解析结果的格式。
目前解析过程仍基于原有的DOM树结构，然后通过转换方法将其转换为标准格式。

注意：当前解析器仍使用原有的DOM树结构，后续计划将直接解析为StandardDomTree格式。

"""

from typing import List, Optional, Literal, Any, Union
from pydantic import BaseModel, Field, root_validator
import tiktoken

# 布局类型映射表：将旧解析器的布局类型映射到新的标准类型
# 注意：这个映射表是临时的，后续计划统一布局类型定义
layout_type_mapping = {
    "Catalog": "Catalog",
    "Title": "Title",
    "List": "ListItem",
    "Formula": "Formula",
    "Code": "Code",
    "Text": "Text",

    "Figure": "Figure",
    "FigureName": "FigureName",
    "FigureNote": "Text",  # 目前实际解析出来没有

    "Table": "Table",
    "TableName": "TableName",
    "TableNote": "Text",  # 目前实际解析出来没有
}



class SourceFile(BaseModel):
    id: str  # 文件ID，唯一标识符，类型为string
    name: str  # 文件名，文档的名称，类型为string
    type: Optional[str]  # 文件类型，例如：pdf、docx等
    mime_type: Optional[str]  # MIME类型，例如：application/pdf、application/msword等


class StandardPosition(BaseModel):
    bbox: List[float]  # 文档中的矩形坐标信息，例如：[90.1,263.8,101.8,274.3]
    page: int  # 页码


class StandardImage(BaseModel):
    type: Literal["image_url", "image_base64", "image_file"]  # 图片类型约束
    url: Optional[str] = None  # 链接地址
    base64: Optional[str] = None  # 图片base64编码
    file_id: Optional[str] = None  # 上传到file-api的文件ID


class Cell(BaseModel):
    """表格单元格"""
    path: Optional[List[Union[int, List[int]]]] = Field(default_factory=list)  # 单元格路径
    text: Optional[str] = None  # 文本内容
    nodes: Optional[List['StandardNode']] = Field(default_factory=list)


class StandardRow(BaseModel):
    """表格行"""
    cells: List[Cell] = Field(default_factory=list)  # 单元格列表


class StandardBaseElement(BaseModel):
    type: str  # 类型，例如["Text","Title","List","Catalog","Table","Figure","Formula","Code","ListItem"]
    positions: Optional[List[StandardPosition]] = None  # 位置信息，可能跨页所以是个数组


class StandardElement(StandardBaseElement):
    text: Optional[str] = None  # 文本信息，图片ocr的文字


class StandardTableElement(StandardBaseElement):
    name: Optional[str] = None  # 如果类型是Table、Figure为其名字
    description: Optional[str] = None  # 如果类型是Table、Figure为其描述
    rows: List[StandardRow] = Field(default_factory=list)  # 表格行
    
    @root_validator(pre=True)
    def validate_table_type(cls, values):
        """确保只有type='Table'的数据才能创建StandardTableElement"""
        if values.get('type') != 'Table':
            raise ValueError(f"StandardTableElement只能用于type='Table'的数据，当前type='{values.get('type')}'")
        return values


class StandardImageElement(StandardElement):
    name: Optional[str] = None  # 如果类型是Table、Figure为其名字
    description: Optional[str] = None  # 如果类型是Table、Figure为其描述
    image: Optional[StandardImage] = None  # 图片信息
    
    @root_validator(pre=True)
    def validate_image_type(cls, values):
        """确保只有type='Figure'的数据才能创建StandardImageElement"""
        if values.get('type') != 'Figure':
            raise ValueError(f"StandardImageElement只能用于type='Figure'的数据，当前type='{values.get('type')}'")
        return values


class StandardNode(BaseModel):
    source_file: Optional[SourceFile] = None  # 文档来源，表示文档的来源信息
    summary: Optional[str] = None  # 摘要，文档的简要概述
    tokens: Optional[int] = None  # token预估数量，文档中的token数量估计
    path: Optional[List[int]] = Field(default_factory=list)  # 编号的层级信息，例如：1.2.1
    element: Optional[Union[StandardTableElement, StandardImageElement, StandardElement]] = None  # 元素信息，当前节点的元素详情
    children: Optional[List["StandardNode"]] = Field(default_factory=list)  # 子节点信息，当前节点的所有子节点
    


class StandardDomTree(BaseModel):
    root: StandardNode  # 根节点

    def to_markdown(self) -> str:
        """
        将StandardDomTree转换为Markdown格式的字符串

        Returns:
            str: Markdown格式的字符串
        """
        markdown_res = ""

        def _generate_markdown(node: StandardNode, level: int, low_than_text: int = 0) -> str:
            nonlocal markdown_res
            child_low_than_text = 0

            if node.element:
                # 根据不同的type生成Markdown
                if node.element.type == "Figure" and isinstance(node.element, StandardImageElement):
                    # 添加图片名称
                    if node.element.name:
                        markdown_res += f"**{node.element.name}**\n\n"
                    if node.element.image and node.element.image.url:
                        markdown_res += f"![Figure]({node.element.image.url})\n\n"
                    if node.element.text:
                        md_ocr_res = self._convert_to_markdown_quote(node.element.text)
                        markdown_res += f"{md_ocr_res}\n\n"
                    # 添加图片描述
                    if node.element.description:
                        markdown_res += f"*{node.element.description}*\n\n"

                elif node.element.type == "Table" and isinstance(node.element, StandardTableElement):
                    # 添加表格名称
                    if node.element.name:
                        markdown_res += f"**{node.element.name}**\n\n"
                    table_md = self._list_to_html_table(node.element.rows)
                    markdown_res += f"{table_md}\n\n"
                    # 添加表格描述
                    if node.element.description:
                        markdown_res += f"*{node.element.description}*\n\n"

                elif (level <= 6  # 标题必须小于等于6级
                      and (node.element.type in ["Title"]  # 认定为Title 或者 父节点非text的ListItem
                           or (node.element.type in ["ListItem"] and not low_than_text))):
                    # Title只能识别6级，大于6级的按普通文本处理
                    markdown_res += '#' * level + f" {node.element.text}\n\n"
                elif node.element.type in ["Title"]:
                    markdown_res += f"{node.element.text}\n\n"
                elif node.element.type in ["Text"]:
                    markdown_res += f"{node.element.text}\n\n"
                    child_low_than_text = low_than_text + 1  # Text节点的子节点标记
                elif node.element.type in ["ListItem"]:
                    markdown_res += '\t' * (low_than_text - 1) + f"- {node.element.text}\n\n"
                # Formula、Catalog、Code等元素的处理
                else:
                    markdown_res += f"{node.element.text}\n\n"

            for child in node.children:
                _generate_markdown(child, level + 1, child_low_than_text)

        # 从根节点开始生成，跳过根节点本身
        for child in self.root.children:
            _generate_markdown(child, 1, 0)

        return markdown_res

    def _convert_to_markdown_quote(self, text: str) -> str:
        """将文本转换为markdown引用格式"""
        if not text:
            return ""
        lines = text.split('\n')
        quoted_lines = ['> ' + line for line in lines]
        return '\n'.join(quoted_lines)

    def _list_to_html_table(self, rows: List[StandardRow]) -> str:
        """将表格行转换为HTML表格"""
        if not rows:
            return ""

        html_text = "<table>"
        for row in rows:
            html_text += "<tr>"
            for cell in row.cells:
                # 从path中提取rowspan和colspan信息
                if len(cell.path) >= 4:
                    start_row, end_row, start_col, end_col = cell.path[:4]
                    rowspan = end_row - start_row + 1
                    colspan = end_col - start_col + 1
                else:
                    rowspan = colspan = 1

                cell_text = cell.text or ""
                html_text += f"<td rowspan='{rowspan}' colspan='{colspan}'>{cell_text}</td>"
            html_text += "</tr>"
        html_text += "</table>"
        return html_text

    @classmethod
    def from_domtree_dict(cls, domtree: dict, file_info):
        """
        将旧的DOM树字典格式转换为新的StandardDomTree格式

        注意：这是临时的转换方法，用于兼容现有的解析器输出。
        后续计划将解析器直接输出StandardDomTree格式，避免这个转换步骤。

        Args:
            domtree: 源DOM树字典对象（旧格式）
            file_info: 文件信息字典，包含文件ID、文件名等信息
        Returns:
            StandardDomTree: 转换后的标准化DOM树对象
        """
        # 创建 SourceFile 对象
        source_file = None
        if file_info:
            source_file = SourceFile(
                id=file_info['id'],
                name=file_info['filename'],
                type=file_info.get('type'),
                mime_type=file_info.get('mime_type')
            )

        # 转换根节点，构建树结构（不计算path）
        standard_root = cls._from_domtree_nodes(domtree.get('root'), source_file)

        return cls(root=standard_root)

    @classmethod
    def _from_domtree_nodes(cls, node: dict, source_file: SourceFile) -> StandardNode:
        """
        处理所有节点
        """
        # 根节点，创建一个空的 StandardNode
        standard_root_node = StandardNode(
            source_file=source_file,
            summary="",
            tokens=0,  # 先设置为 0，后面再计算
            path=None,
            element=None,
            children=[]
        )

        # 递归处理子节点
        for child in node.get('child', []):
            standard_child = cls._from_domtree_node_to_base_info(child)  # 不传递path参数
            if standard_child:  # 确保子节点不为 None
                standard_root_node.children.append(standard_child)

        # 处理 FigureName 和 TableName 节点（合并节点）
        cls._process_special_nodes(standard_root_node)

        # 计算所有节点的path
        cls._calculate_paths(standard_root_node)

        # 计算 token 数量：子节点 token 数量之和
        tokens = 0
        for child in standard_root_node.children:
            tokens += child.tokens

        # 设置 token 数量
        standard_root_node.tokens = tokens

        return standard_root_node

    @classmethod
    def _calculate_paths(cls, node: StandardNode, parent_path: List[int] = None):
        """
        计算所有节点的path

        Args:
            node: 当前处理的节点
            parent_path: 父节点的path
        """
        if parent_path is None:
            parent_path = []

        # 为子节点计算path
        for i, child in enumerate(node.children, start=1):
            child_path = parent_path + [i]
            child.path = child_path

            # 递归计算子节点的path
            cls._calculate_paths(child, child_path)

    @classmethod
    def _process_special_nodes(cls, node: StandardNode):
        """
        处理特殊节点（FigureName 和 TableName）

        注意：这是临时的处理逻辑，用于处理旧解析器输出的特殊节点类型。
        后续计划将解析器直接输出正确的节点结构，避免这种后处理。

        Args:
            node: 当前处理的节点
        """
        if not node or not node.children:
            return

        # 创建一个新的子节点列表，用于存储处理后的子节点
        new_children = []
        i = 0

        while i < len(node.children):
            current = node.children[i]

            # 检查当前节点是否为 FigureName 或 TableName
            if current.element and current.element.type in ['FigureName', 'TableName']:
                target_type = 'Figure' if current.element.type == 'FigureName' else 'Table'
                merged = False

                # 检查前一个节点
                if i > 0:
                    prev_sibling = node.children[i - 1]
                    # 找到对应类型的前一个兄弟节点，合并节点
                    merged = ( prev_sibling.element and prev_sibling.element.type == target_type and
                               cls._merge_nodes(prev_sibling, current, target_type))

                # 如果没有与前一个节点合并，检查后一个节点
                if not merged and i < len(node.children) - 1:
                    next_sibling = node.children[i + 1]
                    # 找到对应类型的后一个兄弟节点，合并节点
                    merged = (next_sibling.element and next_sibling.element.type == target_type and
                              cls._merge_nodes(next_sibling, current, target_type))

                # 如果没有找到对应类型的兄弟节点，将当前节点类型改为 Text
                if not merged:
                    current.element.type = 'text'
                    new_children.append(current)
            else:
                new_children.append(current)

            i += 1

        # 更新子节点列表
        node.children = new_children

        # 递归处理子节点
        for child in node.children:
            cls._process_special_nodes(child)

    @classmethod
    def _merge_nodes(cls, target_node: StandardNode, source_node: StandardNode, node_type: str) -> bool:
        """
        合并两个节点，将source_node的信息合并到target_node中

        Args:
            target_node: 目标节点（Figure或Table节点）
            source_node: 源节点（FigureName或TableName节点）
            node_type: 节点类型（'Figure'或'Table'）

        Returns:
            bool: 是否成功合并
        """
        # 定义节点类型与元素类型的映射
        type_element_mapping = {
            'Figure': StandardImageElement,
            'Table': StandardTableElement
        }

        can_merge = (node_type in type_element_mapping and
            isinstance(target_node.element, type_element_mapping[node_type]))

        # 检查节点类型是否支持且目标节点元素类型匹配
        if can_merge:
            # 将源节点的文本作为目标节点的 name
            target_node.element.name = source_node.element.text
            # 更新 tokens 计数
            target_node.tokens += source_node.tokens
            # 将源节点的位置添加到目标节点中
            target_node.element.positions += source_node.element.positions

        return can_merge

    @classmethod
    def _from_domtree_node_to_base_info(cls, node: dict) -> Optional[StandardNode]:
        """
        将单个旧格式Node转换为StandardNode

        注意：这是临时的转换方法，用于处理旧解析器输出的节点格式。
        后续计划将解析器直接输出StandardNode格式，避免这种转换。

        Args:
            node: 源Node对象（旧格式字典）
        Returns:
            StandardNode: 转换后的标准化节点对象
        """
        if not node:
            return

        element = node['element']

        text = ""
        # 映射的类型
        element_type = layout_type_mapping.get(element['layout_type'], "Text")  # 默认类型为 text
        positions = [StandardPosition(bbox=element['bbox'], page=element['page_num'][0])]  # 位置列表，目前page_num元素个数只会是1个

        standard_node = None
        if element_type == "Figure":
            # 处理图片信息
            image = None
            text = element.get('image_ocr_result', '')
            if 'image_link' in element and element['image_link']:
                image = StandardImage(
                    type="image_url",
                    url=element['image_link']
                )

            # 创建StandardImageElement实例
            image_element = StandardImageElement(
                type=element_type,
                positions=positions,
                name="",
                description="",
                text=text,
                image=image,
            )
            
            # 使用construct方法跳过validator，保持正确的element类型
            standard_node = StandardNode.construct(
                summary="",
                tokens=0,  # 先设置为 0，后面再计算
                path=[],  # 初始化为空列表，后续再计算
                element=image_element,
                children=[]
            )
        elif element_type == "Table":
            rows = []
            cell_texts = []  # 收集所有单元格的文本，用于计算 token 数量
            if 'rows' in element:
                for row_data in element['rows']:
                    cells = []
                    if 'cells' in row_data:
                        for cell_data in row_data['cells']:
                            cell_text = cell_data.get('text', '')
                            cell_texts.append(cell_text)
                            # 不计算cell_path，后续再计算
                            cell = Cell(
                                path=[cell_data['start_row'], cell_data['end_row'], cell_data['start_col'],
                                      cell_data['end_col']],
                                text=cell_text,
                                # 目前只会有一个元素,且是Text类型，Path重新从头编号，相对cell是root
                                nodes=[StandardNode(summary="", tokens=cls.count_tokens(cell_text), path=[1], children=[],
                                                    element=StandardElement(
                                                        type='Text',
                                                        positions=[],
                                                        text=cell_text
                                                    )
                                                    )]
                            )
                            cells.append(cell)
                    # 使用 StandardRow 的构造函数创建行
                    row = StandardRow(cells=cells)
                    rows.append(row)

            # 将所有单元格的文本合并，用于计算 token 数量
            text = " ".join(cell_texts)

            # 创建StandardTableElement实例
            table_element = StandardTableElement(
                type=element_type,
                positions=positions,
                name="",
                description="",
                rows=rows
            )
            
            # 使用construct方法跳过validator，保持正确的element类型
            standard_node = StandardNode.construct(
                summary="",
                tokens=0,  # 先设置为 0，后面再计算
                path=[],  # 初始化为空列表，后续再计算
                element=table_element,
                children=[]
            )
        else:
            text = element.get('text', '')
            standard_node = StandardNode(
                summary="",
                tokens=0,  # 先设置为 0，后面再计算
                path=[],  # 初始化为空列表，后续再计算
                element=StandardElement(
                    type=element_type,
                    positions=positions,
                    text=text
                ),
                children=[]
            )

        # 递归处理子节点
        if 'child' in node:
            for child in node['child']:
                standard_child = cls._from_domtree_node_to_base_info(child)
                if standard_child:  # 确保子节点不为 None
                    standard_node.children.append(standard_child)

        # 计算 token 数量：自身 text 的 token 数量 + 子节点 token 数量
        tokens = cls.count_tokens(text)
        for child in standard_node.children:
            tokens += child.tokens

        # 设置 token 数量
        standard_node.tokens = tokens

        return standard_node

    @classmethod
    def count_tokens(cls, text: str) -> int:
        """
        计算文本的token数量

        Args:
            text: 要计算的文本

        Returns:
            int: token数量
        """
        model = "gpt-4" # 使用模型默认为gpt-4
        if not text:
            return 0
        encoding = tiktoken.encoding_for_model(model)
        tokens = encoding.encode(text)
        # 计算标记列表的长度，即标记的数量
        token_count = len(tokens)
        # 返回标记的数量
        return token_count


# 更新forward references
StandardNode.update_forward_refs()
Cell.update_forward_refs()