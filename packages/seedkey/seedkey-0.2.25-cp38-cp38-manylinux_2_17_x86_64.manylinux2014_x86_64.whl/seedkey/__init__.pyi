"""
Pybind11 example plugin
-----------------------

.. currentmodule:: seedkey

.. autosummary::
    :toctree: _generate

    seedkey
    activate
"""

def activate(product: str, key: str) -> bool:
    """
    activate

    直接激活许可证函数

    参数:
        product (str): 产品名称，可以是"seedmip"、"seedsat"、"seedsmt"、"seedkcompiler"
        key (str): 激活码

    返回:
        bool: 激活成功返回True，失败返回False

    示例:
        activate("seedmip", "1234567890")
    """
    ...
