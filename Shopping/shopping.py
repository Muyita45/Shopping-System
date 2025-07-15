import sqlite3
import hashlib
from tabulate import tabulate

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()
def register_user():
    conn = sqlite3.connect('Kullanici_veritabanı.db')  # DB adı Türkçe kaldı
    cur = conn.cursor()

    choice = input("Press (1) to return to menu\nPress any other key to continue registration\n=> ")
    if choice == "1":
        return

    print("\nWelcome to the Registration System\n")
    while True:
        username = input("Enter your username: ").strip().lower()
        cur.execute("SELECT * FROM kullanicilar WHERE kullanici_adi = ?", (username,))
        if cur.fetchone():
            print("This username is already taken. Please choose a different one.")
        else:
            break

    password = input("Enter your desired password: ").strip()
    hashed_password = hash_password(password)

    while True:
        phone = input("Enter your 11-digit phone number: ").strip()
        if len(phone) != 11 or not phone.isdigit():
            print("Please enter a valid 11-digit phone number.")
            continue
        cur.execute("SELECT * FROM kullanicilar WHERE telefon = ?", (phone,))
        if cur.fetchone():
            print("This phone number is already registered. Please use another number or log in.")
            continue
        break

    address = input("Enter your address: ").strip()

    print("\nYou must add a card for payment. Please enter the details correctly.")

    while True:
        card_number = input("Enter your 16-digit card number: ").replace(" ", "")
        if len(card_number) != 16 or not card_number.isdigit():
            print("Please enter a valid 16-digit card number.")
            continue
        break

    while True:
        cvv = input("Enter your 3-digit CVV code: ").strip()
        if len(cvv) != 3 or not cvv.isdigit():
            print("Please enter a valid 3-digit CVV code.")
            continue
        break

    while True:
        expiry_input = input("Enter expiration date (MM YY): ").strip()
        expiry_date = expiry_input.replace(" ", "")
        if len(expiry_date) != 4 or not expiry_date.isdigit():
            print("Please enter a valid date in MMYY format.")
            continue
        break

    try:
        cur.execute("""
            INSERT INTO kullanicilar 
            (kullanici_adi, sifre, telefon, adres, kart_numarasi, cvv, son_kullanma_tarihi) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (username, hashed_password, phone, address, card_number, cvv, expiry_date))
        conn.commit()
        print(f"\nCongratulations {username}, you have successfully registered!")
    except sqlite3.IntegrityError as e:
        print("Database error occurred: ", e)
    finally:
        conn.close()
def login_user():
    conn = sqlite3.connect('Kullanici_veritabanı.db')
    cur = conn.cursor()

    print("\nWelcome to the Login Panel\n")

    username = input("Enter your username: ").strip().lower()
    password = input("Enter your password: ").strip()
    hashed_password = hash_password(password)

    cur.execute("SELECT * FROM kullanicilar WHERE kullanici_adi = ? AND sifre = ?", (username, hashed_password))
    user = cur.fetchone()

    if user:
        print(f"\nWelcome, {username}! You have successfully logged in.")
        shop(username)
    else:
        print("\nInvalid username or password. Please try again.")
    conn.close()
def admin_panel():
    conn = sqlite3.connect('Kullanici_veritabanı.db')
    cur = conn.cursor()

    while True:
        choice = input(
            "\n1) List all users\n"
            "2) Delete user\n"
            "3) Search user\n"
            "4) Add/Update product\n"
            "5) Delete product\n"
            "6) Check stock\n"
            "7) Create coupon\n"
            "9) Return to main menu\n"
            "=> "
        )
        if choice == "1":
            cur.execute("SELECT kullanici_adi, telefon, adres FROM kullanicilar")
            users = cur.fetchall()
            if users:
                table = tabulate(users, headers=["Username", "Phone", "Address"], tablefmt="fancy_grid")
                print("\nRegistered Users:\n")
                print(table)
            else:
                print("No users found.")

        elif choice == "2":
            username = input("Enter the username to delete: ").strip().lower()
            cur.execute("SELECT * FROM kullanicilar WHERE kullanici_adi = ?", (username,))
            if cur.fetchone():
                cur.execute("DELETE FROM kullanicilar WHERE kullanici_adi = ?", (username,))
                conn.commit()
                print(f"User '{username}' has been deleted.")
            else:
                print("No such user found.")

        elif choice == "3":
            search = input("Enter username to search: ")
            cur.execute("SELECT * FROM kullanicilar WHERE kullanici_adi = ?", (search,))
            result = cur.fetchone()
            if result:
                print("User found:", result)
            else:
                print("User not found.")

        elif choice == "4":
            print("\nAdd/Update Product")
            category = input("Enter category: ").strip().capitalize()
            name = input("Enter product name: ").strip().capitalize()
            cur.execute("SELECT * FROM urunler WHERE kategori = ? AND isim = ?", (category, name))
            existing_product = cur.fetchone()
            try:
                price = int(input("Price: "))
                stock = int(input("Stock quantity: "))
            except ValueError:
                print("Price and stock must be numbers.")
                conn.close()
                return
            if existing_product:
                cur.execute("""
                    UPDATE urunler
                    SET fiyat = ?, stok = ?
                    WHERE kategori = ? AND isim = ?
                """, (price, stock, category, name))
                print(f"Product '{name}' updated (category: {category})")
            else:
                cur.execute("""
                    INSERT INTO urunler (kategori, isim, fiyat, stok)
                    VALUES (?, ?, ?, ?)
                """, (category, name, price, stock))
                print(f"Product '{name}' added (category: {category})")
            conn.commit()

        elif choice == "5":
            print("\nDelete Product")
            category = input("Enter category of product to delete: ").strip().capitalize()
            name = input("Enter product name to delete: ").strip().capitalize()
            cur.execute("SELECT * FROM urunler WHERE kategori = ? AND isim = ?", (category, name))
            product = cur.fetchone()
            if product:
                confirm = input(f"Are you sure you want to delete '{name}'? (y/n): ").strip().lower()
                if confirm == "y":
                    cur.execute("DELETE FROM urunler WHERE kategori = ? AND isim = ?", (category, name))
                    conn.commit()
                    print(f"Product '{name}' deleted.")
                else:
                    print("Delete operation cancelled.")
            else:
                print("Product not found.")

        elif choice == "6":
            limit = int(input("Show products with stock less than or equal to: "))
            cur.execute("SELECT kategori, isim, fiyat, stok FROM urunler WHERE stok <= ?", (limit,))
            low_stock = cur.fetchall()
            if low_stock:
                print("\nLow Stock Products:\n")
                print(tabulate(low_stock, headers=["Category", "Name", "Price", "Stock"], tablefmt="fancy_grid"))
            else:
                print("All products have sufficient stock.")

        elif choice == "7":
            coupon_code = input("Enter new coupon code: ")
            quantity = input("Enter coupon quantity: ")
            min_cart = input("Minimum cart total for discount: ")
            discount = input("Discount amount: ")

            cur.execute("""
                INSERT INTO kupon (kod, adet, minsepet, indirim)
                VALUES (?, ?, ?, ?)
            """, (coupon_code, quantity, min_cart, discount))
            conn.commit()
            print("Coupon created successfully.")

        elif choice == "9":
            print("Returning to main menu...")
            break
        else:
            print("Invalid choice! Please select a valid option.")
    conn.close()
def shop(username):
    conn = sqlite3.connect('Kullanici_veritabanı.db')
    cur = conn.cursor()

    while True:
        option = input(
            "1) Show all products\n"
            "2) Select category\n"
            "3) Search product\n"
            "8) Exit\n"
            "9) View cart\n"
            "=> "
        )
        if option == "1":
            cur.execute("SELECT rowid, kategori, isim, fiyat, stok FROM urunler")
            products = cur.fetchall()
            if products:
                print("\nAll Products:\n")
                print(tabulate(products, headers=["ID", "Category", "Name", "Price", "Stock"], tablefmt="fancy_grid"))
                add_to_cart(conn)
            else:
                print("No products found.")

        elif option == "2":
            category = input("Enter category: ").strip().capitalize()
            cur.execute("SELECT rowid, kategori, isim, fiyat, stok FROM urunler WHERE kategori = ?", (category,))
            products = cur.fetchall()
            if not products:
                print(f"\nNo products found in category: {category}")
            else:
                print(f"\nProducts in {category}:\n")
                print(tabulate(products, headers=["ID", "Category", "Name", "Price", "Stock"], tablefmt="fancy_grid"))
                add_to_cart(conn)

        elif option == "3":
            search = input("Enter product name: ").strip().capitalize()
            cur.execute("SELECT rowid, kategori, isim, fiyat, stok FROM urunler WHERE isim = ?", (search,))
            result = cur.fetchall()
            if result:
                print(tabulate(result, headers=["ID", "Category", "Name", "Price", "Stock"], tablefmt="fancy_grid"))
                add_to_cart(conn)
            else:
                print("Product not found.")

        elif option == "8":
            break

        elif option == "9":
            view_cart(username, conn)
def add_to_cart(conn):
    cur = conn.cursor()
    try:
        product_id = int(input("\nEnter the ID of the product you want: "))
    except ValueError:
        print("Invalid ID! Must be a number.")
        return
    cur.execute("SELECT rowid, isim, fiyat, stok FROM urunler WHERE rowid = ?", (product_id,))
    product = cur.fetchone()
    if product:
        id, name, price, stock = product
        if stock == 0:
            print(f"Sorry, '{name}' is out of stock.")
        else:
            try:
                quantity = int(input(f"How many of '{name}' do you want? "))
            except ValueError:
                print("Invalid input. Must be a number.")
                return
            if quantity <= 0:
                print("Quantity must be greater than zero.")
            elif quantity > stock:
                print(f"Only {stock} units available.")
            else:
                total = price * quantity
                cart.append([id, name, quantity, price, total])
                new_stock = stock - quantity
                cur.execute("UPDATE urunler SET stok = ? WHERE rowid = ?", (new_stock, product_id))
                conn.commit()
                print(f"{quantity} unit(s) of '{name}' added to cart.")
    else:
        print("Product ID not found.")
def view_cart(username, conn):
    cur = conn.cursor()
    while True:
        total_cart = 0
        cart_table = []
        print("\nYour Cart:\n")
        for item in cart:
            total_cart += item[4]
            cart_table.append(item)
        if cart_table:
            print(tabulate(cart_table, headers=["ID", "Product", "Quantity", "Price", "Total"], tablefmt="fancy_grid"))
            print(f"\nTotal Price = {total_cart}")
        else:
            print("Your cart is empty.")
        option = input(
            "1) Remove product\n"
            "2) Clear cart\n"
            "3) Checkout\n"
            "9) Go back\n"
            "=> "
        )

        if option == "1":
            if not cart:
                print("Cart is already empty.")
            try:
                remove_id = int(input("Enter the ID of the product to remove: "))
            except ValueError:
                print("Invalid number.")
            removed = False
            for item in cart:
                if item[0] == remove_id:
                    cart.remove(item)
                    print(f"{item[1]} removed from cart.")
                    removed = True
                    break
            if not removed:
                print("Product ID not found in cart.")

        elif option == "2":
            if not cart:
                print("Cart is already empty.")
            else:
                confirm = input("Are you sure you want to clear the cart? (y/n): ").lower()
                if confirm == "y":
                    cart.clear()
                    print("Cart cleared.")
                else:
                    print("Operation cancelled.")

        elif option == "3":
            coupon_code = input("Do you have a coupon code? (y/n): ").lower()
            final_total = total_cart
            if coupon_code == "y":
                code_input = input("Enter coupon code: ").strip().upper()
                cur.execute("SELECT kod, adet, minsepet, indirim FROM kupon WHERE kod = ?", (code_input,))
                coupon = cur.fetchone()
                if coupon:
                    code, quantity, min_cart, discount = coupon
                    if int(quantity) <= 0:
                        print("This coupon is no longer valid (used up).")
                    elif total_cart < float(min_cart):
                        print(f"Minimum cart total must be {min_cart} to use this coupon.")
                    else:
                        final_total -= float(discount)
                        print(f"Coupon applied! {discount} discount applied. New total: {final_total} ₺")
                        cur.execute("UPDATE kupon SET adet = adet - 1 WHERE kod = ?", (code_input,))
                        conn.commit()
                else:
                    print("Invalid coupon code.")
            else:
                print("No coupon applied.")
            make_payment(username, conn)
            break

        elif option == "9":
            break
def make_payment(username, conn):
    cur = conn.cursor()
    cur.execute("SELECT kart_numarasi, cvv, son_kullanma_tarihi FROM kullanicilar WHERE kullanici_adi = ?", (username,))
    card_info = cur.fetchone()
    if card_info:
        card_number, cvv, expiry = card_info
        print(f"Card: **** **** **** {card_number[-4:]}  (Expiry: {expiry[:2]}/{expiry[2:]})")
        while True:
            input_cvv = input("Enter CVV to proceed (or 0 to cancel): ").strip()
            if input_cvv == cvv:
                print("Payment successful.\n\n")
                break
            elif input_cvv == "0":
                break
            else:
                print("CVV does not match.")
cart = []
while True:
    main_menu = input(
        "\nLogin => (1)\n"
        "Admin Login => (2)\n"
        "New Registration => (3)\n"
        "Exit => (5)\n=> "
    )
    if main_menu == "1":
        login_user()
    elif main_menu == "2":
        admin_password = input("Enter admin password: ")
        if admin_password == "admin45":
            admin_panel()
        else:
            print("Incorrect password.")
    elif main_menu == "3":
        register_user()
    elif main_menu == "5":
        print("Exiting...")
        break
    else:
        print("Please enter a valid option.")
