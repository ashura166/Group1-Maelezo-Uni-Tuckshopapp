import tkinter as tk
from tkinter import messagebox
from google.cloud import firestore
from google.oauth2 import service_account
import firebase_admin
from firebase_admin import credentials
import threading
import os

# Initialize Firebase only if it hasn't been initialized yet
if not firebase_admin._apps:
    cred = service_account.Credentials.from_service_account_file(
        'C:/Users/asha/Maelezo Uni Tuckshop/ServiceAccountKey.json'
    )
    firebase_admin.initialize_app(cred)

# Replace with your service account JSON file path
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\asha\Maelezo Uni Tuckshop\ServiceAccountKey.json"

# Initialize Firestore client
db = firestore.Client()
# Firebase references
items_ref = db.collection('items')
offers_ref = db.collection('offers')
purchases_ref = db.collection('purchases')

# Admin credentials
admin_username = "Admin"
admin_password = "1234"

class TuckShopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tuck Shop Admin")
        self.root.geometry("800x600")  # Increase the size of the window
        self.root.configure(bg='light blue')  # Set background color to light blue

        self.login_frame = tk.Frame(self.root, bg='light blue')
        self.login_frame.place(relx=0.5, rely=0.5, anchor='center')  # Center the login frame

        self.username_label = tk.Label(self.login_frame, text="Admin Username:", bg='light blue', font=('Arial', 16))
        self.username_label.grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.username_entry = tk.Entry(self.login_frame, bg='white', font=('Arial', 16), width=30)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)

        self.password_label = tk.Label(self.login_frame, text="Admin Password:", bg='light blue', font=('Arial', 16))
        self.password_label.grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.password_entry = tk.Entry(self.login_frame, show="*", bg='white', font=('Arial', 16), width=30)
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        self.login_button = tk.Button(self.login_frame, text="Login", command=self.do_login, bg='white', font=('Arial', 16))
        self.login_button.grid(row=2, column=0, columnspan=2, pady=10)

        self.login_message = tk.Label(self.login_frame, text="", fg="red", bg='light blue', font=('Arial', 16))
        self.login_message.grid(row=3, column=0, columnspan=2)

    def do_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if username == admin_username and password == admin_password:
            self.login_frame.place_forget()
            self.create_main_frame()
            # Load items and offers in a separate thread
            threading.Thread(target=self.load_items).start()
            threading.Thread(target=self.load_offers).start()
        else:
            self.login_message.config(text="Invalid credentials. Please try again.")

    def create_main_frame(self):
        self.main_frame = tk.Frame(self.root, bg='light blue')
        self.main_frame.pack(pady=20)

        self.item_name_label = tk.Label(self.main_frame, text="Item Name:", bg='light blue', font=('Arial', 16))
        self.item_name_label.grid(row=0, column=0, padx=5, pady=5)
        self.item_name_entry = tk.Entry(self.main_frame, bg='white', font=('Arial', 16))
        self.item_name_entry.grid(row=0, column=1, padx=5, pady=5)

        self.item_price_label = tk.Label(self.main_frame, text="Item Price:", bg='light blue', font=('Arial', 16))
        self.item_price_label.grid(row=1, column=0, padx=5, pady=5)
        self.item_price_entry = tk.Entry(self.main_frame, bg='white', font=('Arial', 16))
        self.item_price_entry.grid(row=1, column=1, padx=5, pady=5)

        self.item_category_label = tk.Label(self.main_frame, text="Item Category:", bg='light blue', font=('Arial', 16))
        self.item_category_label.grid(row=2, column=0, padx=5, pady=5)
        self.item_category_entry = tk.Entry(self.main_frame, bg='white', font=('Arial', 16))
        self.item_category_entry.grid(row=2, column=1, padx=5, pady=5)

        self.add_item_button = tk.Button(self.main_frame, text="Add Item", command=self.add_item, bg='white', font=('Arial', 16))
        self.add_item_button.grid(row=3, column=0, columnspan=2, pady=10)

        self.items_listbox = tk.Listbox(self.main_frame, bg='white', font=('Arial', 16), width=50, height=8)
        self.items_listbox.grid(row=4, column=0, columnspan=2, pady=10)

        self.offers_listbox = tk.Listbox(self.main_frame, bg='white', font=('Arial', 16), width=50, height=4)
        self.offers_listbox.grid(row=5, column=0, columnspan=2, pady=10)

        self.purchase_item_name_label = tk.Label(self.main_frame, text="Item Name to Purchase:", bg='light blue', font=('Arial', 16))
        self.purchase_item_name_label.grid(row=6, column=0, padx=5, pady=5)
        self.purchase_item_name_entry = tk.Entry(self.main_frame, bg='white', font=('Arial', 16))
        self.purchase_item_name_entry.grid(row=6, column=1, padx=5, pady=5)

        self.purchase_quantity_label = tk.Label(self.main_frame, text="Quantity:", bg='light blue', font=('Arial', 16))
        self.purchase_quantity_label.grid(row=7, column=0, padx=5, pady=5)
        self.purchase_quantity_entry = tk.Entry(self.main_frame, bg='white', font=('Arial', 16))
        self.purchase_quantity_entry.grid(row=7, column=1, padx=5, pady=5)

        self.purchase_item_button = tk.Button(self.main_frame, text="Purchase Item", command=self.purchase_item, bg='white', font=('Arial', 16))
        self.purchase_item_button.grid(row=8, column=0, columnspan=2, pady=10)

        self.purchase_message = tk.Label(self.main_frame, text="", fg="green", bg='light blue', font=('Arial', 16))
        self.purchase_message.grid(row=9, column=0, columnspan=2)

    def load_items(self):
        self.items_listbox.delete(0, tk.END)
        try:
            items = items_ref.stream()
            for item in items:
                item_data = item.to_dict()
                self.root.after(0, self.items_listbox.insert, tk.END, f"{item_data['name']} - {item_data['price']}")
        except Exception as e:
            print(f"Error loading items: {e}")

    def load_offers(self):
        self.offers_listbox.delete(0, tk.END)
        try:
            offers = offers_ref.stream()
            for offer in offers:
                offer_data = offer.to_dict()
                self.root.after(0, self.offers_listbox.insert, tk.END, offer_data['description'])
        except Exception as e:
            print(f"Error loading offers: {e}")

    def add_item(self):
        name = self.item_name_entry.get()
        price = self.item_price_entry.get()
        category = self.item_category_entry.get()
        if name and price and category:
            items_ref.add({
                'name': name,
                'price': price,
                'category': category
            })
            self.load_items()
            self.item_name_entry.delete(0, tk.END)
            self.item_price_entry.delete(0, tk.END)
            self.item_category_entry.delete(0, tk.END)

    def purchase_item(self):
        item_name = self.purchase_item_name_entry.get()
        quantity = int(self.purchase_quantity_entry.get())
        items = items_ref.where('name', '==', item_name).stream()
        for item in items:
            item_data = item.to_dict()
            total_price = int(item_data['price'].split()[1]) * quantity
            purchase = {
                'item_id': item.id,
                'item_name': item_data['name'],
                'quantity': quantity,
                'total_price': f"Ksh {total_price}"
            }
            purchases_ref.add(purchase)
            self.purchase_message.config(text=f"Purchase successful! Total price: {purchase['total_price']}")
            self.purchase_item_name_entry.delete(0, tk.END)
            self.purchase_quantity_entry.delete(0, tk.END)
            return
        self.purchase_message.config(text="Item not found.")

if __name__ == '__main__':
    root = tk.Tk()
    app = TuckShopApp(root)
    root.mainloop()