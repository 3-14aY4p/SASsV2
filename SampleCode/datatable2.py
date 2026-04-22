# import flet as ft


# def _cell(label: str, color: str = ft.Colors.SURFACE_CONTAINER_HIGHEST) -> ft.DataCell:
#     return ft.DataCell(
#         ft.Container(
#             width=90,
#             height=32,
#             alignment=ft.Alignment.CENTER,
#             bgcolor=color,
#             border=ft.Border.all(1, ft.Colors.BLACK_26),
#             content=ft.Text(label, size=12, weight=ft.FontWeight.W_600),
#         )
#     )


# def main(page: ft.Page):
#     page.scroll = ft.ScrollMode.AUTO
#     page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
#     page.theme_mode = ft.ThemeMode.DARK

#     def update_spacing() -> None:
#         table.horizontal_margin = horizontal_margin_slider.value
#         table.column_spacing = column_spacing_slider.value
#         table.update()

#     def handle_spacing_change(_: ft.Event[ft.Slider]) -> None:
#         update_spacing()

#     def set_preset(horizontal_margin: float, column_spacing: float) -> None:
#         horizontal_margin_slider.value = horizontal_margin
#         column_spacing_slider.value = column_spacing
#         horizontal_margin_slider.update()
#         column_spacing_slider.update()
#         update_spacing()

#     horizontal_margin_slider = ft.Slider(
#         min=0,
#         max=40,
#         divisions=40,
#         value=16,
#         label="{value}",
#         on_change=handle_spacing_change,
#     )
#     column_spacing_slider = ft.Slider(
#         min=0,
#         max=40,
#         divisions=40,
#         value=16,
#         label="{value}",
#         on_change=handle_spacing_change,
#     )

#     table = ft.DataTable(
#         border=ft.Border.all(1, ft.Colors.ON_SURFACE_VARIANT),
#         horizontal_margin=horizontal_margin_slider.value,
#         column_spacing=column_spacing_slider.value,
#         horizontal_lines=ft.BorderSide(1, ft.Colors.ON_SURFACE_VARIANT),
#         vertical_lines=ft.BorderSide(1, ft.Colors.ON_SURFACE_VARIANT),
#         heading_row_height=40,
#         data_row_min_height=40,
#         data_row_max_height=40,
#         columns=[
#             ft.DataColumn(label="Col A"),
#             ft.DataColumn(label="Col B"),
#             ft.DataColumn(label="Col C"),
#         ],
#         rows=[
#             ft.DataRow(cells=[_cell("A1"), _cell("B1"), _cell("C1")]),
#             ft.DataRow(cells=[_cell("A2"), _cell("B2"), _cell("C2")]),
#         ],
#     )

#     page.appbar = ft.AppBar(title="DataTable spacing")
#     page.add(
#         ft.SafeArea(
#             content=ft.Column(
#                 horizontal_alignment=ft.CrossAxisAlignment.CENTER,
#                 controls=[
#                     ft.Container(
#                         width=520,
#                         padding=12,
#                         border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
#                         border_radius=8,
#                         content=ft.Column(
#                             horizontal_alignment=ft.CrossAxisAlignment.CENTER,
#                             controls=[
#                                 ft.Text("horizontal_margin (outer edges)"),
#                                 horizontal_margin_slider,
#                                 ft.Text("column_spacing (between columns)"),
#                                 column_spacing_slider,
#                                 ft.Row(
#                                     wrap=True,
#                                     controls=[
#                                         ft.FilledButton(
#                                             "Reset",
#                                             on_click=lambda _: set_preset(16, 16),
#                                         ),
#                                         ft.OutlinedButton(
#                                             "Compact preset",
#                                             on_click=lambda _: set_preset(0, 0),
#                                         ),
#                                         ft.OutlinedButton(
#                                             "Spacious preset",
#                                             on_click=lambda _: set_preset(24, 32),
#                                         ),
#                                     ],
#                                 ),
#                             ],
#                         ),
#                     ),
#                     table,
#                 ],
#             ),
#         )
#     )


# if __name__ == "__main__":
#     ft.run(main)

import flet as ft


def main(page: ft.Page):
    inventory_items = [
        {"id": 1, "name": "Alpha", "qty": 4},
        {"id": 2, "name": "Bravo", "qty": 9},
        {"id": 3, "name": "Charlie", "qty": 2},
        {"id": 4, "name": "Delta", "qty": 6},
        {"id": 5, "name": "Echo", "qty": 3},
        {"id": 6, "name": "Foxtrot", "qty": 8},
        {"id": 7, "name": "Golf", "qty": 1},
        {"id": 8, "name": "Hotel", "qty": 7},
        {"id": 9, "name": "India", "qty": 5},
        {"id": 10, "name": "Juliet", "qty": 10},
    ]
    displayed_items = list(inventory_items)
    selected_item_ids: set[int] = {1, 3, 5}

    sort_key_for_column = {
        0: lambda item: str(item["name"]).lower(),
        1: lambda item: int(item["qty"]),
    }

    def build_rows(items: list[dict[str, int | str]]) -> list[ft.DataRow]:
        return [
            ft.DataRow(
                selected=item["id"] in selected_item_ids,
                on_select_change=handle_row_selection_change,
                data=item["id"],
                cells=[
                    ft.DataCell(ft.Text(item["name"])),
                    ft.DataCell(ft.Text(str(item["qty"]))),
                ],
            )
            for item in items
        ]

    def refresh_table_rows() -> None:
        table.rows = build_rows(displayed_items)
        table.update()

    def handle_row_selection_change(e: ft.Event[ft.DataRow]) -> None:
        row = e.control
        item_id = row.data
        is_selected = e.data

        if is_selected:
            selected_item_ids.add(item_id)
        else:
            selected_item_ids.discard(item_id)

        row.selected = is_selected
        row.update()

    def handle_select_all(e: ft.Event[ft.DataTable]) -> None:
        if e.data:
            selected_item_ids.update(int(item["id"]) for item in displayed_items)
        else:
            selected_item_ids.clear()

        refresh_table_rows()

    def handle_column_sort(e: ft.DataColumnSortEvent) -> None:
        displayed_items.sort(
            key=sort_key_for_column[e.column_index],
            reverse=not e.ascending,
        )

        table.sort_column_index = e.column_index
        table.sort_ascending = e.ascending
        refresh_table_rows()

    table = ft.DataTable(
        width=700,
        bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
        border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
        border_radius=10,
        vertical_lines=ft.border.BorderSide(1, ft.Colors.OUTLINE_VARIANT),
        horizontal_lines=ft.border.BorderSide(1, ft.Colors.OUTLINE_VARIANT),
        sort_column_index=0,
        sort_ascending=True,
        heading_row_color=ft.Colors.SURFACE_CONTAINER_HIGHEST,
        heading_row_height=100,
        data_row_color={
            ft.ControlState.HOVERED: ft.Colors.with_opacity(0.08, ft.Colors.PRIMARY),
            ft.ControlState.SELECTED: ft.Colors.with_opacity(0.14, ft.Colors.PRIMARY),
        },
        show_checkbox_column=True,
        on_select_all=handle_select_all,
        divider_thickness=1,
        column_spacing=200,
        columns=[
            ft.DataColumn(
                label=ft.Text("Item"),
                on_sort=handle_column_sort,
            ),
            ft.DataColumn(
                label=ft.Text("Quantity"),
                tooltip="Numeric quantity",
                numeric=True,
                on_sort=handle_column_sort,
            ),
        ],
        rows=build_rows(displayed_items),
    )

    page.add(
        ft.SafeArea(
            content=table,
        )
    )


if __name__ == "__main__":
    ft.run(main)