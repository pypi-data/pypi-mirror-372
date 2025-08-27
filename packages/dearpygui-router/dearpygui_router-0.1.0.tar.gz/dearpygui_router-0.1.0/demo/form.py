import dearpygui.dearpygui as dpg
import dearpygui_router as router

class FormStep1:
    def __init__(self):
        self.data = {}

    def add_to_context(self):
        print("Render page 1")
        dpg.add_input_text(label="name", tag="s1_name")
        dpg.add_input_text(label="email", tag="s1_email")
        dpg.add_spacer(height=10)
        dpg.add_button(label="Next", width=100, callback=self._on_btn_next)

    def _on_btn_next(self):
        self.data["name"] = dpg.get_value("s1_name")
        self.data["email"] = dpg.get_value("s1_email")
        router.navigate("step2")

class FormStep2:
    def __init__(self):
        self.data = {}

    def add_to_context(self):
        dpg.add_combo(items=["Cat", "Dog", "Gerbil"], label="Pet Type", tag="s2_pet")
        dpg.add_input_int(label="Pet Age", tag="s2_age")
        dpg.add_spacer(height=10)
        dpg.add_button(label="Next", width=100, callback=self._on_btn_next)

    def _on_btn_next(self):
        self.data["petType"] = dpg.get_value("s2_pet")
        self.data["petAge"] = dpg.get_value("s2_age")
        router.navigate("step3")

def summary_page():
    with dpg.group():
        dpg.add_text("Summary of your responses")
        dpg.add_spacer(height=10)

        with router.router():
            with router.screen("you", is_initial=True):
                name = step1.data["name"]
                email = step1.data["email"]
                dpg.add_text("You", color=(30, 220, 30))
                dpg.add_text(f"Your name is {name} and your email is {email}")
                dpg.add_spacer(height=10)
                dpg.add_button(label="Your Pet", width=100, callback=lambda: router.navigate("step3/pet"))

            with router.screen("pet"):
                pet_type = step2.data["petType"]
                age = step2.data["petAge"]
                dpg.add_text("Your Pet", color=(30, 220, 30))
                dpg.add_text(f"You have a pet {pet_type} that is {age} years old")
                dpg.add_spacer(height=10)
                dpg.add_button(label="You", width=100, callback=lambda: router.navigate("step3/you"))

step1 = FormStep1()
step2 = FormStep2()

dpg.create_context()
dpg.create_viewport()
dpg.setup_dearpygui()

with dpg.window(tag="_main_window", label="Router Demo: Form"):
    dpg.add_text("Please fill out this form")
    dpg.add_spacer(height=30)

    with router.router():
        router.add_screen_object("step1", step1, is_initial=True)
        router.add_screen_object("step2", step2)
        router.add_screen_function("step3", summary_page)
    

dpg.show_viewport()
dpg.set_primary_window("_main_window", True)
dpg.start_dearpygui()
dpg.destroy_context()