"""
分页工具模块
提供通用的分页功能
"""
from typing import List, Dict, Any
from telegram import InlineKeyboardButton


def paginate(items: List[Any], page: int = 1, page_size: int = 5) -> Dict[str, Any]:
    """
    对列表进行分页处理
    
    Args:
        items: 要分页的数据列表
        page: 当前页码（从1开始）
        page_size: 每页显示的数量
    
    Returns:
        包含分页信息的字典：
        {
            'items': 当前页的数据,
            'total': 总数据量,
            'page': 当前页码,
            'total_pages': 总页数,
            'has_prev': 是否有上一页,
            'has_next': 是否有下一页
        }
    """
    total = len(items)
    total_pages = (total + page_size - 1) // page_size  # 向上取整
    
    # 确保页码在有效范围内
    page = max(1, min(page, total_pages if total_pages > 0 else 1))
    
    # 计算切片索引
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    
    return {
        'items': items[start_idx:end_idx],
        'total': total,
        'page': page,
        'total_pages': total_pages,
        'has_prev': page > 1,
        'has_next': page < total_pages
    }


def create_pagination_keyboard(
    page: int,
    total_pages: int,
    callback_prefix: str,
    back_button_text: str = "🏠 返回主菜单",
    back_callback: str = "main_menu"
) -> List[List[InlineKeyboardButton]]:
    """
    创建分页导航按钮
    
    Args:
        page: 当前页码
        total_pages: 总页数
        callback_prefix: 回调数据前缀（如 'lottery_page_'）
        back_button_text: 返回按钮文本
        back_callback: 返回按钮的回调数据
    
    Returns:
        按钮列表
    """
    keyboard = []
    
    # 只有多于1页时才显示分页按钮
    if total_pages > 1:
        nav_buttons = []
        
        # 上一页按钮
        if page > 1:
            nav_buttons.append(
                InlineKeyboardButton(
                    "⬅️ 上一页",
                    callback_data=f"{callback_prefix}{page - 1}"
                )
            )
        
        # 页码指示器
        nav_buttons.append(
            InlineKeyboardButton(
                f"📄 {page}/{total_pages}",
                callback_data="page_info"  # 不响应点击
            )
        )
        
        # 下一页按钮
        if page < total_pages:
            nav_buttons.append(
                InlineKeyboardButton(
                    "➡️ 下一页",
                    callback_data=f"{callback_prefix}{page + 1}"
                )
            )
        
        keyboard.append(nav_buttons)
    
    # 返回按钮
    keyboard.append([InlineKeyboardButton(back_button_text, callback_data=back_callback)])
    
    return keyboard
