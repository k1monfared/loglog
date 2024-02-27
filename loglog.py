import os
import re


class TreeNode(object):
    def __init__(self, name="", children=None, data=""):
        self.name = name
        self.children = []
        self.data = data
        self.get_type()
        if children is not None:
            for child in children:
                self.add_child(child)

    def __repr__(self):
        return self.name

    def add_child(self, node):
        assert isinstance(node, TreeNode)
        self.children.append(node)

    def get_type(self):
        if self.is_todo():
            self.type = "todo"
            self.todo_status()
        else:
            self.type = "regular"
        # regular item
        regex = re.compile("- *")
        if re.match(regex, self.data.lower()):
            self.data = self.data[1:].strip()

    def is_todo(self):
        regex1 = re.compile("^\[.\]")
        regex2 = re.compile("^\[\]")
        if re.match(regex1, self.data.lower()) or re.match(regex2, self.data.lower()):
            return True
        else:
            return False

    def todo_status(self):
        if self.data.lower().startswith("[]"):
            done = False
            data = self.data[2:].strip()
        elif self.data.lower().startswith("[ ]"):
            done = False
            data = self.data[3:].strip()
        elif self.data.lower().startswith("[x]"):
            done = True
            data = self.data[3:].strip()
        else:
            done = None
            data = self.data[3:].strip()
        self.status = done
        # I'll probably need to extend this status to a dict with different statuses for different things. At the moment I don't know what other statuses I might need though, so I'm living it as only for todo items.
        self.data = data


class Tree(object):
    def __init__(self):
        pass


def build_tree_from_text(text_lines):
    root = TreeNode(name="")  # Create a root node
    root.type = "root"
    stack = [(-1, root)]  # Stack to keep track of parent nodes at each level

    for line in text_lines:
        line = line.replace("\t", " " * 4)
        depth = 0
        while line.startswith(" " * 4):
            depth += 1
            line = line[4:]
        if len(line.strip()):
            while stack and depth <= stack[-1][0]:
                stack.pop()
            if stack:
                parent_depth, parent = stack[-1]
                node_numbering = parent.name + str(len(parent.children)) + "."
                node = TreeNode(name=node_numbering, data=line)
                parent.add_child(node)  # Add node as a child of the parent
            stack.append((depth, node))

    return root


def get_node(root, address):
    adr = [int(a) for a in address.split(".") if a != ""]
    parent = root
    while len(adr):
        node = parent.children[adr[0]]
        adr = adr[1:]
        parent = node
    return node


def print_tree(node, depth=0, numbered=False, decor="type"):
    if numbered:
        num_str = f"{node.name} "
    else:
        num_str = ""
    # decorate start of line
    line_start = decor
    if decor == "type":
        if node.type == "todo":
            if node.status == True:
                line_start = "[x] "
            elif node.status == False:
                line_start = "[] "
            else:
                line_start = "[?] "
        elif node.type == "regular":
            line_start = "- "
    # do not print root
    if node.type == "root":
        pass
    # print all children
    else:
        print_str = f"{' ' * 4 * (depth - 1)}{line_start}{num_str}{node.data}"
        print(print_str)
    for child in node.children:
        print_tree(child, depth + 1, numbered=numbered, decor=decor)


def build_tree_from_file(file_path):
    with open(file_path, "r") as file:
        text_lines = file.readlines()
    root = build_tree_from_text(text_lines)
    root.data = file_path
    return root
