import customtkinter

# Appearance와 테마 설정
customtkinter.set_appearance_mode("system")  # Modes: "system", "light", "dark"
customtkinter.set_default_color_theme("blue")  # Themes: "blue", "dark-blue", "green"

# 앱 초기화
app = customtkinter.CTk()
app.geometry("600x400")
app.title("Windows Application with CustomTkinter")

# 라벨 추가
label = customtkinter.CTkLabel(
    master=app, 
    text="Hello, Windows!", 
    text_color="white", 
    font=("Arial", 24)
)
label.pack(pady=20)

# 버튼 추가
def on_button_click():
    label.configure(text="Button Clicked!")

button = customtkinter.CTkButton(
    master=app, 
    text="Click Me", 
    command=on_button_click
)
button.pack(pady=20)

# 입력창 추가
entry = customtkinter.CTkEntry(
    master=app, 
    placeholder_text="Type something..."
)
entry.pack(pady=10)

# 스위치 추가
switch = customtkinter.CTkSwitch(
    master=app, 
    text="Toggle Theme",
    command=lambda: customtkinter.set_appearance_mode("dark" if switch.get() else "light")
)
switch.pack(pady=10)

# 앱 실행
app.mainloop()
