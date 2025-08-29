from lxml.etree import _Element

STEP_DISTANCE = 1


def is_empty(s):
    return s is None or s == ''


def get_xpath(node: _Element):
    if node is None:
        return None
    array = []
    while node.getparent() is not None:
        parent: _Element = node.getparent()
        if not "android.widget.EditText" == node.get('class') and not is_empty(node.get('text')):
            array.append("*[@text=\"" + node.get('text') + "\"]")
            break
        elif not is_empty(node.get('content-desc')):
            array.append("*[@content-desc=\"" + node.get('content-desc') + "\"]")
            break
        elif not is_empty(node.get('resource-id')):
            array.append("*[@resource-id=\"" + node.get('resource-id') + "\"]")
            break
        else:
            index = 0
            for n in parent.getchildren():
                if n is None:
                    continue
                if n.get('class') == node.get('class'):
                    index += 1
                if n == node:
                    break
            array.append(node.get('class') + "[" + str(index) + "]")
        node = parent
    if len(array) == 0:
        return "//" + node.get('classname')
    array.reverse()
    return "//" + "/".join(array)


def find_node_by_xpath(root: _Element, xpath, find_nodes):
    elements = root.xpath(".//*")
    for child in elements:
        if child is None or child.get('visible-to-user') == 'false':
            continue
        child_xpath = get_xpath(child)
        if xpath == child_xpath:
            print("xPath完全匹配找到控件:" + child_xpath)
            find_nodes[0] = child
            return
        if is_xpath_similarity(xpath, child_xpath):
            print("xPath相似控件:" + child_xpath)
            find_nodes[1] = child


def is_xpath_similarity(ori_xpath, curr_xpath):
    if not curr_xpath:
        return False
    ori_xpath_arr = ori_xpath.replace("//", "").replace("id/", "").split("/")
    curr_xpath_arr = curr_xpath.replace("//", "").replace("id/", "").split("/")

    # 1.索引改变 2 层级增加或者减少
    origin_xpath_arr_len = len(ori_xpath_arr)
    curr_xpath_arr_len = len(curr_xpath_arr)
    if abs(origin_xpath_arr_len - curr_xpath_arr_len) > STEP_DISTANCE:
        # 目前最多变化1层
        return False
    min_xpath_arr_len = min(origin_xpath_arr_len, curr_xpath_arr_len)
    start_index = check_first_different_index(ori_xpath_arr, curr_xpath_arr)
    if start_index == min_xpath_arr_len:
        # xpath 完全相同
        return True
    end_index = check_last_different_index(ori_xpath_arr, curr_xpath_arr)

    diff_distance = origin_xpath_arr_len - start_index - end_index
    if start_index > 0 and end_index > 0 and diff_distance <= STEP_DISTANCE:
        # 第一个最后一个类名必须一样
        return True
    return False


def check_first_different_index(origin_xpath_arr, curr_xpath_arr):
    start_index = 0
    min_len = min(len(origin_xpath_arr), len(curr_xpath_arr))
    for i in range(min_len):
        if origin_xpath_arr[i] != curr_xpath_arr[i]:
            break
        start_index += 1
    return start_index


def check_last_different_index(origin_xpath_arr, curr_xpath_arr):
    origin_xpath_arr_len = len(origin_xpath_arr)
    curr_xpath_arr_len = len(curr_xpath_arr)
    min_len = min(origin_xpath_arr_len, curr_xpath_arr_len)
    end_index = 0
    for i in range(min_len):
        if origin_xpath_arr[origin_xpath_arr_len - 1 - i] != curr_xpath_arr[curr_xpath_arr_len - 1 - i]:
            break
        end_index += 1
    return end_index
