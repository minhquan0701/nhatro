# app_nhatro.py
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import sqlite3
import re
from datetime import datetime
import hashlib
from auth_module import open_owner_login, open_tenant_page  # đăng nhập


# -----------------------
# HÀM KIỂM TRA MẬT KHẨU MẠNH
# -----------------------
def validate_password(pw):
    if len(pw) < 8:
        return "Mật khẩu phải có ít nhất 8 ký tự!"
    if not re.search(r"[A-Z]", pw):
        return "Mật khẩu phải chứa ít nhất 1 chữ in hoa!"
    if not re.search(r"[a-z]", pw):
        return "Mật khẩu phải chứa ít nhất 1 chữ thường!"
    if not re.search(r"[0-9]", pw):
        return "Mật khẩu phải chứa ít nhất 1 chữ số!"
    return None  # hợp lệ

# -----------------------
# DATABASE INIT
# -----------------------
def init_db():
    conn = sqlite3.connect("nhatro.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS User (
            User_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Username TEXT UNIQUE,
            Password TEXT,
            VaiTro INTEGER,
            HoTen TEXT,
            NgaySinh TEXT,
            Email TEXT,
            SDT TEXT,
            CCCD TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# -----------------------
# HÀM ĐĂNG KÝ CHUNG
# -----------------------
def register_user(parent, vaitro, title):
    reg_window = tk.Toplevel(parent)
    reg_window.title(title)
    reg_window.geometry("420x560")
    reg_window.config(bg="#f9f9f9")

    tk.Label(reg_window, text=title, font=("Arial", 14, "bold"), bg="#f9f9f9").pack(pady=12)

    fields = {}
    labels = [
        ("Họ và tên:", "HoTen"),
        ("Ngày sinh (dd/mm/yyyy):", "NgaySinh"),
        ("Email (Gmail):", "Email"),
        ("Số điện thoại:", "SDT"),
        ("CCCD/CMND:", "CCCD"),
        ("Tên đăng nhập:", "Username"),
        ("Mật khẩu:", "Password"),
        ("Nhập lại mật khẩu:", "Confirm")
    ]

    for label, key in labels:
        tk.Label(reg_window, text=label, bg="#f9f9f9").pack(anchor='w', padx=20)
        entry = tk.Entry(reg_window, width=40, show="*" if "Mật khẩu" in label else "")
        entry.pack(pady=4, padx=20)
        fields[key] = entry

    def do_register():
        data = {k: v.get().strip() for k, v in fields.items()}

        # 1. Kiểm tra bắt buộc
        if not all([data["HoTen"], data["Username"], data["Password"], data["Confirm"], data["SDT"], data["Email"]]):
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đủ các trường bắt buộc.")
            return

        # 2. Mật khẩu khớp
        if data["Password"] != data["Confirm"]:
            messagebox.showerror("Lỗi", "Mật khẩu nhập lại không khớp.")
            return

        # 3. Họ tên
        if not re.match(r"^[A-Za-zÀ-ỹ\s]+$", data["HoTen"]):
            messagebox.showerror("Lỗi", "Họ tên chỉ được chứa chữ cái và khoảng trắng.")
            return

        # 4. Ngày sinh
        parsed = None
        if data["NgaySinh"]:
            for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"):
                try:
                    parsed = datetime.strptime(data["NgaySinh"], fmt)
                    break
                except Exception:
                    continue
            if parsed is None:
                # Normalize single-digit day/month
                parts = data["NgaySinh"].replace("-", "/").split("/")
                if len(parts) == 3 and all(part.isdigit() for part in parts):
                    d, m, y = parts
                    d = d.zfill(2)
                    m = m.zfill(2)
                    try:
                        parsed = datetime.strptime(f"{d}/{m}/{y}", "%d/%m/%Y")
                    except Exception:
                        parsed = None
            if parsed is None:
                messagebox.showerror("Lỗi", "Ngày sinh không hợp lệ! Định dạng dd/mm/yyyy.")
                return

        # 5. Email Gmail
        if not re.match(r"^[a-zA-Z0-9._%+-]+@gmail\.com$", data["Email"]):
            messagebox.showerror("Lỗi", "Email không hợp lệ! Vui lòng nhập Gmail.")
            return

        # 6. SĐT
        if not re.match(r"^(0[0-9]{9})$", data["SDT"]):
            messagebox.showerror("Lỗi", "Số điện thoại không hợp lệ! Phải gồm 10 chữ số và bắt đầu bằng 0.")
            return

        # 7. CCCD
        if data["CCCD"]:
            if not re.match(r"^\d{9}$", data["CCCD"]) and not re.match(r"^\d{12}$", data["CCCD"]):
                messagebox.showerror("Lỗi", "CCCD/CMND phải gồm 9 hoặc 12 chữ số.")
                return

        # 8. Username
        if len(data["Username"]) < 4 or " " in data["Username"]:
            messagebox.showerror("Lỗi", "Tên đăng nhập phải có ít nhất 4 ký tự và không chứa khoảng trắng.")
            return

        # 9. Mật khẩu mạnh
        pw_error = validate_password(data["Password"])
        if pw_error:
            messagebox.showerror("Lỗi", pw_error)
            return

        # 10. Lưu vào DB (mã hóa mật khẩu)
        conn = sqlite3.connect("nhatro.db")
        c = conn.cursor()
        try:
            hashed_pw = hashlib.sha256(data["Password"].encode()).hexdigest()
            c.execute("""
                INSERT INTO User (Username, Password, VaiTro, HoTen, NgaySinh, Email, SDT, CCCD)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (data["Username"], hashed_pw, vaitro, data["HoTen"], data["NgaySinh"], data["Email"], data["SDT"], data["CCCD"]))
            conn.commit()
            role_text = "Chủ trọ" if vaitro == 1 else "Người thuê"
            messagebox.showinfo("Thành công", f"Đăng ký {role_text} thành công!")
            reg_window.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Lỗi", "Tên đăng nhập đã tồn tại.")
        finally:
            conn.close()

    tk.Button(reg_window, text="Đăng ký", bg="#4CAF50", fg="white",
              font=("Arial", 11, "bold"), width=18, command=do_register).pack(pady=16)

# -----------------------
# BillingApp (paste nguyên code từ bản gốc)
# -----------------------
class BillingApp:
    def __init__(self, parent, readonly=False):
        # tạo cửa sổ riêng
        self.window = tk.Toplevel(parent)
        self.window.title("Hóa đơn thanh toán")
        self.window.geometry("820x520")
        self.readonly = readonly

        # Danh sách phòng mẫu (nếu muốn có persist cho phòng, có thể thêm bảng SQLite sau)
        self.rooms = ["Phòng 101", "Phòng 102", "Phòng 103"]
        self.rooms_data = {
            room: {"items": [], "total_amount": 0.0, "total_paid": 0.0, "payment_status": "Unpaid"}
            for room in self.rooms
        }
        self.current_room = tk.StringVar(value=self.rooms[0])

        top = tk.Frame(self.window)
        top.pack(pady=8, fill='x')

        self.back_btn = tk.Button(top, text="🔙 Quay lại", width=12, command=self.window.destroy, bg="white")
        self.back_btn.pack(side='left', padx=(8,4))

        tk.Label(top, text="Chọn phòng thuê để thanh toán:").pack(side='left', padx=(6,0))
        self.room_combo = ttk.Combobox(top, values=self.rooms, textvariable=self.current_room, state='readonly', width=22)
        self.room_combo.pack(side='left', padx=6)
        self.room_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_display())

        # badge
        self.status_badge = tk.Label(top, text="", width=16, relief="ridge", bd=2, bg="white")
        self.status_badge.pack(side='left', padx=(8,0))

        btn_frame = tk.Frame(self.window)
        btn_frame.pack(pady=6)

        # nút, nếu read-only thì disable
        btn_state = 'normal' if not self.readonly else 'disabled'
        self.btn_rent = tk.Button(btn_frame, text="💼 Tiền thuê/phòng/tháng", width=22, command=self.add_rent, bg="white", state=btn_state)
        self.btn_rent.grid(row=0, column=0, padx=5, pady=5)
        self.btn_edit_rent = tk.Button(btn_frame, text="🛠️ Sửa giá thuê", width=22, command=self.edit_rent, bg="white", state=btn_state)
        self.btn_edit_rent.grid(row=0, column=1, padx=5, pady=5)
        self.btn_electric = tk.Button(btn_frame, text="⚡ Tiền điện", width=22, command=self.add_electric, bg="white", state=btn_state)
        self.btn_electric.grid(row=0, column=2, padx=5, pady=5)
        self.btn_water = tk.Button(btn_frame, text="💧 Tiền nước", width=22, command=self.add_water, bg="white", state=btn_state)
        self.btn_water.grid(row=1, column=0, padx=5, pady=5)
        self.btn_service = tk.Button(btn_frame, text="🧰 Dịch vụ khác", width=22, command=self.add_service, bg="white", state=btn_state)
        self.btn_service.grid(row=1, column=1, padx=5, pady=5)
        self.btn_update = tk.Button(btn_frame, text="🧾 Cập nhật trạng thái thanh toán", width=22, command=self.update_payment_window, bg="white", state=btn_state)
        self.btn_update.grid(row=1, column=2, padx=5, pady=5)

        self.reset_btn = tk.Button(self.window, text="Reset", command=self.reset, width=20, bg="white", state=btn_state)
        self.reset_btn.pack(pady=5)

        summary_frame = tk.Frame(self.window)
        summary_frame.pack(padx=10, pady=10, fill='both', expand=True)

        self.items_text = tk.Text(summary_frame, height=16, width=86)
        self.items_text.pack(side='left', fill='both', expand=True)
        self.scroll = tk.Scrollbar(summary_frame, command=self.items_text.yview)
        self.scroll.pack(side='right', fill='y')
        self.items_text.config(yscrollcommand=self.scroll.set, state='disabled')

        self.status_label = tk.Label(self.window, text="", anchor='w', justify='left')
        self.status_label.pack(fill='x', padx=10, pady=5)

        self.refresh_display()

    def _status_and_color_from(self, data):
        if data['total_amount'] == 0:
            return "Chưa tính toán", "#f1c40f"
        if data.get('payment_status') == "Paid":
            return "Đã thanh toán", "#28a745"
        return "Chưa thanh toán", "#dc3545"

    def add_rent(self):
        room = self.current_room.get()
        data = self.rooms_data[room]
        if any(it['type'] == 'Rent' for it in data['items']):
            messagebox.showinfo("Thông báo", "Tiền thuê/phòng/tháng đã được thiết lập cho phòng này.")
            return
        amount = simpledialog.askfloat("Nhập Tiền thuê/phòng", "Nhập tiền thuê/phòng theo tháng (VND):", minvalue=0.0)
        if amount is None:
            return
        self._add_item(room, "Rent", amount, "Thuê/phòng theo tháng")

    def edit_rent(self):
        room = self.current_room.get()
        data = self.rooms_data[room]
        rent_item = next((it for it in data['items'] if it['type'] == "Rent"), None)
        if not rent_item:
            messagebox.showinfo("Thông báo", "Chưa thiết lập giá thuê.")
            return
        old = rent_item['amount']
        new = simpledialog.askfloat("Sửa giá thuê", f"Nhập lại giá thuê/phòng (VND) hiện tại {old:.0f}:", minvalue=0.0)
        if new is None:
            return
        delta = new - old
        rent_item['amount'] = new
        self.rooms_data[room]['total_amount'] += delta
        self.refresh_display()

    def add_electric(self):
        room = self.current_room.get()
        consumption = simpledialog.askfloat("Nhập Tiền điện", "Nhập số điện tiêu thụ (kWh):", minvalue=0.0)
        if consumption is None:
            return
        amount = consumption * 4000
        self._add_item(room, "Electricity", amount, f"Điện ({consumption} kWh)")

    def add_water(self):
        room = self.current_room.get()
        consumption = simpledialog.askfloat("Nhập Tiền nước", "Nhập số nước tiêu thụ (m3):", minvalue=0.0)
        if consumption is None:
            return
        amount = consumption * 30000
        self._add_item(room, "Water", amount, f"Nước ({consumption} m3)")

    def add_service(self):
        room = self.current_room.get()
        amount = 100000
        self._add_item(room, "OtherService", amount, "Dịch vụ khác")

    def _add_item(self, room, item_type, amount, description):
        item = {"type": item_type, "amount": amount, "description": description}
        self.rooms_data[room]['items'].append(item)
        self.rooms_data[room]['total_amount'] += amount
        self.refresh_display()

    def update_payment_window(self):
        room = self.current_room.get()
        data = self.rooms_data[room]
        types_present = {it['type'] for it in data['items']}
        required = {'Rent','Electricity','Water','OtherService'}
        if not required.issubset(types_present):
            messagebox.showinfo("Thông báo", "Cần nhập đủ 4 loại phí: Tiền thuê, Tiền điện, Tiền nước, Dịch vụ khác.")
            return

        remaining = data['total_amount'] - data['total_paid']
        if remaining <= 0 and data.get('payment_status') == "Paid":
            messagebox.showinfo("Thông báo", f"Phòng {room} đã thanh toán đầy đủ.")
            return

        win = tk.Toplevel(self.window)
        win.title("Cập nhật trạng thái thanh toán")
        win.geometry("360x210")
        tk.Label(win, text=f"Cập nhật trạng thái thanh toán cho {room}", font=('Arial', 12, 'bold')).pack(pady=8)

        def set_paid():
            data['total_paid'] = max(data['total_paid'], data['total_amount'])
            data['payment_status'] = "Paid"
            win.destroy()
            self.refresh_display()
            messagebox.showinfo("Thông báo", f"Phòng {room} thanh toán thành công.")

        def set_unpaid():
            data['payment_status'] = "Unpaid"
            win.destroy()
            self.refresh_display()
            messagebox.showinfo("Thông báo", f"Phòng {room} đã được chuyển sang trạng thái chưa thanh toán.")

        tk.Button(win, text="✅ Đã thanh toán", width=16, command=set_paid).pack(pady=6)
        tk.Button(win, text="❌ Chưa thanh toán", width=16, command=set_unpaid).pack(pady=6)

    def reset(self):
        for r in self.rooms:
            self.rooms_data[r] = {"items": [], "total_amount": 0.0, "total_paid": 0.0, "payment_status": "Unpaid"}
        self.refresh_display()

    def refresh_display(self):
        room = self.current_room.get()
        data = self.rooms_data[room]
        self.items_text.config(state='normal')
        self.items_text.delete('1.0', tk.END)
        self.items_text.insert(tk.END, f"Phòng: {room}\n")
        self.items_text.insert(tk.END, "Danh sách khoản phí:\n")
        if not data['items']:
            self.items_text.insert(tk.END, "Chưa có khoản phí nào được thêm cho phòng này.\n")
        else:
            for idx, item in enumerate(data['items'], start=1):
                type_name_map = {
                    'Rent': 'Tiền thuê/phòng',
                    'Electricity': 'Tiền điện',
                    'Water': 'Tiền nước',
                    'OtherService': 'Dịch vụ khác'
                }
                display_type = type_name_map.get(item['type'], item['type'])
                self.items_text.insert(tk.END, f"{idx}. {display_type}: {item['amount']:.0f} VND - {item['description']}\n")
        self.items_text.config(state='disabled')

        status, color = self._status_and_color_from(data)
        self.status_badge.config(text=status, bg=color)

        balance = data['total_amount'] - data['total_paid']
        summary = (
            f"Tổng số tiền: {data['total_amount']:.0f} VND\n"
            f"Đã thanh toán:   {data['total_paid']:.0f} VND\n"
            f"Số nợ:      {max(balance,0):.0f} VND\n"
            f"Trạng thái:   {status}"
        )
        self.status_label.config(text=summary)

# -----------------------
# GIAO DIỆN CHÍNH
# -----------------------
def main():
    root = tk.Tk()
    root.title("Ứng dụng Quản lý Nhà trọ")
    root.geometry("440x360")
    root.config(bg="#f2f2f2")

    tk.Label(root, text="Chào mừng đến với Ứng dụng Quản lý Nhà trọ",
             font=("Arial", 14, "bold"), bg="#f2f2f2", wraplength=380, justify="center").pack(pady=28)

    tk.Button(root, text="👑 Chủ trọ", font=("Arial", 12, "bold"),
              bg="#4CAF50", fg="white", width=18, height=2,
              command=lambda: open_owner_login(root)).pack(pady=8)

    tk.Button(root, text="🏠 Người thuê", font=("Arial", 12, "bold"),
              bg="#2196F3", fg="white", width=18, height=2,
              command=lambda: open_tenant_page(root)).pack(pady=6)

    tk.Label(root, text="© 2025 - Ứng dụng Quản lý Nhà trọ", font=("Arial", 9), bg="#f2f2f2", fg="gray").pack(side="bottom", pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
