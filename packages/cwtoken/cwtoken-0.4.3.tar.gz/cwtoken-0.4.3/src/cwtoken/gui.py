import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from .key_manager import cwapi
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from dotenv import load_dotenv
import json
import textwrap


root = tk.Tk()


logged_in = False
save_cred = tk.IntVar()
save_csv = tk.IntVar()
save_query = tk.IntVar()
clubcode_entry = None
token_entry = None
global_data_text = None
df = None
global_client = None
global_query = None

def try_login():
    global global_client
    clubcode = clubcode_entry.get()
    api_token = token_entry.get()
    save_credentials = save_cred.get()

    global_client = cwapi(api_token, clubcode=clubcode)
    if global_client.access_token is not None:
        logged_in = True

        if save_credentials == 1:
            config_dir = Path.home() / ".cwtoken"
            config_dir.mkdir(exist_ok=True)
            cred_path = config_dir / "static_api.env"
            with open(cred_path, "w") as f:
                f.write(f"CLUBCODE={global_client.clubcode}\nAPI_TOKEN={global_client.api_token}\n")

        show_main_app()
    else:
        messagebox.showerror("Login Failed", "Invalid clubcode or API token.")
       

def save_query():
    file_path = filedialog.asksaveasfilename(
        defaultextension=".json",
        filetypes=[
            ("JSON files", "*.json"),
            ("All files", "*.*")
        ],
        title="Save Query As"
    )
    dir_path = os.path.dirname(file_path)
    if not file_path:
        return
    _, ext = os.path.splitext(file_path)
    
    data = {
        "query": global_query.compose_url(),
        "table": global_query.endpoint,
        "select": global_query._params.get('select'),
        "filters": getattr(global_query, "_filters", None),
        "order": global_query._params.get('order'),
        "limit": global_query._params.get('limit'),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "club_code": global_client.clubcode,
        "last_run_at": datetime.now(timezone.utc).isoformat(),
        "load_count": 1,
    }
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Query + metadata saved to {file_path}")

def insert_keywords():
    global global_query
    today = datetime.today().date()
    keywords = {
            "today": today,
            "tomorrow": today + timedelta(days=1),
            "yesterday": today - timedelta(days=1),
            "beginning_of_month": today.replace(day=1)
        }
    for i, f in enumerate(global_query._filters):
        global_query._filters[i] = f.format(**keywords)

def run_query():
    global df
    if not global_query:
        messagebox.showerror("Input Error", "Please enter a query URL.")
        return
    if not global_client.access_token:
        messagebox.showerror("Error", "Access token missing. Please login again.")
        return
    insert_keywords()
    print(f"Running query: {global_query.compose_url()}")
    df = global_query.fetch(diagnostic=True)
    if df is None:
        messagebox.showerror("Error", "Invalid query")
        return
    show_results()

def load_query():
    global global_query
    finish = 1
    while finish:
        file_path = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ],
            title="Open query file"
        )
        dir_path = os.path.dirname(file_path)
        
        if not file_path:
            return
            
        _, ext = os.path.splitext(file_path) 
        if os.path.isdir(dir_path):
            finish = 0
            with open(file_path, 'r') as json_File:
                load_file = json.load(json_File)
            global_query = global_client.table(load_file["table"])
            if load_file.get("select"):
                global_query.select(load_file.get("select"))
            if load_file.get("filters"):
                global_query.filters(load_file.get("filters"))
            if load_file.get("order"):
                global_query.order(load_file.get("order"))
            if load_file.get("limit"):
                global_query.limit(load_file["limit"])
            current_count = load_file["load_count"]
            load_file["load_count"] = current_count + 1
            
            load_file["last_run_at"] = datetime.now(timezone.utc).isoformat()

            with open(file_path, "w") as f:
                json.dump(load_file, f, indent=4)

        else:
            print("Error: file path doesn't exist")

def save_file():
    finish = 1
    while finish:
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Save CSV As"
        )
        dir_path = os.path.dirname(file_path)
        if not file_path:
            return
        if os.path.isdir(dir_path):
            df.to_csv(f"{file_path}")
            finish = 0
        else:
            print("Error: file path doesn't exist")

def generatepy():
    script_content = textwrap.dedent(f"""
        from cwtoken import cwapi
        from datetime import datetime, timedelta

        today = datetime.today().date()
        keywords = {{
            "today": today,
            "tomorrow": today + timedelta(days=1),
            "yesterday": today - timedelta(days=1),
            "beginning_of_month": today.replace(day=1)
        }}

        clubcode = '{global_client.clubcode}'
        api_token = '{global_client.api_token}'
        
        client = cwapi(api_token=api_token,clubcode=clubcode)
        
        raw_request = '{global_query.compose_url()}'
        request = raw_request.format(**keywords)
        
        df = client.raw_query(request).fetch()
        print(df)
    """)

    finish = 1
    while finish:
        file_path = filedialog.asksaveasfilename(
            defaultextension=".py",
            filetypes=[("py files", "*.py")],
            title="Save PY As"
        )
        dir_path = os.path.dirname(file_path)
        if not file_path:
            return
        if os.path.isdir(dir_path):
            with open(file_path, "w") as f:
                f.write(script_content)
            finish = 0
            print(f"PY file saved to {file_path}")
        else:
            print("Error: file path doesn't exist")

# --- Pages ---

def show_results():
    for widget in root.winfo_children():
        widget.destroy()

    root.geometry("800x600")
    root.title("Query Results")

    if not df.empty:
        container = tk.Frame(root)
        container.pack(fill="both", expand=True, padx=10, pady=10)


        display_df = tk.LabelFrame(container, text="Your query results")
        display_df.pack(fill="both", expand=True)


        tv1 = ttk.Treeview(display_df)
        tv1.pack(side="left", fill="both", expand=True)
        treescrolly = tk.Scrollbar(display_df, orient="vertical", command=tv1.yview)
        treescrollx = tk.Scrollbar(container, orient="horizontal", command=tv1.xview)
        tv1.configure(xscrollcommand=treescrollx.set, yscrollcommand=treescrolly.set)
        
        treescrolly.pack(side="right", fill="y")
        treescrollx.pack(side="bottom", fill="x")
        
        tv1["columns"] = list(df.columns)
        tv1["show"] = "headings"
        
        for column in tv1["columns"]:
            tv1.heading(column, text=column)
        
        df_rows = df.to_numpy().tolist()
        tv1["displaycolumns"] = ()
        for row in df_rows:
            tv1.insert("", "end", values=row)
        tv1["displaycolumns"] = list(df.columns)
    else:
        tk.Label(root, text="Query returned empty array!", font=("Arial", 14)).pack(pady=10, anchor="w", padx=10)



    button_frame = tk.Frame(root)
    button_frame.pack(pady=20)

    tk.Button(button_frame, text="Save to CSV", command=save_file).pack(side="left", padx=20)
    tk.Button(button_frame, text="Generate PY file", command=generatepy).pack(side="left", padx=20)
    tk.Button(button_frame, text="Back to Query Creator", command=show_main_app).pack(side="left", padx=20)

            
def show_main_app():
    global data_text, save_csv, save_query, global_query
    for widget in root.winfo_children():
        widget.destroy()
    
    global_query = None
    
    root.geometry("800x600")
    root.title("POSTGREST data request")

    # make columns expand
    root.columnconfigure(0, weight=0)  # labels don't expand
    root.columnconfigure(1, weight=1)  # entries expand
    root.columnconfigure(2, weight=0)  # buttons don't expand
    
    tk.Label(
        root, text=f"Welcome! Clubcode: {global_client.clubcode}", font=("Arial", 14)
    ).grid(row=0, column=0, pady=10, sticky="w", padx=10, columnspan=3)
    
    desc_text = (
        "Enter your PostgREST API URL below.\n\n"
        "1. Add the table you want to query (press Add).\n"
        "2. Add any column selections, filters, or parameters (press Add each time).\n"
        "3. Save the query (optional) and press Run to fetch results.\n\n"
        "You can also save outputs from the results page."
    )

    tk.Label(root, text=desc_text, justify="left", wraplength=600).grid(
        row=1, column=0, padx=10, pady=(0, 10), sticky="w", columnspan=3
    )
    def update_preview():
        if global_query:
            query_preview_var.set("Query preview:" + " " + global_query.compose_url())
        else:
            query_preview_var.set("Query preview:")
    def start_query():
        global global_query
        global_query = global_client.table(table_entry.get())
        update_preview()
    def load_update():
        load_query()
        update_preview()
    def clear_query():
        global global_query
        global_query = None
        update_preview()
    
    options_frame = tk.Frame(root)
    options_frame.grid(row=2, column=0, sticky="w", padx=10, columnspan=3)
    
    tk.Button(options_frame, text="Save query", command=save_query).pack(side="left")
    tk.Button(options_frame, text="Load query", command=load_update).pack(side="left", padx=10)
    
    # --- Inputs ---
    tk.Label(root, text="Table:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
    table_entry = tk.Entry(root, width=20)
    table_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
    tk.Button(root, text="Add",command=start_query).grid(row=3, column=2, padx=5, pady=5, sticky="w")
    
    tk.Label(root, text="Select:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
    select_entry = tk.Entry(root, width=50)
    select_entry.grid(row=4, column=1, padx=5, pady=5, sticky="ew")
    tk.Button(root, text="Add",command=lambda: (global_query.select(select_entry.get()), select_entry.delete(0, tk.END), update_preview())).grid(row=4, column=2, padx=5, pady=5, sticky="w")
    
    tk.Label(root, text="Filter:").grid(row=5, column=0, padx=5, pady=5, sticky="w")
    filter_entry = tk.Entry(root, width=50)
    filter_entry.grid(row=5, column=1, padx=5, pady=5, sticky="ew")
    tk.Button(root, text="Add",command=lambda: (global_query.filters(filter_entry.get()), filter_entry.delete(0, tk.END), update_preview())).grid(row=5, column=2, padx=5, pady=5, sticky="w")
    
    tk.Label(root, text="Order:").grid(row=6, column=0, padx=5, pady=5, sticky="w")
    order_entry = tk.Entry(root, width=50)
    order_entry.grid(row=6, column=1, padx=5, pady=5, sticky="ew")
    tk.Button(root, text="Add",command=lambda: (global_query.order(order_entry.get()), order_entry.delete(0, tk.END), update_preview())).grid(row=6, column=2, padx=5, pady=5, sticky="w")
    
    tk.Label(root, text="Limit:").grid(row=7, column=0, padx=5, pady=5, sticky="w")
    limit_entry = tk.Entry(root, width=50)
    limit_entry.grid(row=7, column=1, padx=5, pady=5, sticky="ew")
    tk.Button(root, text="Add",command=lambda: (global_query.limit(limit_entry.get()), limit_entry.delete(0, tk.END), update_preview())).grid(row=7, column=2, padx=5, pady=5, sticky="w")
    
    query_preview_var = tk.StringVar()
    query_preview_var.set("Query preview:")  # initial text
    preview_label = tk.Label(root, textvariable=query_preview_var, justify="left", wraplength=700)
    preview_label.grid(row=8, column=0, columnspan=3, padx=5, pady=5, sticky="w")
    
    # --- Bottom ---
    bottom_frame = tk.Frame(root)
    bottom_frame.grid(row=9, column=0, columnspan=3, sticky="w", pady=10, padx=10)
    tk.Button(bottom_frame, text="Run query", command=run_query).pack(side="left", padx=10)
    tk.Button(bottom_frame, text="Clear Query", command=clear_query).pack(side="left", padx=10)



def setup_login_screen():
    global clubcode_entry, token_entry
    root.title("Clubwise Login")
    root.geometry("300x220")
    
    tk.Label(root, text="Enter Clubcode:").pack(pady=5)
    clubcode_entry = tk.Entry(root)
    clubcode_entry.pack()
    
    tk.Label(root, text="Enter API Token:").pack(pady=5)
    token_entry = tk.Entry(root, show="*")
    token_entry.pack()
    
    tk.Checkbutton(root, text="Save credentials?", variable=save_cred).pack()
    config_dir = Path.home() / ".cwtoken"
    cred_path = config_dir / "static_api.env"

    if cred_path.exists():
        try:
            with open(cred_path, 'r') as f:
                load_dotenv(dotenv_path=cred_path)
                clubcode = os.getenv("CLUBCODE")
                api_token = os.getenv("API_TOKEN")

                clubcode_entry.insert(0, clubcode)
                token_entry.insert(0, api_token)
        except ValueError:
            print("Credential file format invalid.")

    tk.Button(root, text="Login", command=try_login).pack(pady=20)


def main():
    setup_login_screen()
    root.mainloop()

if __name__ == "__main__":
    main()
