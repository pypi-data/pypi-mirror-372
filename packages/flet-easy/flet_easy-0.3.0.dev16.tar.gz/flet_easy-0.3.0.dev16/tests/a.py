import flet as ft
import asyncio


def main(page: ft.Page):
    page.title = "Routes Example"
    history_pages = {}
    counter = ft.TextField(value="0", text_size=50)

    async def method_counter(e):
        for i in range(100):
            counter.value = str(int(counter.value) + 1)
            page.update()
            await asyncio.sleep(1)

    def confirm_route_pop(e):
        print("on_confirm_pop")
        # page.go("/xd")
        e.control.confirm_pop(False)
        page.go("/xd")

    def route_change(e):
        page.views.clear()

        if page.route == "/":
            view = (
                history_pages.get("/")
                if history_pages.get("/")
                else ft.View(
                    "/",
                    [
                        ft.AppBar(title=ft.Text("Flet app"), bgcolor=ft.Colors.GREEN),
                        ft.Button("Visit Store", on_click=lambda _: page.go("/store")),
                        counter,
                        ft.FilledButton("start", on_click=method_counter),
                    ],
                    can_pop=False,
                    on_confirm_pop=confirm_route_pop,
                )
            )
            history_pages[page.route] = view

        if page.route == "/store":
            view = (
                history_pages.get("/store")
                if history_pages.get("/store")
                else ft.View(
                    "/store",
                    [
                        ft.AppBar(title=ft.Text("Store"), bgcolor=ft.Colors.BLUE),
                        ft.Button("Go Home", on_click=lambda _: page.go("/")),
                        counter,
                        ft.FilledButton("start", on_click=method_counter),
                    ],
                    can_pop=False,
                    on_confirm_pop=confirm_route_pop,
                )
            )
            history_pages[page.route] = view

        if page.route == "/xd":
            view = (
                history_pages.get("/xd")
                if history_pages.get("/xd")
                else ft.View(
                    "/xd",
                    [
                        ft.AppBar(title=ft.Text("XD"), bgcolor=ft.Colors.RED),
                        ft.Button("Go Home", on_click=lambda _: page.go("/")),
                        counter,
                        ft.FilledButton("start", on_click=method_counter),
                    ],
                    can_pop=False,
                    on_confirm_pop=confirm_route_pop,
                )
            )
            history_pages[page.route] = view

        page.views.append(view)
        page.update()

    def view_pop(e):
        print("view_pop")
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    page.go(page.route)


ft.app(main)
