from compiler import ast


def sem(root):
    Walker().walk(root)
