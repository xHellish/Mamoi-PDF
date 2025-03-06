# --------------------------------------- #
import libs
import aux_tools_funcs

# --------------------------------------- #
# VARIABLES
entry = None                # Texto en buscador
found_pdfs_window = None    # Resultados pdfs
root = None                 # Ventana main
search_button = None        # Referencia botón buscar pdf
results_frame_layer = None  # Referencia al frame de los results
logs_frame = None           # Ref a los logs 
logs_layout = None
is_in_searching = False     # Flag si está buscando

PDFs_error_count = 0        # PDFs fallidos

# --------------------------------------- #
# FUNCIONES

# Inicio de la búsqueda
def search_pdf():

    global PDFs_error_count, is_in_searching, search_button, results_frame_layer, label_current_state, logs_frame, preview_frame  # GLOBALES

    if is_in_searching:
        return

    is_in_searching = True

    aux_tools_funcs.clear_frame(results_frame_layer)
    aux_tools_funcs.clear_frame(logs_frame)
    libs.QApplication.processEvents()

    label_current_state.setText("Buscando...")
    label_current_state.setStyleSheet("""
        color: #A5D6A7;  /* Rosado claro */
        font: bold 12px Courier;
        border: none;
    """)

    query = entry.text()

    libs.QTimer.singleShot(100, lambda: search_pdf_worker(query))

def search_pdf_worker(query):
    global is_in_searching, PDFs_error_count, results_frame_layer, search_button, label_current_state, preview_frame, logs_frame, logs_layout

    if query == "":
        label_current_state.setText("Inactivo")
        label_current_state.setStyleSheet("""
            color: #d1a1d1;  /* Rosado claro */
            font: bold 12px Courier;
            border: none;
        """)

        # Mostrar un cuadro de diálogo de información (más amigable)
        info_dialog = libs.QMessageBox()
        info_dialog.setIcon(libs.QMessageBox.Information)  # Usamos el ícono de información en lugar de advertencia
        info_dialog.setText("No se puede buscar en blanco !!")  # Mensaje más amigable
        info_dialog.setWindowTitle("AVISO")
        info_dialog.setStandardButtons(libs.QMessageBox.Ok)  # Solo el botón "Aceptar"

        # Esperar a que el usuario haga clic en "Aceptar"
        info_dialog.exec_()

        # Habilitar el botón de búsqueda nuevamente
        search_button.setEnabled(True)
        is_in_searching = False
        return


    # --------------------------------------- #
    links = list(aux_tools_funcs.search_pdf_online(query))  # Obtener resultados

    # --------------------------------------- #
    # Crear el área de desplazamiento
    scroll_area = libs.QScrollArea()
    scroll_area.setWidgetResizable(True)  # Permite ajustar el tamaño del contenido
    scroll_area.setStyleSheet("QScrollArea { border: none; }")  # Sin borde
    scroll_area.setVerticalScrollBarPolicy(libs.Qt.ScrollBarAlwaysOff)
    scroll_area.setHorizontalScrollBarPolicy(libs.Qt.ScrollBarAlwaysOff)

    # --------------------------------------- #
    # Frame contenedor de los resultados
    results_container_frame = libs.QFrame()
    results_container_frame.setStyleSheet("""
        background-color: #e5c0e3;  /* Rosado más claro */
        border: 5px solid #9b4d96;  /* Morado oscuro */
        border-radius: 5px;
        border: none;
    """)
    results_container_frame.setLayout(libs.QVBoxLayout())
    results_container_frame.layout().setAlignment(libs.Qt.AlignTop)  # Alinea los widgets arriba
    results_container_frame.layout().setSpacing(10)  # Espaciado adecuado entre los elementos

    # Agregar el frame contenedor al QScrollArea
    scroll_area.setWidget(results_container_frame)

    # Agregar el scroll_area al layout principal
    results_frame_layer.layout().addWidget(scroll_area)
    results_frame_layer.setUpdatesEnabled(False)  # Bloquear actualización

    # Agregar los links de PDF a la lista dentro del contenedor
    for link in links:
        add_pdf_to_list(link, results_container_frame)

    results_frame_layer.setUpdatesEnabled(True)  # Desbloquear actualización

    # Mensaje final console
    label_ready_find = libs.QLabel("[⚜] ¡Búsqueda Terminada con Éxito!", logs_frame)
    label_ready_find.setStyleSheet("""
        background-color: black;  /* Fondo negro */
        color: yellow;             /* Texto amarillo */
        font: bold 12px 'Courier';
        padding: 0px;
        border: none;
    """)

    logs_frame.layout().addWidget(label_ready_find)

    label_errors_finds = libs.QLabel(f"PDFs no accesibles: {PDFs_error_count}", logs_frame)
    label_errors_finds.setStyleSheet("""
        background-color: black;  /* Fondo negro */
        color: gray;             /* Texto amarillo */
        font: bold 10px 'Courier';
        padding: 0px;
        border: none;
    """)

    logs_frame.layout().addWidget(label_errors_finds)

    # ------------------------------------------------ #
    # Luego de encontrar
    label_current_state.setText("Inactivo")
    label_current_state.setStyleSheet("""
        color: #d1a1d1;  /* Rosado claro */
        font: bold 12px Courier;
        border: none;
    """)

    PDFs_error_count = 0
    search_button.setEnabled(True)  # Activar botón de buscar
    is_in_searching = False
    logs_frame.update()  # Actualizar log
    scroll_area.show()  # Asegurar que el scroll area se renderice correctamente


# --------------------------------------- #
# Añadir PDF al frame
def add_pdf_to_list(pdf_url, widget_cont):
    global PDFs_error_count, logs_frame

    try:
        # ------------------------------------------------ #
        # Crear el contenedor del PDF
        frame_container_pdf = libs.QFrame(widget_cont)
        frame_container_pdf.setStyleSheet("""
            background-color: #D1A1D1;
            border: 2px solid #9b4d96;  /* Morado más claro */
            border-radius: 10px;
        """)
        frame_container_pdf.setFixedSize(375, 200)
        frame_container_pdf.setLayout(libs.QVBoxLayout())

        # Crear contenedor para la imagen dentro del frame del PDF
        frame_container_image_pixmap = libs.QFrame(frame_container_pdf)
        frame_container_image_pixmap.setStyleSheet("""
            background-color: #D1A1D1;
            padding: 5px;
            border: none;
        """)
        frame_container_image_pixmap.setFixedSize(150, 190)
        frame_container_image_pixmap.move(3, 3)

        # Intentar obtener la imagen del PDF
        try:

            # ------------------------------------------------ #
            # IMAGEN
            label_imagen_pdf_page1 = libs.QLabel(frame_container_image_pixmap)

            # Obtener el pixmap de la primera página
            page_1_pdf_pixmap = aux_tools_funcs.pdf_page_to_pixmap(pdf_url, 30)
            
            # Asegurarse de que la imagen es un QPixmap
            page_1_pdf_Qpixmap = aux_tools_funcs.pix_to_Qpix(page_1_pdf_pixmap)

            # Redimensionar el pixmap a un tamaño estándar manteniendo la relación de aspecto
            scaled_pixmap = page_1_pdf_Qpixmap.scaled(150, 200, libs.Qt.KeepAspectRatio)

            # Establecer el pixmap redimensionado en el label
            label_imagen_pdf_page1.setPixmap(scaled_pixmap)
            
            # ------------------------------------------------ #
            # BOTONES
            preview_button = libs.QPushButton("Previsualizar", frame_container_pdf)
            preview_button.setStyleSheet("""
                background-color: #9b4d96;  /* Morado oscuro */
                color: white;
                font: 12px 'Segoe UI';
                padding: 10px;
                border-radius: 10px;
                border: none;
            """)
            preview_button.setFixedWidth(170)
            preview_button.setFixedHeight(35)

            preview_button.move(180, 70)
            aux_tools_funcs.animate_hover(preview_button, (155, 77, 150), (225, 120, 177), 150)
            preview_button.clicked.connect(lambda: load_pdf_from_url(pdf_url, preview_frame))
            
            download_button = libs.QPushButton("Descargar", frame_container_pdf)
            download_button.setStyleSheet("""
                background-color: #9b4d96;  /* Morado oscuro */
                color: white;
                font: 12px 'Segoe UI';
                padding: 10px;
                border-radius: 10px;
                border: none;
            """)
            download_button.setFixedWidth(170)
            download_button.setFixedHeight(35)

            download_button.move(180, 115)
            aux_tools_funcs.animate_hover(download_button, (155, 77, 150), (225, 120, 177), 150)

            download_button.clicked.connect(lambda: aux_tools_funcs.descargar_pdf(pdf_url, pdf_url.split("/")[-1]))
            
            # ------------------------------------------------ #
            # NOMBRE
            label_pdf_name = libs.QLabel(f"{pdf_url.split("/")[-1][:22]}", frame_container_pdf)
            label_pdf_name.setStyleSheet("""
                background-color: #e5c0e3;  /* Fondo */
                color: #9b4d96;             /* Texto */
                font: bold 12px 'Segoe UI';
                padding: 5px;
                border: none;

            """)
            label_pdf_name.setWordWrap(True)  
            label_pdf_name.setFixedWidth(170)
            label_pdf_name.setFixedHeight(35)
            label_pdf_name.adjustSize()
            label_pdf_name.move(180, 25)

        except Exception as ex: 
            aux_tools_funcs.destroy_frame(frame_container_pdf)
            raise Exception(f"Imagen PIXMAP no disponible - pdf cancelado: {str(ex)}")

        # ------------------------------------------------ #
        # Añadir el frame con la imagen al layout
        widget_cont.layout().addWidget(frame_container_pdf)

        # ------------------------------------------------ #
        # Consola
        aux_tools_funcs.add_console_pdf_found(pdf_url, logs_frame)

        # ------------------------------------------------ #
        # Actualizar la consola después de procesar el PDF
        libs.QApplication.processEvents() 

    except Exception as e:
        print(e)

        # ------------------------------------------------ #
        # Consola para mostrar error
        aux_tools_funcs.add_console_pdf_not_found(logs_frame)
        PDFs_error_count = PDFs_error_count + 1
        libs.QApplication.processEvents() # FORZAR ACTUALIZACIÓN DE LA UI

# ------------------------------------------------ #
# Preview del PDF

def load_pdf_from_url(pdf_url, frame):
    global current_page, pdf_document, preview_label, preview_frame

    aux_tools_funcs.clear_frame(frame)

    # Función interna para mostrar una página específica
    def show_page(page_number):
        global current_page, pdf_document, preview_label

        if pdf_document is None or page_number < 0 or page_number >= len(pdf_document):
            return

        current_page = page_number

        # Cargar la página específica
        page = pdf_document.load_page(current_page)
        pix = page.get_pixmap()  # Obtener un pixmap (imagen) de la página

        # Convertir el pixmap a un QImage
        img = libs.QImage(pix.samples, pix.width, pix.height, pix.stride, libs.QImage.Format_RGB888)

        # Convertir el QImage a un QPixmap
        pixmap = libs.QPixmap.fromImage(img)

        # Verificar si el QPixmap es válido
        if pixmap.isNull():
            raise Exception("No se pudo generar el QPixmap")

        # Crear o actualizar el QLabel para mostrar el PDF
        if preview_label is None:
            preview_label = libs.QLabel(frame)
            preview_label.setAlignment(libs.Qt.AlignCenter)
            frame.layout().addWidget(preview_label)
        preview_label.setPixmap(pixmap.scaled(frame.size(), libs.Qt.KeepAspectRatio))

    # Función para ir a la página anterior
    def previous_page():
        global current_page
        if current_page > 0:
            show_page(current_page - 1)

    # Función para ir a la página siguiente
    def next_page():
        global current_page
        if pdf_document and current_page < len(pdf_document) - 1:
            show_page(current_page + 1)

    # Inicializar variables
    current_page = 0
    pdf_document = None
    preview_label = None

    try:
        # Descargar el archivo PDF desde la URL
        response = libs.requests.get(pdf_url)
        response.raise_for_status()  # Verificar si la descarga fue exitosa

        # Abrir el archivo PDF desde los bytes descargados
        pdf_document = libs.fitz.open(stream=libs.BytesIO(response.content))

        # Mostrar la primera página
        show_page(current_page)

        buttons_frame = libs.QFrame(frame)
        buttons_frame.setStyleSheet("""
            background-color: #d1a1d1;  /* Rosado claro */
            border: 0px solid #9b4d96;  /* Morado oscuro */
            border-radius: 10px;
            border: none;

        """)
        buttons_frame.setFixedSize(530, 55)
        buttons_frame.setLayout(libs.QHBoxLayout())

        # ---------------------------------------- #
        # Crear botones de navegación
        btn_previous = libs.QPushButton("<<< Anterior", frame)
        btn_previous.setStyleSheet("""
            background-color: #9b4d96;  /* Morado oscuro */
            color: white;
            font: 12px 'Segoe UI';
            padding: 10px;
            border-radius: 10px;
            border: none;
        """)
        btn_previous.setFixedWidth(200)
        aux_tools_funcs.animate_hover(btn_previous, (155, 77, 150), (225, 120, 177), 150)
        btn_previous.clicked.connect(previous_page)

        btn_next = libs.QPushButton("Siguiente >>>", frame)
        btn_next.setStyleSheet("""
            background-color: #9b4d96;  /* Morado oscuro */
            color: white;
            font: 12px 'Segoe UI';
            padding: 10px;
            border-radius: 10px;
            border: none;
        """)
        btn_next.setFixedWidth(200)
        aux_tools_funcs.animate_hover(btn_next, (155, 77, 150), (225, 120, 177), 150)
        btn_next.clicked.connect(next_page)

        # Agregar los botones
        buttons_frame.layout().addWidget(btn_previous)
        buttons_frame.layout().addWidget(btn_next)

        frame.layout().addWidget(buttons_frame)

    except libs.requests.exceptions.RequestException as e:
        print(f"Error al descargar el PDF: {e}")
    except Exception as e:
        print(f"Error al procesar el PDF: {e}")

# --------------------------------------- #
# AL CERRAR
def on_closing(event):
    app.quit()

# ----------------------------------------- #
# APLICATION
app = libs.QApplication(libs.sys.argv)

# Crear la ventana principal
root = libs.QWidget()
root.setWindowTitle("MAMOI PDF")
root.setWindowIcon(libs.QtGui.QIcon("mmoi_pdf.ico"))
root.setGeometry(100, 100, 1280, 720)  # Establecer el tamaño de la ventana
root.setStyleSheet("""
    background-color: #9b4d96;  /* Morado oscuro */
    font-family: 'Segoe UI', sans-serif;
""")  # Establecer el color de fondo de la ventana

root.setFixedSize(1280, 760)  # No cambiar tamaño

# Quitar la barra de título del sistema operativo
root.setWindowFlags(libs.Qt.FramelessWindowHint)

# Conectar la acción de cerrar ventana
root.closeEvent = on_closing

# Crear los Frames usando QFrame
search_frame = libs.QFrame(root)
search_frame.setStyleSheet("""
    background-color: #d1a1d1;  /* Rosado claro */
    border: 5px solid #9b4d96;  /* Morado oscuro */
    border-radius: 10px;
""")
search_frame.setFixedSize(320, 150)

results_frame_layer = libs.QFrame(root)
results_frame_layer.setStyleSheet("""
    background-color: #e5c0e3;  /* Rosado más claro */
    border: 5px solid #9b4d96;  /* Morado oscuro */
    border-radius: 10px;
""")
results_frame_layer.setFixedSize(420, 720)

logs_frame = libs.QFrame(root)
logs_frame.setStyleSheet("""
    background-color: #000000;
    border: 5px solid #9b4d96;  /* Morado más claro */
    border-radius: 10px;
""")
logs_frame.setFixedSize(320, 530)

logs_state_frame = libs.QFrame(root)
logs_state_frame.setStyleSheet("""
    background-color: #000000;
    border: 5px solid #9b4d96;  /* Morado más claro */
    border-radius: 10px;
""")
logs_state_frame.setFixedSize(320, 45)

preview_frame = libs.QFrame(root)
preview_frame.setStyleSheet("""
    background-color: #d1a1d1;  /* Rosado claro */
    border: 0px solid #9b4d96;  /* Morado oscuro */
    border-radius: 5px;

""")
preview_frame.setFixedSize(530, 710)

# Colocar los frames en la ventana
search_frame.move(0, 35)
results_frame_layer.move(318, 35)
logs_frame.move(0, 225)
logs_state_frame.move(0, 183)
preview_frame.move(740, 40)

# Título en el search_frame
label_title = libs.QLabel("Busca un PDF", search_frame)
label_title.setStyleSheet("""
    font: bold 24px 'Segoe UI';
    color: #9b4d96;  /* Morado oscuro */
    padding: 10px;
    border: none;
""")
label_title.move(65, 10)

# Título de Mamoi PDF
label_title = libs.QLabel("🌺 Mamoi PDF", root)
label_title.setStyleSheet("""
    font: 20px 'Segoe UI';
    color: #cccccc;  /* Morado oscuro */
    padding: 5px;
    border: none;
""")
label_title.move(0, 0)

# Estado en el logs_frame
label_logs_tittle = libs.QLabel("Estado: ", logs_state_frame)
label_logs_tittle.setStyleSheet("""
    color: white;
    font: bold 12px Courier;
    border: none;
""")
label_logs_tittle.move(20, 15)

label_current_state = libs.QLabel("Inactivo", logs_state_frame)
label_current_state.setStyleSheet("""
    color: #d1a1d1;  /* Rosado claro */
    font: bold 12px Courier;
    border: none;
""")
label_current_state.move(90, 15)
label_current_state.setFixedWidth(100)

# Caja de texto (entrada)
entry = libs.QLineEdit(search_frame)
entry.setStyleSheet("""
    font: 12px 'Segoe UI';
    padding: 5px;
    border: 2px solid #9b4d96;  /* Morado oscuro */
    border-radius: 8px;
    background-color: #e5c0e3;  /* Rosado más claro */
    color: #3e1d61;  /* Morado oscuro */
""")
entry.setFixedWidth(260)
entry.move(20, 60)

# Asociar Enter con la búsqueda
entry.returnPressed.connect(search_pdf)

# Botón de búsqueda con estilo
search_button = libs.QPushButton("Encontrar en la WEB", search_frame)
search_button.setStyleSheet("""
    background-color: #9b4d96;  /* Morado oscuro */
    color: white;
    font: 12px 'Segoe UI';
    padding: 10px;
    border-radius: 10px;
    border: none;
""")
search_button.setFixedWidth(200)
search_button.move(50, 100)

# --------------------------------------------------------------- #
# Crear barra de título personalizada con botones de minimizar y cerrar
title_bar = libs.QFrame(root)
title_bar.setStyleSheet("""
    background-color: #9b4d96;
    border-radius: 10px 10px 0 0;
    padding: 0;  /* Eliminar el padding de la barra */
""")
title_bar.setFixedHeight(35)
title_bar.move(1190, 3)

# --------------------------- #
# MOVER VENTANA
move_bar = libs.QFrame(root)
move_bar.setStyleSheet("""
    background-color: transparent;
    padding: 0;  /* Eliminar el padding de la barra */
""")
move_bar.setFixedHeight(35)
move_bar.setFixedWidth(1180)
move_bar.move(0, 0)

aux_tools_funcs.make_frame_movable(move_bar, root)

# --------------------------- #
# Asegurar que el layout no tenga padding ni márgenes
title_bar_layout = libs.QHBoxLayout(title_bar)
title_bar_layout.setContentsMargins(0, 0, 0, 0)
title_bar.setLayout(title_bar_layout)

# Crear botones
minimize_button = libs.QPushButton('_', title_bar)
close_button = libs.QPushButton('×', title_bar)

title_bar_layout.addWidget(minimize_button)
title_bar_layout.addWidget(close_button)

# Estilos base
minimize_button.setStyleSheet("background-color: #9b4d96; color: white; font: bold 16px; border: none; width: 40px; height: 30px; border-radius: 5px;")
close_button.setStyleSheet("background-color: #9b4d96; color: white; font: bold 16px; border: none; width: 40px; height: 30px; border-radius: 5px;")

# ------------------------------------------- #
# BOTONES ANIMATION AND CALL

# Aplicar animación de hover
aux_tools_funcs.animate_hover(minimize_button, (155, 77, 150), (255, 182, 193), 150)  # Rosa suave
aux_tools_funcs.animate_hover(close_button, (155, 77, 150), (255, 0, 0), 150)  # Rojo
aux_tools_funcs.animate_hover(search_button, (155, 77, 150), (225, 120, 177), 150)

# Call
minimize_button.clicked.connect(root.showMinimized)
close_button.clicked.connect(root.close)
search_button.clicked.connect(search_pdf)

# ------------------------------------------- #
# LAYOUTS
if preview_frame.layout() is None:
    preview_frame.setLayout(libs.QVBoxLayout())

if results_frame_layer.layout() is None:
    results_frame_layer.setLayout(libs.QVBoxLayout())

if logs_frame.layout() is None:
    logs_frame.setLayout(libs.QVBoxLayout())

# Configurar la alineación del layout
logs_frame.layout().setAlignment(libs.Qt.AlignTop)  # Alinea los widgets al principio (arriba)
logs_frame.layout().setSpacing(8)

# ------------------------------------------- #

# Mostrar la ventana
root.show()

# Ejecutar la aplicación
libs.sys.exit(app.exec_())