import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageDraw, ImageFont

root = tk.Tk()
root.title("Meme Generator")
root.geometry('1280x720')

# Frames
sidebar = tk.Frame(
    root,
    bg='#1a1a2e',
    width=240
)

sidebar.pack(
    side='left',
    fill='y'
)
sidebar.pack_propagate(False)

title = tk.Label(
    sidebar,
    text="MEME STUDIO",
    bg="#ef476f",
    font=("Segoe UI", 22, "italic",'bold'),
    fg='white',
    bd=0,
    padx=20,
    pady=20
    )

title.pack(pady=30)


def divider(parent):
    tk.Frame(parent, bg="#23395d", height=1).pack(fill="x", padx=20, pady=10)

editor_frame = tk.Frame(
    root,
    bg="#05051a"
)

editor_frame.pack(
    side="left",
    fill="both",
    expand=True
)

canvas = tk.Canvas(
        editor_frame,
        bg="#05051a",
        highlightthickness=0
    )
canvas.pack(fill='both', expand=True)

placeholder = canvas.create_text(
    0, 0,
    text="Open an image to start",
    fill="#8d99ae",
    font=("Segoe UI", 12)
)

def reposition_placeholder(event):
    if 'original_image' not in globals():
        canvas.coords(placeholder, event.width // 2, event.height // 2)

canvas.bind('<Configure>', reposition_placeholder)

# Necessary tools
text_items = []
selected_text = None
selected_box = None
selected_handle = None
resize_mode = False

selected_font = tk.StringVar()
selected_font.set("Arial")


font_options = [
    "Arial",
    "Impact",
    "Comic Sans MS",
    "Helvetica",
    "Times New Roman"
]

selected_color = tk.StringVar()
selected_color.set("white")

color_options = [
    "white",
    "black",
    "red",
    "yellow",
    "blue",
    "green"
]

selected_stroke = tk.StringVar()
selected_stroke.set("black")

stroke_options = [
    "black",
    "white"
]

selected_stroke_width = tk.StringVar()
selected_stroke_width.set("2")

stroke_width_options = [
    "0",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6"
]
# Functions
# Open Image
def open_image():
    file_path = filedialog.askopenfilename(initialdir="E:/Python/pythonProject3/Templates")

    global original_image, preview_image, scale_x, scale_y

    original_image = Image.open(file_path)
    original_width = original_image.width
    original_height = original_image.height

    preview_image = original_image.copy()
    preview_image.thumbnail((700,500))
    preview_width = preview_image.width
    preview_height = preview_image.height

    scale_x = original_width / preview_width
    scale_y = original_height / preview_height

    tk_image = ImageTk.PhotoImage(preview_image)
    global image_x, image_y

    canvas.update()

    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()

    image_x = (canvas_width - preview_image.width) // 2
    image_y = (canvas_height - preview_image.height) // 2
    canvas.create_image(
        image_x,
        image_y,
        anchor="nw",
        image=tk_image
    )
    canvas.image = tk_image

def shrink_font(text, max_width, max_height, start_size):

    font_size = start_size

    while True:

        temp_font = (selected_font.get(), font_size)

        temp_text = canvas.create_text(
            250,
            200,
            text=text,
            font=temp_font,
            width=max_width
        )

        bbox = canvas.bbox(temp_text)

        text_height = bbox[3] - bbox[1]

        canvas.delete(temp_text)

        if text_height <= max_height:
            break

        font_size -= 1

    return font_size

# Get text
def get_text():
    user_text = text_entry.get()
    global text_item, preview_font_size
    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()
    cx = canvas_width // 2
    cy = canvas_height // 2
    preview_font_size = shrink_font(user_text,200,150,30)

    new_text = canvas.create_text(
        cx,
        cy,
        text=user_text,
        width=200,
        font=(selected_font.get(),preview_font_size),
        fill=selected_color.get()
    )

    bbox = canvas.bbox(new_text)
    padding = 10

    x1 = bbox[0] - padding
    y1 = bbox[1] - padding
    x2 = bbox[2] + padding
    y2 = bbox[3] + padding


    box = canvas.create_rectangle(
        x1,
        y1,
        x2,
        y2,
        outline="",
        width=2
    )

    handle_size = 10
    handle = canvas.create_rectangle(
        x2 - handle_size,
        y2 - handle_size,
        x2 + handle_size,
        y2 + handle_size,

        fill=""
    )

    text_data = {
        'id': new_text,
        'rect id': box,
        "handle_id": handle,
        'text': user_text,
        'font_size': preview_font_size,
        'font_name': selected_font.get(),
        'wrap_width': 200,
        'snap_image_x': image_x,
        'snap_image_y': image_y,
        'color': selected_color.get(),
        'stroke_color': selected_stroke.get(),
        'stroke_width': int(selected_stroke_width.get()),
        'x': cx,
        'y': cy,
        'x1': x1,
        'y1': y1,
        'x2': x2,
        'y2': y2
    }
    canvas.tag_lower(box, new_text)
    text_items.append(text_data)
    text_entry.delete(0, tk.END)

# Drag system
last_x = 0
last_y = 0

def start_drag(event):

    global last_x, last_y, selected_text, selected_box, resize_rect
    global resize_mode, selected_handle

    last_x = event.x
    last_y = event.y

    resize_mode = False
    selected_handle = None

    for item in text_items:
        canvas.itemconfig(
            item['rect id'],
            outline=""
        )

        canvas.itemconfig(
            item['handle_id'],
            fill=""
        )

    hits = canvas.find_overlapping(event.x - 3, event.y - 3, event.x + 3, event.y + 3)
    for cid in reversed(hits):
        for item in text_items:
            if item['handle_id'] == cid:
                resize_mode = True
                selected_handle = cid

                selected_text = item['id']
                selected_box = item['rect id']

                canvas.itemconfig(
                    item['rect id'],
                    outline="cyan"
                )

                canvas.itemconfig(
                    item['handle_id'],
                    fill="cyan"
                )

                return
            if item['id'] == cid or item['rect id'] == cid:
                selected_text = item['id']
                selected_box = item['rect id']
                resize_rect = item['handle_id']

                canvas.itemconfig(
                    item['rect id'],
                    outline="cyan"
                )

                canvas.itemconfig(
                    item['handle_id'],
                    fill="cyan"
                )
                return



def drag(event):
    global last_x, last_y, resize_mode

    dx = event.x - last_x
    dy = event.y - last_y

    if resize_mode:
        for item in text_items:
            if item['id'] == selected_text:
                new_width = event.x - item['x']
                if new_width < 50:
                    new_width = 50
                item['wrap_width'] = new_width

                canvas.itemconfig(
                    selected_text,
                    width=new_width
                )
                bbox = canvas.bbox(selected_text)

                padding = 10

                x1 = bbox[0] - padding
                y1 = bbox[1] - padding
                x2 = bbox[2] + padding
                y2 = bbox[3] + padding

                canvas.coords(
                    selected_box,
                    x1,
                    y1,
                    x2,
                    y2
                )
                handle_size = 10
                canvas.coords(
                    item['handle_id'],

                    x2 - handle_size,
                    y2 - handle_size,

                    x2 + handle_size,
                    y2 + handle_size
                )
                item['x1'] = x1
                item['y1'] = y1
                item['x2'] = x2
                item['y2'] = y2
                return

    else:
        canvas.move(selected_text, dx, dy)
        canvas.move(selected_box, dx, dy)

        for item in text_items:
            if item['id'] == selected_text:
                item['x'] += dx
                item['y'] += dy
                item['x1'] += dx
                item['y1'] += dy
                item['x2'] += dx
                item['y2'] += dy
                canvas.move(item['handle_id'], dx, dy)
                break

    last_x = event.x
    last_y = event.y

# Delete text
def delete_text():
    global selected_text, selected_box, resize_rect
    if selected_text is not None:
        canvas.delete(selected_text)
        canvas.delete(selected_box)
        canvas.delete(resize_rect)
        for item in text_items:
            if item['id'] == selected_text or item['rect id'] == selected_text:
                text_items.remove(item)
                selected_text = None
                selected_box = None
                break

def save_meme():
    if 'original_image' not in globals():
        return
    final_image = original_image.copy()
    draw = ImageDraw.Draw(final_image)

    for item in text_items:
        real_x = (item['x1'] + 10 - item["snap_image_x"]) * scale_x
        real_y = (item['y1'] + 10 - item["snap_image_y"]) * scale_y
        dpi = root.winfo_fpixels('1i')
        real_font_size = int(item["font_size"] * scale_x * dpi / 72)

        font_map = {
            "Arial": "arial.ttf",
            "Impact": "impact.ttf",
            "Comic Sans MS": "comic.ttf",
            "Helvetica": "arial.ttf",
            "Times New Roman": "times.ttf"
        }
        font_file = font_map.get(item['font_name'], "arial.ttf")
        font = ImageFont.truetype(font_file, real_font_size)
        max_width = item['wrap_width'] * scale_x

        words = item["text"].split()
        current_line = ''
        lines = []

        for word in words:
            test_line = word if current_line == '' else current_line + ' ' + word
            text_width = draw.textlength(test_line, font=font)
            if text_width <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        lines.append(current_line)

        line_heights = []
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            line_heights.append(bbox[3] - bbox[1])

        total_height = sum(line_heights) + 10 * (len(lines) - 1)
        current_y = real_y

        for i, line in enumerate(lines):
            line_width = draw.textlength(line, font=font)
            line_x = real_x
            draw.text(
                (line_x, current_y),
                line,
                font=font,
                fill=item['color'],
                stroke_width=item['stroke_width'],
                stroke_fill=item['stroke_color']
            )
            current_y += line_heights[i] + 10
    final_image.save("final_meme.png")

# Buttons
# Open Button
def make_button(text, command):
    button = tk.Button(
        sidebar,
        text=text,
        command=command,
        bg="#123d7a",
        fg="white",
        activebackground="#1f5fbf",
        activeforeground="white",
        relief="flat",
        bd=0,
        font=("Segoe UI", 11, "bold"),
        cursor="hand2"
    )

    button.pack(
        pady=10,
        padx=10,
        fill="x"
    )
    return button

open_button = make_button('Open Image', open_image)
divider(sidebar)

text_entry = tk.Entry(
    sidebar,
    bg="#FFE9E5",
    fg="black",
    insertbackground="white",
    bd=0,
    font=("Segoe UI", 14),
    highlightthickness=2,
    highlightbackground="#ef476f",
    highlightcolor="#ef476f"
)
text_entry.pack(pady=20)

text_button = make_button('Add Text', get_text)

font_label = tk.Label(
    sidebar,
    text="Font",
    bg="#1a1a2e",
    fg="white",
    font=("Segoe UI", 10, "bold")
)

font_label.pack(
    anchor="w",
    padx=10
)

font_menu = tk.OptionMenu(
    sidebar,
    selected_font,
    *font_options
)
font_menu.config(
    bg="#123d7a",
    fg="white",
    activebackground="#1f5fbf",
    activeforeground="white",
    font=("Segoe UI", 10),
    bd=0,
    highlightthickness=0
)
font_menu["menu"].config(
    bg="#123d7a",
    fg="white",
    activebackground="#1f5fbf",
    activeforeground="white",
    font=("Segoe UI", 10)
)
font_menu.pack(
    fill="x",
    padx=10,
    pady=10
)
selected_font.get()

color_label = tk.Label(
    sidebar,
    text="Text Color",
    bg="#1a1a2e",
    fg="white",
    font=("Segoe UI", 10, "bold")
)

color_label.pack(
    anchor="w",
    padx=10
)

color_menu = tk.OptionMenu(
    sidebar,
    selected_color,
    *color_options
)
color_menu.config(
    bg="#123d7a",
    fg="white",
    activebackground="#1f5fbf",
    activeforeground="white",
    font=("Segoe UI", 10),
    bd=0,
    highlightthickness=0
)
color_menu["menu"].config(
    bg="#123d7a",
    fg="white",
    activebackground="#1f5fbf",
    activeforeground="white",
    font=("Segoe UI", 10)
)
color_menu.pack(
    fill="x",
    padx=10,
    pady=10
)

stroke_label = tk.Label(
    sidebar,
    text="Stroke Color",
    bg="#1a1a2e",
    fg="white",
    font=("Segoe UI", 10, "bold")
)

stroke_label.pack(
    anchor="w",
    padx=10
)

stroke_menu = tk.OptionMenu(
    sidebar,
    selected_stroke,
    *stroke_options
)
stroke_menu.config(
    bg="#123d7a",
    fg="white",
    activebackground="#1f5fbf",
    activeforeground="white",
    font=("Segoe UI", 10),
    bd=0,
    highlightthickness=0
)
stroke_menu["menu"].config(
    bg="#123d7a",
    fg="white",
    activebackground="#1f5fbf",
    activeforeground="white",
    font=("Segoe UI", 10)
)
stroke_menu.pack(
    fill="x",
    padx=10,
    pady=10
)

stroke_width_label = tk.Label(
    sidebar,
    text="Stroke Width",
    bg="#1a1a2e",
    fg="white",
    font=("Segoe UI", 10, "bold")
)

stroke_width_label.pack(
    anchor="w",
    padx=10
)

stroke_width_menu = tk.OptionMenu(
    sidebar,
    selected_stroke_width,
    *stroke_width_options
)
stroke_width_menu.config(
    bg="#123d7a",
    fg="white",
    activebackground="#1f5fbf",
    activeforeground="white",
    font=("Segoe UI", 10),
    bd=0,
    highlightthickness=0
)
stroke_width_menu["menu"].config(
    bg="#123d7a",
    fg="white",
    activebackground="#1f5fbf",
    activeforeground="white",
    font=("Segoe UI", 10)
)
stroke_width_menu.pack(
    fill="x",
    padx=10,
    pady=10
)

divider(sidebar)

delete_button = make_button('Delete Selected', delete_text)
save_button = make_button('Save', save_meme)

canvas.bind('<Button-1>', start_drag)
canvas.bind('<B1-Motion>', drag)

root.mainloop()

