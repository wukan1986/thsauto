from lxml import etree


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
        self._curr_hierarchy = self._d.dump_hierarchy()
        self._root = etree.fromstring(self._curr_hierarchy.encode('utf-8'))

        # 处理后，才能与uiautomator2的查询语句完全一样
        for node in self._root.xpath("//node"):
            node.tag = node.attrib.pop("class", "node")

    def same_hierarchy(self) -> bool:
        """两次的层次是否相同"""
        if self._last_hierarchy is None:
            return False
        if self._curr_hierarchy is None:
            return False
        # 使用后半部分进行比较，前半部分可能有时间更新而导致不同
        return self._last_hierarchy[len(self._last_hierarchy) // 2:] == self._curr_hierarchy[len(self._curr_hierarchy) // 2:]

    def xpath(self, _path: str):
        """返回xpath匹配的结果"""
        return self._root.xpath(_path)
