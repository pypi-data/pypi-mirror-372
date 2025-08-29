# 描述

一个基于 JSON 文件的键-值存储类。它提供了一种方便的方法来操作 JSON 文件，与操作 Python 字典类似，但每次修改后都会自动进行持久化。

# 作者

姓名: 许灿标

作者相关链接: [主页](https://lcctoor.com/) \| [Github](https://github.com/lcctoor) \| [PyPi](https://pypi.org/user/lcctoor) \| [微信](https://lcctoor.com/cdn/wechat_qrc.jpg) \| [邮箱](mailto:lcctoor@outlook.com) \| [捐赠](https://lcctoor.com/cdn/donation_qrc_0rmb.jpg)

# 教程

## 安装或更新

```
pip install --upgrade arts
```

## 导入

```python
from arts import Dict_file
```

## 初始化

首先，初始化一个实例：

```python
stock = Dict_file(rf'C:\bpath\downloads\ig_test.json')
```

## 增加键

要增加一个键，只需像操作字典那样赋值：

```python
stock['hat'] = 10
stock['shoe'] = 20
stock['jacket'] = 30
```

## 更新键

更新一个键的方法与增加一个键的方法相同:

```python
stock['jacket'] = 31
```

## 查询键

要查询键的值，只需像操作字典那样：

```python
jacket_count = stock['jacket']
```

如果该键不存在，此操作会抛出一个 `KeyError` 。为避免错误，你可以使用 `get` 方法：

```python
mouse_count = stock.get('mouse', default=0)
```

## 删除键

使用 `pop` 方法删除指定的键并返回其值：

```python
shoe_count = stock.pop('shoe')
```

如果指定的键不存在，`pop` 会抛出一个 `KeyError` 。如果你想避免这个错误并在键不存在时返回一个默认值，可以这样做：

```python
mouse_count = stock.pop('mouse', 0)
```
