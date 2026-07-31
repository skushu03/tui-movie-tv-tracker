# class Header(Placeholder):
#     DEFAULT_CSS = """
#     Header {
#         height: 2;
#         dock: top;
#     }
#     """
#
#
# class Footer(Placeholder):
#     DEFAULT_CSS = """
#     Footer {
#         height: 2;
#         dock: bottom;
#     }
#     """

# class PaneContainer(Horizontal):
#     pass
#
#
# class Item(Static):
#     # DEFAULT_CSS = """
#     # Item {
#     #     height: 4;
#     #     width: 1fr;
#     # }
#     # """
#     pass
#
#
# class Column(VerticalScroll):
#     DEFAULT_CSS = """
#     Column {
#             height:1fr;
#             width: 1fr;
#             margin: 0 10;
#             background: transparent;
#     }
#     """
#
#     def compose(self):
#         for num in range(1, 20):
#             yield Item(id=f"Item{num}")
