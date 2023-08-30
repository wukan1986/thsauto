from lxml import etree
from uiautomator2 import UiObject


def center(text: str):
    # {"x":80,"y":834,"width":280,"height":88}
    # '[80,834][360,922]'
    x1, y1, x2, y2 = eval(text.replace('][', ','))
    return (x1 + x2) // 2, (y1 + y2) // 2


class XPath:
    def __init__(self, d: 'uiautomator2.Device') -> None:
        self._d = d
        self._last_hierarchy = None
        self._curr_hierarchy = None
        self._root = None

    def dump_hierarchy(self) -> None:
        """dump层次，并初始化xpath"""
        # 记录上次的层次，方便比较是否变更
        self._last_hierarchy = self._curr_hierarchy
        self._curr_hierarchy = self._d.dump_hierarchy(compressed=False, pretty=False)
        self._root = etree.fromstring(self._curr_hierarchy.encode('utf-8'))

        # 处理后，才能与uiautomator2的查询语句完全一样
        for node in self._root.xpath("//node"):
            node.tag = node.attrib.pop("class", "node")

        return self._curr_hierarchy

    def same_hierarchy(self) -> bool:
        """两次的层次是否相同"""
        if self._last_hierarchy is None:
            return False
        if self._curr_hierarchy is None:
            return False
        # 使用后半部分进行比较，前半部分可能有时间更新而导致不同
        return self._last_hierarchy[len(self._last_hierarchy) // 2:] == self._curr_hierarchy[len(self._curr_hierarchy) // 2:]

    def xpath(self, path: str):
        """返回xpath匹配的结果"""
        return self._root.xpath(path)

    def exists(self, path):
        return len(self.xpath(path)) > 0

    def click_by_path(self, path: str):
        """点击对应位置控件

        Parameters
        ----------
        path

        Notes
        -----
        需要提前`dump_hierarchy`

        Examples
        --------
        >>> x = XPath(d)
        >>> x.dump_hierarchy()
        >>> x.click_by_path('//*[@resource-id="com.hexin.plat.android:id/ok_btn"]/@bounds')

        """
        """通过xpth来点击"""
        # 需要取按钮位置
        if not path.endswith('/@bounds'):
            path += '/@bounds'
        # 这里有约100~150ms的耗时，能不能更快?
        self.click_by_point(*center(self.xpath(path)[0]))

    def click_by_point(self, x, y):
        self._d.jsonrpc.click(x, y)

    def set_text(self, obj: UiObject, text: str):
        """设置文本

        Parameters
        ----------
        obj: UiObject
        text: str

        Notes
        -----
        跳过了等待过程

        Examples
        --------
        >>> x = XPath(d)
        >>> node = d(resourceId="com.hexin.plat.android:id/stockvolume").child(className="android.widget.EditText")
        >>> x.set_text(node, '123')

        """
        self._d.jsonrpc.setText(obj.selector, text)
