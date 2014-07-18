from compiler import map


def sem(root):
    Walker().walk(root)
