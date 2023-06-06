import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
from PIL import ImageTk, Image

class Obrazki:
    def __init__(self, master):
        self.master = master
        self.master.title("Obrazki")

        self.image_path = None
        self.original_image = None
        self.processed_image = None

        self.create_widgets()

    def create_widgets(self):
        # Przyciski do wywołania funkcji przetwarzających obraz
        self.reconstruction_button = tk.Button(self.master, text="Algorytm rekonstrukcji", command=self.reconstruction)
        self.reconstruction_button.grid(row=0, column=0, padx=10, pady=10)

        self.marker_reconstruction_button = tk.Button(self.master, text="Rekonstrukcja markerów", command=self.marker_reconstruction)
        self.marker_reconstruction_button.grid(row=0, column=1, padx=10, pady=10)

        self.clean_edges_button = tk.Button(self.master, text="Czyszczenie brzegów", command=self.clean_edges)
        self.clean_edges_button.grid(row=0, column=2, padx=10, pady=10)

        self.fill_holes_button = tk.Button(self.master, text="Zalewanie otworów", command=self.fill_holes)
        self.fill_holes_button.grid(row=0, column=3, padx=10, pady=10)

        # Przycisk do wczytywania obrazu
        self.load_image_button = tk.Button(self.master, text="Wczytaj obraz", command=self.load_image)
        self.load_image_button.grid(row=1, column=0, padx=10, pady=10)

        # Wyświetlanie obrazu
        self.original_image_label = tk.Label(self.master)
        self.original_image_label.grid(row=2, column=0, padx=5, pady=5)

        self.processed_image_label = tk.Label(self.master)
        self.processed_image_label.grid(row=2, column=1, padx=5, pady=5)

        self.processed_image_label = tk.Label(self.master)
        self.processed_image_label.grid(row=2, column=1, padx=10, pady=10)

        self.all_operations_button = tk.Button(self.master, text="Wykonaj wszystkie operacje",command=self.perform_all_operations)
        self.all_operations_button.grid(row=0, column=4, padx=10, pady=10)

    def load_image(self):
        # Wczytanie obrazu z pliku
        self.image_path = filedialog.askopenfilename(filetypes=[("Plik obrazu", "*.jpg;*.jpeg;*.png;*.bmp")])
        if self.image_path:
            self.original_image = cv2.imread(self.image_path, cv2.IMREAD_COLOR)

            # Konwersja obrazu do formatu obsługiwanego przez Tkinter
            img_rgb = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(img_rgb)
            img_resized = img_pil.resize((350, 350))
            img_tk = ImageTk.PhotoImage(img_resized)

            # Wyświetlenie obrazu w interfejsie
            self.original_image_label.config(image=img_tk)
            self.original_image_label.image = img_tk

    def reconstruction(self):
        if self.original_image is not None:
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            marker = cv2.erode(self.original_image, kernel)
            self.processed_image = cv2.dilate(marker, kernel)
            self.show_processed_image()

    def marker_reconstruction(self):
        if self.original_image is not None:
            marker = np.zeros_like(self.original_image)
            marker[50:100, 50:100] = [255, 0, 0]  # Ustawienie czerwonego markeru
            mask = cv2.dilate(marker, np.ones((3, 3), np.uint8))
            prev_mask = np.zeros_like(mask)
            while not np.array_equal(mask, prev_mask):
                prev_mask = mask
                mask = cv2.erode(mask, np.ones((3, 3), np.uint8))
                mask = cv2.max(self.original_image, mask)
            self.processed_image = mask
            self.show_processed_image()

    def clean_edges(self):
        if self.original_image is not None:
            kernel = np.ones((5, 5), np.uint8)
            mask = cv2.morphologyEx(self.original_image, cv2.MORPH_CLOSE, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            mask[0, :] = [255, 255, 255]
            mask[-1, :] = [255, 255, 255]
            mask[:, 0] = [255, 255, 255]
            mask[:, -1] = [255, 255, 255]
            self.processed_image = mask
            self.show_processed_image()

    def fill_holes(self):
        if self.original_image is not None:
            # Konwertowanie obrazu do skali szarości
            gray_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)

            # Binaryzacja obrazu
            _, binary_image = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)

            # Wypełnianie otworów
            filled_image = binary_image.copy()
            contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                cv2.drawContours(filled_image, [cnt], 0, 255, -1)

            # Odwrócenie obrazu
            filled_image = cv2.bitwise_not(filled_image)

            self.processed_image = filled_image
            self.show_processed_image()

    def perform_all_operations(self):
        if self.original_image is not None:
            self.reconstruction()
            self.marker_reconstruction()
            self.clean_edges()
            self.fill_holes()
            self.show_processed_image()

    def show_processed_image(self):
        if self.processed_image is not None:
            # Konwersja obrazu do formatu obsługiwanego przez Tkinter
            img_rgb = cv2.cvtColor(self.processed_image, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(img_rgb)
            img_resized = img_pil.resize((350, 350))
            img_tk = ImageTk.PhotoImage(img_resized)

            # Wyświetlenie przetworzonego obrazu w interfejsie
            self.processed_image_label.config(image=img_tk)
            self.processed_image_label.image = img_tk


root = tk.Tk()
app = Obrazki(root)
root.mainloop()