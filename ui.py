import tkinter as tk
from tkinter import ttk, messagebox
import asyncio
import ast
import threading


class MeshWeaverUI:

    def __init__(
        self,
        node,
        node_loop
    ):

        self.node = node
        self.node_loop = node_loop

        # =====================================================
        # WINDOW
        # =====================================================

        self.root = tk.Tk()

        self.root.title(
            "MeshWeaver - P2P Async Task Broker"
        )

        self.root.geometry(
            "1100x720"
        )

        self.root.minsize(
            950,
            600
        )

        # =====================================================
        # COLORS
        # =====================================================

        self.bg = "#0f172a"
        self.panel = "#1e293b"
        self.panel_dark = "#111827"
        self.text = "#f8fafc"
        self.muted = "#94a3b8"
        self.accent = "#38bdf8"
        self.green = "#22c55e"
        self.red = "#ef4444"
        self.yellow = "#facc15"

        self.root.configure(
            bg=self.bg
        )

        self.setup_style()

        self.create_layout()

        self.update_dashboard()

    # =========================================================
    # STYLE
    # =========================================================

    def setup_style(self):

        style = ttk.Style()

        style.theme_use(
            "clam"
        )

        style.configure(
            "Treeview",
            background=self.panel_dark,
            foreground=self.text,
            fieldbackground=self.panel_dark,
            rowheight=32,
            borderwidth=0,
            font=("Segoe UI", 9)
        )

        style.configure(
            "Treeview.Heading",
            background=self.panel,
            foreground=self.text,
            font=("Segoe UI", 9, "bold"),
            borderwidth=0
        )

        style.map(
            "Treeview",
            background=[
                ("selected", "#334155")
            ],
            foreground=[
                ("selected", self.text)
            ]
        )

    # =========================================================
    # MAIN LAYOUT
    # =========================================================

    def create_layout(self):

        # =====================================================
        # HEADER
        # =====================================================

        header = tk.Frame(
            self.root,
            bg=self.panel,
            height=80
        )

        header.pack(
            fill="x"
        )

        header.pack_propagate(
            False
        )

        title_frame = tk.Frame(
            header,
            bg=self.panel
        )

        title_frame.pack(
            side="left",
            padx=25
        )

        tk.Label(
            title_frame,
            text="MESHWEAVER",
            font=("Segoe UI", 23, "bold"),
            fg=self.text,
            bg=self.panel
        ).pack(
            anchor="w"
        )

        tk.Label(
            title_frame,
            text="P2P ASYNC TASK BROKER",
            font=("Segoe UI", 9),
            fg=self.muted,
            bg=self.panel
        ).pack(
            anchor="w"
        )

        self.status_label = tk.Label(
            header,
            text="● ONLINE",
            font=("Segoe UI", 11, "bold"),
            fg=self.green,
            bg=self.panel
        )

        self.status_label.pack(
            side="right",
            padx=25
        )

        # =====================================================
        # MAIN CONTENT
        # =====================================================

        main = tk.Frame(
            self.root,
            bg=self.bg
        )

        main.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )

        # =====================================================
        # LEFT PANEL
        # =====================================================

        left = tk.Frame(
            main,
            bg=self.bg,
            width=300
        )

        left.pack(
            side="left",
            fill="y",
            padx=(0, 15)
        )

        left.pack_propagate(
            False
        )

        # -----------------------------------------------------
        # NODE INFORMATION
        # -----------------------------------------------------

        node_card = tk.Frame(
            left,
            bg=self.panel
        )

        node_card.pack(
            fill="x",
            pady=(0, 15)
        )

        tk.Label(
            node_card,
            text="NODE INFORMATION",
            font=("Segoe UI", 11, "bold"),
            fg=self.text,
            bg=self.panel
        ).pack(
            anchor="w",
            padx=18,
            pady=(15, 10)
        )

        self.node_id_label = self.info_label(
            node_card,
            "Node ID: Loading..."
        )

        self.port_label = self.info_label(
            node_card,
            "Port: Loading..."
        )

        self.peer_count_label = self.info_label(
            node_card,
            "Peers: 0"
        )

        # -----------------------------------------------------
        # SYSTEM LOAD
        # -----------------------------------------------------

        system_card = tk.Frame(
            left,
            bg=self.panel
        )

        system_card.pack(
            fill="x"
        )

        tk.Label(
            system_card,
            text="SYSTEM LOAD",
            font=("Segoe UI", 11, "bold"),
            fg=self.text,
            bg=self.panel
        ).pack(
            anchor="w",
            padx=18,
            pady=(15, 15)
        )

        self.cpu_label = self.info_label(
            system_card,
            "CPU: 0%"
        )

        self.cpu_bar = ttk.Progressbar(
            system_card,
            orient="horizontal",
            mode="determinate",
            maximum=100
        )

        self.cpu_bar.pack(
            fill="x",
            padx=18,
            pady=(0, 10)
        )

        self.ram_label = self.info_label(
            system_card,
            "RAM: 0%"
        )

        self.ram_bar = ttk.Progressbar(
            system_card,
            orient="horizontal",
            mode="determinate",
            maximum=100
        )

        self.ram_bar.pack(
            fill="x",
            padx=18,
            pady=(0, 18)
        )

        # =====================================================
        # RIGHT PANEL
        # =====================================================

        right = tk.Frame(
            main,
            bg=self.bg
        )

        right.pack(
            side="left",
            fill="both",
            expand=True
        )

        # =====================================================
        # NETWORK PEERS
        # =====================================================

        peer_card = tk.Frame(
            right,
            bg=self.panel
        )

        peer_card.pack(
            fill="both",
            expand=True,
            pady=(0, 15)
        )

        tk.Label(
            peer_card,
            text="NETWORK PEERS",
            font=("Segoe UI", 11, "bold"),
            fg=self.text,
            bg=self.panel
        ).pack(
            anchor="w",
            padx=18,
            pady=15
        )

        columns = (
            "node_id",
            "address",
            "cpu",
            "ram"
        )

        self.peer_table = ttk.Treeview(
            peer_card,
            columns=columns,
            show="headings"
        )

        self.peer_table.heading(
            "node_id",
            text="NODE ID"
        )

        self.peer_table.heading(
            "address",
            text="ADDRESS"
        )

        self.peer_table.heading(
            "cpu",
            text="CPU"
        )

        self.peer_table.heading(
            "ram",
            text="RAM"
        )

        self.peer_table.column(
            "node_id",
            width=190
        )

        self.peer_table.column(
            "address",
            width=160
        )

        self.peer_table.column(
            "cpu",
            width=80
        )

        self.peer_table.column(
            "ram",
            width=80
        )

        self.peer_table.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(0, 15)
        )

        # =====================================================
        # TASK SUBMISSION
        # =====================================================

        task_card = tk.Frame(
            right,
            bg=self.panel
        )

        task_card.pack(
            fill="x",
            pady=(0, 15)
        )

        tk.Label(
            task_card,
            text="TASK SUBMISSION",
            font=("Segoe UI", 11, "bold"),
            fg=self.text,
            bg=self.panel
        ).grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="w",
            padx=18,
            pady=(15, 10)
        )

        tk.Label(
            task_card,
            text="Function",
            font=("Segoe UI", 9),
            fg=self.muted,
            bg=self.panel
        ).grid(
            row=1,
            column=0,
            sticky="w",
            padx=18,
            pady=5
        )

        self.function_entry = tk.Entry(
            task_card,
            bg=self.panel_dark,
            fg=self.text,
            insertbackground=self.text,
            relief="flat",
            font=("Segoe UI", 10)
        )

        self.function_entry.insert(
            0,
            "square_sum"
        )

        self.function_entry.grid(
            row=1,
            column=1,
            sticky="ew",
            padx=18,
            pady=5
        )

        tk.Label(
            task_card,
            text="Arguments",
            font=("Segoe UI", 9),
            fg=self.muted,
            bg=self.panel
        ).grid(
            row=2,
            column=0,
            sticky="w",
            padx=18,
            pady=5
        )

        self.args_entry = tk.Entry(
            task_card,
            bg=self.panel_dark,
            fg=self.text,
            insertbackground=self.text,
            relief="flat",
            font=("Segoe UI", 10)
        )

        self.args_entry.insert(
            0,
            "10, 20"
        )

        self.args_entry.grid(
            row=2,
            column=1,
            sticky="ew",
            padx=18,
            pady=5
        )

        task_card.columnconfigure(
            1,
            weight=1
        )

        self.submit_button = tk.Button(
            task_card,
            text="SUBMIT TASK",
            command=self.submit_task,
            bg=self.accent,
            fg=self.bg,
            activebackground="#7dd3fc",
            activeforeground=self.bg,
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2",
            padx=25,
            pady=8
        )

        self.submit_button.grid(
            row=3,
            column=0,
            columnspan=2,
            pady=12
        )

        # =====================================================
        # RESULT
        # =====================================================

        result_card = tk.Frame(
            right,
            bg=self.panel
        )

        result_card.pack(
            fill="x"
        )

        tk.Label(
            result_card,
            text="TASK RESULT",
            font=("Segoe UI", 10, "bold"),
            fg=self.text,
            bg=self.panel
        ).pack(
            anchor="w",
            padx=18,
            pady=(12, 5)
        )

        self.result_label = tk.Label(
            result_card,
            text="No task executed yet.",
            font=("Consolas", 10),
            fg=self.muted,
            bg=self.panel,
            anchor="w"
        )

        self.result_label.pack(
            fill="x",
            padx=18,
            pady=(0, 12)
        )

        # =====================================================
        # LIVE LOG
        # =====================================================

        log_frame = tk.Frame(
            self.root,
            bg=self.panel
        )

        log_frame.pack(
            fill="x",
            padx=20,
            pady=(0, 20)
        )

        tk.Label(
            log_frame,
            text="LIVE SYSTEM LOG",
            font=("Segoe UI", 10, "bold"),
            fg=self.text,
            bg=self.panel
        ).pack(
            anchor="w",
            padx=15,
            pady=(10, 5)
        )

        self.log_box = tk.Text(
            log_frame,
            height=5,
            bg=self.panel_dark,
            fg=self.muted,
            insertbackground=self.text,
            relief="flat",
            font=("Consolas", 9)
        )

        self.log_box.pack(
            fill="x",
            padx=15,
            pady=(0, 12)
        )

        self.log(
            "MeshWeaver UI initialized."
        )

        self.log(
            f"Connected to node on port {self.node.port}."
        )

    # =========================================================
    # LABEL HELPER
    # =========================================================

    def info_label(
        self,
        parent,
        text
    ):

        label = tk.Label(
            parent,
            text=text,
            font=("Segoe UI", 10),
            fg=self.muted,
            bg=self.panel
        )

        label.pack(
            anchor="w",
            padx=18,
            pady=5
        )

        return label

    # =========================================================
    # LOGGING
    # =========================================================

    def log(
        self,
        message
    ):

        try:

            self.log_box.insert(
                "end",
                f"{message}\n"
            )

            self.log_box.see(
                "end"
            )

        except Exception:
            pass

    # =========================================================
    # DASHBOARD UPDATE
    # =========================================================

    def update_dashboard(self):

        try:

            node_id = self.node.node_id

            if node_id:

                self.node_id_label.config(
                    text=(
                        "Node ID: "
                        f"{node_id[:16]}..."
                    )
                )

            self.port_label.config(
                text=f"Port: {self.node.port}"
            )

            peer_count = (
                self.node.dht.peer_count()
            )

            self.peer_count_label.config(
                text=f"Peers: {peer_count}"
            )

            cpu = self.node.load.get(
                "cpu",
                0
            )

            ram = self.node.load.get(
                "ram",
                0
            )

            self.cpu_label.config(
                text=f"CPU: {cpu}%"
            )

            self.ram_label.config(
                text=f"RAM: {ram}%"
            )

            self.cpu_bar["value"] = cpu
            self.ram_bar["value"] = ram

            self.update_peers()

        except Exception:
            pass

        self.root.after(
            2000,
            self.update_dashboard
        )

    # =========================================================
    # PEER TABLE
    # =========================================================

    def update_peers(self):

        for item in self.peer_table.get_children():

            self.peer_table.delete(
                item
            )

        peers = self.node.dht.peers()

        for peer in peers.values():

            load = peer.get(
                "load",
                {}
            )

            cpu = load.get(
                "cpu",
                0
            )

            ram = load.get(
                "ram",
                0
            )

            self.peer_table.insert(
                "",
                "end",
                values=(
                    peer["node_id"][:12],
                    f"{peer['host']}:{peer['port']}",
                    f"{cpu}%",
                    f"{ram}%"
                )
            )

    # =========================================================
    # TASK SUBMISSION
    # =========================================================

    def submit_task(self):

        function_name = (
            self.function_entry
            .get()
            .strip()
        )

        argument_text = (
            self.args_entry
            .get()
            .strip()
        )

        if not function_name:

            messagebox.showerror(
                "Task Error",
                "Please enter a function name."
            )

            return

        # -----------------------------------------------------
        # Parse arguments
        # -----------------------------------------------------

        try:

            if argument_text:

                args = ast.literal_eval(
                    "(" +
                    argument_text +
                    ",)"
                )

            else:

                args = ()

        except Exception:

            messagebox.showerror(
                "Task Error",
                "Invalid arguments."
            )

            return

        # -----------------------------------------------------
        # Find function
        # -----------------------------------------------------

        try:

            from demo_tasks import (
                square_sum,
                complex_math,
                matrix_sum
            )

            functions = {

                "square_sum":
                    square_sum,

                "complex_math":
                    complex_math,

                "matrix_sum":
                    matrix_sum
            }

            function = functions.get(
                function_name
            )

            if function is None:

                messagebox.showerror(
                    "Task Error",
                    f"Unknown function: "
                    f"{function_name}"
                )

                return

        except Exception as error:

            messagebox.showerror(
                "Task Error",
                str(error)
            )

            return

        # -----------------------------------------------------
        # UI state
        # -----------------------------------------------------

        self.submit_button.config(
            state="disabled",
            text="RUNNING..."
        )

        self.result_label.config(
            text="Task is being processed...",
            fg=self.yellow
        )

        self.log(
            f"[Task] Submitted: {function_name}"
        )

        # -----------------------------------------------------
        # Run task in background
        # -----------------------------------------------------

        thread = threading.Thread(
            target=self.run_task,
            args=(
                function,
                args
            ),
            daemon=True
        )

        thread.start()

    # =========================================================
    # RUN ASYNC TASK ON NODE'S EVENT LOOP
    # =========================================================

    def run_task(
        self,
        function,
        args
    ):

        try:

            future = (
                asyncio
                .run_coroutine_threadsafe(
                    self.node.submit_task(
                        function,
                        *args
                    ),
                    self.node_loop
                )
            )

            result = future.result(
                timeout=30
            )

            self.root.after(
                0,
                lambda: self.show_result(
                    result
                )
            )

        except Exception as error:

            self.root.after(
                0,
                lambda: self.show_result(
                    f"ERROR: {error}"
                )
            )

    # =========================================================
    # SHOW RESULT
    # =========================================================

    def show_result(
        self,
        result
    ):

        self.submit_button.config(
            state="normal",
            text="SUBMIT TASK"
        )

        if isinstance(
            result,
            str
        ) and result.startswith(
            "ERROR:"
        ):

            self.result_label.config(
                text=result,
                fg=self.red
            )

            self.log(
                f"[Task] {result}"
            )

            return

        self.result_label.config(
            text=f"Result: {result}",
            fg=self.green
        )

        self.log(
            f"[Task] COMPLETED -> {result}"
        )

    # =========================================================
    # RUN APPLICATION
    # =========================================================

    def run(self):

        self.root.mainloop()