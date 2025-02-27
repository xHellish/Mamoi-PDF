import tkinter as tk
from tkinter import Entry, Button, messagebox, filedialog, ttk
from PIL import Image, ImageTk
import requests
import fitz  # PyMuPDF
from googlesearch import search
import os

# --------------------------------------- #
# VARIABLES
entry = None  # Texto en buscador
found_pdfs_window = None  # Resultados pdfs
root = None  # Ventana main
PDFs_error_count = 0  # PDFs fallidos
search_button = None  # Referencia botón buscar pdf
results_frame = None  # Referencia al frame de los results
logs_frame = None     # Ref a los logs 

# --------------------------------------- #
# FUNCIONES

def search_pdf():
    global PDFs_error_count, search_button, results_frame, label_current_state, logs_frame, preview_frame  # GLOBALES

    clear_frame(logs_frame)
    
    label_logs_tittle = tk.Label(logs_frame, text="Estado: ", padx=10, pady=5, fg="white", bg="black", font=("Courier", 12, "bold"))
    label_logs_tittle.pack(side="top", anchor="w")

    label_current_state = tk.Label(logs_frame, text="Buscando...", padx=10, pady=5, fg="purple", bg="black", font=("Courier", 12, "bold"))
    label_current_state.place(x=80, y=0)

    query = entry.get()
    search_button.config(state="disabled")

    root.after(100, search_pdf_worker, query)  # Ejecuta después de 100ms

def search_pdf_worker(query):

    global PDFs_error_count, results_frame, search_button, label_current_state, preview_frame

    if query == "":
        label_current_state.config(text="Inactivo", fg="gray")
        messagebox.showerror("Error de Búsqueda", "Debes escribir algo mamoi...")
        search_button.config(state="normal")

        return

    clear_frame(preview_frame)
    clear_frame(results_frame)

    # Procesar invisibles
    results_frame.place_forget()

    # --------------------------------------- #
    links = list(search_pdf_online(query))  # Obtener resultados

    canvas = tk.Canvas(results_frame)
    scroll_y = tk.Scrollbar(results_frame, orient="vertical", command=canvas.yview)
    canvas.config(yscrollcommand=scroll_y.set)

    frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=frame, anchor="nw")
    canvas.pack(side="left", fill="both", expand=True)
    scroll_y.pack(side="right", fill="y")

    for link in links:
        add_pdf_to_list(link, frame)

    frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))
    canvas.bind_all("<MouseWheel>", lambda event, canvas=canvas: on_mouse_wheel(event, canvas))

    # Luego de encontrar
    label_current_state.config(text="Inactivo", fg="gray")
    label_new_pdf_find = tk.Label(logs_frame, text=f"[💕] LISTO !!", padx=10, pady=5, fg="yellow", bg="black", font=("Courier", 12, "bold"))
    label_new_pdf_find.pack(side="top", anchor="w")

    label_total_errors = tk.Label(logs_frame, text=f"(PDFs haciendo el PAPEL: {PDFs_error_count-1})", padx=10, pady=5, fg="gray", bg="black", font=("Courier", 10, "bold"))
    label_total_errors.pack(side="top", anchor="w")
    PDFs_error_count = 0

    results_frame.place(x=320, y=0)         # Ver frame de resultados
    search_button.config(state="normal")    # Activar botón de buscar
    logs_frame.update()                     # Actualizar log

def open_pdf_from_url(pdf_url):

    global preview_frame

    #Resets
    clear_frame(preview_frame)

    try:

        # Descargar el PDF desde la URL
        response = requests.get(pdf_url)
        response.raise_for_status()

        # Guardar el archivo PDF temporalmente
        with open("temp.mmoi.pdf", "wb") as f:
            f.write(response.content)

        # Abrir el PDF con PyMuPDF
        doc = fitz.open("temp.mmoi.pdf")

        # Cargar la primera página para obtener su tamaño
        first_page = doc.load_page(0)
        zoom_scale = 1.0
        pix = first_page.get_pixmap(matrix=fitz.Matrix(zoom_scale, zoom_scale))
        pdf_width, pdf_height = pix.width, pix.height

        current_page = 0
        start_x, start_y = 0, 0  # Variables para el arrastre con botón central

        # Crear un Canvas para la imagen
        canvas = tk.Canvas(preview_frame, bg="black")
        canvas.pack(fill="both", expand=True)

        img_id = None  # ID de la imagen en el Canvas

        def show_page(page_num):
            nonlocal img_id, zoom_scale
            try:
                page = doc.load_page(page_num)
                pix = page.get_pixmap(matrix=fitz.Matrix(zoom_scale, zoom_scale))
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                tk_img = ImageTk.PhotoImage(img)

                # Eliminar imagen anterior y agregar la nueva
                canvas.delete("all")
                img_id = canvas.create_image(0, 0, anchor="nw", image=tk_img)
                canvas.image = tk_img  # Guardar referencia

                # Ajustar el área del canvas al tamaño de la imagen
                canvas.config(scrollregion=canvas.bbox("all"))

            except Exception as e:
                print(f"Error al mostrar la página: {e}")

        # Mostrar la primera página
        show_page(current_page)

        def next_page():
            nonlocal current_page
            if current_page < len(doc) - 1:
                current_page += 1
                show_page(current_page)

        def prev_page():
            nonlocal current_page
            if current_page > 0:
                current_page -= 1
                show_page(current_page)

        def zoom(event):
            nonlocal zoom_scale, img_id
            if event.state & 0x4:  # Verifica si Ctrl está presionado
                factor = 1.1 if event.delta > 0 else 0.9
                new_zoom_scale = zoom_scale * factor

                # Obtener la posición del mouse en el canvas
                x_mouse, y_mouse = -event.x, -event.y

                # Obtener el tamaño de la imagen actual
                page = doc.load_page(current_page)
                pix = page.get_pixmap(matrix=fitz.Matrix(new_zoom_scale, new_zoom_scale))
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                tk_img = ImageTk.PhotoImage(img)

                # Eliminar la imagen actual
                canvas.delete("all")

                # Mostrar la nueva imagen con la nueva escala
                img_id = canvas.create_image(0, 0, anchor="nw", image=tk_img)
                canvas.image = tk_img  # Guardar la referencia de la imagen

                # Calcular la diferencia de desplazamiento entre la posición anterior y la nueva imagen
                bbox = canvas.bbox(img_id)
                if bbox:
                    # Calcular la diferencia entre la posición del mouse y la esquina superior izquierda de la imagen
                    delta_x = x_mouse - bbox[0]
                    delta_y = y_mouse - bbox[1]

                    # Ajustar la posición de la imagen para que el área debajo del mouse se mantenga centrada
                    canvas.move(img_id, delta_x, delta_y)

                zoom_scale = new_zoom_scale  # Actualizar el factor de zoom

                # Ajustar el área del canvas al tamaño de la imagen
                canvas.config(scrollregion=canvas.bbox("all"))

        # ARRASTRAR
        def start_pan(event):
            """Guarda la posición inicial cuando se presiona el botón central."""
            nonlocal start_x, start_y
            start_x, start_y = event.x, event.y

        def do_pan(event):
            """Mueve la imagen dentro del Canvas al arrastrar con el botón central."""
            nonlocal start_x, start_y
            dx = event.x - start_x
            dy = event.y - start_y
            canvas.move(img_id, dx, dy)
            start_x, start_y = event.x, event.y

        # Botones de navegación
        button_prev_style = ttk.Style()
        button_prev_style.configure("button_prev.TButton",
                                      relief="flat", 
                                      padding=5, 
                                      background="lightgray", 
                                      foreground="black",
                                      font=("Segoe UI", 11, "bold"),
                                      width=10)

        button_prev = ttk.Button(preview_frame, text="◀ Anterior", style="button_prev.TButton", command=prev_page)
        button_prev.pack(side="left", padx=20, pady=10)

        button_next_style = ttk.Style()
        button_next_style.configure("button_next.TButton",
                                      relief="flat", 
                                      padding=5, 
                                      background="lightgray", 
                                      foreground="black",
                                      font=("Segoe UI", 11, "bold"),
                                      width=10)

        button_next = ttk.Button(preview_frame, text="Siguiente ▶", style="button_next.TButton", command=next_page)
        button_next.pack(side="right", padx=20, pady=10)

        # Eventos de zoom con la rueda del mouse
        canvas.bind("<MouseWheel>", zoom)  # Windows/Mac
        canvas.bind("<Button-4>", zoom)  # Linux scroll up
        canvas.bind("<Button-5>", zoom)  # Linux scroll down

        # Eventos para arrastrar con el botón central
        canvas.bind("<ButtonPress-2>", start_pan)
        canvas.bind("<B2-Motion>", do_pan)

    except Exception as e:
        messagebox.showerror("QUE??", f"No se puede ver por aquí lastimosamente... ")

def add_pdf_to_list(pdf_url, frame):
    
    global PDFs_error_count, logs_frame

    try:
        response = requests.get(pdf_url)
        response.raise_for_status()  # Verificar si hubo un error en la descarga

        with open("temp.mmoi.pdf", "wb") as f:
            f.write(response.content)

        doc = fitz.open("temp.mmoi.pdf")
        page = doc.load_page(0)

        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        img = img.resize((100, 150))

        tk_img = ImageTk.PhotoImage(img)

        # Frame principal
        item_frame = tk.Frame(frame)
        item_frame.pack(pady=5, fill="x", padx=5)

        # Imagen del PDF
        label_img = tk.Label(item_frame, image=tk_img)
        label_img.image = tk_img  # Guardar referencia a la imagen
        label_img.pack(side="left", padx=10)

        # Frame para el label y botones
        frame_info = tk.Frame(item_frame)
        frame_info.pack(side="left", padx=10, anchor="w")

        # Label con el nombre del PDF (alineado a la izquierda)
        label_text = tk.Label(frame_info, text=pdf_url.split('/')[-1][:27], font=("Segoe UI", 12, "bold"))
        label_text.pack(fill="x", anchor="w")

        # --------------------------------------------------- #
        # BOTONES
        # Frame para los botones (alineado a la izquierda)
        frame_botones = tk.Frame(frame_info)
        frame_botones.pack(side="top", anchor="w")  # Esto mantiene los botones alineados a la izquierda

        # Botón para abrir el PDF
        button_open_style = ttk.Style()
        button_open_style.configure("button_open.TButton",
                                      relief="flat", 
                                      padding=5, 
                                      background="lightgray", 
                                      foreground="black",
                                      font=("Segoe UI", 11, "bold"),
                                      width=10)

        button_open = ttk.Button(frame_botones, text="VER", style="button_open.TButton", command=lambda: open_pdf_from_url(pdf_url))
        button_open.pack(side="left", padx=5, anchor="w")

        # Botón para descargar el PDF
        button_down_style = ttk.Style()
        button_down_style.configure("button_down.TButton",
                                      relief="flat", 
                                      padding=5, 
                                      background="lightgray", 
                                      foreground="black",
                                      font=("Segoe UI", 11, "bold"),
                                      width=10)

        button_down = ttk.Button(frame_botones, text="DESCARGAR", style="button_down.TButton", command=lambda: download_pdf(pdf_url))
        button_down.pack(side="left", padx=5, anchor="w")

        # ---------------------------------------------------- #
        # LOG

        #print(f"\033[92m[✔] PDF DISPONIBLE\033[0m - 📄 {pdf_url.split('/')[-1]}")

        label_new_pdf_find = tk.Label(logs_frame, text=f"[✔] 📄 {pdf_url.split('/')[-1][:21]}", padx=10, pady=5, fg="green", bg="black", font=("Courier", 12, "bold"))
        label_new_pdf_find.pack(side="top", anchor="w")
        logs_frame.update()

    except Exception as e:

        PDFs_error_count += 1

        if PDFs_error_count != 1:
            label_new_pdf_find = tk.Label(logs_frame, text=f"[💔] 📄 PDF inaccesible", padx=10, pady=5, fg="red", bg="black", font=("Courier", 12, "bold"))
            label_new_pdf_find.pack(side="top", anchor="w")
            logs_frame.update()

        pass


# --------------------------------------- #
# AUX
def on_mouse_wheel(event, canvas):
    # Verificar si Ctrl está presionado (evento de rueda sin Ctrl)
    if not (event.state & 0x4):  # Si Ctrl no está presionado
        if event.delta > 0:
            canvas.yview_scroll(-1, "units")  # Desplazar hacia arriba
        else:
            canvas.yview_scroll(1, "units")  # Desplazar hacia abajo


# DOWNLOAD
def download_pdf(pdf_url, save_path=None):
    try:
        # Solicitar al usuario el directorio de descarga si no se pasa un save_path
        if not save_path:
            save_path = filedialog.asksaveasfilename(initialfile=f"{pdf_url.split('/')[-1]}", defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
            if not save_path:
                return  # Si el usuario cancela el cuadro de diálogo, no hacer nada

        response = requests.get(pdf_url)
        response.raise_for_status()  # Verificar si hubo un error en la descarga

        # Guardar el archivo PDF en el disco
        with open(save_path, "wb") as f:
            f.write(response.content)

        messagebox.showinfo("Éxito", f"PDF descargado correctamente y guardado en: {save_path}")
    
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Error al descargar el PDF: {e}")

# SEARCH
def search_pdf_online(query):
    """
    Busca archivos PDF en Internet utilizando Google.

    :param query: Término de búsqueda.
    :return: Lista de URLs que contienen archivos PDF.
    """
    pdf_urls = []
    for url in search(f"{query} filetype:pdf", num_results=10):
        pdf_urls.append(url)
    
    return pdf_urls

# CLOSE APP
def on_closing():

    global preview_frame
    clear_frame(preview_frame)  # Dejar de usar archivo temporal
    clear_frame(results_frame)

    file_path = "temp.mmoi.pdf"


    if os.path.exists(file_path):       # Verifica si el archivo existe
        os.remove(file_path)            # Borra el archivo
        
    else:
        pass

    print("Cerrando la aplicación...")
    root.destroy()  # Cierra la ventana

def clear_frame(frame):
    # Destruir todos los widgets dentro del frame
    for widget in frame.winfo_children():
        widget.destroy()
        frame.update()

# --------------------------------------- #

root = tk.Tk()
root.title("MAMOI PDF")
root.geometry("1280x720")
root.configure(bg="darkgray")
root.resizable(False, False)  # No cambiar tamaño
root.protocol("WM_DELETE_WINDOW", on_closing)  # Al cerrar

# --------------------------------------- #
# FRAMES
# Crear el Frame de búsqueda y darle estilo con bordes
search_frame = tk.Frame(root, width=300, height=200, bg="lightgray", bd=5, relief="solid")  # Borde sólido alrededor del Frame
search_frame.place(x=0, y=0)

# Results
results_frame_layer = tk.Frame(root, width=420, height=720, bg="lightgray", bd=5, relief="solid")  # Borde sólido alrededor del Frame
results_frame_layer.place(x=320, y=0)
results_frame_layer.pack_propagate(False)

results_frame = tk.Frame(root, width=420, height=720, bg="lightgray", bd=5, relief="solid")  # Borde sólido alrededor del Frame
results_frame.place(x=320, y=0)
results_frame.pack_propagate(False)

# Logs
logs_frame = tk.Frame(root, width=320, height=565, bg="black", bd=5, relief="solid")  # Borde sólido alrededor del Frame
logs_frame.place(x=0, y=155)
logs_frame.pack_propagate(False)

# Preview
preview_frame = tk.Frame(root, width=545, height=720, bg="lightgray", bd=5, relief="solid")  # Borde sólido alrededor del Frame
preview_frame.place(x=735, y=0)
preview_frame.pack_propagate(False)

# --------------------------------------- #
# Título
label_title = tk.Label(search_frame, text="Busque un PDF baboi", font=("Segoe UI", 14, "bold"), bg="lightgray")
label_title.pack(pady=10)

label_logs_tittle = tk.Label(logs_frame, text="Estado: ", padx=10, pady=5, fg="white", bg="black", font=("Courier", 12, "bold"))
label_logs_tittle.pack(side="top", anchor="w")

label_current_state = tk.Label(logs_frame, text="Inactivo", padx=10, pady=5, fg="gray", bg="black", font=("Courier", 12, "bold"))
label_current_state.place(x=80, y=0)

# --------------------------------------- #
# Caja de texto
entry = tk.Entry(search_frame, width=30, font=("Segoe UI", 12))
entry.pack(pady=5, padx=20)

# Asociar Enter con la búsqueda
entry.bind("<Return>", lambda event: search_pdf())

# Botón con estilo
search_button_style = ttk.Style()
search_button_style.configure("Rounded.TButton",
                              relief="flat", 
                              padding=5, 
                              background="gray", 
                              foreground="black",
                              font=("Segoe UI", 12),
                              width=20)

# Botón con estilo moderno
search_button = ttk.Button(search_frame, text="Buscar <3", style="Rounded.TButton", command=search_pdf)

# Agregar el botón al Frame
search_button.pack(pady=10)

root.mainloop()


