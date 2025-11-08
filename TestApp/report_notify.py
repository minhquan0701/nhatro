import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# Danh sách phòng
rooms = ["P101", "P102", "P103", "P201", "P202", "P203"]

# Dữ liệu doanh thu mẫu
revenues = {
    (2025, 1): {"P101": 950, "P102": 1150, "P103": 980, "P201": 1250, "P202": 970, "P203": 1100},
    (2025, 2): {"P101": 920, "P102": 1120, "P103": 990, "P201": 1180, "P202": 980, "P203": 1080},
    (2025, 3): {"P101": 980, "P102": 1200, "P103": 990, "P201": 1300, "P202": 1000, "P203": 1120},
    (2025, 4): {"P101": 1000, "P102": 1180, "P103": 970, "P201": 1250, "P202": 990, "P203": 1100},
}

def get_revenue(year, month):
    return revenues.get((year, month), {})

def show_monthly_report(parent):
    # Ẩn giao diện chính
    parent.withdraw()

    win = tk.Toplevel(parent)
    win.title("📈 Báo cáo doanh thu tháng")

    # Khi đóng cửa sổ con, hiện lại giao diện chính
    def on_close():
        win.destroy()
        parent.deiconify()

    win.protocol("WM_DELETE_WINDOW", on_close)

    # Nút quay lại ở đầu cửa sổ (quay về giao diện chính)
    header = tk.Frame(win)
    header.pack(fill='x', padx=5, pady=5)
    back_btn = tk.Button(header, text="⬅️ Quay lại", command=on_close)
    back_btn.pack(side='left')

    top = tk.Frame(win)
    top.pack(padx=10, pady=5, anchor="w")

    current = datetime.now()
    year_var = tk.IntVar(value=current.year)
    month_var = tk.IntVar(value=current.month)

    tk.Label(top, text="Năm:").grid(row=0, column=0, sticky='e')
    year_spin = tk.Spinbox(top, from_=2000, to=2100, textvariable=year_var, width=6)
    year_spin.grid(row=0, column=1, padx=5)

    tk.Label(top, text="Tháng:").grid(row=0, column=2, sticky='e')
    month_spin = tk.Spinbox(top, from_=1, to=12, textvariable=month_var, width=4)
    month_spin.grid(row=0, column=3, padx=5)

    # Text hiển thị báo cáo ở chế độ read-only
    result = tk.Text(win, width=60, height=15, state='disabled')
    result.pack(padx=10, pady=5)

    def on_report():
        y = int(year_var.get())
        m = int(month_var.get())
        data = get_revenue(y, m)
        total = sum(data.values())

        # Mở để ghi và sau đó đóng lại để khóa chỉnh sửa
        result.config(state='normal')
        result.delete(1.0, tk.END)
        result.insert(tk.END, f"Báo cáo doanh thu tháng {y}-{m:02d}\n\n")
        for r in rooms:
            amount = data.get(r, 0)
            result.insert(tk.END, f"{r}: {amount}\n")
        result.insert(tk.END, f"\nTổng doanh thu: {total}\n")
        result.config(state='disabled')  # khóa lại để người dùng chỉ xem

    ttk.Button(top, text="📊 Tổng hợp", command=on_report).grid(row=0, column=4, padx=5)

def show_notify_window(parent):
    # Ẩn giao diện chính
    parent.withdraw()

    win = tk.Toplevel(parent)
    win.title("Gửi thông báo")

    # Đảm bảo khi đóng cửa sổ con sẽ hiện lại giao diện chính
    def on_close():
        win.destroy()
        parent.deiconify()

    win.protocol("WM_DELETE_WINDOW", on_close)

    # Nút quay lại ở đầu cửa sổ để quay lại giao diện chính
    header = tk.Frame(win)
    header.pack(fill='x', padx=5, pady=5)
    back_btn = tk.Button(header, text="⬅️ Quay lại", command=on_close)
    back_btn.pack(side='left')

    content = tk.Frame(win)
    content.pack(fill="both", expand=True)

    # Hàm xóa nội dung hiện tại
    def clear_content():
        for w in content.winfo_children():
            w.destroy()

    # Màn hình chọn loại thông báo (2 nút lớn)
    def render_type_selection():
        clear_content()

        # Hai nút lớn với icon
        btn_common = tk.Button(content, text="✉️ Thông báo chung", 
                               bg="#FFFFFF", fg="black",
                               font=("Segoe UI", 14, "bold"),
                               padx=20, pady=18, command=render_common)
        btn_private = tk.Button(content, text="💬 Thông báo riêng",
                                bg="#FFFFFF", fg="black",
                                font=("Segoe UI", 14, "bold"),
                                padx=20, pady=18, command=render_private)

        btn_common.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        btn_private.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        content.grid_rowconfigure(0, weight=1)
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=1)

    # Màn hình thông báo chung
    def render_common():
        clear_content()

        back = tk.Button(content, text="⬅️ Quay lại", command=render_type_selection)
        back.pack(anchor='w', padx=5, pady=5)

        predefined = [
            "Cầu thang máy bị hỏng vui lòng dùng thang bộ.",
            "Nước bị cắt 1 ngày mọi người hãy chuẩn bị kĩ.",
            "Ngày mai đến lịch đổ rác mọi người hãy mang rác ra ngoài."
        ]
        common_frame = tk.Frame(content)
        common_frame.pack(fill="both", expand=True, padx=5, pady=5)

        common_vars = [tk.BooleanVar(value=False) for _ in predefined]

        for i, msg in enumerate(predefined):
            cb = tk.Checkbutton(common_frame, text=msg, anchor='w', variable=common_vars[i])
            cb.pack(anchor='w')

        tk.Label(common_frame, text="📝 Nhập thông báo:").pack(anchor='w')
        common_manual = tk.Text(common_frame, height=3, width=40)
        common_manual.pack()

        status = tk.StringVar(value="Chưa gửi")
        tk.Label(common_frame, textvariable=status).pack(side="bottom", fill="x")

        def build_message():
            msgs = [predefined[i] for i, v in enumerate(common_vars) if v.get()]
            manual_msg = common_manual.get("1.0", tk.END).strip()
            final = " ".join(msgs)
            if manual_msg:
                final = (final + " " if final else "") + manual_msg
            return final.strip()

        def send_all():
            message = build_message()
            if not message:
                messagebox.showwarning("Cảnh báo", "Vui lòng nhập nội dung thông báo.")
                return
            print("Gửi thông báo chung tới tất cả các phòng:", message)
            status.set("Đã gửi thông báo chung tới tất cả các phòng.")

        btn_send = ttk.Button(common_frame, text="📤 Gửi", command=send_all)
        btn_send.pack(pady=5)

    # Màn hình thông báo riêng
    def render_private():
        clear_content()

        back = tk.Button(content, text="⬅️ Quay lại", command=render_type_selection)
        back.pack(anchor='w', padx=5, pady=5)

        private_frame = tk.Frame(content)
        private_frame.pack(fill="both", expand=True, padx=5, pady=5)

        tk.Label(private_frame, text="🗂️ Chọn phòng nhận thông báo:").pack(anchor='w')
        private_rooms = tk.Listbox(private_frame, selectmode='multiple', height=6)
        for r in rooms:
            private_rooms.insert(tk.END, r)
        private_rooms.pack()

        tk.Label(private_frame, text="📝 Nhập thông báo:").pack(anchor='w')
        private_manual = tk.Text(private_frame, height=3, width=40)
        private_manual.pack()

        status = tk.StringVar(value="Chưa gửi")
        tk.Label(private_frame, textvariable=status).pack(side="bottom", fill="x")

        def send_private():
            indices = private_rooms.curselection()
            if not indices:
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn ít nhất một phòng.")
                return
            selected_rooms = [private_rooms.get(i) for i in indices]
            message = private_manual.get("1.0", tk.END).strip()
            if not message:
                messagebox.showwarning("Cảnh báo", "Vui lòng nhập nội dung thông báo.")
                return
            print(f"Gửi thông báo tới {selected_rooms}: {message}")
            status.set(f"Gửi thông báo tới {len(selected_rooms)} phòng.")

        btn_send_private = ttk.Button(private_frame, text="📤 Gửi", command=send_private)
        btn_send_private.pack(pady=5)

    render_type_selection()

def show_warning_window(parent):
    # Ẩn giao diện chính
    parent.withdraw()

    win = tk.Toplevel(parent)
    win.title("⚠️ Gửi cảnh báo")

    # Đảm bảo khi đóng cửa sổ con sẽ hiện lại giao diện chính
    def on_close():
        win.destroy()
        parent.deiconify()

    win.protocol("WM_DELETE_WINDOW", on_close)

    # Nút quay lại ở đầu cửa sổ để đóng và trở về giao diện chính
    header = tk.Frame(win)
    header.pack(fill='x', padx=5, pady=5)
    back_btn = tk.Button(header, text="⬅️ Quay lại", command=on_close)
    back_btn.pack(side='left')

    # Chọn phòng nhận cảnh báo
    left_frame = tk.LabelFrame(win, text="⚠️ Chọn phòng nhận cảnh báo:")
    left_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    rooms_list = tk.Listbox(left_frame, selectmode='multiple', height=6)
    for r in rooms:
        rooms_list.insert(tk.END, r)
    rooms_list.pack()

    # Cảnh báo riêng có sẵn + thủ công
    right_frame = tk.LabelFrame(win, text="🔔 Cảnh báo có sẵn + thủ công:")
    right_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)

    predefined_warn = [
        "Bạn đã quá hạn nộp tiền trọ.",
        "Hợp đồng của bạn sắp hết hạn vui lòng gia hạn thêm."
    ]
    warn_vars = [tk.BooleanVar(value=False) for _ in predefined_warn]
    for i, msg in enumerate(predefined_warn):
        cb = tk.Checkbutton(right_frame, text=msg, variable=warn_vars[i], anchor='w')
        cb.pack(anchor='w')

    tk.Label(right_frame, text="📝 Nhập cảnh báo:").pack(anchor='w')
    manual_warn = tk.Text(right_frame, height=3, width=40)
    manual_warn.pack()

    status = tk.StringVar(value="Chưa gửi")
    status_label = tk.Label(win, textvariable=status)
    status_label.pack(side="bottom", fill="x")

    def build_message(selected_warnings, manual):
        msgs = [m for m in selected_warnings if m]
        final = " ".join(msgs)
        manual_msg = manual.strip()
        if manual_msg:
            if final:
                final = final + " " + manual_msg
            else:
                final = manual_msg
        return final.strip()

    def send_warning():
        indices = rooms_list.curselection()
        if not indices:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn ít nhất một phòng.")
            return
        selected_rooms = [rooms_list.get(i) for i in indices]
        selected_warns = [predefined_warn[i] for i, v in enumerate(warn_vars) if v.get()]
        manual = manual_warn.get("1.0", tk.END)
        message = build_message(selected_warns, manual)
        if not message:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập nội dung cảnh báo.")
            return
        print(f"Gửi cảnh báo tới {selected_rooms}: {message}")
        status.set(f"Gửi cảnh báo tới {len(selected_rooms)} phòng.")

    btn_send = ttk.Button(right_frame, text="📤 Gửi", command=send_warning)
    btn_send.pack(pady=5)

def main():
    root = tk.Tk()
    root.title("Hệ thống quản lý nhà trọ")

    # Nút quay lại ở đầu giao diện chính để thoát ứng dụng
    top_nav = tk.Frame(root)
    top_nav.pack(fill='x')
    back_main = tk.Button(top_nav, text="⬅️ Quay lại", command=root.destroy)
    back_main.pack(side='left', padx=5, pady=5)

    # Giao diện chính
    frame = tk.Frame(root)
    frame.pack(padx=20, pady=20)

    # Màu cho các nút chính (không dùng ttk để đảm bảo màu đúng trên mọi nền)
    btn_report = tk.Button(frame, text="📈 Tạo báo cáo doanh thu tháng",
                           command=lambda: show_monthly_report(root),
                           bg="#1E90FF", fg="white",
                           activebackground="#1C86EE", activeforeground="white",
                           padx=10, pady=6)
    btn_report.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

    btn_notify = tk.Button(frame, text="📣 Gửi thông báo",
                           command=lambda: show_notify_window(root),
                           bg="#FFD700", fg="black",
                           activebackground="#FFC000", activeforeground="black",
                           padx=10, pady=6)
    btn_notify.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

    btn_warning = tk.Button(frame, text="⚠️ Gửi cảnh báo",
                           command=lambda: show_warning_window(root),
                           bg="#FF4C4C", fg="white",
                           activebackground="#E03333", activeforeground="white",
                           padx=10, pady=6)
    btn_warning.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

    frame.grid_columnconfigure(0, weight=1)

    root.mainloop()
